"""Downloads of kinematic model products."""

from django.http import HttpResponse
from modules.core.models import Run
from modules.core.utils.io import tarfile_write
from modules.core.views.common import _attachment, _id_parameter, _single_product, _tarball
from modules.wallaby.models import KinematicModel, KinematicModel_3KIDNAS, WKAPP_Product, WRKP_Product
from urllib.request import pathname2url


KINEMATIC_MODEL_PRODUCTS = [
    "baroloinput",
    "barolomod",
    "barolosurfdens",
    "diagnosticplot",
    "diffcube",
    "fatinput",
    "fatmod",
    "fullresmodcube",
    "fullresproccube",
    "modcube",
    "procdata",
]


KINEMATIC_MODEL_3KIDNAS_PRODUCTS = [
    "bootstrapfits",
    "diagnosticplot",
    "diffcube",
    "flag",
    "modcube",
    "procdata",
    "pvmajordata",
    "pvmajormod",
    "pvminordata",
    "pvminormod",
]


def _kinematic_model_products(request, model, product_model, relation, parameter, products):
    """Download the products of a kinematic model, or the product in the request parameter."""
    kinematic_model_id, error = _id_parameter(request)
    if error:
        return error

    product_arg = request.GET.get(parameter, None)
    if product_arg is not None:
        product_arg = product_arg.lower()
        if product_arg not in products:
            return HttpResponse(f"not a valid {model._meta.db_table} {parameter}.", status=400)

    kinematic_model = model.objects.get(id=kinematic_model_id)
    product = product_model.objects.get(**{relation: kinematic_model})
    run = Run.objects.get(id=kinematic_model.detection.run_id)
    name = f"{run.name}_{kinematic_model.detection.name}"
    name = pathname2url(name.replace(" ", "_"))

    if product_arg is not None:
        return _single_product(getattr(product, product_arg), name, product_arg)

    def write(tar):
        for p in products:
            tarfile_write(tar, f"{name}_{p}.fits", getattr(product, p))

    return _attachment(_tarball(write), f"{name}.tar.gz")


def wkapp_products(request):
    return _kinematic_model_products(
        request, KinematicModel, WKAPP_Product, "kinematic_model_id", "wkapp_product", KINEMATIC_MODEL_PRODUCTS
    )


def wrkp_products(request):
    return _kinematic_model_products(
        request,
        KinematicModel_3KIDNAS,
        WRKP_Product,
        "kinematic_model_3kidnas",
        "wrkp_product",
        KINEMATIC_MODEL_3KIDNAS_PRODUCTS,
    )
