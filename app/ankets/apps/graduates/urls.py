from django.urls import path
from . import views

app_name = 'graduates'

urlpatterns = [
    #path('<int:respondent_type>/', views.index, name='index'),
    path('', views.index, name='index'),
    path('<str:respondent_id>/', views.anket, name='anket'),
    #path('saveanket/<int:respondent_type>/', views.saveanket, name='saveanket'),
    path('saveanket/<str:respondent_id>/', views.saveanket, name='saveanket'),
    path('ajaxsave/<str:respondent_id>/', views.ajaxsave, name='ajaxsave'),

]