"""Downloads of detection products and task files (core module)."""

import os
from django.http import HttpResponse, StreamingHttpResponse
from modules.core.models import Detection, FileTaskReturn, Instance, Product, Run, Task
from modules.core.utils.io import DETECTION_PRODUCT_FILES, detection_file_name, tarfile_write, tarfile_write_products
from modules.core.utils.plot import plot_html
from modules.core.views.common import _attachment, _detections_products, _id_parameter, _single_product, _tarball


PRODUCTS = list(DETECTION_PRODUCT_FILES)


def test(request):
    return HttpResponse("Authorized", status=200)


def summary_image(request):
    detection_id = request.GET.get("id", None)
    if detection_id is None:
        return HttpResponse("No summary image found", status=200)
    else:
        d = Detection.objects.get(id=detection_id)
        img = d.summary_image(size=(12, 9))
        return HttpResponse(img, status=200)


def instance_products(request):
    """Download products for all detections of an instance
    from the Admin portal.

    """
    instance_id, error = _id_parameter(request)
    if error:
        return error

    instance = Instance.objects.filter(id=instance_id).first()
    if not instance:
        return HttpResponse("instance not found.", status=404)

    detections = Detection.objects.filter(instance=instance)
    return _detections_products(detections, f"{instance.run.name}_{instance.filename}.tar")


def _read_in_chunks(filename, chunk_size=1024 * 64):
    with open(filename, "rb") as infile:
        while True:
            chunk = infile.read(chunk_size)
            if chunk:
                yield chunk
            else:
                # The chunk was empty, which means we're at the end
                # of the file
                return


def task_file_download(request):
    task_id = request.GET.get("id", None)
    if not task_id:
        return HttpResponse("task id does not exist.", status=400)

    task = Task.objects.filter(id=task_id).first()
    if task.func not in [
        "download_accepted_sources",
        "download_accepted_sources_catalog",
        "download_summaries",
    ]:
        return HttpResponse("No data.", status=404)

    if task.state != "COMPLETED":
        return HttpResponse("Task failed or not ready", status=400)

    if request.user.username != task.user:
        return HttpResponse("Unauthorized", status=401)

    task = task.get_return()
    if isinstance(task, FileTaskReturn) is False:
        return HttpResponse("Not a File Task", status=400)

    filename = task.get_paths()[0]
    response = StreamingHttpResponse(streaming_content=_read_in_chunks(filename))
    response["Content-Disposition"] = f"attachment; filename={os.path.basename(filename)}"
    response["Content-Length"] = os.path.getsize(filename)
    return response


def detection_products(request):
    detect_id, error = _id_parameter(request)
    if error:
        return error

    product_arg = request.GET.get("product", None)
    if product_arg is not None:
        product_arg = product_arg.lower()
        if product_arg not in PRODUCTS:
            return HttpResponse("not a valid detection product.", status=400)

    # Only the products that are downloaded are read from the database
    fields = [product_arg] if product_arg else [*PRODUCTS, "plot"]
    product = (
        Product.objects.filter(detection=detect_id)
        .select_related("detection", "detection__instance", "detection__run")
        .only("detection__name", "detection__instance__id", "detection__run__name", *fields)
        .first()
    )
    if not product:
        return HttpResponse("Products not found.", status=404)

    name = detection_file_name(product.detection)
    if product_arg is not None:
        return _single_product(getattr(product, product_arg), name, product_arg)

    def write(tar):
        tarfile_write_products(tar, product, name)
        if product.plot is not None:
            # Summary plot is either an image or HTML
            html = plot_html(product.plot)
            if html is None:
                tarfile_write(tar, f"{name}_plot.png", product.plot)
            else:
                tarfile_write(tar, f"{name}_plot.html", html.encode("utf-8"))

    return _attachment(_tarball(write), f"{name}.tar.gz")


def run_products(request):
    """Download products for all detections of a run
    from the Admin portal.

    """
    run_id, error = _id_parameter(request)
    if error:
        return error

    run = Run.objects.filter(id=run_id).first()
    if not run:
        return HttpResponse("run not found.", status=404)

    detections = Detection.objects.filter(run=run)
    return _detections_products(detections, f"{run.id}_{run.name}_products.tar")
