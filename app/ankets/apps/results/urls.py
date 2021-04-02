from django.urls import path, include
from . import views


app_name = 'results'

urlpatterns = [
    path('', views.index, name='index'),
    path('respondents/<str:respondent_strtype>/', views.respondentsresult, name='respondentsresult'),
    path('exittables/<str:respondent_strtype>/<int:ter>/', views.exittables, name='exittables'),
    path('unloading/<str:respondent_strtype>/', views.unloading, name='unloading'),
    path('ankets/<str:respondent_strtype>/', views.anketsresult, name='anketsresult'),
    path('ankets/<str:respondent_strtype>/<str:respondent_id>/', views.answers, name='answers'),
    path('ajaxgetreport/<str:respondent_strtype>/', views.ajaxgetreport, name='ajaxgetreport'),
    path('ajaxgetprofspec/<str:respondent_strtype>/', views.ajaxgetprofspec, name='ajaxgetprofspec'),
]

