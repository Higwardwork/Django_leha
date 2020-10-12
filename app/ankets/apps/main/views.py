from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from graduates.models import Respondent
#from .models import Spravochnik, Respondent, Question, Answer, Result
from django.urls import reverse


# Create your views here.

def index(request):
    #return HttpResponse('test')
     respondent = Respondent.objects.order_by('respondent_type')
     return render(request, 'main/index.html', {'respondent': respondent})