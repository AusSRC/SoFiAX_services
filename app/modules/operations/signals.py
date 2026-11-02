from django.dispatch import Signal

# Sent for each detection when the sources of a run are released, with the argument detection
detection_released = Signal()
