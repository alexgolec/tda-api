import os

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    '''
    A discord user.
    '''
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)

    # Time when this user was first observed
    addition_time = Column(DateTime(timezone=True), server_default=func.now())
    # User's username on discord on the message which prompted them to be added 
    # to the DB. They might go by a different username now.
    discord_username = Column(String)
    # Discord ID of the user. Immutable on Discord's side.
    discord_id = Column(Integer, index=True, unique=True)

    # Prompts which were triggered for this user.
    triggered_prompts = relationship('TriggeredPrompt')


    def __repr__(self):
        return (f'User(id={self.id}, addition_time={self.addition_time}, '+
                f'discord_username={self.discord_username}, '+
                f'discord_id={self.discord_id})')


    @classmethod
    def new_user(cls, discord_user_name, discord_user_id):
        'Create a new user'
        return User(
                discord_username=discord_user_name,
                discord_id=discord_user_id)


    @classmethod
    def get_user_with_discord_id(cls, session, discord_user_id):
        'Get user by ID'
        return (session
                .query(User)
                .filter_by(discord_id=discord_user_id)
                .scalar())


    @classmethod
    def get_triggered_prompt_for_user(cls, session, prompt_name, discord_user_id):
        '''Get a triggered prompt for a given user, or returns None if the user 
        never triggered that prompt.'''
        return (session
                .query(TriggeredPrompt)
                .filter_by(prompt_name=prompt_name)
                .join(User)
                .filter(User.discord_id == discord_user_id)
                .all())


class TriggeredPrompt(Base):
    __tablename__ = 'TriggeredPrompt'

    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    # Name of triggered prompt. See the config.yml file for details. Represented
    # as the keys of the config['prompts'] dictionary.
    prompt_name = Column(String, primary_key=True)
    # Time when the message was recorded as shown *on the SQL server side.* This 
    # time is only loosely tied to the actual send time of the message.
    trigger_time = Column(
            DateTime(timezone=True),
            server_default=func.now(),
            primary_key=True)

    # Full text of the message which triggered this showing.
    trigger_message = Column(String)
    # Trigger string that was matched against the message.
    trigger_string = Column(String)


    @classmethod
    def record_prompt_for_user(
            cls, user, prompt_name, msg_content, trigger_string):
        return TriggeredPrompt(
                user_id=user.id,
                prompt_name=prompt_name,
                trigger_message=msg_content,
                trigger_string=trigger_string)


def get_engine(db_file):
    db_file = os.path.abspath(db_file)
    db_path = f'sqlite:///{db_file}'
    return create_engine(db_path, echo=False)
