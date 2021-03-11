.. _getting_started:

===============
Getting Started
===============

Welcome to ``tda-api``! Read this page to learn how to install and configure 
your first TD Ameritrade Python application.

++++++++++++++++++++++++
TD Ameritrade API Access
++++++++++++++++++++++++

All API calls to the TD Ameritrade API require an API key. Before we do 
anything with ``tda-api``, you'll need to create a developer account with TD 
Ameritrade and register an application. By the end of this section, you'll have 
accomplished the three prerequisites for using ``tda-api``:

1. Create an application.
#. Choose and save the callback URL (important for authenticating).
#. Receive an API key.

You can create a developer account `here <https://developer.tdameritrade.com/
user/register>`__. The instructions from here on out assume you're logged in,
so make sure you log into the developer site after you've created your account.

Next, you'll want to `create an application
<https://developer.tdameritrade.com/user/me/apps/add>`__. The app name and 
purpose aren't particularly important right now, but the callback URL is. In a 
nutshell, the `OAuth login flow <https://requests-oauthlib.readthedocs.io/en/
latest/oauth2_workflow.html#web-application-flow>`__ that TD Ameritrade uses
works by opening a TD Ameritrade login page, securely collecting credentials on 
their domain, and then sending an HTTP request to the callback URL with the 
token in the URL query.

How you use to choose your callback URL depends on whether and how you 
plan on distributing your app. If you're writing an app for your own personal 
use, and plan to run entirely on your own machine, use ``https://localhost``. If
you plan on running on a server and having users send requests to you, use a URL
you own, such as a dedicated endpoint on your domain.

Once your app is created and approved, you will receive your API key, also known
as the Client ID. This will be visible in TDA's `app listing page <https://
developer.tdameritrade.com/user/me/apps>`__. Record this key, since it 
is necessary to access most API endpoints.

++++++++++++++++++++++
Installing ``tda-api``
++++++++++++++++++++++

This section outlines the installation process for client users. For developers, 
check out :ref:`contributing`.

The recommended method of installing ``tda-api`` is using ``pip`` from
`PyPi <https://pypi.org/project/tda-api/>`__ in a `virtualenv <https://
virtualenv.pypa.io/en/latest/>`__. First create a virtualenv in your project 
directory. Here we assume your virtualenv is called ``my-venv``:

.. code-block:: shell

  pip install virtualenv
  virtualenv -v my-venv
  source my-venv/bin/activate

You are now ready to install ``tda-api``:

.. code-block:: shell

  pip install tda-api

That's it! You're done! You can verify the install succeeded by importing the 
package:

.. code-block:: python

  import tda

If this succeeded, you're ready to move on to :ref:`auth`.

Note that if you are using a virtual environment and switch to a new terminal
your virtual environment will not be active in the new terminal,
and you need to run the activate command again.
If you want to disable the loaded virtual environment in the same terminal window,
use the command:

.. code-block:: shell

  deactivate

++++++++++++
Getting Help
++++++++++++

If you are ever stuck, feel free to  `join our Discord server
<https://discord.gg/M3vjtHj>`__ to ask questions, get advice, and chat with 
like-minded people. If you feel you've found a bug, you can :ref:`fill out a bug 
report <help>`.
