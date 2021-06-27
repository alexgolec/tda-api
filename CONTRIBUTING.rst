===========================
Contributing to ``tda-api``
===========================

Fixing a bug? Adding a feature? Just cleaning up for the sake of cleaning up? 
Great! No improvement is too small for me, and I'm always happy to take pull 
requests. Read this guide to learn how to set up your environment so you can 
contribute.

------------------------------
Setting up the Dev Environment
------------------------------

Dependencies are listed in the `requirements.txt` file. These development 
requirements are distinct from the requirements listed in `setup.py` and include 
some additional packages around testing, documentation generation, etc.

Before you install anything, I highly recommend setting up a `virtualenv` so you 
don't pollute your system installation directories:

.. code-block:: shell

  pip install virtualenv
  virtualenv -v virtualenv
  source virtualenv/bin/activate

Next, install project requirements:

.. code-block:: shell

  pip install ".[dev]"

Finally, verify everything works by running tests:

.. code-block:: shell

  make test

At this point you can make your changes.

Note that if you are using a virtual environment and switch to a new terminal
your virtual environment will not be active in the new terminal,
and you need to run the activate command again.
If you want to disable the loaded virtual environment in the same terminal window,
use the command:

.. code-block:: shell

  deactivate

----------------------
Development Guidelines
----------------------

+++++++++++++++++
Test your changes
+++++++++++++++++

This project aims for high test coverage. All changes must be properly tested, 
and we will accept no PRs that lack appropriate unit testing. We also expect 
existing tests to pass. You can run your tests using: 

.. code-block:: shell

  make test

++++++++++++++++++
Document your code
++++++++++++++++++

Documentation is how users learn to use your code, and no feature is complete 
without a full description of how to use it. If your PR changes external-facing 
interfaces, or if it alters semantics, the changes must be thoroughly described 
in the docstrings of the affected components. If your change adds a substantial 
new module, a new section in the documentation may be justified. 

Documentation is built using `Sphinx <https://www.sphinx-doc.org/en/master/>`__. 
You can build the documentation using the `Makefile.sphinx` makefile. For 
example you can build the HTML documentation like so:

.. code-block:: shell

  make -f Makefile.sphinx
