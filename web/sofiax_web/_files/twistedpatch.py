"""
Code to add some basic nevow functionality back to twisted.

This needs ot be imported as early as possible after importing twisted.web
for the first time.

The features were adding include:

* have nevow tag[] syntax again.
* to swallow attributes with None values in tags
* (Ab) use slotData to manage what was nevow:data, pass it into the
  render method as tag.slotData
"""

#c Copyright 2008-2020, the GAVO project
#c
#c This program is free software, covered by the GNU GPL.  See the
#c COPYING file in the source distribution.


from twisted.web import _flatten
from twisted.web import _stan 
from twisted.web import template
from future.utils import iteritems


class _NoData(object):
    """A sentinel to signifiy no data was passed to clone.
    """
    def __bool__(self):
        return False


_StanTag = _stan.Tag


class Tag(_StanTag):
    def __init__(self, tagName, attributes=None, children=None, render=None,
                 filename=None, lineNumber=None, columnNumber=None, data=None):
        _StanTag.__init__(self, tagName, attributes, children, render, 
            filename, lineNumber, columnNumber)
        self.slotData = data

    def __getitem__(self, stuff):
        if isinstance(stuff, (list, tuple)):
            return self(*stuff)
        else:
            return self(stuff)
    
    def __call__(self, *items, **attrs):
        for key, value in list(attrs.items()):
            if value is None:
                attrs.pop(key)
        return _StanTag.__call__(self, *items, **attrs)

    def _cloneSlotData(self, deep, newData):
        """returns a clone of this tag's slot data.

        This is always a copy if slotData is a dict; otherwise, for
        non-deep copying we hope people don't change data and we
        save copying.  For deep copying, we'll have to copy
        sequences, too, because the may contain tags like slot and
        such.
        """
        if not self.slotData:
            return self.slotData

        if isinstance(self.slotData, dict):
            # t.w code
            newslotdata = self.slotData.copy()
            for key in newslotdata:
                newslotdata[key] = self._clone(newslotdata[key], True, newData)
            return newslotdata
        
        if deep:
            if isinstance(self.slotData, (list, tuple)):
                return self._clone(self.slotData, True, newData)

            else:
                # we *probably* should still copy this, but that may
                # really be expensive, and we should outlaw modifying
                # data in render and data methods anyway.
                return self.slotData
        else:
            return self.slotData


    def _clone(self, obj, deep, newData):
        """
        Clone an arbitrary object; used by L{Tag.clone}.

        @param obj: an object with a clone method, a list or tuple, or something
            which should be immutable.

        @param deep: whether to continue cloning child objects; i.e. the
            contents of lists, the sub-tags within a tag.

        @return: a clone of C{obj}.
        """
        # we override this to set the slotData on tags while we're cloning
        if hasattr(obj, 'clone'):
            return obj.clone(deep, newData)
        elif isinstance(obj, (list, tuple)):
            return [self._clone(x, deep, newData) for x in obj]
        else:
            return obj


    def clone(self, deep=True, newData=_NoData):
        """
        Return a clone of this tag. If deep is True, clone all of this tag's
        children. Otherwise, just shallow copy the children list without copying
        the children themselves.
        """
        # We have to override clone because we need to manage slotData
        # somewhat more carefully now.  This is clone as of 18.9.0,
        # with newslotdata code taken out and replaced with a call
        # to _cloneSlotData; also, we're passing newData to _clone.
        if newData is _NoData:
            newData = self._cloneSlotData(deep, newData)

        if deep:
            newchildren = [self._clone(x, True, newData) 
                for x in self.children]
        else:
            newchildren = self.children[:]
        newattrs = self.attributes.copy()
        for key in list(newattrs.keys()):
            newattrs[key] = self._clone(newattrs[key], True, newData)

        newtag = Tag(
            self.tagName,
            attributes=newattrs,
            children=newchildren,
            render=self.render,
            filename=self.filename,
            lineNumber=self.lineNumber,
            columnNumber=self.columnNumber)
        newtag.slotData = newData

        return newtag

# we have to monkeypatch a couple of places in twisted.web
_stan.Tag = Tag
template.Tag = Tag
_flatten.Tag = Tag


class Raw(object):
    """a thing to stick into stan trees that can write whatever
    it wants into the serialised result.

    Just override getContent and return a byte string from it.
    """
    def getContent(self, destFile):
        raise NotImplementedError("You have to override getContent.")


# I extremely regret I have to overwrite the complex and fairly
# crazy _flattenElement from t.w._flatten, but managing
# the data attribute in any other way is just mad.
#
# This is form twisted 18.9.0, and we'll have to update it now and then.
#
# Changes are:
# * we evaluate newov:data attributes on tags (exactly like this;
#   namespace processing happens in nevow's _ToStan
# * we support Raw instances that can write whatever the
#   heck they like.
# * we render ints in the tree

def _flattenElement(request, root, write, slotData, renderFactory,
                    dataEscaper):
    """
    Make C{root} slightly more flat by yielding all its immediate contents as
    strings, deferreds or generators that are recursive calls to itself.

    @param request: A request object which will be passed to
        L{IRenderable.render}.

    @param root: An object to be made flatter.  This may be of type C{unicode},
        L{str}, L{slot}, L{Tag <twisted.web.template.Tag>}, L{tuple}, L{list},
        L{types.GeneratorType}, L{Deferred}, or an object that implements
        L{IRenderable}.

    @param write: A callable which will be invoked with each L{bytes} produced
        by flattening C{root}.

    @param slotData: A L{list} of L{dict} mapping L{str} slot names to data
        with which those slots will be replaced.

    @param renderFactory: If not L{None}, an object that provides
        L{IRenderable}.

    @param dataEscaper: A 1-argument callable which takes L{bytes} or
        L{unicode} and returns L{bytes}, quoted as appropriate for the
        rendering context.  This is really only one of two values:
        L{attributeEscapingDoneOutside} or L{escapeForContent}, depending on
        whether the rendering context is within an attribute or not.  See the
        explanation in L{writeWithAttributeEscaping}.

    @return: An iterator that eventually yields L{bytes} that should be written
        to the output.  However it may also yield other iterators or
        L{Deferred}s; if it yields another iterator, the caller will iterate
        it; if it yields a L{Deferred}, the result of that L{Deferred} will
        either be L{bytes}, in which case it's written, or another generator,
        in which case it is iterated.  See L{_flattenTree} for the trampoline
        that consumes said values.
    @rtype: An iterator which yields L{bytes}, L{Deferred}, and more iterators
        of the same type.
    """
    def keepGoing(newRoot, dataEscaper=dataEscaper,
                  renderFactory=renderFactory, write=write):
        return _flattenElement(request, newRoot, write, slotData,
                               renderFactory, dataEscaper)
    if isinstance(root, (bytes, str)):
        write(dataEscaper(root))
    elif isinstance(root, _flatten.slot):
        slotValue = _flatten._getSlotValue(root.name, slotData, root.default)
        yield keepGoing(slotValue)
    elif isinstance(root, _flatten.CDATA):
        write(b'<![CDATA[')
        write(_flatten.escapedCDATA(root.data))
        write(b']]>')
    elif isinstance(root, _flatten.Comment):
        write(b'<!--')
        write(_flatten.escapedComment(root.data))
        write(b'-->')
    elif isinstance(root, Tag):
        if "nevow:data" in root.attributes:
            root = _loadNevowData(request, root, renderFactory)
        slotData.append(root.slotData)
        if root.render is not None:
            rendererName = root.render
            rootClone = root.clone(False)
            rootClone.render = None
            renderMethod = renderFactory.lookupRenderMethod(rendererName)
            result = renderMethod(request, rootClone)
            yield keepGoing(result)
            slotData.pop()
            return

        if not root.tagName:
            yield keepGoing(root.children)
            return

        write(b'<')
        if isinstance(root.tagName, str):
            tagName = root.tagName.encode('ascii')
        else:
            tagName = root.tagName
        write(tagName)
        for k, v in iteritems(root.attributes):
            if isinstance(k, str):
                k = k.encode('ascii')
            write(b' ' + k + b'="')
            # Serialize the contents of the attribute, wrapping the results of
            # that serialization so that _everything_ is quoted.
            yield keepGoing(
                v,
                _flatten.attributeEscapingDoneOutside,
                write=_flatten.writeWithAttributeEscaping(write))
            write(b'"')
        if root.children or _flatten.nativeString(tagName) not in _flatten.voidElements:
            write(b'>')
            # Regardless of whether we're in an attribute or not, switch back
            # to the escapeForContent dataEscaper.  The contents of a tag must
            # be quoted no matter what; in the top-level document, just so
            # they're valid, and if they're within an attribute, they have to
            # be quoted so that after applying the *un*-quoting required to re-
            # parse the tag within the attribute, all the quoting is still
            # correct.
            yield keepGoing(root.children, _flatten.escapeForContent)
            write(b'</' + tagName + b'>')
        else:
            write(b' />')

    elif isinstance(root, (tuple, list, _flatten.GeneratorType)):
        for element in root:
            yield keepGoing(element)
    elif isinstance(root, _flatten.CharRef):
        escaped = '&#%d;' % (root.ordinal,)
        write(escaped.encode('ascii'))
    elif isinstance(root, _flatten.Deferred):
        yield root.addCallback(lambda result: (result, keepGoing(result)))
# For now, no coroutines in DaCHS, and stretch twisted doesn't have iscoroutine
# yet.
#    elif _flatten.iscoroutine(root):
#        d = _flatten.ensureDeferred(root)
#        yield d.addCallback(lambda result: (result, keepGoing(result)))
    elif isinstance(root, int):
        write(str(root).encode("ascii"))
    elif _flatten.IRenderable.providedBy(root):
        result = root.render(request)
        yield keepGoing(result, renderFactory=root)
    elif isinstance(root, Raw):
        stuff = root.getContent()
        assert(isinstance(stuff, bytes))
        write(stuff)
    elif root is None:
        write(b"&lt;&lt;NULL&gt;&gt;")
    else:
        raise _flatten.UnsupportedType(root)

_flatten._flattenElement = _flattenElement

def _loadNevowData(request, tag, renderFactory):
    """updates slotData on tag from its nevow:data attribute.

    This will shallow-copy tag if it changes slotData.
    """
    if "nevow:data" not in tag.attributes:
        return tag
   
    dataFct = renderFactory.lookupDataMethod(
        tag.attributes["nevow:data"])

    newData = dataFct(request, tag)

    res = tag.clone(True, newData)
    del res.attributes["nevow:data"]
    return res
