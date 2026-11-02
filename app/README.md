# HI web portal

## Project structure

```
app/
│── manage.py
│── config/             # Settings and urls, the modules to install are set by MODULES
│── modules/
│   ├── core/           # Runs, instances, detections, products, tags, comments, manual inspection
│   ├── operations/     # Observations, survey components, external conflicts, cross matching, release
│   ├── wallaby/        # Tiles, source extraction regions, kinematic models (requires operations)
│   └── dingo/          # GAMA matches of detections
└── tests/
```

The application is run locally with `make start`, or as the `app` service in Docker (see the [`README.md`](../README.md) in the root of the repository and [`server/README.md`](../server/README.md)). The configuration is read from the `.env` file in the root of the repository when it is run locally.

The dependencies are listed in `pyproject.toml` in the root of the repository and locked in `uv.lock`. After changing them run `uv lock`.

## Modules

Each module is a Django application with its own `models.py`, `admin.py`, `views.py`, `urls.py` and templates. Only the modules listed in the `MODULES` environment variable are installed, and `core` is always required. Nothing has to be registered anywhere else:

* the admin pages are loaded from the `admin.py` of each installed module
* the views and REST API endpoints are loaded from its `urls.py` (`urlpatterns` and `api_routes`)

The core module does not depend on the other modules. A module changes a page of the core module by registering a subclass of its admin class (for example the run page in `modules/operations/admin.py`), or by connecting to a signal (`modules/core/signals.py`).

To add a module create a folder in `modules` with an `apps.py`, and add its name to `AVAILABLE_MODULES` in `config/settings.py`.

## User permissions

You can create users that are not superusers and give them read-only permissions for the tables in the Django admin pages.

```
from django.contrib.auth.models import User
user = User.objects.create('username')
user.first_name = 'Austin'
user.last_name = 'Shen'
user.is_staff = True  # This is required for access to the portal
user.save

from django.contrib.auth.models import Permission
Permission.objects.all()
user.user_permissions.add(Permission.objects.get(codename='view_run'))  # Can do this for a number of different permission objects
user.save
```