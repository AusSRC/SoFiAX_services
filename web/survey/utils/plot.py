import io
import gzip
import binascii
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from html.parser import HTMLParser
from django.utils.safestring import mark_safe


class MyHTMLChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_html = False

    def handle_starttag(self, tag, attrs):
        self.found_html = True


def check_content(content):
    """Check some string contains html.
    """
    checker = MyHTMLChecker()
    checker.feed(content)
    return checker.found_html


def product_summary_image(products, size=(3, 2), binary_image=False):
    """Generate a summary image for a detection. Currently able to handle gzipped HTML or PNG images.
    """
    if not products:
        return None

    plot = products.plot
    if plot is None:
        return None

    try:
        # Check if compressed html
        decompressed_bytes = gzip.decompress(plot)
        content = decompressed_bytes.decode('utf-8')
        if check_content(content):
            return mark_safe(content)

        # Parse matplotlib object if PNG
        img_bytes = io.BytesIO(plot)
        if Image.open(img_bytes).format == "PNG":
            fig, ax = plt.subplots(nrows=1, ncols=1)
            fig.set_size_inches(*size)
            mpl_img = mpimg.imread(img_bytes)
            plt.imshow(mpl_img)
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

            plt.close(fig)
            base_img = binascii.b2a_base64(image_data.getvalue()).decode()
            img_src = f'<img src=\"data:image/png;base64,{base_img}\", style="border-radius: 3%;">'
            return mark_safe(img_src)

        return None

    # Failing loading as png or html, return None
    except Exception as e:
        print(f"Error generating product summary image: {e}")
        return None
