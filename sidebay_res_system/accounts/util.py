from django.contrib.auth import login
from django.core.mail import BadHeaderError, send_mail

def login_user(request, user):
    login(request, user)

def res_send_mail(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)

def test_send_email():
    """題名"""
    subject = "題名"

    """本文"""
    message = "本文です/n林翔吾用のテストです"
    """送信元メールアドレス"""
    from_email = "information@res_system.com"
    """宛先メールアドレス"""
    recipient_list = [
        "sennseikou@gmail.com"
    ]
    res_send_mail(subject, message, from_email, recipient_list)

def send_password(mail_address: str, password: str):
    """
    引数のメールアドレスに引数のパスワードを送付する
    :param mail_address: メールアドレス
    :param password: メールアドレスに紐づくパスワード
    :return: なし
    """
    subject = "パスワード再送"
    message = "password: " + password
    from_email = "information@res_system.com"
    recipient_list = [
        mail_address
    ]
    res_send_mail(subject, message, from_email, recipient_list)
