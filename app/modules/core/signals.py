from django.dispatch import Signal

# Sent when the manual inspection page of a detection is shown, with the argument detection.
# Receivers return a dictionary {name: value} of matches with other catalogues to show.
inspection_matches = Signal()

# Sent when the manual inspection page of a detection is shown, with the argument detection.
# Receivers return a dictionary {name: value} of properties to show instead of the default ones.
inspection_properties = Signal()
