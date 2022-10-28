import re
from survey.models import Run, Detection


WALLABY_SURVEY_COMPONENTS = {
    'Pre-phase2': ['Hydra_DR1', 'Hydra_DR2', 'NGC4636_DR1', 'Norma_DR1'],
    'Phase2-NGC5044_DR1': ['NGC5044_4'],
    'Phase2-NGC5044_DR2': [
        '198-13_198-19_204-17',
        '198-19_204-17_204-22',
        '198-13_a',
        '198-13_r',
        '198-13',
        '198-19_198-13',
        '198-19',
        '198-19_r',
        '198-19_b',
        '204-22_b',
        '204-22_l',
        '204-22',
        '204-17_204-22',
        '204-17_a',
        '204-17_l',
        '204-17',
    ],
    'Phase2-Other': ['Vela', 'NGC4808']
}


def WALLABY_release_name(name):
    """Release name from detection name

    """
    parts = re.split('[+-]', name.replace('SoFiA', 'WALLABY'))
    return re.search('[+-]', name).group().join(
        list(map(lambda x: x.split('.')[0], parts))
    )


def get_survey_component(detection):
    run = detection.run
    for k, v in WALLABY_SURVEY_COMPONENTS.items():
        if run.name in v:
            return k
    raise Exception("Detection and run not found in survey component list.")
