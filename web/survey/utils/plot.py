import io
import gzip
import logging
import binascii
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from html.parser import HTMLParser
from django.utils.safestring import mark_safe


class HTMLChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_html = False

    def handle_starttag(self, tag, attrs):
        self.found_html = True


def plot_html(plot):
    """Return the content of a summary plot if it is HTML (optionally gzipped), otherwise None.

    """
    data = bytes(plot)
    if data[:2] == b'\x1f\x8b':
        try:
            data = gzip.decompress(data)
        except OSError:
            return None
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError:
        return None
    checker = HTMLChecker()
    checker.feed(content)
    return content if checker.found_html else None


def product_summary_image(products, size=(3, 2), binary_image=False):
    """Generate a summary image for a detection from the plot product, which is either
    an image (e.g. PNG) or HTML (optionally gzipped). There is no binary image for HTML plots.

    """
    if not products:
        return None
    plot = products.plot
    if plot is None:
        return None

    content = plot_html(plot)
    if content is not None:
        return None if binary_image else mark_safe(content)

    try:
        img = mpimg.imread(io.BytesIO(plot))
    except Exception as e:
        logging.error(f'Failed to read summary plot: {e}')
        return None

    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(*size)
    plt.imshow(img)
    plt.axis('off')
    plt.tight_layout()
    ax = plt.gca()
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    with io.BytesIO() as image_data:
        fig.savefig(image_data, format='png')
        if binary_image:
            plt.close(fig)
            return image_data.getvalue()

        base_img = binascii.b2a_base64(image_data.getvalue()).decode()
        img_src = f'<img src=\"data:image/png;base64,{base_img}\", style="border-radius: 3%;">'
        plt.close(fig)
        return mark_safe(img_src)
