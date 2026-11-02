from modules.gaskap.properties import peak_velocity, rms_mjy, rounded, snr


def gaskap_properties(sender, detection, **kwargs):
    """Properties for the manual inspection page."""
    return {
        "Glong[deg]": rounded(detection.l, 4),
        "Glat[deg]": rounded(detection.b, 4),
        "Peak_flux[Jy]": rounded(detection.f_max, 2),
        "Vel_peak[km/s]": peak_velocity(detection),
        "Vel_range[km/s]": peak_velocity(detection),
        "RMS[mJy]": rms_mjy(detection, 2),
        "SNR": snr(detection, 2),
    }
