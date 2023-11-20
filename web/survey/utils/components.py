import re
from django.conf import settings
from survey.models import Run, Detection, SurveyComponent


def get_survey_components():
    components_dict = {}
    for sc in SurveyComponent.objects.all():
        components_dict[sc.name] = [i.run.name for i in sc.surveycomponentrun_set.all()]
    return components_dict


def get_release_name(name):
    """Return name of source depending on the project.

    """
    PROJECT = settings.PROJECT
    if PROJECT == 'DINGO':
        return dingo_release_name(name)
    elif PROJECT == 'WALLABY':
        return wallaby_release_name(name)
    else:
        parts = re.split('[+-]', name.replace('SoFiA', PROJECT).replace('_', ' '))
        return re.search('[+-]', name).group().join(parts)


def wallaby_release_name(name):
    """Release name from detection name

    """
    parts = re.split('[+-]', name.replace('SoFiA', 'WALLABY').replace('_', ' '))
    return re.search('[+-]', name).group().join(
        list(map(lambda x: x.split('.')[0], parts)))


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
