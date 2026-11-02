import io
import tarfile
import time
from datetime import datetime
from urllib.request import pathname2url


def tarfile_write(tar, filename, content):
    """Helper function for writing content to a tarfile."""
    info = tarfile.TarInfo(filename)
    info.size = len(content)
    info.mtime = time.mktime(datetime.now().timetuple())
    tar.addfile(info, io.BytesIO(initial_bytes=content))


# Products of a detection and the extension of their files
DETECTION_PRODUCT_FILES = {
    "mom0": "fits",
    "mom1": "fits",
    "mom2": "fits",
    "cube": "fits",
    "mask": "fits",
    "chan": "fits",
    "spec": "txt",
    "pv": "fits",
}


def detection_file_name(detection):
    """Name for the files of a detection."""
    name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
    return pathname2url(name.replace(" ", "_"))


def tarfile_write_products(tar, product, prefix):
    """Write the products of a detection to a tarfile as <prefix>_<product>.<extension>.
    The pv product is optional.

    """
    for name, extension in DETECTION_PRODUCT_FILES.items():
        content = getattr(product, name)
        if name == "pv" and content is None:
            continue
        tarfile_write(tar, f"{prefix}_{name}.{extension}", content)
