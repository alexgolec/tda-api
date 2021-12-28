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

    addition_time = Column(DateTime(timezone=True), server_default=func.now())
    discord_username = Column(String)
    discord_id = Column(Integer, index=True, unique=True)
    triggered_prompts = relationship('TriggeredPrompt')


    def __repr__(self):
        return (f'User(id={self.id}, addition_time={self.addition_time}, '+
                f'discord_username={self.discord_username}, '+
                f'discord_id={self.discord_id})')


    @classmethod
    def new_user(cls, discord_user_name, discord_user_id):
        return User(
                discord_username=discord_user_name,
                discord_id=discord_user_id)


    @classmethod
    def get_user_with_id(cls, session, discord_user_id):
        return (session
                .query(User)
                .filter_by(discord_id=discord_user_id)
                .scalar())


    @classmethod
    def get_triggered_prompt_for_user(cls, session, prompt_name, discord_user_id):
        return (session
                .query(User)
                .filter_by(discord_id=discord_user_id)
                .join(
                    TriggeredPrompt,
                    TriggeredPrompt.user_id == User.id)
                .filter_by(prompt_name=prompt_name)
                .scalar())


class TriggeredPrompt(Base):
    __tablename__ = 'TriggeredPrompt'

    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    prompt_name = Column(String, primary_key=True)

    trigger_time = Column(DateTime(timezone=True), server_default=func.now())
    trigger_message = Column(String)
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



