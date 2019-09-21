from django.shortcuts import render
from django.template.response import TemplateResponse
from accounts.models import User, UserDao, Reservations, ResDao, Lodging, LodginDao, Lottery_pool, LotDao
from django.shortcuts import redirect
from accounts.util import test_send_email, send_password
import datetime
from dateutil.relativedelta import relativedelta
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session

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


def check_login_user(request) -> TemplateResponse:
    """セッション情報にログインユーザ情報が存在するかを確認"""
    if not LOG_USR in request.session:
        return TemplateResponse(request, URL_REBGST001, {})


def top(request):
    """ログイン画面を表示"""
    return TemplateResponse(request, URL_REBGST001, {})


def main(request):
    """ログイン画面からログイン処理を実施。
    ・ID、パスワードが登録情報と一致しない場合、エラーメッセージをログイン画面に表示
    ・ID、パスワードが登録情報と一致する場合、予約画面へ遷移
    """

    # 画面からログイン認証情報(メールアドレス、パスワード)が送られてきた場合
    if request.method == 'POST':

        user_id = request.POST.get("user_id", "")
        password = request.POST.get("password","")
        user = UserDao.get_user(user_id)

        """エラーへの対処法 → no such table: django_session
        以下のコマンドを実施して、セッションテーブルを作成する
        python manage.py migrate --run-syncdb
        """
        # ユーザが存在する場合、セッション情報にユーザ情報を登録して、予約画面へ遷移
        if user is not None:
            if user.check_pass(password):

                request.session[LOG_USR] = user.user_id
                request.session[LOG_NAME] = user.username
                request.session[LOG_MAIL] = user.mail_address

                return TemplateResponse(request, URL_REBGST002)
            # ユーザID、パスワードが登録情報と一致しない場合、ログイン画面を表示
            else:
                return TemplateResponse(request, URL_REBGST001,
                                        {"error": "Your password was not available!!",
                                         "user_id": user_id,})
        # ユーザが存在しない場合、ログイン画面を表示
        else:
            return TemplateResponse(request, URL_REBGST001,
                                    {"error": "Your username was not available!!",
                                     "user_id": user_id})
    # ログイン画面以外からアクセスした場合、ログイン画面を表示
    else:
        return TemplateResponse(request, URL_REBGST001, {})

def lottery(request):
    """予約日入力画面を表示"""

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    check_login_user(request)

    print("session情報を表示")
    for session_info in UserDao.test_session():
        print(session_info.get_decoded())

    return TemplateResponse(request, URL_REBGST002, {})

def lottery_sample():
    pass

def request_password(request):
    """画面側で入力したメールアドレスにパスワードを送信"""

    mail_address = request.POST.get("mail_address", "")

    if not mail_address == KARA:
        user = UserDao.get_user(mail_address)
        if user is not None:
            send_password(mail_address, user.password)


def logout_user(request):
    Session.objects.all().delete()
    print("session情報を表示")
    for session_info in UserDao.test_session():
        print(session_info.get_decoded())
    return TemplateResponse(request, URL_REBGST001, {})

def test_database(request):
    """
    テスト用のユーザー情報へ遷移する　
    :param request: request
    :return: ユーザー一覧画面
    """

    # POSTで情報が送られてきた場合、ユーザー情報を登録する
    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("username", "")
        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password", "")
        UserDao.create_user(user_id, username, mail_address, password)

    # 一覧表示するユーザー情報を取得
    users = UserDao.get_users()

    # TODO 削除予定
    json_data = JsonUtil.create_json_data(2019, 8)

    return TemplateResponse(request, TEST_SCREEN, {"users": users, "json_data": json_data})

def test_get_back_database(request, user_id):
    """予約画面からユーザー一覧画面へ戻る"""
    return HttpResponseRedirect(reverse('test_database'))

def test_reservation(request, user_id):
    """
    テスト用の予約作成画面へ遷移する
    :param request: request
    :param mail_address: 宿泊対象者のメールアドレス
    :return: 対象ユーザーの宿泊予約一覧画面
    """

    # 対象のユーザーネームを取得
    user = UserDao.get_user(user_id)

    # 対象のユーザーアドレスに紐づく宿泊日付を取得
    reservations = ResDao.get_res_list(user_id)
    lotterys = LotDao.get_res_list(user_id)

    return TemplateResponse(request, TEST_RES_SCREEN, {"reservations": reservations,"lotterys": lotterys, "username": user.username})


def register_reservation(request, user_id):
    """
    予約情報を登録する
    :param request: request
    :param mail_address: 宿泊登録者のメールアドレス
    :return: ユーザー一覧画面
    """

    if request.method == "POST":
        lottery_flag = request.POST.get("lottery_flag", None)
        check_in_date = datetime.date.fromisoformat(request.POST.get("check_in_date", ""))
        check_out_date = datetime.date.fromisoformat(request.POST.get("check_out_date", ""))
        number_of_rooms = request.POST.get("number_of_rooms", "")
        number_of_guests = request.POST.get("number_of_guests", "")
        purpose = request.POST.get("purpose", "")

        # 抽選フラグが"1"の場合、抽選エンティティを作成
        if lottery_flag:
            LotDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests,
                                            purpose)

        # 抽選フラグが指定されていない場合、予約エンティティを作成
        else:
            ResDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests, purpose)

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def turn_lottery_into_reservation(request, user_id):
    """
    抽選エンティティを予約エンティティへ変換する
    :param request:
    :param user_id:
    :param reservation_id:
    :return:
    """
    reservation_id = int(request.POST.get("reservation_id", 0))
    print("reservation_idは",reservation_id)
    ResDao.create_res_by_lottery(reservation_id)
    LotDao.delete_by_reservation_id(reservation_id)
    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def delete_lottery_or_reservation(request, user_id):
    """
    予約IDに紐づく予約or抽選情報を削除する
    :param request:
    :param user_id:
    :return:
    """
    reservation_id = int(request.POST.get("reservation_id", 0))
    if reservation_id:
        ResDao.delete_by_reservation_id(reservation_id)
        LotDao.delete_by_reservation_id(reservation_id)
        LodginDao.delete_by_reservation_id(reservation_id)

    return HttpResponseRedirect(reverse('test_reservation', args=(user_id,)))

def delete_user(request):
    """
    ユーザIDに紐づくユーザーを削除する
    :param request:
    :param user_id:
    :return:
    """
    user_id = int(request.POST.get("user_id", 0))
    if user_id:
        UserDao.delete_user_by_user_id(user_id)
        ResDao.delete_by_user_id(user_id)
        LotDao.delete_by_user_id(user_id)
        LodginDao.delete_by_user_id(user_id)

    return HttpResponseRedirect(reverse('test_database'))


def get_back_to_main_from_test_register(request, user_id):
    """
    ユーザー登録画面からログイン画面へ遷移する
    :param request: request
    :param user_id: 宿泊者のユーザID
    :return: ユーザー一覧画面
    """

    # 表示するユーザー情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, URL_REBGST001, {})

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

        res_list = ResDao.get_res_by_year_and_month(year, month)

        # 予約情報のQuerySetを取得からjson情報を作成する
        for res_set in res_list:

            # 予約情報が持つ連泊数ごとにjsonレコードを作成・追記
            for lodging_date in LodginDao.get_lodging_by_reservation_id(res_set.reservation_id):

                # チェックイン日と連泊日数をもとに、キーとなる日付を取得
                res_date = lodging_date.lodging_date.strftime('%Y-%m-%d')

                json_data = reservation_dict.setdefault(res_date, {RES_DATE:res_date, ROOMS: 0})
                subscriber = USER + str(len(json_data) - 1)
                json_data[subscriber] = UserDao.get_user(res_set.user_id).username
                json_data[ROOMS] = json_data[ROOMS] + res_set.number_of_rooms

        for res_inf in reservation_dict.values():
            if res_inf[ROOMS] == 4:
                res_inf[ROOMS] = IN_USE
            else:
                res_inf[ROOMS] = VACANT

        # テスト用にreturnを実施
        return list(reservation_dict.values())