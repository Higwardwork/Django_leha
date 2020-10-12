from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from .models import Questionblock, Spravochnik, Respondent, Question, Answer, Result, Raw, Links
import datetime
from django.template.defaulttags import register
from urllib.parse import unquote
import uuid

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

def index(request, respondent_strtype):
#def index(request, respondent_type):
#def index(request, respondent_id):
    if respondent_strtype == 'graduates':
        respondent_type = 1
        respondent_label = 'Выпускник'
    elif respondent_strtype == 'employers':
        respondent_type = 2
        respondent_label = 'Работодатель'
    elif respondent_strtype == 'organizations':
        respondent_type = 3
        respondent_label = 'Образовательная организация'
    else:
        respondent_type = 0
        return HttpResponse("Страница не найдена!")

    respondent_id = uuid.uuid4()
    #strlink = 'https://statedu.ru/'+str(respondent_strtype)+'/'+str(respondent_id)
    strlink = '/'+str(respondent_strtype)+'/'+str(respondent_id)
    return render(request, 'graduates/link.html', {'strlink': strlink, 'respondent_label': respondent_label})
    #написать ссылку, отправить на е-мейл, сгенерированный линк сохранить в бд + сохранить e-mail в бд



def anket(request, respondent_strtype, respondent_id):
    #return HttpResponse(respondent_id)
    if respondent_strtype == 'graduates':
        respondent_type = 1
    elif respondent_strtype == 'employers':
        respondent_type = 2
    elif respondent_strtype == 'organizations':
        respondent_type = 3
    else:
        respondent_type = 0
        return HttpResponse("Страница не найдена!")

    link = Links.objects.filter(respondent_id=respondent_id)
    if link:
        if link.status != 0:
            return render(request, "main/index.html", {'msg': "Опрос по данной ссылке уже пройден!"})
    else:
        linkobj = Links()
        linkobj.respondent_id = respondent_id
        linkobj.status = 0
        linkobj.respondent_type_id = respondent_type
        print("df")
        #linkobj.save()
    return HttpResponse(respondent_id)

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
        questionblock = Questionblock.objects.filter(respondent_type_id=link.respondent_type_id).order_by('id')
        questions = Question.objects.filter(respondent_type_id=link.respondent_type_id).order_by('question_number')
        answers = Answer.objects.filter(respondent_type_id=link.respondent_type_id)
    except:
        raise Http404("Страница не найдена!")
    if len(questions) > 0 and len(answers) > 0:
        return render(request, 'graduates/form.html', {'questionblock': questionblock, 'questions': questions, 'answers': answers, 'spravochnik': spravochnik, 'respondent_type': link.respondent_type_id, 'respondent_id': link.respondent_id, 'raw': nraw, 'essanceraw': essanceraw, 'buttons': buttons, 'questionraw': questionraw})
    else:
        return HttpResponse("Страница не найдена!")



#def saveanket(request, respondent_type):
def saveanket(request, respondent_id):
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
            return render(request, "main/index.html", {'msg': "Опрос по данной ссылке уже пройден!"})
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
        return render(request, "main/index.html", {'msg': msg})

def ajaxsave(request, respondent_id):
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
