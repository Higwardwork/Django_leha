from django.urls import path, include
from . import views


app_name = 'results'

urlpatterns = [
    path('', views.index, name='index'),
    path('ankets/<str:respondent_strtype>/', views.anketsresult, name='anketsresult'),
    path('ankets/<str:respondent_strtype>/<str:respondent_id>/', views.answers, name='answers'),
]

