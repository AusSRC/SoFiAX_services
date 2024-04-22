import uuid
import tarfile

from survey.models import Product, FileTaskReturn
from survey.utils.io import tarfile_write
from urllib.request import pathname2url

from survey.utils.task import task


@task()
def download_accepted_sources(request, queryset):
    ids = [i.detection.id for i in queryset]
    products = Product.objects.filter(detection_id__in=ids)

    uuid_id = str(uuid.uuid4())
    uuid_filename = f"/tmp/{uuid_id}.tar.gz"

    with tarfile.open(uuid_filename, mode='w:gz') as tar:
        for product in products:
            detection = product.detection
            name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
            name = pathname2url(name.replace(' ', '_'))
            folder = f'{detection.run.name}'.replace(' ', '_')

            tarfile_write(tar, f'{folder}/{name}_mom0.fits', product.mom0)
            tarfile_write(tar, f'{folder}/{name}_mom1.fits', product.mom1)
            tarfile_write(tar, f'{folder}/{name}_mom2.fits', product.mom2)
            tarfile_write(tar, f'{folder}/{name}_cube.fits', product.cube)
            tarfile_write(tar, f'{folder}/{name}_mask.fits', product.mask)
            tarfile_write(tar, f'{folder}/{name}_chan.fits', product.chan)
            tarfile_write(tar, f'{folder}/{name}_spec.txt', product.spec)
            tarfile_write(tar, f'{folder}/{name}_summary.png', detection.summary_image(size=(8, 6), binary_image=True))

    return FileTaskReturn([uuid_filename])


def download_summaries_for_run(request, queryset):
    uuid_id = str(uuid.uuid4())
    uuid_filename = f"/tmp/{uuid_id}.tar.gz"

    with tarfile.open(uuid_filename, mode='w:gz') as tar:
        for detection in queryset[0].detection_set.all():
            name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
            name = pathname2url(name.replace(' ', '_'))
            folder = f'{detection.run.name}'.replace(' ', '_')

            tarfile_write(tar, f'{folder}/{name}_summary.png', detection.summary_image(size=(8, 6), binary_image=True))

    return FileTaskReturn([uuid_filename])