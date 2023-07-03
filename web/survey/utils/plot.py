import io
import math
import numpy as np
import binascii
from astropy.visualization import PercentileInterval
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.image as mpimg
from django.utils.safestring import mark_safe


def summary_image(products, size=(3, 2)):
    if not products:
        return None
    plot = products.plot
    if plot is None:
        return None
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(*size)
    img = mpimg.imread(io.BytesIO(plot))
    plt.imshow(img)
    plt.axis('off')
    plt.tight_layout()
    ax = plt.gca()
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    with io.BytesIO() as image_data:
        fig.savefig(image_data, format='png')
        base_img = binascii.b2a_base64(image_data.getvalue()).decode()
        img_src = f'<img src=\"data:image/png;base64,{base_img}\">'
        plt.close(fig)
        return mark_safe(img_src)
