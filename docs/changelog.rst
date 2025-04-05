.. _changelog:

=========
Changelog
=========

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