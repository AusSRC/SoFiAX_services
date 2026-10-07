# HI web portal

## Project structure

```
web/
│── survey/
│   ├── __init__.py
│   ├── views.py
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   ├── ...
│   └── templates/
│
│── ...
│
│── project             # Code for custom applications can be moved here
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   ├── ...
│   └── views.py
│
│── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── ...
│   └── asgi.py
│
│── manage.py
│── requirements.txt
│── ...
└── README.md
```

## Core functionality

Under the `survey` project the views and models for the key functionality of the project are provided...

## Extending

To write custom features that make use of this core set of features you can create a new project.

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