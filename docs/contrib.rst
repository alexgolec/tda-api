.. _contrib:

===================================
Community-Contributed Functionality
===================================


When maintaining ``tda-api``, the authors have two goals: make common things 
easy, and make uncommon things possible. This meets the needs of vast majority 
of the community, while allowing advanced users or those with very niche 
requirements to progress using potentially custom approaches. 

However, this philosophy explicitly excludes functionality that is potentially 
useful to many users, but is either not directly related to the core 
functionality of the API wrapper. This is where the ``contrib`` module comes 
into play. 

This module is a collection of high-quality code that was produced by the 
community and for the community. It includes utility methods that provide 
additional functionality beyond the core library, fixes for quirks in API 
behavior, etc. This page lists the available functionality. If you'd like to 
discuss this or propose/request new additions, please join our `Discord server
<https://discord.gg/Ddha8cm6dx>`__.


.. _custom_json_decoding:

--------------------
Custom JSON Decoding
--------------------

For reasons known only to TDAmeritrade's development team, the API occasionally 
emits invalid stream responses for some endpoints. Because this issue does not 
affect all endpoints, and because ``tda-api``'s authors are not in the business 
of handling quirks of an API they don't control, the library simply passes these
errors up to the user. 

However, some applications cannot handle complete failure. What's more, some 
users have insight into how to work around these decoder errors. The streaming 
client supports setting a custom JSON decoder to help with this: 

.. automethod:: tda.streaming.StreamClient.set_json_decoder

Although the ``contrib`` module currently only defines an abstract base class for
these decoders, some users have expressed an interest in sharing their own 
implementations. When this happens, we will update this module with those 
implementations. Until then, the reader must implement their own decoder as a 
subclass of the following abstract base class. If you have such a decoder and 
would like to contribute it, please join our `Discord server
<https://discord.gg/Ddha8cm6dx>`__:

.. autoclass:: tda.contrib.util::StreamJsonDecoder
  :members:
  :undoc-members:
