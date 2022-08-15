from datetime import datetime
from aiogram.dispatcher.filters import Filter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from bot_init import PURCHASED_SUBSCRIPTIONS
from messages_bot import (BUTTON_BUY_SUBSCRIPTION,
                          BUTTON_HELP,
                          BUTTON_SUPPORT,
                          BUTTON_REBUY_SUBSCRIPTION,
                          BUTTON_SETTINGS,
                          BUTTON_MONITORING
                          )
class StateBot(StatesGroup):
    # StateLogo = State()
    StateLogo = State()
    StatePgSubscription = State()
    StateSettings = State()
    StateStartAllMontoringCards = State()
    StateStopAllMontoringCards = State()
    StatePhoneNumber = State()
    StateEnterPasswordYesOrNo = State()
    StateEnterPassword = State()
    StateSendCodeAuthorized = State()
    StateInformAttention = State()
    StateCards = State()
    StateCreateCard = State()
    StateChoisePushing = State()
    StateChangePushing = State()
    StateChoiseMonitoring = State()
    StateChangeProfile = State()
    StateChangeTitleCard = State()
    StateChangeDescriptionCard = State()
    StatePatterns = State()
    StatePatternInput = State()
    StatePatternChangeDescr = State()
    PatternDelete = State()
    CardDelete = State()

    
    
async def user_is_subscribed_local(message: types.Message) -> bool:
    user = message.from_user
    if user.is_bot:
        user = message.chat
    sub_user = PURCHASED_SUBSCRIPTIONS.get(user.id)
    if sub_user is None:
        return False
    dt_now = datetime.utcnow()
    bd_time = sub_user.date_end_subscriptions.replace(tzinfo=None)
    if bd_time < dt_now:
        return False
    return True

class InlineFilte(Filter):

    def __init__(self, key_btn: str, *args, **kwargs) -> None:
        self.key = key_btn
        super().__init__(*args, **kwargs)

    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and self.key in callback.data 


class CommandBuySubscription(Filter):
    keys = [
        BUTTON_BUY_SUBSCRIPTION,
        BUTTON_REBUY_SUBSCRIPTION
    ]

    async def check(self, message: types.Message):
        return message.text in self.keys


class CommandShowSettings(Filter):
    keys = [
        BUTTON_SETTINGS
    ]

    async def check(self, message: types.Message):
        is_sub = await user_is_subscribed_local(message)
        return is_sub and message.text in self.keys


class CommandShowMonitoring(Filter):
    keys = [
        BUTTON_MONITORING
    ]

    async def check(self, message: types.Message):
        is_sub = await user_is_subscribed_local(message)
        return is_sub and message.text in self.keys


class SubscriptionPage(Filter):
    async def check(self, callback: types.CallbackQuery):
        return callback.data.split('#')[0] == 'character'


class CardPage(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'card'


class PatternPage(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'pattern'


class PaymentFilter(Filter):
    async def check(self, callback: types.CallbackQuery):
        return callback.data.split(':')[0] == 'btn_payment'


class PushingChannelPage(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'push_ch'


class PushingChannelChoise(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_choise_push_ch'


class PushingChannelChange(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_CPC'


class SettingsCard_Monitoring(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_monitoring_card'
    


class DeleteCard_Monitoring(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_delete_card'


class SettingsCard_Pattern(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_pattern_card'


class SettingsCard_Pushing(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_pushing_card'


class SettingsCard_Profile(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_profile_card'


class MonitoringChannelChoise(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_CMC'


class ChangeTitleCard(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_CT'


class ChangeDescriptionCard(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_CD'


class MonitoringChannelPage(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'monitoring_ch'


class PatternCreate(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_CrPtt'


class PatternChange(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_ChPtt'


class PatternDelete(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_DeletePtt'


class DeleteYes(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data == 'delete:yes'


class DeleteNo(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data == 'delete:no'


class PatternDescription(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_ChDescPtt'


class StartMonitoringCard(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_StartM'


class StopMonitoringCard(Filter):
    async def check(self, callback: types.CallbackQuery):
        is_sub = await user_is_subscribed_local(callback.message)
        return is_sub and callback.data.split(':')[0] == 'btn_StopM'
