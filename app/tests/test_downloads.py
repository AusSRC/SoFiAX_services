"""Product and catalogue downloads."""

import io
import tarfile

PRODUCT_FILES = ["mom0.fits", "mom1.fits", "mom2.fits", "cube.fits", "mask.fits", "chan.fits", "spec.txt"]


def tar_names(response):
    with tarfile.open(fileobj=io.BytesIO(response.content)) as tar:
        return tar.getnames()


def test_detection_products(admin_client, survey):
    response = admin_client.get(f"/detection_products?id={survey.pending.id}")
    assert response.status_code == 200
    prefix = f"test_run_{survey.instance.id}_pending_1"
    assert response["Content-Disposition"] == f"attachment; filename={prefix}.tar.gz"
    assert tar_names(response) == [f"{prefix}_{name}" for name in [*PRODUCT_FILES, "plot.png"]]


def test_detection_single_product(admin_client, survey):
    response = admin_client.get(f"/detection_products?id={survey.pending.id}&product=spec")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain"
    assert response.content == b"# chan freq flux\n1 1.0 2.0\n2 2.0 3.0\n"

    response = admin_client.get(f"/detection_products?id={survey.pending.id}&product=mom0")
    assert response.status_code == 200
    assert response["Content-Type"] == "image/fits"
    assert response["Content-Disposition"].endswith("_pending_1_mom0.fits")


def test_detection_product_errors(admin_client, survey):
    assert admin_client.get("/detection_products").status_code == 400
    assert admin_client.get("/detection_products?id=abc").status_code == 400
    assert admin_client.get(f"/detection_products?id={survey.pending.id}&product=nope").status_code == 400
    # The detections of the fixture have no pv product
    assert admin_client.get(f"/detection_products?id={survey.pending.id}&product=pv").status_code == 404
    assert admin_client.get("/detection_products?id=999999").status_code == 404


def test_run_and_instance_products(admin_client, survey):
    for url in [f"/run_products?id={survey.run.id}", f"/instance_products?id={survey.instance.id}"]:
        response = admin_client.get(url)
        assert response.status_code == 200, url
        names = tar_names(response)
        # One folder for each of the four detections
        assert len(names) == 4 * len(PRODUCT_FILES)
        assert f"pending_1/test_run_{survey.instance.id}_pending_1_mom0.fits" in names


def test_run_catalog(admin_client, survey):
    response = admin_client.get(f"/catalog?id={survey.run.id}")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/xml"
    assert "pending_1" in response.content.decode()
