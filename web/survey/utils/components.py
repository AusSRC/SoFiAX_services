import re
from django.conf import settings
from survey.models import Run, Detection, SurveyComponent


def get_survey_components():
    components_dict = {}
    for sc in SurveyComponent.objects.all():
        components_dict[sc.name] = sc.runs
    return components_dict


def get_release_name(name):
    """Return name of source depending on the project.

    """
    project = settings.PROJECT
    if project == 'dingo':
        return dingo_release_name(name)
    elif project == 'wallaby':
        return wallaby_release_name(name)
    else:
        raise Exception(f"Unexpected value for PROJECT environment variable ({project}).")


def wallaby_release_name(name):
    """Release name from detection name

    """
    parts = re.split('[+-]', name.replace('SoFiA', 'WALLABY').replace('_', ' '))
    return re.search('[+-]', name).group().join(
        list(map(lambda x: x.split('.')[0], parts))
    )


def dingo_release_name(name):
    """Release name for a DINGO source.

    """
    parts = re.split('[+-]', name.replace('SoFiA', 'DINGO').replace('_', ' '))
    return re.search('[+-]', name).group().join(parts)


def get_survey_component(detection):
    run = detection.run
    survey_components = get_survey_components()
    for k, v in survey_components.items():
        if run.name in v:
            return k
    raise Exception("Detection and run not found in survey component list.")
