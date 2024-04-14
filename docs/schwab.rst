.. _schwab:


=====================================
``tda-api`` and the Schwab Transition
=====================================

In 2020, Charles Schwab acquired TDAmeritrade, and in late 2022 they announced 
their transition plan. This page outlines the implications for current and 
prospective ``tda-api`` users. 


**Disclaimer:** This page contains information about a transition in which the 
author is merely an observer. It attempts to collect and synthesize information 
provided by TDAmeritrade/Charles Schwab, and may be incorrect or out of date.  
Please refer to official communications for authoritative information. If you 
have a different interpretation of the available information, please `visit our 
discord server <https://discord.gg/BEr6y6Xqyv>`__ and share it with us. Use the 
information this page at your own risk.

------------------
What is happening?
------------------

Charles Schwab now owns TDAmeritrade. TDAmeritrade appears to be continuing 
their operations as a broker, but is transitioning their customers onto new 
Charles Schwab accounts. This process was announced in late 2022 and is slated 
to happen in 2023. 

If you are reading this, you are likely interested in using the TDAmeritrade 
REST API. This transition has significant implications for both new and existing 
``tda-api`` users. Please keep reading for more. 


--------------------------
Existing ``tda-api`` Users
--------------------------

As far as we understand it, the implications of this transition for existing 
``tda-api`` users are as follows:

* All accounts will be transitioned to Schwab over the course of 2023.
* Once an account is transitioned to Schwab, it will lose access to the TDAmeritrade REST API. This means all API wrappers will stop working on that account, including ``tda-api``.
* Schwab has announced their intention to provide an API for retail traders, but no such API has materialized yet. They have also `stated that this API will be largely similar to the existing TDAmeritrade API <https://developer.tdameritrade.com/content/trader-api-schwab-integration-guide-june-2023-update>`__, with some modifications. Again, details are forthcoming. 


+++++++++++++++++++++++++++++++++++++
When will my account be transitioned?
+++++++++++++++++++++++++++++++++++++

We understand this will happen in 2023, although details have no yet been 
provided. Schwab advises to `"log in to your TD Ameritrade account and visit the 
Schwab Transition Center" <https://welcome.schwab.com/?aff=WKV>`__, although as 
of this writing the author has not seen any such option on his brokerage page.


+++++++++++++++++++++++++++++++++++++++++++++++++
Will I control when my account gets transitioned?
+++++++++++++++++++++++++++++++++++++++++++++++++

It seems not. Our understanding is that each account will be assigned a 
"transition weekend" on which they will be migrated, and has `provided a 
timeline <https://welcome.schwab.com/?aff=WKV>`__ relative to that weekend. How 
that weekend is chosen and whether it can be altered by the user is unclear.


+++++++++++++++++++++++++++++++++++++++++++++++++++++
What happens to my app before my account transitions?
+++++++++++++++++++++++++++++++++++++++++++++++++++++

There do not appear to be any changes to existing TDAmeritrade accounts, 
including access to the REST API. This suggests that ``tda-api`` should continue 
to work as normal until your account is transitioned.


+++++++++++++++++++++++++++++++++++++++++++++++++++++++
What happens to the ``tda-api`` app after I transition?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

It stops working. You will need to migrate your app to the upcoming Schwab API, 
once it becomes available.

We have begun developing a new ``schwab-py`` API `(linked here) <https://github.com/alexgolec/schwab-py>`__
which implements much of the functionality of ``tda-api``, but is adapted
for `Charles Schwab's API <https://developer.schwab.com/>`__.  This new API
will be maintained and supported going forward, and replaces ``tda-api``.
``schwab-py`` is still under development with more features rolling out
quickly, and already implements much of the functionality of the original
``tda-api``.

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
What if I transition before the new Schwab API becomes available?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

While not confirmed, it appears your account may be transitioned to Schwab 
before the new Schwab API is made available. If this happens, our understanding 
is that you will not have access to either the previous TDAmeritrade API (and 
``tda-api`` as well) or to the as-yet-unreleased Schwab API. 

It's important to note that this scenario is still hypothetical. For all we 
know, the Schwab API will be made available before your account is transitioned, 
and your access to a retail trading API will not be interrupted. However, this 
scenario has not been ruled out, either. TDAmeritrade's/Schwab's `integration 
guide
<https://developer.tdameritrade.com/content/trader-api-schwab-integration-guide-june-2023-update>`__ 
says *"It is possible that a TDA brokerage account may not be migrated to Schwab 
brokerage before Schwab endpoints are live,"* although we're frankly at a loss 
for how to interpret that statement.


+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
How do I migrate my ``tda-api`` app to this new Schwab API?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Until the new Schwab API becomes available, there is nothing you can do. Once it 
becomes available, the maintainers of ``tda-api`` will evaluate the situation 
and decide how to move forward. Our tentative plan is as follows, although note 
this is based on preliminary information and subject to change at any time:

* Schwab has announced that their new API will resemble the old TDAmeritrade API, with some modifications. Notably, it appears all functionality will be carried forward except for saved orders and watchlists. It seems there will be some changes to the authentication flow as well. 
* The ``tda-api`` authors currently intend to implement a new API wrapper to support this new API. Wherever possible, the functionality and interface of ``tda-api`` will be kept intact.
* This new library will be a separate package from ``tda-api``. We are in the process of constructing placeholders and registering PyPI packages.
* Your app will almost certainly need to be modified to use this new library, although we aim to minimize the work required to do so.
* TDAmeritrade/Schwab has also confirmed that you will need to register a new 
  application, i.e. receive a new API key. Schwab has announced this will happen 
  in `"early 2023." 
  <https://developer.tdameritrade.com/content/trader-api-schwab-integration-guide-june-2023-update>`__


---------------------
New ``tda-api`` Users
---------------------

Unfortunately, as part of this transition, TDAmeritrade has closed registration 
of new applications. This means you cannot get a API key for your application, 
so if you're not currently a ``tda-api`` user, you cannot become one. This is an 
unfortunate state of affairs, but we are powerless to change it. 


++++++++++++++++++++++++++++++++++++
Can I borrow someone else's API key?
++++++++++++++++++++++++++++++++++++

According to the ``tda-api`` authors' interpretation of `the TDAmeritrade API's 
terms of service <https://developer.tdameritrade.com/legal>`__, no. In fact, 
they explicitly say *"All API Keys assigned to you are unique to you and are 
solely for your own use in connection with your participation in the Program.  
You may not provide any third party with access to any API Key."* We're not 
lawyers, so take our advice with a grain of salt, but that seems pretty 
unambiguous to us. 

We are enforcing this interpretation on our discord server. Your first request 
for a third-party API key will be met with a warning, and subsequent requests 
will result in your being banned from the server. 


++++++++++++++++++++++++++++++++++++++++++++++++
Wait, so I'm locked out of the TDAmeritrade API?
++++++++++++++++++++++++++++++++++++++++++++++++

Sadly, it would appear so. We still recommend `joining our discord server 
<https://discord.gg/BEr6y6Xqyv>`__ to discuss trading with like-minded people 
and learn about temporary alternatives. Once a replacement is made available, 
members of that server will be the first to learn about it.


----------------
More information
----------------

You can get more information directly from TDAmeritrade and Charles Schwab at 
the following links:

* `TDAmeritrade Transition Overview <https://welcome.schwab.com/?aff=WKV>`__ at Charles Schwab
* `TDAmeritrade & Charles Schwab: What to Know <https://www.tdameritrade.com/why-td-ameritrade/td-ameritrade-charles-schwab.html>`__ at TDAmeritrade
* `Trader API Schwab Integration Guide <https://developer.tdameritrade.com/content/trader-api-schwab-integration-guide-june-2023-update>`__ at TDAmeritrade's developer portal