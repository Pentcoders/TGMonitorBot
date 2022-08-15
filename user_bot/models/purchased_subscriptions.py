from datetime import datetime
import pytz
import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.future import select

from .database import BaseModel, async_session
from .users_crm import UserCRM
from .subscriptions import Subscribtion


class PurchasedSubscriptions(BaseModel):
    __tablename__ = 'purchased_subscriptions'

    id_ps = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    date_end_subscriptions = Column(DateTime)

    # relationship out
    user_crm_id = Column(Integer, ForeignKey(
        'users_crm.id_user_crm'), unique=True, nullable=False)
    user_crm = relationship(
        'UserCRM', backref='purchased_subscription', cascade="all")

    subscribtion_id = Column(Integer, ForeignKey(
        'subscriptions.id_subscriptions'), nullable=False)
    subscribtion: Subscribtion = relationship(
        'Subscribtion', backref='purchased_subscription', cascade="all", lazy='joined')

    async def commit(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def set_purchased_subscription(cls, user_crm: UserCRM, subscribtion: Subscribtion):
        purchased_subscription = PurchasedSubscriptions(
            date_end_subscriptions=(datetime.utcnow()+subscribtion.term),
            user_crm_id=user_crm.id_user_crm,
            subscribtion_id=subscribtion.id_subscriptions,
            subscribtion=subscribtion
        )

        async with async_session() as session:
            result = await session.execute(
                select(PurchasedSubscriptions).
                where(PurchasedSubscriptions.user_crm_id ==
                      purchased_subscription.user_crm_id)
            )
            subscrdb: PurchasedSubscriptions = result.scalars().first()

        if not subscrdb:
            cls = await purchased_subscription.commit()
        else:
            date_start = datetime.utcnow()
            bd_time = subscrdb.date_end_subscriptions.replace(tzinfo=None)
            if (date_start < bd_time):
                date_start = bd_time
            subscrdb.date_end_subscriptions = date_start + \
                subscribtion.term
            
            if subscrdb.subscribtion == subscribtion:
                subscrdb.subscribtion = subscribtion
                subscrdb.subscribtion_id = subscribtion.id_subscriptions

            await subscrdb.commit()
            cls = subscrdb
        return cls

    @staticmethod
    async def from_user_crm_id(id_user_crm: int):
        async with async_session() as session:
            result = await session.execute(
                select(PurchasedSubscriptions).\
                where(PurchasedSubscriptions.user_crm_id == id_user_crm))
            
            pursh_sub_db:PurchasedSubscriptions  = result.scalars().first()

        if pursh_sub_db is None:
            return None

        return pursh_sub_db