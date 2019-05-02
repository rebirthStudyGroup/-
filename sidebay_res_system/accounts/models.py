from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

# Create your models here.
class User(AbstractUser):
    """
    ユーザ情報を提供するDTOクラス
    """
    user_id = models.IntegerField(verbose_name='ユーザID', primary_key=True)
    username = models.CharField(verbose_name='ユーザ名', unique=True, max_length=40, default=None, blank=True)
    mail_address = models.EmailField(verbose_name='メールアドレス', unique=True, default=None)
    password = models.CharField(verbose_name='パスワード', max_length=10, default=None) #パスワードの入力制限は設けるか

    USERNAME_FIELD = 'mail_address'

    def check_pass(self, password):
        return password == User.objects.filter(mail_address=self.mail_address).first().password

    def __str__(self):
        return self.mail_address

    def get_full_name(self):
        return self.mail_address

    def get_short_name(self):
        return self.mail_address

class Lottery_pool(models.Model):
    """
    抽選申込情報を提供するDTOクラス
    """
    mail_address = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='mail_address'
    )
    check_in_date = models.DateField()
    stay_term = models.IntegerField() #連泊数の最大値は設定するか
    number_of_guests = models.SmallIntegerField()
    purpose = models.SmallIntegerField()

class Request_pool(models.Model):
    """
    本申込情報を提供するDTOクラス
    """
    mail_address = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='mail_address'
    )
    check_in_date = models.DateField()
    stay_term = models.IntegerField() #連泊数の最大値は設定するか
    number_of_guests = models.SmallIntegerField()
    purpose = models.SmallIntegerField()
    request_status = models.SmallIntegerField()
    expire_date = models.DateField()

class Reservations(models.Model):
    """
    予約情報を提供するDTOクラス
    """
    mail_address = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='mail_address'
    )
    check_in_date = models.DateField()
    stay_term = models.IntegerField() #連泊数の最大値は設定するか
    number_of_guests = models.SmallIntegerField()
    purpose = models.SmallIntegerField()

class Inventory(models.Model):
    """
    備品マスタ情報を提供するDTOクラス
    """
    inventory_name = models.TextField()
    description = models.TextField()

class Inventory_list(models.Model):
    """
    備品情報を提供するDTOクラス
    """
    inventory_name = models.ForeignKey(
        'Inventory',
        on_delete=models.CASCADE,
    )
