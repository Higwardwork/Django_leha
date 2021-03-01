from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from .models import Questionblock, Spravochnik, Respondent, Question, Answer, Result, Raw, Links, Okpdtr, Okz
import datetime
from django.template.defaulttags import register
import urllib
from django.shortcuts import redirect
from urllib.parse import unquote
import uuid
from django.core.mail import send_mail
from django import forms
from captcha.fields import CaptchaField
from django.core import serializers
import requests
from django.conf import settings



#Пользовательские фильтры:
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def concatstr(str1, str2):
    return str(str1)+str(str2)

@register.filter
def split_str(strk, whatnumberget):
    a = str(strk).split('_')
    return a[whatnumberget]

@register.filter
def unquotestrk(strk):
    return unquote(strk)


class EmployersOrganizationsForm(forms.Form):
    respondentmail = forms.CharField(label='Введите Ваш адрес электронной почты', max_length=100, widget=forms.TextInput(attrs={'class': "form-control", 'type': "email", 'id': "respondentmail"}))
    captcha = CaptchaField(label='')

class GraduatesForm(forms.Form):
    region = forms.ModelChoiceField(queryset=Spravochnik.objects.filter(spravochnik_number=3).order_by('id'), to_field_name="spravochnik_kod", empty_label='Выберите субъект РФ', label='Выберите регион, где Вы обучались', widget=forms.Select(attrs={'class': "form-control chosen-select"}))
    respondentmail = forms.CharField(label='Введите Ваш адрес электронной почты', max_length=100, widget=forms.TextInput(attrs={'class': "form-control", 'type': "email", 'id': "respondentmail"}))
    captcha = CaptchaField(label='')

def index(request, respondent_strtype):
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
    except:
        return HttpResponse("Страница не найдена!")
    respondent_id = 'badcapcha'
    # if request.method == 'POST':
    #     form = EmployersOrganizationsForm(request.POST)
    #     #if form.is_valid():
    #          #return HttpResponse('thanks')
    # else:
    if respondent_type == 111: #Планировалось для выпускников сделать свою форму с выбором субъекта, чтобы потом ограничить кол-во ОО в списке выбора, но непонятно, что делать, если он учился в филиале
        form = GraduatesForm()
    else:
        form = EmployersOrganizationsForm()
    return render(request, 'graduates/link.html', {'form': form, 'respondent_id': respondent_id, 'respondent_strtype': respondent_strtype, 'respondent_type': respondent_type})
    #return render(request, 'graduates/link.html', {'respondent_id': respondent_id, 'respondent_strtype': respondent_strtype, 'respondent_type': respondent_type})


def anket(request, respondent_strtype, respondent_id):
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
    except:
        return HttpResponse("Страница не найдена!")
    try:
        link = Links.objects.get(respondent_id=respondent_id)
    except:
        return HttpResponse("Страница не найдена!")
    if link:
        linkget = Links.objects.get(respondent_id=respondent_id)
        if linkget.status != 0:
            return render(request, "graduates/message.html", {'msg': "Опрос по данной ссылке уже пройден!",
                                                              "respondent_type": respondent_type})
    #return HttpResponse(respondent_id)
    #spravochnik = Spravochnik.objects.order_by('spravochnik_kod')
    spravochnik = Spravochnik.objects.order_by('id')
    raw = Raw.objects.filter(respid=respondent_id)
    nraw = dict()
    essanceraw = dict()
    questionraw = dict()
    buttons = dict()
    if len(raw) > 0:
        raw = str(raw.latest('id'))
        raw = raw.split('&')
        for rval in raw:
            rval = rval.split('=')
            sub = rval[0].split('_')
            nraw[rval[0]] = rval[1]
            if sub[0] == 'essance':
                #essanceraw[sub[1]+"_"+sub[3]] = rval[1]
                if sub[2] == 'freequestion':
                    essanceraw[rval[0]] = unquote(rval[1])
                else:
                    essanceraw[rval[0]] = rval[1]
                buttons[int(sub[1])] = int(sub[2])
            elif sub[0] == 'question':
                questionraw[int(sub[1])] = int(rval[1])
            elif sub[0] == 'freequestion':
                questionraw[int(sub[1])] = unquote(rval[1])

    try:
        questionblock = Questionblock.objects.filter(respondent_type_id=respondent_type).order_by('id')
        questions = Question.objects.filter(respondent_type_id=respondent_type).order_by('question_number')
        answers = Answer.objects.filter(respondent_type_id=respondent_type)
    except:
        raise Http404("Страница не найдена!")
    if len(questions) > 0 and len(answers) > 0:
        return render(request, 'graduates/form.html', {'questionblock': questionblock, 'questions': questions, 'answers': answers, 'spravochnik': spravochnik, 'respondent_type': respondent_type, 'respondent_id': respondent_id, 'raw': nraw, 'essanceraw': essanceraw, 'buttons': buttons, 'questionraw': questionraw, 'respondent_strtype': respondent_strtype})
    else:
        return HttpResponse("Страница не найдена!")


def sendmail(request, respondent_strtype, respondent_id):
    #return HttpResponse(request.path)
    if request.method == 'POST':
        try:
            respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
            respondent_type = int(respondent_obj.respondent_type)
        except:
            return HttpResponse("Страница не найдена!")
        if respondent_type == 111:
            form = GraduatesForm(request.POST)
        else:
            form = EmployersOrganizationsForm(request.POST)
        if form.is_valid():
            respondent_id = uuid.uuid4()
            mailaddr = str(request.POST.get('respondentmail'))
            #msg = 'Ваша ссылка для доступа к анкете: ' + 'https://statedu.ru/' + str(
            link = 'https://statedu.ru/' + str(respondent_strtype) + '/anket/' + str(respondent_id)
            msg = 'Ваша ссылка для доступа к анкете: <a href="' + link + '">' + link + '</a>'
            # sm = send_mail('Ваша ссылка на опрос о трудоустройстве выпускников', msg, 'support@statedu.ru', [mailaddr],
            #                fail_silently=False)
            auth = {"username": getattr(settings, 'EMAIL_HOST_USER'), "password": getattr(settings, 'EMAIL_HOST_PASSWORD')}
            token = requests.post(getattr(settings, 'EMAIL_HOST')+'/token', data=auth)
            token = token.json()["access_token"]
            jsn = {"subject": "Ваша ссылка на опрос о трудоустройстве выпускников", "recipients": [mailaddr],
                   "body": msg}
            sm = requests.post('https://apimail.miccedu.ru/email', headers={"Authorization": f"Bearer {token}"},
                          data=jsn)
            if sm:
                linkobj = Links()
                linkobj.respondent_id = respondent_id
                linkobj.status = 0
                linkobj.mail = mailaddr
                linkobj.respondent_type_id = respondent_type
                linkobj.save()
                return redirect('/' + respondent_strtype + '/mailcomplete/')
            else:
                return HttpResponse('Ошибка при отправке сообщения')
        else:
            return render(request, "graduates/badcapcha.html",
                          {"respondent_type": respondent_type, 'respondent_strtype': respondent_strtype})


def mailcomplete(request, respondent_strtype):
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
    except:
        return HttpResponse("Страница не найдена!")
    return render(request, "graduates/message.html", {'msg': "На Ваш адрес электронной почты выслана ссылка для прохождения опроса. Эту страницу можно закрыть.", "respondent_type": respondent_type})


#def saveanket(request, respondent_type):
def saveanket(request, respondent_strtype, respondent_id):
    # x = 1
    # while x <= 4500:
    #     link = Links()
    #     link.respondent_type_id = 3
    #     link.respondent_id = uuid.uuid4()
    #     link.status = 0
    #     link.save()
    #     x = x + 1
    # return HttpResponse(x)
    #return HttpResponse(request.POST.items())
    #respid = uuid.uuid4()
    try:
        link = Links.objects.get(respondent_id=respondent_id)
        if link.status != 0:
            return render(request, "graduates/message.html", {'msg': "Опрос по данной ссылке уже пройден!", "respondent_type": int(link.respondent_type_id)})
    except:
        return HttpResponse("Страница не найдена!")

    if request.method == "POST":
        for key, value in request.POST.items():
            if (key != 'csrfmiddlewaretoken') and (key != 'essencequestion') and (key != 'essancefreequestion'):
                question_number = key.split('_')
                #q[question_number[1]] = value
                res = Result()
                res.respondent_type_id = link.respondent_type_id
                res.block_number_id = 3 #может, он не нужен?
                res.respondent_id = respondent_id
                res.result_date = datetime.datetime.now().replace(microsecond=0)   #'2020-08-31'
                if question_number[0] == 'freequestion':    #свободный вопрос
                    res.question_number_id = question_number[1]
                    res.result_result = '0'
                    res.result_free = value
                elif question_number[0] == 'essance':
                    res.question_number_id = question_number[4]
                    res.essence_id = question_number[2]
                    if question_number[3] == 'freequestion':
                        res.result_result = '0'
                        res.result_free = value
                    else:
                        if value == 'null':
                            value = 0
                        res.result_result = value
                else:
                    res.question_number_id = question_number[1]
                    res.result_result = value
                try:
                    res.save()
                    msg = 'Спасибо за участие в опросе!'
                except Exception:
                    msg = 'Ошибка.'
        #ajaxsave(request, respondent_id)
        link.status = 1
        link.save()
        return render(request, "graduates/message.html",
                      {'msg': msg, "respondent_type": int(link.respondent_type_id)})


def ajaxsave(request, respondent_id, respondent_strtype):
        #return HttpResponse(request.POST['form'])
        raw = Raw()
        raw.respid = respondent_id
        #raw.datapost = str(request.POST['form'])
        raw.datapost = str(request.POST['form'])
        raw.result_date = datetime.datetime.now().replace(microsecond=0)
        try:
            raw.save()
            msg = 'ok'
        except:
            msg = 'ошибка'
        return HttpResponse(msg)


def ajaxgetprofession(request, respondent_id, respondent_strtype):
    userval = str(request.POST['userval'])
    modela = str(request.POST['modela'])
    if modela == 'okpdtr':
        qs = Okpdtr.objects.filter(name_okpdtr__icontains=userval).order_by('kod_okpdtr')
    elif modela == 'okz':
        qs = Okz.objects.filter(name_okpdtr__icontains=userval).order_by('kod_okpdtr')
    else:
        return HttpResponse('Ошибка')
    qs_json = serializers.serialize('json', qs)
    return HttpResponse(qs_json, content_type='application/json')


# def ajaxgetorganizations(request, respondent_id, respondent_strtype):
#     ter = int(request.POST['ter'])
#     qs = Spravochnik.objects.filter(ter=ter).order_by('spravochnik_name')
#     qs_json = serializers.serialize('json', qs)
#     return HttpResponse(qs_json, content_type='application/json')