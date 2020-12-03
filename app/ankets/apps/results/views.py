from django.shortcuts import render
from django.http import HttpResponse
from django.template.defaulttags import register
from django.db import connection

#Пользовательские фильтры:
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def index(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM v_graph_date")
    rawresults = cursor.fetchall()
    cursor.close()
    res_1 = []
    res_2 = []
    res_3 = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res_1.append(int(value[1]))
        res_2.append(int(value[2]))
        res_3.append(int(value[3]))
    raw_date = {'data_1': res_1, 'data_2': res_2, 'data_3': res_3, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT respondent_name, COUNT(respondent_id) AS qount_answer FROM graduates_result "
                   "    INNER JOIN graduates_respondent ON graduates_result.respondent_type_id = graduates_respondent.respondent_type "
                   "    WHERE graduates_result.question_number_id = 71 OR graduates_result.question_number_id = 30 OR graduates_result.question_number_id = 3 "
                   " GROUP BY graduates_respondent.respondent_type, respondent_name"
                   " ORDER BY graduates_respondent.respondent_type")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(value[1])
    all_resp = sum(res)
    raw_type = {'data': res, 'labels': labels, 'all_resp': all_resp}

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM v_graph_sub")
    rawresults = cursor.fetchall()
    cursor.close()
    res_1 = []
    res_2 = []
    res_3 = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res_1.append(int(value[1]))
        res_2.append(int(value[2]))
        res_3.append(int(value[3]))
    raw_sub = {'data_1': res_1, 'data_2': res_2, 'data_3': res_3, 'labels': labels}

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
    all_grad = sum(res)
    raw_spec = {'data': res, 'labels': labels, 'all_grad': all_grad}

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM v_exit_1_graduates")
    rawresults = cursor.fetchall()
    cursor.close()
    raw_exit_1_graduates = rawresults

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM v_exit_1_oospo")
    rawresults = cursor.fetchall()
    cursor.close()
    raw_exit_1_oospo = rawresults

    return render(request, 'results/index.html',
                  {'raw_sub': raw_sub, 'raw_spec': raw_spec, 'raw_type': raw_type, 'raw_date': raw_date, 'raw_exit_1_graduates': raw_exit_1_graduates, 'raw_exit_1_oospo': raw_exit_1_oospo})


def anketsresult(request, respondent_strtype):
    cursor = connection.cursor()
    cursor.execute("SELECT respondent_id, status, mail, link_name FROM graduates_links INNER JOIN graduates_respondent ON graduates_links.respondent_type_id = graduates_respondent.respondent_type WHERE graduates_links.status=1 AND graduates_respondent.link_name = '"+respondent_strtype+"'")
    rawresults = cursor.fetchall()
    cursor.close()
    return render(request, 'results/anketsresult.html',
                  {'rawresults': rawresults, 'respondent_strtype': respondent_strtype})


def answers(request, respondent_strtype, respondent_id):
    #return HttpResponse(respondent_id)
    cursor = connection.cursor()
    cursor.execute("SELECT respondent_id, question_name, essense, result, result_date FROM v_results WHERE link_name = '"+respondent_strtype+"' AND respondent_id = '"+respondent_id+"'")
    rawresults = cursor.fetchall()
    cursor.close()
    respondents = {}
    for value in rawresults:
        respondents[value[0]] = rawresults #не привильно, если больше одного ключа
    raw = {'respondents': respondents}
    return render(request, 'results/answers.html',
                  {'raw': raw, 'respondent_strtype': respondent_strtype})