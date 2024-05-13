import logging
from django.contrib import messages
from survey.models import Comment, Tag, TagDetection


logging.basicConfig(level=logging.INFO)


def _get_or_create_tag(request):
    try:
        tag_select = request.POST['tag_select']
        tag_create = str(request.POST['tag_create'])
        tag_description = str(request.POST['tag_create'])
        if tag_select == 'None':
            if tag_create == '':
                messages.error(request, "No tag selected or created")
                return
            else:
                if tag_description == '':
                    tag_description = None
                tag = Tag.objects.create(
                    name=tag_create,
                    description=tag_description
                )
        else:
            tag = Tag.objects.get(id=int(tag_select))
        return tag
    except Exception as e:
        messages.error(request, str(e))
        raise Exception(e)


def _add_tag(request, detection, tag_select_input='tag_select', tag_create_input='tag_create'):
    try:
        tag = _get_or_create_tag(request)
        TagDetection.objects.create(
            detection=detection,
            tag=tag,
            author=str(request.user)
        )
        return tag
    except Exception as e:
        messages.error(request, str(e))
        raise Exception(e)


def _add_comment(request, detection, comment_input='comment'):
    try:
        comment = str(request.POST[comment_input])
        if comment != '':
            logging.info(f'Adding comment {comment} to detection {detection.name}')
            Comment.objects.create(
                comment=comment,
                author=str(request.user),
                detection=detection
            )
        return comment
    except Exception as e:
        messages.error(request, str(e))
        raise Exception(e)
