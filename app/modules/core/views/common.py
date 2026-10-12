"""Helpers shared by the views."""

import io
import tarfile
from django.http import HttpResponse
from modules.core.models import Product
from modules.core.utils.io import detection_file_name, tarfile_write_products


def _id_parameter(request):
    """The id parameter of a request as (id, None), or (None, response) if it is not valid."""
    value = request.GET.get("id", None)
    if not value:
        return None, HttpResponse("id does not exist.", status=400)
    try:
        return int(value), None
    except ValueError:
        return None, HttpResponse("id is not an integer.", status=400)


def _attachment(data, filename, content_type="application/x-tar"):
    response = HttpResponse(data, content_type=content_type)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response["Content-Length"] = len(data)
    return response


def _tarball(write):
    """Contents of a gzipped tarfile written by write(tar)."""
    fh = io.BytesIO()
    with tarfile.open(fileobj=fh, mode="w:gz") as tar:
        write(tar)
    return fh.getvalue()


def _single_product(data, name, product):
    """Response to download one product, text for spectra and FITS for everything else."""
    if data is None:
        return HttpResponse(f"{product} product not found.", status=404)
    if product == "spec":
        return _attachment(data, f"{name}_{product}.txt", "text/plain")
    return _attachment(data, f"{name}_{product}.fits", "image/fits")


def _detections_products(detections, filename):
    """Response to download the products of the detections, one folder for each detection."""
    products = []
    for d in detections:
        product = Product.objects.filter(detection=d).first()
        if product is None:
            return HttpResponse(f"no products for detection {d.id}.", status=404)
        folder = f"{d.name}".replace(" ", "_")
        products.append((product, f"{folder}/{detection_file_name(d)}"))

    def write(tar):
        for product, prefix in products:
            tarfile_write_products(tar, product, prefix)

    return _attachment(_tarball(write), filename)
