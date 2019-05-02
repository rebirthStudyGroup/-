from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),
    path('main', views.main, name='main'),
    # 以下テスト
    path('lottery', views.lottery, name='lottery'),
    path('login', views.login, name='login')
]

