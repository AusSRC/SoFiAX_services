"""Fixtures for the web application tests.

The tests run against a throwaway database created by tests/run.sh. They refuse
to run against anything else, so they cannot touch a deployed database.
"""

import io
from types import SimpleNamespace

import numpy as np
import pytest
from astropy.io import fits
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from PIL import Image

# Name of the database created by tests/run.sh
TEST_DATABASE_NAME = "sofiax_test"


def check_test_database():
    name = settings.DATABASES["default"]["NAME"]
    if name != TEST_DATABASE_NAME:
        pytest.exit(
            f"Refusing to run the tests against database '{name}'. "
            f"Run them with tests/run.sh, which creates the '{TEST_DATABASE_NAME}' database.",
            returncode=2,
        )


def pytest_sessionstart(session):
    check_test_database()


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Use the database created by tests/run.sh as it is, instead of letting Django
    create a test database (the survey tables are not managed by Django).

    Only the tables of the Django apps (users, sessions) are created here.
    """
    check_test_database()
    with django_db_blocker.unblock():
        call_command("migrate", verbosity=0, interactive=False)


def png_image():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), color=(40, 80, 160)).save(buffer, format="PNG")
    return buffer.getvalue()


def fits_image():
    buffer = io.BytesIO()
    fits.PrimaryHDU(np.arange(16, dtype="float32").reshape(4, 4)).writeto(buffer)
    return buffer.getvalue()


def create_detection(run, instance, name, accepted, position):
    """Detection above the default thresholds (n_pix, rel) with its products."""
    from survey.models import Detection, Product

    detection = Detection.objects.create(
        run=run,
        instance=instance,
        name=name,
        x=position,
        y=position,
        z=position,
        x_min=0,
        x_max=10,
        y_min=0,
        y_max=10,
        z_min=0,
        z_max=10,
        n_pix=500,
        f_min=0.1,
        f_max=1.0,
        f_sum=5.0,
        rel=0.9,
        rms=0.01,
        w20=100.0,
        w50=80.0,
        ell_maj=5.0,
        ell_min=3.0,
        ell_pa=10.0,
        err_f_sum=1.0,
        ra=10.0 + position,
        dec=-30.0,
        freq=1.4e9,
        flag=0,
        unresolved=False,
        accepted=accepted,
    )
    Product.objects.create(
        detection=detection,
        plot=png_image(),
        mom0=fits_image(),
        spec=b"# chan freq flux\n1 1.0 2.0\n2 2.0 3.0\n",
    )
    return detection


@pytest.fixture
def survey(db):
    """A run with two detections waiting for inspection, one accepted and one rejected."""
    from survey.models import Instance, Run

    run = Run.objects.create(name="test_run", sanity_thresholds={}, created=timezone.now())
    instance = Instance.objects.create(run=run, filename="test.fits", boundary="{0,10,0,10,0,10}", parameters={})
    pending = create_detection(run, instance, "pending_1", None, 1)
    pending_2 = create_detection(run, instance, "pending_2", None, 2)
    accepted = create_detection(run, instance, "accepted_1", True, 3)
    rejected = create_detection(run, instance, "rejected_1", False, 4)
    return SimpleNamespace(
        run=run,
        instance=instance,
        pending=pending,
        pending_2=pending_2,
        accepted=accepted,
        rejected=rejected,
    )
