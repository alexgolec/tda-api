``tda-api`` Helper Bot
======================

A bot that listens on tda-api server traffic and chimes in whenever it feels a 
user is asking a frequently-asked question.


How does it work?
-----------------

It listens on incoming messages and matches them against a configured list of 
trigger prompts. When one of those prompts triggers, it responds to the message 
with a (hopefully) helpful link to the appropriate FAQ page. It avoids showing 
the same message to users over and over again by maintaining a database of the 
messages each user has triggered. 


How do I deploy it?
-------------------

This bot is packaged as a docker container. I use an M1 MacBook, the 
``Dockerfile`` builds an image using the ``arm64v8`` version of Alpine Linux.  
This also *happens* to be suitable for deployment to a Raspberry Pi 4B.  

To deploy, first build the docker container: 

.. code-block:: bash
   cd /tda-api/repo/path/discord_help_bot
   docker build .

Create the volume on which you'll store the state DB: 

.. code-block:: bash
   docker volume create discord_bot_state

   # Find the ID of the created image here:
   docker images

Initialize the state:

.. code-block:: bash
   docker run -t -v discord_bot_state:/state <IMAGE_ID> init --sqlite_db_file 
   /sqlite/state.sqlite_db

Start the bot:

.. code-block:: bash
   docker run -t -v discord_bot_state:/state <IMAGE_ID> run --token 
   <DISCORD_TOKEN>
