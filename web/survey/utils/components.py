import re
from survey.models import Run, Detection, SurveyComponent


def wallaby_survey_components():
    components_dict = {}
    for sc in SurveyComponent.objects.all():
        components_dict[sc.name] = sc.runs
    return components_dict


def wallaby_release_name(name):
    """Release name from detection name

    """
    parts = re.split('[+-]', name.replace('SoFiA', 'WALLABY').replace('_', ' '))
    return re.search('[+-]', name).group().join(
        list(map(lambda x: x.split('.')[0], parts))
    )


def get_survey_component(detection):
    run = detection.run
    survey_components = wallaby_survey_components()
    for k, v in survey_components.items():
        if run.name in v:
            return k
    raise Exception("Detection and run not found in survey component list.")
