.. _changelog:

=========
Changelog
=========

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