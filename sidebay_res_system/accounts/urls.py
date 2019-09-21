from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='top'),
    path(r'main', views.main, name='main'),
    # 以下テスト
    path(r'lottery', views.lottery, name='lottery'),
    path(r'create_json_info', views.create_json_info, name='create_json_info'),
    path(r'login', views.login, name='login'),
    path(r'logout', views.logout_user, name='logout'),

    # 予約情報管理用URL
    path(r'test_reservation/<str:user_id>/', views.test_reservation, name="test_reservation"),
    path(r'test_reservation/<str:user_id>/test_database', views.test_get_back_database, name="test_get_back_database"),
    path(r'test_reservation/<str:user_id>/register_reservation', views.register_reservation, name="register_reservation"),
    path(r'test_reservation/<str:user_id>/turn_lottery_into_reservation', views.turn_lottery_into_reservation, name="turn_lottery_into_reservation"),
    path(r'test_reservation/<str:user_id>/delete_lottery_or_reservation', views.delete_lottery_or_reservation, name="delete_lottery_or_reservation"),

    # ユーザ情報管理用URL
    path(r'test_database', views.test_database, name="test_database"),
    path(r'delete_user', views.delete_user, name="delete_user")
]
