def gama_matches(sender, detection, **kwargs):
    """GAMA catalogue objects near the detection, for the manual inspection page."""
    gama = detection.detectionnearestgama_set.all()
    return {"GAMA": ", ".join([str(g.cata_id) for g in gama])}
