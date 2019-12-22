from django.template.response import TemplateResponse
from accounts.models import User, UserDao, Reservations, ResDao, Lodging, LodginDao, Lottery_pool, LotDao
from accounts.util import test_send_email, send_password
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
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
URL_REBGST003 = "app/registration/REBGST_003.html"
URL_REBGST004 = "app/registration/REBGST_004.html"
URL_REBGST005 = "app/registration/REBGST_005.html"
URL_REBGST006 = "app/registration/REBGST_006.html"
URL_REBGST007 = "app/registration/REBGST_007.html"
URL_REBADM001 = "app/registration/REBADM_001.html"
URL_REBADM002 = "app/registration/REBADM_002.html"
URL_REBADM004 = "app/registration/REBADM_004.html"
URL_REBADM005 = "app/registration/REBADM_005.html"
TEST_SCREEN = "app/registration/test_database.html"
TEST_RES_SCREEN="app/registration/test_reservation.html"

"""抽選フラグ"""
ERROR = 0
LOTTERY = 1
SECOND_APP = 2

def init_login_screen(request):
    """ログイン処理を実施"""
    return TemplateResponse(request, URL_REBGST001, {})


def push_login_button(request):
    """初期処理、ログイン画面からログイン処理を実施。
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
            if UserDao.check_password_between_user_and_input(user, password):

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
    # 初期処理の場合、ログイン画面を表示
    else:
        return TemplateResponse(request, URL_REBGST001, {})

def reset_password(request):
    """パスワードリセット"""

    # ユーザID、メールアドレスを取得
    user_id = request.POST.get("user_id", "")
    mail_address = request.POST.get("mail_address", "")

    # ユーザ情報をDBから取得
    target_user = UserDao.get_user(user_id)

    # ユーザ情報のメールアドレスと画面から取得したメールアドレスが一致するかチェック
    if mail_address != target_user.mail_address:
        return TemplateResponse(request, URL_REBGST001,
                                {"error": "メールアドレスが登録されたメールアドレスと一致しません"})

    #TODO 汎用テーブルからパスワード初期値を取得
    password = "1234"

    #DBのユーザパスワードを初期値に更新
    UserDao.update_user_password(target_user, password)

    #TODO 登録のメールアドレスにパスワード初期化の旨を送信
    print("仮：メールアドレスにパスワード初期値を送信")

    return TemplateResponse(request, URL_REBGST001, {})

def init_res_top_screen(request):
    """予約日入力画面の初期処理"""

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBGST002, {})

def __check_login_user(request) -> TemplateResponse:
    """セッション情報にログインユーザ情報が存在するかを確認"""

    if not LOG_USR in request.session:
        return TemplateResponse(request, URL_REBGST001, {})

def init_my_page_screen(request):
    """ログイン画面からログイン処理を実施。

    """
    __check_login_user(request)
    return TemplateResponse(request, URL_REBGST003, {})

def push_res_app_button(request):
    """予約を実施

    """
    user_id = request.session[LOG_USR]
    check_in_date = datetime.date.fromisoformat(request.POST.get("check_in_date", ""))
    check_out_date = datetime.date.fromisoformat(request.POST.get("check_out_date", ""))
    number_of_rooms = request.POST.get("number_of_rooms", "")
    purpose = request.POST.get("purpose", "")

    error = ""

    #注意：現時点では宿泊人数を使用しないため、常に0を入力
    number_of_guests = 0

    # 抽選期間か2次申込期間かを取得
    app_status_code = __get_app_status_code(check_in_date)

    # 予約月度が過去月度の場合、エラー情報を画面に返却
    if app_status_code == ERROR:
        error = "予約申込対象期間外です"

    # 抽選の場合
    if app_status_code == LOTTERY:
        LotDao.create_res_by_in_and_out(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests,
                                        purpose)

    # 二次申込の場合
    if app_status_code == SECOND_APP:
        if not ResDao.create_res_as_second_reservation(user_id, check_in_date, check_out_date, number_of_rooms, number_of_guests, purpose):
            error = "二次申込が出来ませんでした"

    return TemplateResponse(request, URL_REBGST002, {"error": error})


def __get_app_status_code(check_in_date:datetime.date) -> int:
    """抽選か二次申込かを判定"""

    result = 0

    # 本申込締切日
    DEAD_LINE = 10

    # 今月の月度
    today = datetime.date.today()
    this_month = today.month
    this_date = today.day

    # 予約申込時の月度
    res_month = check_in_date.month
    res_date = check_in_date.day

    # 抽選か二次申込かの判断
    # 本日より過去日付の場合
    if today <= check_in_date:
        pass
    # 翌々月以降の場合
    elif res_month > this_month + 1:
        result = LOTTERY
    # 当月の場合
    elif this_month == res_month:
        result = SECOND_APP
    # 翌月の場合
    else:
        if res_date >= DEAD_LINE:
            result = SECOND_APP
        else:
            pass

    return result

def cancel_res_app(request):
    """抽選申込をキャンセル"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        LotDao.delete_by_reservation_id(reservation_id)
        LodginDao.delete_by_reservation_id(reservation_id)

    return TemplateResponse(request, URL_REBGST003, {"error":""})

def confirm_res(request):
    """予約の確定（本申込期間）"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.change_request_status_to_confirm(reservation_id)
        return HttpResponseRedirect(reverse('URL_REBGST003', {"error": ""} ))

    return TemplateResponse(request, URL_REBGST003)

def cancel_res(request):
    """予約の確定（本申込期間）"""
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.change_request_status_to_cansel(reservation_id)
        return HttpResponseRedirect(reverse('URL_REBGST003', {"error": ""} ))

    return TemplateResponse(request, URL_REBGST003)

def confirm_res_app(request):
    """テスト用予約の確定（本申込期間）"""
    #TODO delete this method
    reservation_id = request.POST.get("reservation_id", "")

    if reservation_id:
        ResDao.create_res_by_lottery(reservation_id)
        LotDao.delete_by_reservation_id(reservation_id)
        return HttpResponseRedirect(reverse('test_reservation', {"error": ""} ))

    return TemplateResponse(request, URL_REBGST003)

def init_password(request):
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

    return TemplateResponse(request, TEST_SCREEN, {"users": users, "json_data": None})

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

def test_delete_user(request):
    """
    ユーザIDに紐づくユーザーを削除する
    :param user_id: ユーザID
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

#TODO 未着手
def init_password_change(request):
    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBGST005, {})

#TODO 未着手
def change_password(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBGST005, {})



def init_admin_manage(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    # 全ユーザ情報を取得
    users = UserDao.get_users()

    return TemplateResponse(request, URL_REBADM001, {"uses": users})

def register_new_user(request):
    """（管理者専用）新規ユーザを登録する"""
    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("username", "")
        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password", "")
        UserDao.create_user(user_id, username, mail_address, password)

    return TemplateResponse(request, URL_REBADM001, {})

def update_user(request):
    """（管理者専用）ユーザ情報を更新する"""
    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        username = request.POST.get("username", "")
        mail_address = request.POST.get("mail_address", "")
        password = request.POST.get("password", "")
        UserDao.update_user(user_id, username, mail_address, password)

    return TemplateResponse(request, URL_REBADM001, {})

def delete_user(request):
    """（管理者専用）ユーザ情報を更新する"""
    if request.method == "POST":
        user_id = request.POST.get("user_id", "")
        if user_id:
            UserDao.delete_user_by_user_id(user_id)
            ResDao.delete_by_user_id(user_id)
            LotDao.delete_by_user_id(user_id)
            LodginDao.delete_by_user_id(user_id)

    return TemplateResponse(request, URL_REBADM001, {})

#TODO 未着手
def init_admin_calendar(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBADM002, {})


def init_user_terms(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBGST006, {})

def init_sidebay_info(request):

    # セッション情報にログインユーザが存在するか確認。存在しなければログイン画面へ遷移
    __check_login_user(request)

    return TemplateResponse(request, URL_REBGST007, {})
