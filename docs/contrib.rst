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

TDA's API occasionally emits invalid JSON in the stream. This class implements 
all known workarounds and hacks to get around these quirks:

.. autoclass:: tda.contrib.util::HeuristicJsonDecoder
  :members:
  :undoc-members:

You can use it as follows: 

.. code-block:: python

  from tda.contrib.util import HeuristicJsonDecoder

  stream_client = # ... create your stream
  stream_client.set_json_decoder(HeuristicJsonDecoder())
  # ... continue as normal

If you encounter invalid stream items that are not fixed by using this decoder, 
please let us know in our `Discord server <https://discord.gg/Ddha8cm6dx>`__ or 
follow the guide in :ref:`contributing` to add new functionality.
