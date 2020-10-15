from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from .models import Questionblock, Spravochnik, Respondent, Question, Answer, Result, Raw, Links
import datetime
from django.template.defaulttags import register
import urllib
from django.shortcuts import redirect
from urllib.parse import unquote
import uuid
from django.core.mail import send_mail

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

# Create your views here.

def index(request,respondent_strtype):
#respondent_strtype = request.path.replace("/", "")
#def index(request, respondent_type):
#def index(request, respondent_id):
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
        #respondent_label = str(respondent_obj.respondent_name)
    except:
        return HttpResponse("Страница не найдена!")
    respondent_id = uuid.uuid4()
    #strlink = 'https://statedu.ru/'+str(respondent_strtype)+'/'+str(respondent_id)
    #strlink = '/'+str(respondent_strtype)+'/'+str(respondent_id)
    return render(request, 'graduates/link.html', {'respondent_id': respondent_id, 'respondent_strtype': respondent_strtype, 'respondent_type': respondent_type})
    #написать ссылку, отправить на е-мейл, сгенерированный линк сохранить в бд + сохранить e-mail в бд



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
    #print(link)
    if link:
        linkget = Links.objects.get(respondent_id=respondent_id)
        if linkget.status != 0:
            return render(request, "graduates/message.html", {'msg': "Опрос по данной ссылке уже пройден!",
                                                              "respondent_type": respondent_type})
    #return HttpResponse(respondent_id)
    spravochnik = Spravochnik.objects.order_by('spravochnik_kod')
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
    mailaddr = str(request.POST.get('respondentmail'))
    msg = 'Ваша ссылка для доступа к анкете: ' + 'https://statedu.ru/'+str(respondent_strtype)+'/anket/'+str(respondent_id)
    sm = send_mail('Ваша ссылка на опрос о трудоустройстве выпускников', msg, 'support@statedu.ru', [mailaddr],
              fail_silently=False)
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
    except:
        return HttpResponse("Страница не найдена!")
    if sm:
        linkobj = Links()
        linkobj.respondent_id = respondent_id
        linkobj.status = 0
        linkobj.mail = mailaddr
        linkobj.respondent_type_id = respondent_type
        linkobj.save()
        #return HttpResponse('Сообщение отправлено')
        return redirect('/'+respondent_strtype+'/mailcomplete/')
    else:
        return HttpResponse('Ошибка при отправке сообщения')
    # try:
    #     send_mail('Ваша ссылка на опрос о трудоустройстве выпускников', msg, 'news@miccedu.ru', [mailaddr], fail_silently=False)
    # except:
    #     return HttpResponse('Ошибка при отправке сообщения')


def mailcomplete(request, respondent_strtype):
    try:
        respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
        respondent_type = int(respondent_obj.respondent_type)
    except:
        return HttpResponse("Страница не найдена!")
    return render(request, "graduates/message.html", {'msg': "На Ваш адрес электронной почты выслана ссылка для прохождения опроса.", "respondent_type": respondent_type})


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
        #return HttpResponseRedirect("/", {'msg': msg} )
        #return HttpResponse('Спасибо!')
        #return render(request, "main/index.html", {'msg': msg})
        return render(request, "graduates/message.html",
                      {'msg': msg, "respondent_type": int(link.respondent_type_id)})


def ajaxsave(request, respondent_id, respondent_strtype):
        #return HttpResponse(json.dumps(request.POST))
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
