Django Rocket
=============

**A Django SaaS boilerplate**

Django Rocket is an almost-ready-to-launch boilerplate framework powered by `Cookiecutter`_.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter

It was initially built to allow me to launch my SaaS projects without having to copy-paste common code, so expect the design decisions and integrations to be targeted for this purpose.

Requirements
------------

To get started, you need to install the dependencies

* `cookiecutter`_
* `django`_

.. _cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _django: https://github.com/django/django

You can install them via `pip`_

.. _pip: https://github.com/pypa/pip

.. code-block:: sh

   pip install cookiecutter==2.1.1 django==4.1.4

.. note::
   Django Rocket works with other versions of Cookiecutter and Django, but it lacks extensive test coverage so there may be small errors. For now it's better to stick to the mentioned versions.

Usage
-----

To build your project with cookiecutter 

.. code-block:: sh 

   cookiecutter gh:ErnestoFGonzalez/djangorocket

You'll be prompted to enter some information

.. code-block:: sh

   project_name [My Project]: 
   project_slug [my_project]:


Output
------

Running this command will create a directory called :code:`my_project` inside the current folder. Inside :code:`my_project`, you'll have the initial project structure:

::

   my_project
   ├── requirements
   │  ├── requiremens-dev.txt
   │  ├── requiremens-docs.txt
   │  ├── requiremens-linting.txt
   │  ├── requiremens-testing.txt
   │  └── requirements.txt
   ├── src
   │  ├── my_project
   │  │  ├── auth 
   │  │  ├── billing
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
   ├── requiremens.txt
   └── runtime.txt

For a deep dive, see :doc:`Initial project structure <initial-project-structure>`.

Start developing
----------------

In order to get started with your development there are a few things you need to do first:

* Install project requirements
* Create and connect a Postgres database
* Run database migrations
* Create and connect a Redis instance
* Set up a Stripe project and product

Go to :doc:`Development <development>` for a step-by-step guide.

License
-------

Django Rocket is distributed under the Apache License 2.0. You can `read the full license here`_.

.. _read the full license here: https://github.com/ErnestoFGonzalez/djangorocket/blob/main/LICENSE.md

.. toctree::
   :hidden:

   self
   initial-project-structure
   development
   changelog


