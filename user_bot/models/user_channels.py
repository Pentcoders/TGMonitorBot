from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger, UniqueConstraint, update

from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from telethon.tl.types import Chat, Channel
from telethon.tl.custom.dialog import Dialog
from .database import BaseModel, async_session
from .users_crm import UserCRM


class UserChannels(BaseModel):
    __tablename__ = 'user_channels'

    id_user_channel = Column(Integer, primary_key=True,
                             unique=True, autoincrement=True)

    id_channel_tg = Column(BigInteger)
    id_chat = Column(BigInteger)

    title_channel_tg = Column(String, nullable=True)
    is_creator = Column(Boolean, default=False)

    # relationship out
    user_crm_id = Column(Integer, ForeignKey(
        'users_crm.id_user_crm'), nullable=False)
    user_crm: UserCRM = relationship(
        'UserCRM', backref='user_channel', lazy='joined')

    UniqueConstraint(id_channel_tg, user_crm_id)

    def __eq__(self, other):
        if isinstance(other, UserChannels):
            return all([
                self.id_channel_tg == other.id_channel_tg,
                self.user_crm_id == other.user_crm_id
            ]) 
        return NotImplemented

    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

            
    @classmethod
    async def add_channels(cls, dialogs: list[Dialog], user_crm: UserCRM):
        user_chs: dict[int, UserChannels] = {}
        for dialog in dialogs:
            if not (dialog.is_channel or dialog.is_group):
                continue

            if not isinstance(dialog.entity, Chat | Channel):
                continue

            user_chs.update({dialog.entity.id:UserChannels(id_chat=dialog.id,
                            id_channel_tg=dialog.entity.id,
                            title_channel_tg=dialog.entity.title,
                            is_creator=dialog.entity.creator,
                            user_crm_id=user_crm.id_user_crm)})

        async with async_session() as session, session.begin():
            result = await session.execute(
                    select(UserChannels).
                    where(UserChannels.user_crm_id == user_crm.id_user_crm)
                )
            chs_db: list[UserChannels] = result.scalars().all()

            for ch_db in chs_db:
                user_ch: Optional[UserChannels] = user_chs.get(ch_db.id_channel_tg)
                if user_ch is None:
                    await session.delete(ch_db)
                    continue
                
                user_chs.pop(ch_db.id_channel_tg)
                if user_ch.title_channel_tg != ch_db.title_channel_tg:
                    ch_db.title_channel_tg = user_ch.title_channel_tg
                    session.add(ch_db)
            
            session.add_all(list(user_chs.values()))
            await session.commit()

    
    @classmethod
    async def update_channel(cls, id_channel_tg:int, new_title:str, user_crm: UserCRM):
        async with async_session() as session, session.begin():
            result = await session.execute(
                    select(UserChannels).
                    where(UserChannels.user_crm_id == user_crm.id_user_crm,
                          UserChannels.id_channel_tg == id_channel_tg)
                )
            ch_db: Optional[UserChannels] = result.scalars().first()
            if ch_db:
                ch_db.title_channel_tg = new_title
                session.add(ch_db)
                await session.commit()


    @classmethod
    async def add_channel(cls, channel: Chat | Channel, user_crm: UserCRM):
        user_ch = UserChannels(id_chat=int(f'-100{channel.id}'),
                            id_channel_tg=channel.id,
                            title_channel_tg=channel.title,
                            is_creator=channel.creator,
                            user_crm_id=user_crm.id_user_crm)

        async with async_session() as session, session.begin():
            cls = await user_ch.commit()
            
        return cls