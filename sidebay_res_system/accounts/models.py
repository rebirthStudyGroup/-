from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.base_user import BaseUserManager

# 試しにメールアドレスでのログイン機能を実装するためのコードを書いてみる
class UserManager(BaseUserManager):
    """ユーザーマネージャー"""

    user_in_migrations = True

    def _create_user(self, mail_address, password, **extra_fields):
        """メールアドレスの登録を必須にする"""
        if not mail_address:
            raise ValueError('The given email must be set')
        email = self.normalize_email(mail_address)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mail_address, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mail_address, password, **extra_fields)

    def create_superuser(self, mail_address, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mail_address, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    ユーザ情報を提供するDTOクラス
    """
    user_id = models.IntegerField(_('ユーザID'), primary_key=True)
    username = models.CharField(_('ユーザ名'), unique=True, max_length=40, default=None, blank=True)
    mail_address = models.EmailField(_('メールアドレス'), unique=True, default=None)
    password = models.CharField(_('パスワード'), max_length=10, default=None) #パスワードの入力制限は設けるか

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    EMAIL_FIELD = 'mail_address'
    USERNAME_FIELD = 'mail_address'
    REQUIRED_FIELDS = []

    def check_pass(self, password: str) -> bool:
        """引数のパスワードとユーザーインスタンスのパスワードが一致するかチェックする

        :param password: 画面入力されたパスワード
        :return: 引数のパスワードとユーザーインスタンスが持つパスワードが一致するかどうかチェックする
        """
        user = UserDao.get_user(str(self.mail_address))
        if user is not None:
            return password == user.password
        return False

class UserDao:
    """Userオブジェクトを操作するクラス"""

    @staticmethod
    def get_user(mail_address: str) -> User:
        """Userオブジェクトを取得

        :param mail_address メールアドレス
        """
        try:
            return User.objects.get(mail_address=mail_address)
        except ObjectDoesNotExist:
            print("対象のオブジェクトがDBに存在しません")

    @staticmethod
    def get_users():
        return User.objects.order_by('username')

    @staticmethod
    def create_user(user_id:int, username:str, mail_address:str, password:str):
        user = User()
        user.user_id = user_id
        user.username = username
        user.mail_address = mail_address
        user.password = password
        user.save()

    @staticmethod
    def test_session():
        return Session.objects.all()

class Lottery_pool(models.Model):
    """
    抽選申込情報を提供するDTOクラス
    """
    reservation_id =models.AutoField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    priority = models.SmallIntegerField(_('希望'))
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)

class Reservations(models.Model):
    """
    予約情報を提供するDTOクラス
    """
    reservation_id =models.IntegerField(_('予約ID'), primary_key=True)
    user_id = models.IntegerField(_('ユーザID'))
    username = models.CharField(_('ユーザ名'), max_length=40)
    check_in_date = models.DateField(_('チェックイン日'))
    number_of_rooms = models.SmallIntegerField(_('部屋数'))
    number_of_guests = models.SmallIntegerField(_('宿泊人数'))
    purpose = models.CharField(_('利用形態'), max_length=10, default=None)
    request_status = models.SmallIntegerField(_('申込ステータス'))
    expire_date = models.DateField(_('有効期限'))

class ResDao:
    """Userオブジェクトを操作するクラス"""

    @staticmethod
    def create_res(user: User, check_in_date: datetime.date, stay_term: int, number_of_rooms: int, number_of_guests: int, purpose: str):
        res = Reservations()
        res.mail_address = user
        res.check_in_date = check_in_date
        res.stay_term = stay_term
        res.number_of_rooms = number_of_rooms
        res.number_of_guests = number_of_guests
        res.purpose = purpose
        res.save()

    @staticmethod
    def get_res_list(user: User) -> list:
        """Userオブジェクトを取得

        :param mail_address メールアドレス
        """
        return Reservations.objects.filter(mail_address=user)

    @staticmethod
    def get_res():
        return Reservations.objects.order_by('username')

    @staticmethod
    def get_res_by_month(month: int) -> Reservations:
        """
        引数の月度に該当する予約を取り出す
        :param month: 対象月度
        :return: 対象月度に該当するReservationsクラス
        """
        return Reservations.objects.filter(check_in_date__range=month)

    def del_res_by_month(month: int):
        """
        引数の月度の予約情報を削除する
        :param month:対象月度
        :return:
        """
        pass

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
