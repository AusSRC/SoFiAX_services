import logging
from survey.models import Comment, Tag, TagSourceDetection


logging.basicConfig(level=logging.INFO)


def add_tag(request, source_detection, tag_select_input='tag_select', tag_create_input='tag_create'):
    tag = None
    tag_select = request.POST[tag_select_input]
    tag_create = str(request.POST[tag_create_input])
    if tag_select == 'None':
        if tag_create != '':
            logging.info(f'Creating new tag: {tag_create}')
            tag = Tag.objects.create(
                name=tag_create
            )
    else:
        tag = Tag.objects.get(id=int(tag_select))
        logging.info(f'Retrieving tag: {tag.name}')
    if tag is not None:
        logging.info(f'Adding tag {tag.name} to source detection {source_detection.id}')
        TagSourceDetection.objects.create(
            source_detection=source_detection,
            tag=tag,
            author=str(request.user)
        )
    return


def add_comment(request, detection, comment_input='comment'):
    comment = str(request.POST[comment_input])
    if comment != '':
        logging.info(f'Adding comment {comment} to detection {detection.name}')
        Comment.objects.create(
            comment=comment,
            author=str(request.user),
            detection=detection
        )
    return
