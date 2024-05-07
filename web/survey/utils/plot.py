import io
import binascii
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from django.utils.safestring import mark_safe


def product_summary_image(products, size=(3, 2), binary_image=False):
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
        if binary_image == True:
            plt.close(fig)
            return image_data.getvalue()

        base_img = binascii.b2a_base64(image_data.getvalue()).decode()
        img_src = f'<img src=\"data:image/png;base64,{base_img}\", style="border-radius: 3%;">'
        plt.close(fig)
        return mark_safe(img_src)
