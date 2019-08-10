from django.shortcuts import render
from django.template.response import TemplateResponse
from accounts.models import User, UserDao, Reservations, ResDao
from django.shortcuts import redirect
from accounts.util import test_send_email, send_password
import datetime
from dateutil.relativedelta import relativedelta
from django.http.response import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .util import login_user

LOG_USR = "login_user_id"
LOG_NAME = "login_username"
LOG_MAIL = "login_mail_address"
KARA = ""

"""画面のURL"""
URL_REBGST001 = 'app/registration/REBGST_001.html'
MAIN_SCREEN = "app/registration/main.html"
URL_REBGST002 = "app/registration/REBGST_002.html"
TEST_SCREEN = "app/registration/test_database.html"
TEST_RES_SCREEN="app/registration/test_reservation.html"

def top(request):
    """"""
    return TemplateResponse(request, URL_REBGST001, {})

def main(request):
    """ログイン画面を表示"""

    # 画面からログイン認証情報(メールアドレス、パスワード)が送られてきた場合
    if request.method == 'POST':

        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password","")
        user = UserDao.get_user(mail_address)

        """エラーへの対処法 → no such table: django_session
        以下のコマンドを実施して、セッションテーブルを作成する
        python manage.py migrate --run-syncdb
        """
        if user is not None:
            if user.check_pass(password):

                request.session[LOG_USR] = user.user_id
                request.session[LOG_NAME] = user.username
                request.session[LOG_MAIL] = user.mail_address
                return TemplateResponse(request, URL_REBGST002)
            else:
                return TemplateResponse(request, URL_REBGST001,
                                        {"error": "Your password was not available!!",
                                         "mail_address": mail_address,})
        else:
            return TemplateResponse(request, URL_REBGST001,
                                    {"error": "Your username was not available!!",
                                     "mail_address": mail_address})
    # ログイン画面以外からアクセスした場合
    else:
        return TemplateResponse(request, URL_REBGST001, {})

def lottery(request):
    """予約日入力画面を表示"""
    print("session情報を表示")
    for session_info in UserDao.test_session():
        print(session_info.get_decoded())

    return TemplateResponse(request, URL_REBGST002, {})

def lottery_sample():
    pass

def login(request):
    pass

def request_password(request):
    """画面側で入力したメールアドレスにパスワードを送信"""

    mail_address = request.POST.get("mail_address", "")

    if not mail_address == KARA:
        user = UserDao.get_user(mail_address)
        if user is not None:
            send_password(mail_address, user.password)


def logout(request):
    request.session.flush()
    print("session情報を表示")
    for session_info in UserDao.test_session():
        print(session_info.get_decoded())
    return TemplateResponse(request, URL_REBGST001, {})

def test_database(request):
    """
    テスト用のユーザー情報を表示・登録する画面
    :param request: request
    :return: ユーザー一覧画面
    """

    # POSTで情報が送られてきた場合、ユーザー情報を登録する
    if request.method == "POST":
        username = request.POST.get("username", "")
        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password", "")
        UserDao.create_user(username, mail_address, password)

    # 一覧表示するユーザー情報を取得
    users = UserDao.get_users()

    json_data = JsonUtil.create_json_data(2019, 7)

    return TemplateResponse(request, TEST_SCREEN, {"users": users, "json_data": json_data})


def test_reservation(request, mail_address):
    """
    テスト用のデータベースを作成する
    :param request: request
    :param mail_address: 宿泊対象者のメールアドレス
    :return: 対象ユーザーの宿泊予約一覧画面
    """

    # 対象のユーザーネームを取得
    user = UserDao.get_user(mail_address)

    # 対象のユーザーアドレスに紐づく宿泊日付を取得
    reservations = ResDao.get_res_list(user)

    return TemplateResponse(request, TEST_RES_SCREEN, {"reservations": reservations, "username": user.username})


def test_register_res(request, mail_address):
    """
    宿泊情報を登録する
    :param request: request
    :param mail_address: 宿泊登録者のメールアドレス
    :return: ユーザー一覧画面
    """

    if request.method == "POST":
        target_user = User.objects.get(mail_address=mail_address)
        check_in_date = request.POST.get("check_in_date", "")
        stay_term = request.POST.get("stay_term", "")
        number_of_rooms = request.POST.get("number_of_rooms", "")
        number_of_guests = request.POST.get("number_of_guests", "")
        purpose = request.POST.get("purpose", "")
        ResDao.create_res(target_user, check_in_date, stay_term, number_of_rooms, number_of_guests, purpose)

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, TEST_SCREEN, {"users": users})

def get_back_to_main_from_test_register(request, mail_address):
    """
    予約登録画面からユーザー登録画面へ遷移する
    :param request: request
    :param mail_address: 宿泊者のメールアドレス
    :return: ユーザー一覧画面
    """

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    json_data = JsonUtil.create_json_data(2019, 7)

    return TemplateResponse(request, TEST_SCREEN, {"users": users, "json_data": json_data})

@ensure_csrf_cookie
def create_json_info(request):

    # テスト用に月度を6月に変更しておく
    target_day = datetime.date.today() - relativedelta(months=1)

    # 結果を格納する変数
    data = []

    # 取り敢えず直近の5か月分(当月から4か月先まで)のjsonデータを取得
    for i in range(5):# 0～4までの数列
        next_day = target_day + relativedelta(months=i)
        next_month = next_day.month
        next_year = next_day.year
        data.extend(JsonUtil.create_json_data(next_year, next_month))

    return JsonResponse(data, safe=False)



class JsonUtil:
    """
    ユーザー情報をjson形式に作成するクラス
    """

    @staticmethod
    def create_json_data(year: int, month: int):
        """
        カレンダー表示用のjsonデータを作成する
        :param month: 取得対象となるjsonデータ
        :return: list形式のjsonデータ
        """

        IN_USE = "空き状況：×"
        AVAILABLE = "空き状況：△"
        VACANT = "空き状況：〇"
        RES_DATE = "start"
        USER = "subscriber"
        ROOMS = "title"

        # key = 日付情報、value = タイトル、予約者、日付情報の辞書型を作成
        reservation_dict = {}

        res_list = Reservations.objects.filter(check_in_date__year=year).filter(check_in_date__month=month)

        # 予約情報のQuerySetを取得からjson情報を作成する
        for res_set in res_list:

            # 予約情報が持つ連泊数ごとにjsonレコードを作成・追記
            for stay_term in range(res_set.stay_term):
                # チェックイン日と連泊日数をもとに、キーとなる日付を取得
                res_date = (res_set.check_in_date + datetime.timedelta(days=stay_term)).strftime('%Y-%m-%d')

                json_data = reservation_dict.setdefault(res_date, {RES_DATE:res_date, ROOMS: 0})
                subscriber = USER + str(len(json_data) - 1)
                json_data[subscriber] = res_set.mail_address.username
                json_data[ROOMS] = json_data[ROOMS] + res_set.number_of_rooms

        for res_inf in reservation_dict.values():
            if res_inf[ROOMS] == 4:
                res_inf[ROOMS] = IN_USE
            else:
                res_inf[ROOMS] = VACANT

        # テスト用にreturnを実施
        return list(reservation_dict.values())