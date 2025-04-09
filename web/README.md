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
