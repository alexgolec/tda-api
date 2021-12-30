FROM arm64v8/alpine:3.15.0

# Install system-level dependcies
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3
RUN ln -sf python3 /usr/bin/python

RUN apk add --update --no-cache build-base
RUN apk add --update --no-cache python3-dev
RUN apk add --update --no-cache sqlite

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Copy application
RUN mkdir /usr/discord_help_bot

COPY config.yml /usr/discord_help_bot
COPY *.py /usr/discord_help_bot
COPY docker-run.sh /usr/discord_help_bot
COPY requirements.txt /usr/discord_help_bot

# Install python requirements
RUN cd /usr/discord_help_bot && pip install -r requirements.txt

ENTRYPOINT ["python", "/usr/discord_help_bot/bot.py"]
