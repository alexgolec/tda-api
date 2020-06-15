.. _orders:

=============================
Creating Order Specifications
=============================

The :meth:`Client.place_order() <tda.client.Client.place_order>` method expects 
a rather complex JSON object that describes the desired order. TDA provides some 
`example order specs 
<https://developer.tdameritrade.com/content/place-order-samples>`__ to
illustrate the process and provides a schema in the `place order documentation 
<https://developer.tdameritrade.com/account-access/apis/post/accounts/
%7BaccountId%7D/orders-0>`__, but beyond that we're on our own. ``tda-api`` aims 
to be useful to everyone, from users who want to easily place common equities 
and options trades, to advanced users who want to place complex multi-leg, 
multi-asset type trades. 

For users interested in simple trades, ``tda-api`` supports pre-built trade 
templates that allow fast construction of the most common trades. Advanced users 
can modify these trades however they like, and can even build trades from 
scratch.

This section begins by listing the supported common trades, and then describing 
the fully-featured order construction system that supports them. Advanced users 
can skip straight to that section.


------------------
Common Order Types
------------------

This section describes how to construct the most common order types. If you feel 
there's an order missing, you're welcome to `request a new one
<https://github.com/alexgolec/tda-api/issues>`__.


++++++++++++++++++++++++++++++++++++
Buying and Selling Equities and ETFs
++++++++++++++++++++++++++++++++++++
