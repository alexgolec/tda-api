.. highlight:: python
.. py:module:: tda.debug

.. _help:

============
Getting Help
============

``tda-api`` is not perfect. Features are missing, documentation may be out of 
date, and it almost certainly contains bugs. If you think of a way in which
``tda-api`` can be improved, we're more than happy to hear it. 

To make your life and ours easier, we ask that you follow a few guidelines when 
submitting your issue: 


--------------
Enable Logging
--------------

Behind the scenes, ``tda-api`` performs diagnostic logging of its activity using 
Python's `logging <https://docs.python.org/3/library/logging.html>`__ module. 
You can enable this debug information by telling the root logger to print these 
messages:

.. code-block:: python

  import logging
  logging.getLogger('').addHandler(logging.StreamHandler())

Sometimes, this additional logging is enough to help you debug. Before you ask 
for help, carefully read through your logs to see if there's anything there that 
helps you.


-------------------------------
Gather Logs For Your Bug Report
-------------------------------

If you still can't figure out what's going wrong, ``tda-api`` has special 
functionality for gathering and preparing logs for filing issues. It works by 
capturing ``tda-api``'s logs, anonymizing them, and then dumping them to the 
console when the program exits. You can enable this by calling this method 
**before doing anything else in your application**:

.. code-block:: python

  tda.debug.enable_bug_report_logging()

This method will redact the logs to scrub them of common secrets, like account 
IDs, tokens, access keys, etc. However, this redaction is not guaranteed to be 
perfect, and it is your responsibility to make sure they are clean before you 
ask for help.

When filing a issue, please upload the logs along with your description. **If
you do not include logs with your issue, your issue may be closed**. 

For completeness, here is this method's documentation:

.. automethod:: tda.debug.enable_bug_report_logging


------------------
Submit Your Ticket
------------------

You are now ready to write your bug. Before you do, be warned that your issue
may be be closed if:

 * It does not include code. The first thing we do when we receive your issue is 
   we try to reproduce your failure. We can't do that if you don't show us your
   code.
 * It does not include logs. It's very difficult to debug problems without logs.
 * Logs are not adequately redacted. This is for your own protection.
 * Logs are copy-pasted into the issue message field. Please write them to a 
   file and attach them to your issue.
 * You do not follow the issue template. We're not *super* strict about this 
   one, but you should at least include all the information it asks for.

You can file an issue on our `GitHub page <https://github.com/alexgolec/tda-api/
issues>`__.
