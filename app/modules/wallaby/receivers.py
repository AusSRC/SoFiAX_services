import logging

from modules.wallaby.models import KinematicModelState


def mark_for_kinematic_modelling(sender, detection, **kwargs):
    """Released detections need kinematic modelling."""
    KinematicModelState.objects.create(detection=detection, attempted=0)
    logging.debug("Created kinematic_model_state entry for detection %s (%i)" % (detection.source_name, detection.id))
