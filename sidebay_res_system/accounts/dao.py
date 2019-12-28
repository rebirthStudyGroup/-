from datetime import date, timedelta
from django.db import connection, transaction

TABLE = "calendar_master"
NG_COL = "ng_date"

class CalendarMaster:
    """施設不可日登録情報を操作するクラス"""

    @staticmethod
    def get_ngdate() -> list:
        """施設利用不可日を取得する"""
        today = date.today().strftime("%Y-%m-%d")
        with connection.cursor() as cursor:
            cursor.execute("select {ng_column} from {table} where ng_date >= '{today}'".format(ng_column=NG_COL, table=TABLE, today=today))
            result = cursor.fetchall()
            return [x[0] for x in result]

    @staticmethod
    def get_ngdata_in_month(year: int, month: int) -> list:
        """引数で受け取った月度の施設利用不可日を取得する"""
        today = date.today().strftime("%Y-%m-%d")
        with connection.cursor() as cursor:
            cursor.execute("select {ng_column} from {table} where (DATE_FORMAT({ng_column}, '%Y%m') = '{Y}{m}')".format(ng_column=NG_COL, table=TABLE, today=today, Y=str(year), m=str(month)))
            result = cursor.fetchall()
            return [x[0] for x in result]


    @staticmethod
    def set_ngdate(ng_date: date, reason:str):
        """施設利用不可日を設定する"""
        with connection.cursor() as cursor:
            cursor.execute("insert into {table} values('{ng_date}', '{reason}')".format(table=TABLE, ng_date=ng_date.strftime("%Y-%m-%d"), reason=reason))
            transaction.commit()

    @staticmethod
    def is_in_ngdate(start_date: date, end_date: date):
        """施設利用不可日に一致するか確認する"""
        ng_days = CalendarMaster.get_ngdate()
        for day in range((end_date - start_date).days):
            if start_date + timedelta(days=day) in ng_days:
                return True
        return False



