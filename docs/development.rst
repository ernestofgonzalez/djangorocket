.. _development:

=========================
Development
=========================

After you have generated your project, there are a few things missing in your development environment to get started:

* Install project requirements
* Set up Docker containers (Postgres and Redis)
* Configure OpenSearch DSL or remove its settings
* Run database migrations
* Set up a Stripe project and product
* Set up Sign in with Google
* Install Tailwind dependencies

We will walk you through each step with what we consider the faster approach. If you know how to do it in another way, fell free to deviate.

The first step is to install the project requirements.

Install project requirements
----------------------------

Open your terminal in the project root

.. code-block:: sh

   pip install -r requirements.txt

This will install all the requirements to develop, format, lint and write docs for your project.

Next up is setting up your Docker containers.

Set up Docker containers
------------------------

We use Docker Compose to set up both Postgres and Redis. If you don't have Compose installed, go over to `Install Compose`_ and then come back.

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

Since Django Rocket also ships with a pre-populated :code:`.env` file, the :code:`POSTGRES_PASSWORD` and :code:`POSTGRES_DB` environment variables have already been set for you. All is left to do is run compose:

.. code-block:: sh

   docker compose up

Configure OpenSearch DSL
------------------------

Before running migrations, you need to either configure OpenSearch DSL with proper AWS credentials or remove it from your settings.

To configure OpenSearch DSL, make sure you have the following environment variables set in your :code:`.env` file:

* AWS_OPEN_SEARCH_HOST
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* AWS_OPEN_SEARCH_REGION_NAME

Your :code:`settings.py` should include this configuration:

.. code-block:: python

   OPENSEARCH_DSL = {
       "default": {
           "hosts": AWS_OPEN_SEARCH_HOST,
           "http_auth": AWSV4SignerAuth(
               boto3.Session(
                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
               ).get_credentials(),
               AWS_OPEN_SEARCH_REGION_NAME,
               "es",
           ),
           "use_ssl": True,
           "verify_certs": True,
           "connection_class": RequestsHttpConnection,
           "pool_maxsize": 20,
       },
   }

If you don't plan to use OpenSearch, you must remove the entire :code:`OPENSEARCH_DSL` setting from your :code:`settings.py` before proceeding with migrations.

.. note::
   The migration command will fail if OpenSearch DSL settings are not properly configured or if the setting is not removed entirely.

Run migrations
--------------

Once you've properly configured or removed OpenSearch DSL, you can run the project migrations. In your terminal:

.. code-block:: sh 

   python src/manage.py migrate

Notice we expect the :code:`manage.py` file to be in the :code:`src` directory.

.. note::
   For a detailed description of the initial project directory, see :doc:`Initial project structure <initial-project-structure>`.

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

Set up Sign in with Google
--------------------------

Open the `Google Developer Console`_. If you don't have a developer account sign up for one.

.. _Google Developer Console: https://console.developers.google.com

`Create a new project`_ for your website. Once you have your project created navigate to `APIs & Services`_, select the `Credentials`_ tab and create a new OAuth client ID with Web application application type. Assign the resulting client id and secret to :code:`GOOGLE_OAUTH_CLIENT_ID` and :code:`GOOGLE_OAUTH_CLIENT_SECRET` respectively in your :code:`.env` file.

.. _Create a new project: https://console.cloud.google.com/projectcreate
.. _APIs & Services: https://console.cloud.google.com/apis/dashboard
.. _Credentials: https://console.cloud.google.com/apis/credentials

Add :code:`http://localhost` and :code:`http://localhost:8000` to the Authorized JavaScript origins and :code:`http://localhost:8000/login/google/` to Authorized redirect URIs and make sure to hit save.

Install Tailwind dependencies
-----------------------------

To Install Tailwind dependencies head over to the terminal 

.. code:: sh 

   python src/manage.py tailwind install

Running the project
-------------------

There are two processes you need running while developing. The first one watches your styles and writes to your stylesheets to include relevant Tailwind utilities 

.. code:: sh 

   python src/manage.py tailwind start

The second one is your familiar Django server

.. code:: sh 

   python src/manage.py runserver

That's it for setting up your development environment.