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
    cursor.execute("SELECT datesave, COUNT(respondent_id) AS qount_answer FROM ( "
                   "SELECT TO_CHAR(result_date, 'DD.MM.YYYY') AS datesave, respondent_id FROM graduates_result  GROUP BY result_date, respondent_id"
                   ") AS sq "
                   "GROUP BY datesave "
                   "ORDER BY datesave")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(value[1])
    raw_date = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT respondent_name, COUNT(respondent_id) AS qount_answer FROM graduates_result "
                   "    INNER JOIN graduates_respondent ON graduates_result.respondent_type_id = graduates_respondent.respondent_type "
                   "    WHERE graduates_result.question_number_id = 71 OR graduates_result.question_number_id = 30 OR graduates_result.question_number_id = 3 "
                   " GROUP BY respondent_name"
                   " ORDER BY respondent_name")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(value[1])
    raw_type = {'data': res, 'labels': labels}

    #return HttpResponse('Нет такой страницы')
    cursor = connection.cursor()
    # cursor.execute('SELECT respondent_name, question_name, essense, result, COUNT([respondent_id]) AS qount_answer FROM v_result group by respondent_name, question_name, essense, result')
    #cursor.execute("SELECT sq.respondent_name, sq.respondent_id, sq.question_number, sq.question_name, sq.essense, CASE WHEN sq.answer_spravochnik Is Not NULL THEN graduates_spravochnik.spravochnik_name ELSE sq.result_free END AS result, sq.result_date FROM (  SELECT graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.question_number, graduates_question.question_name, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free, graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id, CASE WHEN respondent_type=2 And graduates_question.block_number_id=11 THEN 'Работник ' || essence_id ELSE CASE WHEN respondent_type=2 And graduates_question.block_number_id=12 THEN 'Профессия ' || essence_id ELSE CASE WHEN respondent_type=3 And graduates_question.block_number_id=4 THEN 'Выпускник ' || essence_id ELSE '-' END END END AS essense FROM (((graduates_question INNER JOIN graduates_answer ON graduates_question.id = graduates_answer.question_number_id) INNER JOIN graduates_result ON graduates_question.id = graduates_result.question_number_id) LEFT JOIN graduates_spravochnik ON graduates_answer.answer_spravochnik = graduates_spravochnik.spravochnik_number) INNER JOIN graduates_respondent ON graduates_question.respondent_type_id = graduates_respondent.id GROUP BY graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.question_number, graduates_question.question_name, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free,graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id  )  AS sq LEFT JOIN graduates_spravochnik ON (sq.answer_spravochnik = graduates_spravochnik.spravochnik_number) AND (sq.result_result = graduates_spravochnik.spravochnik_kod) GROUP BY sq.respondent_name, sq.respondent_id, sq.question_number, sq.question_name, sq.essense, CASE WHEN sq.answer_spravochnik Is Not NULL THEN graduates_spravochnik.spravochnik_name ELSE sq.result_free END, sq.result_date, sq.block_number_id ORDER BY sq.respondent_id, sq.block_number_id, sq.question_number;")
    # cursor.execute("SELECT sq.respondent_name, COUNT(sq.respondent_id) AS qount_answer "
    #                "FROM ("
    #                "        SELECT graduates_respondent.id, graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.id, graduates_question.question_number, graduates_question.question_name, graduates_question.field_type, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free, graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id,"
    #                "        CASE WHEN respondent_type=2 And graduates_question.block_number_id=11"
    #                "            THEN 'Работник ' || essence_id "
    #                "            ELSE "
    #                "                CASE WHEN respondent_type=2 And graduates_question.block_number_id=12 "
    #                "                    THEN 'Профессия ' || essence_id "
    #                "                    ELSE "
    #                "                        CASE WHEN respondent_type=3 And graduates_question.block_number_id=4 "
    #                "                            THEN 'Выпускник ' || essence_id "
    #                "                            ELSE '-' "
    #                "                        END "
    #                "                    END "
    #                "        END	"
    #                " AS essense "
    #                " FROM (((graduates_question"
    #                "                 INNER JOIN graduates_answer ON graduates_question.id = graduates_answer.question_number_id)"
    #                "                 INNER JOIN graduates_result ON graduates_question.id = graduates_result.question_number_id)"
    #                "                 LEFT JOIN graduates_spravochnik ON graduates_answer.answer_spravochnik = graduates_spravochnik.spravochnik_number)"
    #                "                 INNER JOIN graduates_respondent ON graduates_question.respondent_type_id = graduates_respondent.id "
    #                " GROUP BY graduates_respondent.id, graduates_respondent.respondent_name, graduates_result.respondent_id, graduates_question.id, graduates_question.question_number, graduates_question.question_name, graduates_question.field_type, graduates_answer.answer_spravochnik, graduates_result.essence_id, graduates_result.result_result, graduates_result.result_free,graduates_result.result_date, graduates_respondent.respondent_type, graduates_question.block_number_id"
    #                " )  AS sq"
    #                " LEFT JOIN graduates_spravochnik ON (sq.answer_spravochnik = graduates_spravochnik.spravochnik_number) AND (sq.result_result = graduates_spravochnik.spravochnik_kod)"
    #                " GROUP BY sq.respondent_name, sq.respondent_id ;")
    cursor.execute("SELECT result_result, graduates_spravochnik.spravochnik_name, COUNT(respondent_id) AS qount_answer FROM graduates_result "
                   "    INNER JOIN graduates_respondent ON graduates_result.respondent_type_id = graduates_respondent.respondent_type "
                   "    INNER JOIN graduates_spravochnik ON graduates_result.result_result = graduates_spravochnik.spravochnik_kod"
                   "    WHERE graduates_result.question_number_id = 71 OR graduates_result.question_number_id = 30 OR graduates_result.question_number_id = 3 "
                   " GROUP BY result_result, spravochnik_name"
                   " ORDER BY spravochnik_name")
    rawresults = cursor.fetchall()
    #return HttpResponse(rawresults)
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        #raw1 = {value[1]: {value[3]: value[4]}}
        #types.append(value[1])
        labels.append(value[1])
        res.append(value[2])
    raw_sub = {'data': res, 'labels': labels}


    cursor = connection.cursor()
    cursor.execute("  SELECT name_ugs, SUM(qount_answer) FROM ("
                   "SELECT result_result, graduates_spravochnik.spravochnik_name, t_ugs.kod_ugs || ' - ' || t_ugs.name_ugs AS name_ugs,"
                   "CASE WHEN graduates_result.respondent_type_id = 1 "
                   "THEN COUNT(respondent_id)"
                   " ELSE COUNT(essence_id) "
                   " END AS qount_answer "
                   " FROM graduates_result "
                   " INNER JOIN graduates_respondent ON graduates_result.respondent_type_id = graduates_respondent.respondent_type "
                   " INNER JOIN graduates_spravochnik ON graduates_result.result_result = graduates_spravochnik.spravochnik_kod "
                   " LEFT JOIN t_ugs ON LEFT(graduates_spravochnik.spravochnik_name,2) = t_ugs.kod_ugs "
                   " WHERE graduates_result.question_number_id = 78 OR graduates_result.question_number_id = 39 OR graduates_result.question_number_id = 9 "
                   " GROUP BY respondent_type_id, result_result, spravochnik_name, t_ugs.kod_ugs || ' - ' || t_ugs.name_ugs  "
                   ") AS sq "
                   " GROUP BY name_ugs "
                   " ORDER BY name_ugs ")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
    raw_spec = {'data': res, 'labels': labels}


    return render(request, 'results/index.html',
                  {'rawresults': rawresults, 'raw_sub': raw_sub, 'raw_spec': raw_spec, 'raw_type': raw_type, 'raw_date': raw_date})

