from django.urls import path
from . import views

urlpatterns = [
    path('category', views.CategoryListAPIView.as_view()),
    path('category/<int:category_id>/questions/', views.QuestionListAPIView.as_view()),

    path('result/', views.ResultListAPIView.as_view()),
    path('answer-from-student/', views.ResultCreateAPIView.as_view()),

    path('result-by-account/', views.AverageStatisticsListByAccount.as_view()),
    path('result-by-category/', views.AverageStatisticsListByCategory.as_view()),

    path('result-by-time/', views.TimeStatisticListAPIView.as_view()),

    path('contact/', views.ContactListCreateAPIView.as_view()),
]


