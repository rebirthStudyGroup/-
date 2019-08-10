from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='top'),
    path(r'main', views.main, name='main'),
    # 以下テスト
    path(r'lottery', views.lottery, name='lottery'),
    path(r'create_json_info', views.create_json_info, name='create_json_info'),
    path(r'login', views.login, name='login'),
    path(r'logout', views.logout, name='logout'),

    # データベース作成用URL
    path(r'test_reservation/<str:mail_address>/', views.test_reservation, name="test_reservation"),
    path(r'test_reservation/<str:mail_address>/test_register_res', views.test_register_res, name="test_register_res"),
    path(r'test_reservation/<str:mail_address>/main', views.get_back_to_main_from_test_register, name="get_back_to_main_from_test_register"),
    path(r'test_database', views.test_database, name="test_database"),
]
