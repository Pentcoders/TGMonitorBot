
import asyncio
from datetime import datetime
import re

from typing import Optional
from telethon import TelegramClient, types, events
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import PeerChat, PeerChannel
from telethon.events.newmessage import NewMessage
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhoneCodeExpiredError, UserBotError
from aiogram.utils.markdown import hlink
from teleredis import RedisSession
from loguru import logger

from models import CardsMonitoring, PatternMonitoring, ChannelsMonitoring, UserCRM, UserChannels
from utils import session_storage, tele_log
from config import API_ID, API_HASH, NAME_SIGNAL_BOT
from .admin_bot import admin_send_message
from messages_bot import TEST_MESSAGE


class TGclientChannelMonitoring:

    def __init__(self, *,
                 user_name: str,
                 phone_number: str,
                 uuid_user: str,
                 password: str = None,
                 api_id: int = API_ID,
                 api_hash: str = API_HASH,
                 ) -> None:
        self._user_name = user_name
        self._phone_number = phone_number
        self._password = password

        self.session_name = f'@{user_name}_' + \
            self._phone_number.replace('+', '')
        self.session = RedisSession(self.session_name, session_storage)

        self._uuid_user: str = uuid_user
        self._user_crm: Optional[UserCRM] = None

        self.client = TelegramClient(
            self.session,
            api_id, api_hash,
            flood_sleep_threshold=25,
        )
        self.client.session.set_dc(2, '149.154.167.50', 443)
        self.user_cards: dict = {}
        self.all_monitoring_channels: set = set()
        self.started_monitoring = False
        logger.info(f'[TGUB/init] init UserBot {self}')

    def __repr__(self) -> str:
        return f'user[@{self._user_name}]'

    @tele_log('Connected Telegram API')
    async def send_code(self) -> None:
        if await self.is_authorized():
            return

        logger.info(
            f'[TGUB/send_code] {self} -> Send code authorization')
        result = await self.client.send_code_request(phone=self._phone_number)
        if isinstance(result, types.auth.SentCode):
            self._phone_code_hash = result.phone_code_hash
        else:
            logger.error(
                f'[TGUB/send_code] {self} -> Bad send code request')

    @tele_log('Sign in Telegram API')
    async def sign_in(self, code: str) -> types.User:
        try:
            if not self.client.is_connected():
                await self.client.connect()

            if self._phone_code_hash:
                self.user = await self.client.sign_in(self._phone_number, code)

        except SessionPasswordNeededError:
            logger.info(f'[TGUB/sign_in] {self} -> Password Needed')
            self.user = await self.client.sign_in(password=self._password)

        except PhoneCodeExpiredError as error:
            logger.error(
                f'[TGUB/sign_in] {self} -> Failed to connect', error)
            return 'PhoneCodeExpiredError'

    @tele_log('Authorization in Telegram API')
    async def is_authorized(self) -> bool:
        if self._user_crm is None:
            self._user_crm = await UserCRM.from_uuid_user(self._uuid_user)
        if not self.client.is_connected():
            await self.client.connect()
        return await self.client.is_user_authorized()

    @tele_log('Created monitoring function')
    async def start_filter_message(self):
        @self.client.on(events.NewMessage())
        async def message_event_handler(event):
            await self.filter_message(event)

    @tele_log('Created function update user channel title in DataBase')
    async def start_action_update_channels(self):
        @self.client.on(events.ChatAction)
        async def handler(event):
            if not event.new_title:
                return

            if isinstance(event.action_message.peer_id, PeerChannel):
                channel_id = event.action_message.peer_id.channel_id
            elif isinstance(event.action_message.peer_id, PeerChat):
                channel_id = event.action_message.peer_id.chat_id
            else:
                return

            logger.info(
                f'[TGUB/update] {self} -> Update user_channel [id{channel_id}] new_title=<{event.new_title}>')
            await UserChannels.update_channel(channel_id, event.new_title, self._user_crm)

    @tele_log('Start monitoring cards')
    async def start_monitoring(self):
        if self.started_monitoring:
            return
        event_handlers = self.client.list_event_handlers()
        if len(event_handlers) == 0:
            await self.start_action_update_channels()
            await self.start_filter_message()
        self.started_monitoring = True

    @tele_log('Stop monitoring cards')
    async def stop_monitoring(self):
        event_handlers = self.client.list_event_handlers()
        [self.client.remove_event_handler(*ev_ha) for ev_ha in event_handlers]
        self.started_monitoring = False
        

    async def filter_message(self, event):
        if len(self.user_cards) == 0:
            return
        if isinstance(event.message.to_id, PeerChannel):
            channel_id = event.message.to_id.channel_id
        elif isinstance(event.message.to_id, PeerChat):
            channel_id = event.message.chat_id
        else:
            return

        channel_id = abs(channel_id)
        message: str = event.raw_text.lower()
        for _, card in self.user_cards.items():
            if channel_id not in card.get('channels').keys():
                break
            info = None

            for keyword in card.get('patterns'):
                kw = keyword.lower()
                if message.find(kw) != -1 or len(re.findall(kw, message, re.IGNORECASE)) != 0:
                    info = '\n'.join([f'✅ <b>{keyword}</b>', ''])
                    break

            if info is None:
                break

            dt: datetime = event.message.date
            chat_title = card['channels'][channel_id]

            if isinstance(event.message.to_id, PeerChannel):
                info = '\n'.join([info, f'Channel: {chat_title}'])
            elif isinstance(event.message.to_id, PeerChat):
                info = '\n'.join([info, f'Chat: {chat_title}'])

            link_user = await self.get_link_user(event)
            if link_user is not None:
                info = '\n'.join([info, f'User: {link_user}'])

            link_message = await self.get_link_message(event, channel_id)
            
            info = '\n'.join([info, link_message, event.raw_text, '',
                              f"Time: {dt.strftime('%H:%M %d %B')}"])

            await admin_send_message(card.get('pushing'), info)

    @tele_log('Generate link user')
    async def get_link_user(self, event) -> str | None:
        participants = await self.client.get_participants(event.message.to_id)
        message_dict: dict = event.message.to_dict()
        if len(participants) == 0:
            raise AttributeError(f'Not Found users in channels.')
        
        if message_dict.get('from_id') is None:
            raise AttributeError(f'Message not found.')

        user_id = message_dict['from_id']['user_id']
        users = list(filter(lambda participant: participant.id == user_id, participants))
        
        if len(users) == 0:
            raise AttributeError(f'Not Found user in channels.')
        
        user = users[0]
        link_user = f'{user.first_name} {user.last_name}'
        if user.username:
            link_user = hlink(link_user, f'https://t.me/{user.username}')
        elif user.phone:
            link_user = hlink(link_user, f'https://t.me/+{user.phone}')
        return link_user
    
    @tele_log('Generate link message')
    async def get_link_message(self, event: NewMessage.Event, channel_id:int) -> str | None:
        link_message = f'Message:'
        if isinstance(event.message.to_id, PeerChat):
            return link_message
        
        id_message = event.message.id
        if id_message is not None:
            link_message = hlink(link_message, f'https://t.me/c/{channel_id}/{id_message}')

        return link_message

    @tele_log('Update user channels')
    async def get_all_user_channels(self):
        dialogs = await self.client.get_dialogs()
        user = await UserCRM.from_uuid_user(self._uuid_user)
        await UserChannels.add_channels(dialogs, user)
        logger.info(
            f'[TGUB/get_all_user_channels] {self} -> Found {len(dialogs)} channels')
        return 'UpdateUserChannels'

    async def stop_card_monitoring(self, card_uuid):
        logger.info(
            f'[TGUB/stop_card_monitoring] {self} -> Delete card {card_uuid}')
        card = self.user_cards.get(card_uuid)
        if card is None:
            return
        for channel in card.get('channels').keys():
            self.all_monitoring_channels.remove(channel)
        if card:
            self.user_cards.pop(card_uuid)
        

    async def start_card_monitoring(self):
        if not self.started_monitoring:
            await self.start_monitoring()
            

    @logger.catch
    async def update_card_monitoring(self, card_uuid: str):
        card: CardsMonitoring = await CardsMonitoring.from_uuid(card_uuid)
        channels: list[ChannelsMonitoring] = await ChannelsMonitoring.from_card(card)
        patterns: list[PatternMonitoring] = await PatternMonitoring.from_card(card)
        if channels is None or patterns is None:
            return
        card_ch = {}
        for channel in channels:
            self.all_monitoring_channels.add(channel.channel_monitoring.id_channel_tg)
            card_ch.update({channel.channel_monitoring.id_channel_tg: channel.channel_monitoring.title_channel_tg})
            
        self.user_cards.update(
            {
                card_uuid: {
                    'channels': card_ch,
                    'patterns': [pattern.pattern.lower() for pattern in patterns],
                    'pushing': card.channel_pushing.id_chat
                }
            }
        )
        await card.update_status(True)

    @tele_log('HealthCheck UserBot')
    async def health_check_card_monitoring(self, card_uuid: str):
        logger.info(f'[TGUB/health_check_card_monitoring] {self}')
        event_handlers = self.client.list_event_handlers()
        if len(event_handlers) == 0:
            return 'MonitoringStoped'
        if card_uuid not in list(self.user_cards.keys()):
            return 'CardNotFound'
        return 'CardMonitoringRunning'

    async def drop_cards(self):
        logger.info(
            f'[TGUB/drop_cards] {self} ->  Delete all monitoring cards')
        self.user_cards.clear()
        self.all_monitoring_channels.clear()
        await self.stop_monitoring()

    @tele_log('Create signal channel')
    async def create_signal_channels(self, card: CardsMonitoring) -> types.Channel:
        result = await self.client(CreateChannelRequest(
            title=f'Channel {card.title.split()[1]}',
            about=f'Signal Channel from {card.title}',
            megagroup=True, broadcast=True))
        return result.chats[0]

    @tele_log('Add SignalBot to signal channel')
    async def invite_to_channel_bot(self, channel: types.Channel):
        result = await self.client(ResolveUsernameRequest(NAME_SIGNAL_BOT))
        bot = result.users[0]
        rights = types.ChatAdminRights(
            post_messages=True
        )
        try:
            await self.client(EditAdminRequest(channel.id, bot.id, rights, 'signal_bot'))
            await self.client(InviteToChannelRequest(channel.id, [NAME_SIGNAL_BOT]))
        except UserBotError as error:
            await self.client(EditAdminRequest(channel.id, bot.id, rights, 'signal_bot'))
            logger.error(error)

    async def send_test_message(self, chat_id: int):
        logger.info(f'[TGUB/send_test_message] {self} -> Send Test message')
        result = None
        while result is None:
            result = await admin_send_message(chat_id, TEST_MESSAGE)
            await asyncio.sleep(2)

    async def check_channel(self, chat_id: int):
        try:
            await asyncio.wait_for(self.send_test_message(chat_id), timeout=15)
        except asyncio.TimeoutError:
            logger.error(
                f'[TGUB/check_channel] {self} -> Bad create signal channel')

    @tele_log('Add SignalBot to signal channel')
    async def card_configuration(self, card_uuid: str):
        card: CardsMonitoring = await CardsMonitoring.from_uuid(card_uuid)
        if card is None:
            return None

        channel = await self.create_signal_channels(card)
        if channel is None:
            return None

        db_channel: UserChannels = await UserChannels.add_channel(channel, self._user_crm)
        await card.change_pushing_channels(db_channel.id_user_channel)

        await self.invite_to_channel_bot(channel)
        asyncio.ensure_future(self.check_channel(db_channel.id_chat))

        return 'ChannelСreatedSuccessfully'
