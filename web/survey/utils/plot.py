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


def summary_image_WALLABY(products, size=(3, 2)):
    summary = products.summary

    if summary is None:
        # construct summary image from mom0, mom1 and spectra
        fig, ax = plt.subplots(nrows=2, ncols=2)
        fig.set_size_inches(*size)
        interval = PercentileInterval(95.0)
        interval2 = PercentileInterval(90.0)

        # Open moment 0 image
        with io.BytesIO() as buf:
            buf.write(products.mom0)
            buf.seek(0)
            hdu_mom0 = fits.open(buf)[0]
            wcs = WCS(hdu_mom0.header)
            mom0 = hdu_mom0.data

        # Open moment 1 image
        with io.BytesIO() as buf:
            buf.write(products.mom1)
            buf.seek(0)
            hdu_mom1 = fits.open(buf)[0]
            mom1 = hdu_mom1.data

        # Spectrum
        with io.BytesIO() as buf:
            buf.write(b''.join(products.spec))
            buf.seek(0)
            spectrum = np.loadtxt(buf, dtype="float", comments="#", unpack=True)

        # Extract coordinate information
        nx = hdu_mom0.header["NAXIS1"]
        ny = hdu_mom0.header["NAXIS2"]
        clon, clat = wcs.all_pix2world(nx/2, ny/2, 0)
        tmp1, tmp3 = wcs.all_pix2world(0, ny/2, 0)
        tmp2, tmp4 = wcs.all_pix2world(nx, ny/2, 0)
        width = np.rad2deg(math.acos(math.sin(np.deg2rad(tmp3)) * math.sin(np.deg2rad(tmp4)) + math.cos(np.deg2rad(tmp3)) * math.cos(np.deg2rad(tmp4)) * math.cos(np.deg2rad(tmp1 - tmp2))))
        tmp1, tmp3 = wcs.all_pix2world(nx/2, 0, 0)
        tmp2, tmp4 = wcs.all_pix2world(nx/2, ny, 0)
        height = np.rad2deg(math.acos(math.sin(np.deg2rad(tmp3)) * math.sin(np.deg2rad(tmp4)) + math.cos(np.deg2rad(tmp3)) * math.cos(np.deg2rad(tmp4)) * math.cos(np.deg2rad(tmp1 - tmp2))))

        # Plot moment 0
        ax2 = plt.subplot(2, 2, 1, projection=wcs)
        ax2.imshow(mom0, origin="lower")
        ax2.grid(color="grey", ls="solid")
        ax2.set_xlabel("Right ascension (J2000)")
        ax2.set_ylabel("Declination (J2000)")
        ax2.tick_params(axis="x", which="both", left=False, right=False)
        ax2.tick_params(axis="y", which="both", top=False, bottom=False)
        e = Ellipse((5, 5), 5, 5, 0, edgecolor='peru', facecolor='peru')
        ax2.add_patch(e)

        # Plot moment 1
        bmin, bmax = interval.get_limits(mom1)
        ax3 = plt.subplot(2, 2, 3, projection=wcs)
        ax3.imshow(hdu_mom1.data, origin="lower", vmin=bmin, vmax=bmax, cmap=plt.get_cmap("gist_rainbow"))
        ax3.grid(color="grey", ls="solid")
        ax3.set_xlabel("Right ascension (J2000)")
        ax3.set_ylabel("Declination (J2000)")
        ax3.tick_params(axis="x", which="both", left=False, right=False)
        ax3.tick_params(axis="y", which="both", top=False, bottom=False)

        # Plot spectrum
        xaxis = spectrum[1] / 1e+6
        data  = 1000.0 * np.nan_to_num(spectrum[2])
        xmin = np.nanmin(xaxis)
        xmax = np.nanmax(xaxis)
        ymin = np.nanmin(data)
        ymax = np.nanmax(data)
        ymin -= 0.1 * (ymax - ymin)
        ymax += 0.1 * (ymax - ymin)
        ax4 = plt.subplot(2, 2, 4)
        ax4.step(xaxis, data, where="mid", color="royalblue")
        ax4.set_xlabel("Frequency (MHz)")
        ax4.set_ylabel("Flux density (mJy)")
        ax4.grid(True)
        ax4.set_xlim([xmin, xmax])
        ax4.set_ylim([ymin, ymax])

        # attempt to open DSS image
        if products.plot is not None:
            optical = mpimg.imread(io.BytesIO(products.plot))
            ax1 = plt.subplot(2, 2, 2)
            ax1.set_frame_on(False)
            ax1.get_xaxis().set_visible(False)
            ax1.get_yaxis().set_visible(False)
            ax1.autoscale(enable=True, tight=True)
            ax1.imshow(optical)

        with io.BytesIO() as image_data:
            fig.savefig(image_data, format='png')
            base_img = binascii.b2a_base64(image_data.getvalue()).decode()
            img_src = f'<img src=\"data:image/png;base64,{base_img}\">'
            plt.close()
            return mark_safe(img_src)

    else:
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(*size)
        img = mpimg.imread(io.BytesIO(summary))
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
