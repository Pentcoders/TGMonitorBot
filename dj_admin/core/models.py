from datetime import timedelta
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
import uuid


class TGUsers(models.Model):

    id_user = models.AutoField(primary_key=True)
    id_user_tg = models.BigIntegerField(unique=True, null=False)
    user_name = models.CharField(max_length=32)
    full_name = models.CharField(max_length=32)
    api_refer = models.CharField(max_length=32, null=True)

    class Meta:
        db_table = "tg_users"

    @staticmethod
    def list_display() -> tuple:
        return ('id_user', 'id_user_tg', 'user_name', 'full_name', 'api_refer')


# # Create your models here.
# class UserAdmin(models.Model):

#     id_user_admin = models.AutoField(primary_key=True)
#     id_user_tg = models.IntegerField(unique=True, null=False)
#     user_name = models.CharField(max_length=32)

#     class Meta:
#         db_table = "users_admin"

#     @staticmethod
#     def list_display() -> list[str] | tuple[str]:
#         return ('id_user_admin', 'id_user_tg', 'user_name')


class Subscribtion(models.Model):

    id_subscriptions = models.AutoField(primary_key=True)
    title = models.CharField(unique=True, null=False, max_length=32)
    price = models.IntegerField(null=False)
    term = models.DurationField(null=False, default=timedelta(days=31))
    description = models.TextField()
    count_card_monitoring = models.IntegerField(null=False, default=1)
    count_channels_monitoring = models.IntegerField(null=False, default=5)
    count_pattern_monitoring = models.IntegerField(null=False, default=5)
    api_subscriptions = models.CharField(
        default=uuid.uuid4().hex, max_length=32, editable=False)

    @staticmethod
    def list_display() -> tuple:
        return ('id_subscriptions', 'title', 'price',
                'term', 'description', 'count_card_monitoring',
                'count_channels_monitoring', 'count_pattern_monitoring',
                'api_subscriptions')

    class Meta:
        db_table = "subscriptions"


class UserCRM(models.Model):

    id_user_crm = models.AutoField(primary_key=True)
    uuid_user = models.UUIDField(default=uuid.uuid4, editable=False)
    tg_user = models.ForeignKey(TGUsers, on_delete=models.PROTECT)
    phone_number = PhoneNumberField(null=True, blank=False, default=None)
    password = models.CharField(max_length=32, null=True, default=None)
    is_authorized = models.BooleanField(default=False)

    class Meta:
        db_table = "users_crm"

    @staticmethod
    def list_display() -> tuple:
        return ('id_user_crm', 'uuid_user', 'tg_user',
                'phone_number', 'password')


# class ReferralUsers(models.Model):

#     id_referral = models.AutoField(primary_key=True)
#     api_referral = models.CharField(
#         default=uuid.uuid4().hex, max_length=32, editable=False)
#     user_crm = models.ForeignKey(UserCRM, on_delete=models.CASCADE)
#     count_referral = models.IntegerField(
#         default=0, validators=[MinValueValidator(0)])
#     count_subreferral = models.IntegerField(
#         default=0, validators=[MinValueValidator(0)])

#     def list_display() -> list[str] | tuple[str]:
#         return ('id_referral', 'api_referral', 'user_crm',
#                 'count_referral', 'count_subreferral')

#     class Meta:
#         db_table = "referral_users"


class PurchasedSubscriptions(models.Model):

    id_ps = models.AutoField(primary_key=True)
    user_crm = models.OneToOneField(
        UserCRM, on_delete=models.CASCADE, unique=True)
    subscribtion = models.ForeignKey(
        Subscribtion, on_delete=models.SET_NULL, null=True)
    date_end_subscriptions = models.DateTimeField(null=False)

    @classmethod
    def list_display(cls) -> tuple:
        return ('id_ps', 'user_crm', 'subscribtion',
                'date_end_subscriptions')

    class Meta:
        db_table = "purchased_subscriptions"


# class UserChannels(models.Model):

#     id_user_channel = models.AutoField(primary_key=True)
#     id_channel_tg = models.BigIntegerField(null=False)
#     id_chat = models.BigIntegerField(null=False)
#     title_channel_tg = models.CharField(max_length=100, null=True)
#     is_creator = models.BooleanField(default=False)

#     user_crm = models.ForeignKey(UserCRM, on_delete=models.CASCADE)

#     def list_display() -> list[str] | tuple[str]:
#         return ('id_user_channel', 'user_crm', 'id_channel_tg',
#                 'title_channel_tg', 'is_creator')

#     class Meta:
#         db_table = "user_channels"
#         constraints = [models.UniqueConstraint(fields=['id_channel_tg', 'user_crm_id'], name='unique appversion')]


# class CardsMonitoring(models.Model):

#     id_card = models.AutoField(primary_key=True)
#     card_uuid = models.CharField(default=uuid.uuid4().hex, max_length=32, editable=False)
#     title = models.CharField(null=True, max_length=32)
#     description = models.TextField(null=True)
#     is_running = models.BooleanField(default=False)

#     channel_pushing = models.ForeignKey(
#         UserChannels, null=False, on_delete=models.CASCADE)

#     def list_display() -> list[str] | tuple[str]:
#         return ('id_card', 'title', 'description', 'channel_pushing')

#     class Meta:
#         db_table = "cards_monitoring"


# class ChannelsMonitoring(models.Model):

#     id_monitoring = models.AutoField(primary_key=True)

#     card_monitoring = models.ForeignKey(
#         CardsMonitoring, on_delete=models.CASCADE, null=False)
#     channel_monitoring = models.ForeignKey(
#         UserChannels, on_delete=models.CASCADE, null=False)

#     def list_display() -> list[str] | tuple[str]:
#         return ('id_monitoring', 'card_monitoring', 'channel_monitoring')

#     class Meta:
#         db_table = "channels_monitoring"


# class PatternMonitoring(models.Model):

#     id_pattern = models.AutoField(primary_key=True)
#     pattern = models.TextField()
#     description = models.TextField()

#     card_monitoring = models.ForeignKey(
#         CardsMonitoring, on_delete=models.CASCADE)

#     def list_display() -> list[str] | tuple[str]:
#         return ('id_pattern', 'pattern', 'description', 'card_monitoring')

#     class Meta:
#         db_table = "patterns_monitoring"
