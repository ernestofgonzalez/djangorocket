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


.. toctree::
   :hidden:

   self
   changelog


