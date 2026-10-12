"""Views of the core module."""

from .catalog import run_catalog  # noqa: F401
from .inspection import manual_inspection_detection_view  # noqa: F401
from .products import (  # noqa: F401
    detection_products,
    instance_products,
    run_products,
    summary_image,
    task_file_download,
    test,
)
