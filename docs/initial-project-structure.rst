.. _initial-project-structure:

=========================
Initial project structure
=========================

After you generate your project, the initial project structure is 

::

   [project_slug]
   ├── requirements
   │  ├── requiremens-dev.txt
   │  ├── requiremens-docs.txt
   │  ├── requiremens-linting.txt
   │  ├── requiremens-testing.txt
   │  └── requirements.txt
   ├── src
   │  ├── [project_slug]
   │  │  ├── auth 
   │  │  ├── billing
   |  |  ├── search
   │  │  ├── utils
   │  │  ├── __init__.py
   │  │  ├── asgi.py
   │  │  ├── celery.py
   │  │  ├── context_processors.py
   │  │  ├── model_loaders.py
   │  │  ├── settings.py
   │  │  ├── urls.py
   │  │  ├── views.py
   │  │  └──wsgi.py
   │  ├── static
   │  ├── tailwind_theme
   │  ├── templates
   │  └── manage.py    
   ├── .env
   ├── .env.example
   ├── .flake8
   ├── .isort.cfg
   ├── docker-compose.yml
   ├── Makefile
   ├── pyproject.toml
   ├── pytest.ini
   ├── requiremens.txt
   └── runtime.txt