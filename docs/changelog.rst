.. _changelog:

=========
Changelog
=========

.. _v_1_0_0a2:

1.0.0a2 (2026-10-02)
--------------------

* Added ``djangorocket add`` to install a UI template into an existing project, resolving each component by name and refusing an unknown one
* Added one-command onboarding to generated projects: ``make bootstrap`` creates the virtualenv, installs dependencies, starts Postgres and Redis, and applies migrations
* Added a README to generated projects, covering the project layout, every ``make`` target, the Tailwind workflow and what to set when deploying
* Added an end-to-end test suite that bakes a project, boots it and renders its landing page
* Changed the templates to ship as package data, so ``init`` and ``add`` work from a ``pip`` install
* Changed ``init`` to pick a project directory and host ports that are free, so several generated projects can run on one machine
* Changed ``init`` to run the post-generation hook, so a generated project gets a pre-populated ``.env`` and boots with no further configuration
* Changed ``init`` to report the new project's absolute path instead of a ``cd`` hint
* Upgraded generated projects to Django 5.2.17 and added support for Python 3.10 to 3.14
* Pinned the services a generated project boots to ``postgres:18`` and ``redis:8-alpine``
* Fixed every page of a generated project returning a 500 on Python 3.14
* Fixed the compiled Tailwind stylesheet being excluded from generated projects by the template's ``.gitignore``
* Fixed a ``pkg_resources`` crash in generated projects on Python 3.12 and later
* Fixed ``make test`` discovering no tests in a generated project, and made the bundled suite pass from a clean scaffold
* Fixed ``psycopg2`` failing to build on modern CPython, by pinning 2.9.10

.. _v_1_0_0a1:

1.0.0a1 (2025-04-05)
---------------------------

* Added command line interface with `init`

.. _v_0_6_0:

0.6.0 (2025-01-24)
------------------

* Upgrade to Django 5 (:issue:`47`)

.. _v_0_5_0:

0.5.0 (2025-01-01)
------------------

* Added search with OpenSearch
* Added settings for Mixpanel
* Added error logging with Sentry

.. _v_0_4_3:

0.4.3 (2023-08-11)
------------------

* Fix typo in namespace (:issue:`41`)

.. _v_0_4_2:

0.4.2 (2023-06-07)
------------------

* Fixed the missing Sign In with Google button in the `auth/pages/login.html` template (:issue:`38`)
* Fixed an incorrect assign of the Google account name to `user.email` when creating the account with Google (:issue:`38`)

.. _v_0_4_1:

0.4.1 (2023-06-06)
------------------

* Fixed `createsuperuser` command (:issue:`36`)

.. _v_0_4_0:

0.4.0 (2023-01-27)
------------------

* Added sign in with Google (:issue:`8`)

.. _v_0_3_0:

0.3.0 (2023-01-18)
------------------

* Added a `docker-compose.yml` file to set up Postgres and Redis instances (:issue:`23`)
* Changed index template to add links to documentation and source code (:issue:`23`)

.. _v_0_2_0:

0.2.0 (2023-01-17)
------------------

* Added a pre-populated `.env` file (:issue:`20`)

.. _v_0_1_0:

0.1.0 (2023-01-17)
------------------

* Added billing with Stripe (:issue:`6`)

* Added authentication with custom user model (:issue:`4`)