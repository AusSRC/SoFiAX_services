"""Properties of a detection shown on the GASKAP-OH pages."""


def rounded(value, digits):
    return None if value is None else round(float(value), digits)


def peak_velocity(detection):
    # TODO: update this to use the correct velocity calculation
    if not detection.freq_peak:
        return None
    return round(299792.458 * (1.42040575e9 / float(detection.freq_peak) - 1.0), 2)


def rms_mjy(detection, digits):
    return None if detection.rms is None else round(float(detection.rms) * 10**3, digits)


def snr(detection, digits):
    if detection.f_sum is None or not detection.err_f_sum:
        return None
    return round(float(detection.f_sum) / float(detection.err_f_sum), digits)
