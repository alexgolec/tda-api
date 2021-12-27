import argparse
import collections
import json
import logging
import os

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import literal, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

import discord
import yaml


################################################################################
# Object schema


Base = declarative_base()

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)

    addition_time = Column(DateTime(timezone=True), server_default=func.now())
    discord_username = Column(String)
    discord_id = Column(Integer, index=True, unique=True)
    triggered_prompts = relationship('TriggeredPrompt')

    def __repr__(self):
        return (f'User(id={self.id}, addition_time={self.addition_time}, '+
                f'discord_username={self.discord_username}, '+
                f'discord_id={self.discord_id})')


class TriggeredPrompt(Base):
    __tablename__ = 'TriggeredPrompt'

    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    prompt_name = Column(String, primary_key=True)

    trigger_time = Column(DateTime(timezone=True), server_default=func.now())
    trigger_message = Column(String)
    trigger_string = Column(String)


def get_engine(db_file):
    db_file = os.path.abspath(db_file)
    db_path = f'sqlite:///{db_file}'
    return create_engine(db_path, echo=False)


################################################################################
# Bot implementation


class HelperBot(discord.Client):

    def __init__(self, config_path, db_path):
        super().__init__()

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.engine = get_engine(db_path)
        self.session = sessionmaker(bind=self.engine)()


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        print(message)

        if message.author.id == self.user.id:
            return

        if message.guild.name != 'tda-api':
            return

        for prompt_name, prompt in self.config['prompts'].items():
            for trigger in prompt['triggers']:
                if (trigger in message.content.lower()
                        and self.should_trigger_for_prompt(
                            prompt_name, message.author)):
                    await message.reply(prompt['response'])
                    self.record_prompt_seen(prompt_name, trigger, message)


    def should_trigger_for_prompt(self, prompt_name, discord_user):
        user_id = discord_user.id
        prompts_seen = (self.session
                .query(User)
                .filter_by(discord_id=user_id)
                .join(
                    TriggeredPrompt,
                    TriggeredPrompt.user_id == User.id)
                .filter_by(prompt_name=prompt_name)
                .scalar())
        return prompts_seen is None


    def record_prompt_seen(
            self, prompt_name, triggered_string, discord_message):
        # Get/create the user
        user = (self.session
                .query(User)
                .filter_by(discord_id=discord_message.author.id)
                .scalar())
        if not user:
            user = User(
                    discord_username=discord_message.author.name,
                    discord_id=discord_message.author.id)
            self.session.add(user)
            self.session.flush()

        # Record the triggered prompt
        triggered_prompt = TriggeredPrompt(
                user_id=user.id,
                prompt_name=prompt_name,
                trigger_message=discord_message.content,
                trigger_string=triggered_string)
        self.session.add(triggered_prompt)

        self.session.commit()

        users = (self.session
                .query(User)
                .filter_by(discord_id=discord_message.author.id)
                .all())


################################################################################
# Main functions


def run_bot_main(args):
    client = HelperBot(args.config, args.sqlite_db_file)
    client.run(args.token)


def init_main(args):
    def dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))

    Base.metadata.create_all(get_engine(args.sqlite_db_file))


def main():
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

    args = parser.parse_args()

    if args.command == 'run':
        run_bot_main(args)
    elif args.command == 'init':
        init_main(args)
    else:
        assert False

if __name__ == '__main__':
    main()
