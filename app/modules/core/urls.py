from django.urls import path

from modules.core.views import (
    detection_products,
    instance_products,
    manual_inspection_detection_view,
    run_catalog,
    run_products,
    summary_image,
    task_file_download,
    test,
)

urlpatterns = [
    path("test", test, name="test"),
    path("summary_image", summary_image, name="summary_image"),
    path("detection_products", detection_products, name="detection_products"),
    path("instance_products", instance_products, name="instance_products"),
    path("task_file_download", task_file_download, name="task_file_download"),
    path("run_products", run_products, name="run_products"),
    path("catalog", run_catalog, name="run_catalog"),
    path("inspect_detection", manual_inspection_detection_view, name="inspect_detection"),
]
