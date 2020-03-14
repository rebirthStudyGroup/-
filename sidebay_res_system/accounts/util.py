from django.contrib.auth import login
from django.core.mail import BadHeaderError, send_mail
from accounts.models import UserDao, ResDao, LodginDao, LotDao
from accounts.dao import CalendarMaster

"""固定値"""
LOG_USR = "login_user_id"
EMPTY_STR = ""
ADMIN_FLG = "login_admin_flg"
IS_ADMIN_USER = 1

"""抽選フラグ"""
DISABLED = 0
LOTTERY = 1
SECOND_APP = 2


def login_user(request, user):
    login(request, user)


#
# def res_send_mail(subject, message, from_email, recipient_list):
#     send_mail(subject, message, from_email, recipient_list)
#
#
# def test_send_email():
#     """題名"""
#     subject = "題名"
#
#     """本文"""
#     message = "本文です/n林翔吾用のテストです"
#     """送信元メールアドレス"""
#     from_email = "information@res_system.com"
#     """宛先メールアドレス"""
#     recipient_list = [
#         "sennseikou@gmail.com"
#     ]
#     res_send_mail(subject, message, from_email, recipient_list)
#
#
# def send_password(mail_address: str, password: str):
#     """
#     引数のメールアドレスに引数のパスワードを送付する
#     :param mail_address: メールアドレス
#     :param password: メールアドレスに紐づくパスワード
#     :return: なし
#     """
#     subject = "パスワード再送"
#     message = "password: " + password
#     from_email = "information@res_system.com"
#     recipient_list = [
#         mail_address
#     ]
#     res_send_mail(subject, message, from_email, recipient_list)

def __is_login_user(request) -> bool:
    """セッション情報にログインユーザ情報が存在するかを確認"""
    return LOG_USR in request.session


def __is_admin_user(request) -> bool:
    """セッション情報にユーザーIDが存在するかを確認"""
    return request.session[ADMIN_FLG] == IS_ADMIN_USER


"""
JSONの返却処理を実施
"""

import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http.response import JsonResponse


@ensure_csrf_cookie
# 取得した文字列の日付を日付型に変換
def get_all_res_info(request):
    # 日付を取得
    target_day_str = request.GET.get("yyyymm")

    # セッション情報を確認する
    if not __is_login_user(request):
        return JsonResponse("セッションが切断されました", safe=False)

    target_day = datetime.date(int(target_day_str[0:4]), int(target_day_str[4:6]), 1) - relativedelta(months=1)

    # 結果を格納する変数
    data = []

    # 当月と前後1か月分のjsonデータを取得
    for i in range(3):  # 0～2までの数列
        next_day = target_day + relativedelta(months=i)
        next_month = next_day.month
        next_year = next_day.year
        data.extend(JsonFactory.create_res_info_by_year_month(next_year, next_month))

    return JsonResponse(data, safe=False)


@ensure_csrf_cookie
def get_login_user_res_info(request):
    """ログインユーザの予約情報を取得"""

    # セッション情報を確認する
    if not __is_admin_user(request):
        return JsonResponse("セッションが切断されました", safe=False)

    # ログインユーザのユーザIDを取得
    user_id = request.session[LOG_USR]

    # ログインユーザから宿泊情報のJSONを取得
    data = JsonFactory.create_login_user_res_info_by_user_id(user_id)

    return JsonResponse(data, safe=False)


class JsonFactory:
    """
    ユーザー情報をjson形式に作成するクラス
    """

    # カレンダー情報
    IN_USE_LABEL = "×:空なし"
    VACANT_LABEL = "{num}部屋:空あり"
    BANNED_LABEL = "施設利用不可"
    LOT_LABEL = "抽選"
    RES_DATE = "start"
    USER = "user"
    STATUS = "status"
    TITLE_ROOMS = "title"
    COLOR = "color"
    TEXT_COLOR = "textColor"
    STATUS_DICT = {0: "未確定",
                   1: "確定"}

    # ログインユーザの抽選、予約情報
    RES_ID = "res_id"
    APP_STATUS = "app_status"
    IN_DATE = "check_in_date"
    OUT_DATE = "check_out_date"
    NUM_ROOMS = "number_of_rooms"
    EXPIRE = "expire_date"
    PRIORITY = "priority"

    @staticmethod
    def create_res_info_by_year_month(year: int, month: int) -> list:
        """
        カレンダー表示用のjsonデータを作成する
        :param year: 取得対象となるjsonデータの対象年
        :param month: 取得対象となるjsonデータの対象月度
        :return: list形式のjsonデータ
        """
        today = datetime.date.today()
        app_status = JsonFactory.__get_app_status_code(year, month)

        # 過去月度、翌々月以降の場合、表示しない
        if app_status == DISABLED:
            return list([])

        # key = 日付情報、value = タイトル、予約者、日付情報の辞書型を作成
        reservation_dict = {}

        # 該当月度の最終日
        _, lastday = calendar.monthrange(year, month)

        # 抽選月度の場合
        if app_status == LOTTERY:
            for res_date_day in range(lastday):  # 0,1,2,…,lastday - 1
                res_date = datetime.date(year, month, res_date_day + 1).strftime('%Y-%m-%d')
                reservation_dict[res_date] = {JsonFactory.RES_DATE: res_date,
                                              JsonFactory.TITLE_ROOMS: JsonFactory.LOT_LABEL}

            # 施設利用不可日の登録
            for ng in CalendarMaster.get_ngdata_in_month(year, month):
                ng_date = ng.strftime('%Y-%m-%d')
                reservation_dict[ng_date] = {JsonFactory.RES_DATE: ng_date,
                                             JsonFactory.TITLE_ROOMS: JsonFactory.BANNED_LABEL,
                                             JsonFactory.COLOR: "black", JsonFactory.TEXT_COLOR: "while"}
            return list(reservation_dict.values())

        # 初日
        first_day = 1

        # 当月分表示時は本日日付以降の予約を表示
        if today.month == month:
            first_day = today.day

        # 全ての日付に空の予約情報を設定
        for res_date_day in range(first_day - 1, lastday):  # 0,1,2,…,lastday - 1
            res_date = datetime.date(year, month, res_date_day + 1).strftime('%Y-%m-%d')
            reservation_dict[res_date] = {JsonFactory.RES_DATE: res_date,
                                          JsonFactory.TITLE_ROOMS: 0}

        # 指定の年月から予約情報を取得
        lod_list = LodginDao.get_lodging_date_by_year_and_month_and_grt_day(year, month, first_day)

        # 辞退した予約IDリストを取得
        defeated_list = ResDao.get_defeated_res_list(year, month)

        # 辞退した予約IDを除外する（埋まっていると考えない）
        lod_list = list(filter(lambda x: x.reservation_id not in defeated_list, lod_list))

        # 予約情報のQuerySetを取得からjson情報を作成する
        for lodging in lod_list:

            # チェックイン日と連泊日数をもとに、キーとなる日付を取得
            res_date = lodging.lodging_date.strftime('%Y-%m-%d')

            # 日付情報に紐づくJSON情報を作成する
            reservation_dict.setdefault(res_date, {JsonFactory.RES_DATE: res_date,
                                                   JsonFactory.TITLE_ROOMS: 0})
            json_data = reservation_dict.get(res_date)

            # 辞書のキーに"user"が含まれる要素数 + 1をユーザ、ステータス名に付与する連続番号とする
            serialize_num = len(list(filter(lambda x: JsonFactory.USER in x, list(json_data.keys())))) + 1

            reservation = ResDao.filter_by_reservation_id(lodging.reservation_id).first()
            if reservation:
                # ラベル（ステータス名 = ステータス）
                request_status = reservation.request_status
                status = JsonFactory.STATUS + str(serialize_num)
                json_data[status] = JsonFactory.STATUS_DICT[request_status]

                # ラベル（ユーザ = ユーザ名：予約部屋数）を設定
                check_in_user = JsonFactory.USER + str(serialize_num)
                json_data[check_in_user] = "{username}: {rooms}部屋".format(username=reservation.username,
                                                                          rooms=lodging.number_of_rooms)
                # json_data[check_in_user] = "{username}: {rooms}部屋".format(username=UserDao.get_user(lodging.user_id).username, rooms=lodging.number_of_rooms)

                # ラベル（部屋数 = 部屋数）を設定
                json_data[JsonFactory.TITLE_ROOMS] = json_data[JsonFactory.TITLE_ROOMS] + lodging.number_of_rooms

        for res_inf in reservation_dict.values():
            room_count = int(res_inf[JsonFactory.TITLE_ROOMS])
            if room_count > 3:
                res_inf[JsonFactory.TITLE_ROOMS] = JsonFactory.IN_USE_LABEL
                res_inf[JsonFactory.COLOR] = "black"
                res_inf[JsonFactory.TEXT_COLOR] = "white"
            else:
                res_inf[JsonFactory.TITLE_ROOMS] = JsonFactory.VACANT_LABEL.format(num=(4 - room_count))

        # 施設利用不可日の登録
        for ng in CalendarMaster.get_ngdata_in_month(year, month):
            ng_date = ng.strftime('%Y-%m-%d')
            reservation_dict[ng_date] = {JsonFactory.RES_DATE: ng_date,
                                         JsonFactory.TITLE_ROOMS: JsonFactory.BANNED_LABEL,
                                         JsonFactory.COLOR: "black",
                                         JsonFactory.TEXT_COLOR: "while"}

        # テスト用にreturnを実施
        return list(reservation_dict.values())

    @staticmethod
    def create_login_user_res_info_by_user_id(user_id: int) -> list:
        """ログインユーザに紐づく抽選、宿泊情報を取得"""

        # 返却結果
        result = []

        # 対象ユーザに紐づく抽選、予約情報を取得
        reservations = ResDao.get_res_list(user_id)
        lotteries = LotDao.get_res_list(user_id)

        # 抽選情報の辞書型を作成
        for lottery in lotteries:
            lottery_dict = {JsonFactory.RES_ID: lottery.reservation_id,
                            JsonFactory.APP_STATUS: 0,
                            JsonFactory.IN_DATE: lottery.check_in_date,
                            JsonFactory.OUT_DATE: lottery.check_out_date,
                            JsonFactory.NUM_ROOMS: lottery.number_of_rooms,
                            JsonFactory.EXPIRE: EMPTY_STR,
                            JsonFactory.PRIORITY: lottery.priority}
            result.append(lottery_dict)

        # 予約情報の辞書型を作成
        for reservation in reservations:
            reservation_dict = {JsonFactory.RES_ID: reservation.reservation_id,
                                JsonFactory.APP_STATUS: reservation.request_status + 1,
                                JsonFactory.IN_DATE: reservation.check_in_date,
                                JsonFactory.OUT_DATE: reservation.check_out_date,
                                JsonFactory.NUM_ROOMS: reservation.number_of_rooms,
                                JsonFactory.EXPIRE: reservation.expire_date, JsonFactory.PRIORITY: EMPTY_STR}
            result.append(reservation_dict)

        return result

    @staticmethod
    def __get_app_status_code(year: int, month: int) -> int:
        """引数の月度が抽選か申込か非表示かを判定"""
        result = 0

        # 当月をYYYYmmの数字に変換
        target_month_first_date = datetime.date(year=year, month=month, day=1)
        this_month_first_date = datetime.date.today().replace(day=1)

        # 過去月度
        if target_month_first_date < this_month_first_date:
            return DISABLED

        # 抽選月度
        if target_month_first_date == this_month_first_date + relativedelta(months=2):
            return LOTTERY

        # 抽選月度より先の月度
        if this_month_first_date + relativedelta(months=2) < target_month_first_date:
            return DISABLED

        return SECOND_APP
