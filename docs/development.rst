.. _development:

=========================
Development
=========================

After you have generated your project, there are a few things missing in your development environment to get started:

* Install project requirements
* Create and connect a Postgres database
* Run database migrations
* Create and connect a Redis instance
* Set up a Stripe project and product

We will walk you through each step with what we consider the faster approach. If you know how to do it in another way, fell free to deviate.

The first step is to install the project requirements.

Install project requirements
----------------------------

Open your terminal in the project root

.. code-block:: sh

   pip install -r requirements.txt

This will install all the requirements to develop, format, lint and write docs for your project.

Next up is setting up Postgres and Redis.

Set up Postgres and Redis instances
-----------------------------------

We've built Django Rocket having Postgres in mind so we'll guide you through setting one up. We'll do it using `Docker Compose`_. If you don't have Compose installed, go over to `Install Compose`_ and then come back.

.. _Docker Compose: https://docs.docker.com/compose/
.. _Install Compose: https://docs.docker.com/compose/install/

Your initial project ships with a :code:`docker-compose.yml` file in the root. Here's how it looks:

.. code-block:: yaml

   version: "3.1"

   services:

      postgres:
         image: postgres:latest
         restart: always
         environment:
            - POSTGRES_NAME=${POSTGRES_NAME}
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
            - POSTGRES_DB=${POSTGRES_DB}
         ports:
            - "5432:5432"

      redis:
         image: bitnami/redis:latest
         restart: always
         environment:
            - ALLOW_EMPTY_PASSWORD=yes
         ports:
            - "6379:6379"

Since Django Rocket also ships with a pre-populated :code:`.env` file, the :code:`POSTGRES_NAME`, :code:`POSTGRES_PASSWORD` and :code:`POSTGRES_DB` environment variables have already been set for you. All is left to do is run compose

.. code-block:: sh

   docker compose run

Now that the database is up we can run the project migrations.

Run migrations
--------------

To run the project migrations, in your terminal

.. code-block:: sh 

   python src/manage.py migrate

Notice we expect the :code:`manage.py` file to be in the :code:`src` directory.

.. note::
   For a detailed description of the initial project directory, see :doc:`Initial project structure <initial-project-structure>`.

The final before being able to run your project is setting up Stripe.

Set up Stripe
-------------

For this step, you will need a `Stripe`_ account. Once you are registered in Stripe, navigate to the `dashboard`_ and click on `Developers`_ and in the left sidebar click `API keys`_.

.. _Stripe: https://stripe.com/
.. _dashboard: https://dashboard.stripe.com/dashboard
.. _Developers: https://dashboard.stripe.com/test/developers
.. _API keys: https://dashboard.stripe.com/test/apikeys

From here, you will create a new secret key. The resulting publishable key and secret key should be stored in your :code:`.env` under the keys :code:`STRIPE_PUBLISHABLE_KEY` and :code:`STRIPE_SECRET_KEY`.

Now navigate to `Webhooks`_ and add a webhook endpoint. The URL should be :code:`https://<HOST>/billing/stripe/webhook/`. Make sure to replace :code:`<HOST>` with your host.

.. _Webhooks: https://dashboard.stripe.com/test/webhooks

The final step is to create a product. Navigate to the `Products`_ tab. Click on "Add a product" and make sure you select "Recurring" under "Price". Django Rocket expects your product to be a subscription.  

.. _Products: https://dashboard.stripe.com/test/products?active=true

Fill all the information for your product and once you are done hit save. Then collect the price id and set it in your :code:`.env` under the key :code:`STRIPE_PRICE_ID` 

And that's it with Stripe.

Running the project
-------------------

Now you are ready to run your project. Head to the terminal and under the root directory 

.. code:: sh 

   python src/manage.py runserver


