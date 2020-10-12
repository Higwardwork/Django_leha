from django.shortcuts import render
from django.http import HttpResponse
#from graduates.models import Questionblock, Spravochnik, Respondent, Question, Answer, Result, Raw, Links
from django.template.defaulttags import register
from django.db import connection

#Пользовательские фильтры:

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def index(request):
    cursor = connection.cursor()
    # cursor.execute('SELECT respondent_name, question_name, essense, result, COUNT([respondent_id]) AS qount_answer FROM v_result group by respondent_name, question_name, essense, result')
    cursor.execute('SELECT respondent_name, COUNT([respondent_id]) AS qount_answer FROM v_result group by respondent_name')
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(value[1])
    # res = {}
    # for row in rawresults:
    #     res["respondent_name"] = row[0]
    #     res["question_number"] = row[1]
    #     res["question_name"] = row[2]
    #     res["essense"] = row[3]
    #     res["result"] = row[4]
    #     res["qount_answer"] = row[5]
    raw = {'data': res, 'labels': labels}
    #print(raw)
    return render(request, 'results/index.html',
                  {'rawresults': raw})

