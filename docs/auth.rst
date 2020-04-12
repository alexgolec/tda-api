.. highlight:: python
.. py:module:: tda.auth

.. _auth:

==================================
Authentication and Client Creation
==================================

By now, you should have followed the instructions in :ref:`getting_started` and 
are ready to start making API calls. Read this page to learn how to get over the 
last remaining hurdle: OAuth authentication.

Before we begin, however, note that this guide is meant to users who want to run 
applications on their own machines, without distributing them to others. If you 
plan on distributing your app, or if you plan on running it on a server and 
allowing access to other users, this login flow is not for you.

---------------
OAuth Refresher
---------------

*This section is purely for the curious. If you already understand OAuth (wow,
congrats) or if you don't care and just want to use this package as fast as
possible, feel free to skip this section. If you encounter any weird behavior, 
this section may help you understand that's going on.*

Webapp authentication is a complex beast. The OAuth protocol was created to 
allow applications to access one anothers' APIs securely and with the minimum 
level of trust possible. A full treatise on this topic is well beyond the scope
of this guide, but in order to alleviate
`some <https://www.reddit.com/r/algotrading/comments/brohdx/
td_ameritrade_api_auth_error/>`__
`of <https://www.reddit.com/r/algotrading/comments/alk7yh/
tdameritrade_api_works/>`__
`the <https://www.reddit.com/r/algotrading/comments/914q22/
successful_access_to_td_ameritrade_api/>`__
`confusion <https://www.reddit.com/r/algotrading/comments/c81vzq/
td_ameritrade_api_access_2019_guide/>`__
`and <https://www.reddit.com/r/algotrading/comments/a588l1/
td_ameritrade_restful_api_beginner_questions/>`__
`complexity <https://www.reddit.com/r/algotrading/comments/brsnsm/
how_to_automate_td_ameritrade_api_auth_code_for/>`__
that seems to surround this part of the API, let's give a quick explanation of
how OAuth works in the context of TD Ameritrade's API.

The first thing to understand is that the OAuth webapp flow was created to allow 
client-side applications consisting of a webapp frontend and a remotely hosted 
backend to interact with a third party API. Unlike the `backend application flow
<https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html
#backend-application-flow>`__, in which the remotely hosted backend has a secret 
which allows it to access the API on its own behalf, the webapp flow allows 
either the webapp frontend or the remotely host backend to access the API *on 
behalf of its users*.

If you've ever installed a GitHub, Facebook, Twitter, GMail, etc. app, you've 
seen this flow. You click on the "install" link, a login window pops up, you
enter your password, and you're presented with a page that asks whether you want 
to grant the app access to your account.

Here's what's happening under the hood. The window that pops up is the 
`authentication URL <https://developer.tdameritrade.com/content/
simple-auth-local-apps>`__, which opens a login page for the target API. The 
aim is to allow the user to input their username and password without the webapp 
frontend or the remotely hosted backend seeing it. On web browsers, this is 
accomplished using the browser's refusal to send credentials from one domain to 
another.

Once login here is successful, the API replies with a redirect to a URL that the 
remotely hosted backend controls. This is the callback URL. This redirect will 
contain a code which securely identifies the user to the API, embedded in the 
query of the request.

You might think that code is enough to access the API, and it would be if the 
API author were willing to sacrifice long-term security. The exact reasons why 
it doesn't work involve some deep security topics like robustness against replay
attacks and session duration limitation, but we'll skip them here.

This code is useful only for `fetching a token from the authentication endpoint
<https://developer.tdameritrade.com/authentication/apis/post/token-0>`__. *This 
token* is what we want: a secure secret which the client can use to access API 
endpoints, and can be refreshed over time.

If you've gotten this far and your head isn't spinning, you haven't been paying 
attention. Security-sensitive protocols can be very complicated, and you should 
**never** build your own implementation. Fortunately there exist very robust 
implementations of this flow, and ``tda-api``'s authentication module makes 
using them easy.

--------------------------------------
Fetching a Token and Creating a Client
--------------------------------------

``tda-api`` provides an easy implementation of the client-side login flow in the 
``auth`` package. It uses a `selenium 
<https://selenium-python.readthedocs.io/>`__ webdriver to open the TD Ameritrade 
authentication URL, take your login credentials, catch the post-login redirect, 
and fetch a reusable token. It returns a fully-configured :ref:`client`, ready 
to send API calls. It also handles token refreshing, and writes updated tokens 
to the token file.

.. autofunction:: tda.auth.client_from_login_flow

Once you have a token written on disk, you can reuse it without going through 
the login flow again. 

.. autofunction:: tda.auth.client_from_token_file

The following is a convenient wrapper around these two methods, calling each 
when appropriate: 

.. autofunction:: tda.auth.easy_client
