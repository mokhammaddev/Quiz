from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.AccountListAPIView.as_view()),

    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('retrieve-update/<int:pk>', views.AccountRUView.as_view()),

    path('my_profile/<int:pk>', views.MyProfileListAPIView.as_view()),
]
