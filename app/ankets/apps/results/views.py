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
    #return HttpResponse('Нет такой страницы')
    cursor = connection.cursor()
    # cursor.execute('SELECT respondent_name, question_name, essense, result, COUNT([respondent_id]) AS qount_answer FROM v_result group by respondent_name, question_name, essense, result')
    cursor.execute("SELECT sq.respondent_name, sq.respondent_id, sq.question_number, sq.question_name, sq.essense, CASE WHEN sq.answer_spravochnik Is Not NULL THEN graduates_spravochnik.spravochnik_name ELSE sq.result_free END AS result, sq.result_date FROM (  SELECT graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.question_number, graduates_question.question_name, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free, graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id, CASE WHEN respondent_type=2 And graduates_question.block_number_id=11 THEN 'Работник ' || essence_id ELSE CASE WHEN respondent_type=2 And graduates_question.block_number_id=12 THEN 'Профессия ' || essence_id ELSE CASE WHEN respondent_type=3 And graduates_question.block_number_id=4 THEN 'Выпускник ' || essence_id ELSE '-' END END END AS essense FROM (((graduates_question INNER JOIN graduates_answer ON graduates_question.id = graduates_answer.question_number_id) INNER JOIN graduates_result ON graduates_question.id = graduates_result.question_number_id) LEFT JOIN graduates_spravochnik ON graduates_answer.answer_spravochnik = graduates_spravochnik.spravochnik_number) INNER JOIN graduates_respondent ON graduates_question.respondent_type_id = graduates_respondent.id GROUP BY graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.question_number, graduates_question.question_name, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free,graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id  )  AS sq LEFT JOIN graduates_spravochnik ON (sq.answer_spravochnik = graduates_spravochnik.spravochnik_number) AND (sq.result_result = graduates_spravochnik.spravochnik_kod) GROUP BY sq.respondent_name, sq.respondent_id, sq.question_number, sq.question_name, sq.essense, CASE WHEN sq.answer_spravochnik Is Not NULL THEN graduates_spravochnik.spravochnik_name ELSE sq.result_free END, sq.result_date, sq.block_number_id ORDER BY sq.respondent_id, sq.block_number_id, sq.question_number;")
    rawresults = cursor.fetchall()
    #return HttpResponse(rawresults)
    cursor.close()
    # res = []
    # labels = []
    # for value in rawresults:
    #     labels.append(value[0])
    #     res.append(value[1])
    # raw = {'data': res, 'labels': labels}

    return render(request, 'results/index.html',
                  {'rawresults': rawresults})

