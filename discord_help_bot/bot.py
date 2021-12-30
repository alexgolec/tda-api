import argparse
import collections
import json
import logging
import os
import sys

from sqlalchemy.orm import sessionmaker

import discord
import yaml

from models import Base, User, TriggeredPrompt, get_engine


################################################################################
# Bot implementation


class HelperBot(discord.Client):

    def __init__(self, config, db_engine):
        super().__init__()

        self.config = config
        self.engine = db_engine
        self.session = sessionmaker(bind=self.engine)()


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        for prompt_name, prompt in self.config['prompts'].items():
            for trigger in prompt['triggers']:
                if (trigger in message.content.lower()
                        and self.should_trigger_for_prompt(
                            prompt_name, message.author)):
                    await message.reply(prompt['response'])
                    self.record_prompt_seen(prompt_name, trigger, message)


    def should_trigger_for_prompt(self, prompt_name, discord_user):
        'Indicates whether the user should see the given prompt'
        user_id = discord_user.id
        prompts_seen = User.get_triggered_prompt_for_user(
                self.session, prompt_name, user_id)
        return len(prompts_seen) == 0


    def record_prompt_seen(
            self, prompt_name, triggered_string, discord_message):
        'Record that the author of this message was sent this prompt.'
        # Get/create the user
        user = User.get_user_with_discord_id(
                self.session, discord_message.author.id)
        if not user:
            user = User.new_user(
                    discord_message.author.name, discord_message.author.id)
            self.session.add(user)
            self.session.flush()

        # Record the triggered prompt
        triggered_prompt = TriggeredPrompt(
                user_id=user.id,
                prompt_name=prompt_name,
                trigger_message=discord_message.content,
                trigger_string=triggered_string)
        self.session.add(TriggeredPrompt.record_prompt_for_user(
            user, prompt_name, discord_message.content, triggered_string))

        self.session.commit()

        return triggered_prompt


################################################################################
# Main functions


def run_bot_main(args):
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    engine = get_engine(args.sqlite_db_file)

    client = HelperBot(config, engine)
    client.run(args.token)


def main(argv):
    parser = argparse.ArgumentParser('FAQ-based helper bot for tda-api')
    subparsers = parser.add_subparsers(metavar='', dest='command')

    run_parser = subparsers.add_parser('run', help=
            'Run the Discord bot. Assumes all state is initialized.')
    run_parser.add_argument('--token', required=True, help='Discord API token')
    run_parser.add_argument('--config', required=True, help='Path to config YAML')
    run_parser.add_argument('--sqlite_db_file', required=True, help=
            'Location of sqlite3 database file')

    init_parser = subparsers.add_parser('init', help=
            'Initialize all state, including database state.')
    init_parser.add_argument('--sqlite_db_file', required=True, help=
            'Location of sqlite3 database file')

    args = parser.parse_args(argv)

    if args.command == 'run':
        run_bot_main(args)
    elif args.command == 'init':
        Base.metadata.create_all(get_engine(args.sqlite_db_file))
    else:  # pragma: no cover
        assert False

if __name__ == '__main__':  # pragma: no cover
   main(sys.argv[1:])
