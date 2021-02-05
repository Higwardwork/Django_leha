from django.shortcuts import render
from django.http import HttpResponse
from django.template.defaulttags import register
from django.db import connection
from graduates.models import Respondent

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

    return render(request, 'results/index.html',
                  {'raw_sub': raw_sub, 'raw_spec': raw_spec, 'raw_type': raw_type, 'raw_date': raw_date})



def respondentsresult(request, respondent_strtype):
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name

    if respondent_strtype == 'graduates':
        table = 'v_exit_1_graduates_rf'
    elif respondent_strtype == 'organizations':
        table = 'v_exit_1_oospo'
    elif respondent_strtype == 'employers':
        table = 'v_exit_1_employers'
        #return HttpResponse("<a href='/results/ankets/employers/'>Анкеты</a>")
        return render(request, 'results/respondents.html',
                      {'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name})

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['Трудоустроены', 'Продолжили обучение', 'Призваны в ряды Вооруженных Сил', 'Находятся в отпуске по уходу за ребенком', 'Не трудоустроены']) ,"
                   " unnest(ARRAY[gr2, gr12, gr13, gr14, gr15])"
                   " FROM "+table)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
    raw_employment = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['По профессии/специальности', 'Не по профессии/специальности']) ,"
                   " unnest(ARRAY[gr3, gr2-gr3])"
                   " FROM "+table)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
    raw_employment_prof = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['По найму', 'ИП', 'Самозанятые']) ,"
                   " unnest(ARRAY[gr4, gr6, gr8])"
                   " FROM "+table)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
    raw_employment_types = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['В регионах с постоянной регистрацией', 'В регионах, не связанных с местом постоянной регистрации']) ,"
                   " unnest(ARRAY[gr10, gr11])"
                   " FROM "+table)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
    raw_employment_regions = {'data': res, 'labels': labels}

    return render(request, 'results/respondents.html',
                  {'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name, 'raw_employment': raw_employment, 'raw_employment_types': raw_employment_types, 'raw_employment_prof': raw_employment_prof, 'raw_employment_regions': raw_employment_regions})


def exittables(request, respondent_strtype):
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    cursor = connection.cursor()
    if respondent_strtype == 'graduates':
        #cursor.execute("SELECT * FROM v_exit_1_graduates")
        cursor.execute("SELECT region_name,"
                       " SUM(gr1) AS gr1,"
                       " SUM(gr2) AS gr2,"
                       " SUM(gr3) AS gr3,"
                       " SUM(gr4) AS gr4,"
                       " SUM(gr5) AS gr5,"
                       " SUM(gr6) AS gr6,"
                       " SUM(gr7) AS gr7,"
                       " SUM(gr8) AS gr8,"
                       " SUM(gr9) AS gr9,"
                       " SUM(gr10) AS gr10,"
                       " SUM(gr11) AS gr11,"
                       " SUM(gr12) AS gr12,"
                       " SUM(gr13) AS gr13,"
                       " SUM(gr14) AS gr14,"
                       " SUM(gr15) AS gr15"
                       " FROM v_exit_1_graduates INNER JOIN v_characteristic_graduates ON v_exit_1_graduates.respondent_id = v_characteristic_graduates.respondent_id"
                       " GROUP BY region_name"
                       " ORDER BY region_name")
    elif respondent_strtype == 'organizations':
        cursor.execute("SELECT * FROM v_exit_1_oospo")
    elif respondent_strtype == 'employers':
        return HttpResponse('Нет выходных таблиц по данной группе респондентов')
    rawresults = cursor.fetchall()
    cursor.close()
    results = rawresults
    return render(request, 'results/exittables.html',
                  {'respondent_strtype': respondent_strtype, 'results': results, 'respondent_name': respondent_name})


def unloading(request, respondent_strtype):
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    if respondent_strtype == 'graduates':
        table = 'v_results_graduates_columns'
    elif respondent_strtype == 'organizations':
        table = 'v_results_oospo_columns'
    elif respondent_strtype == 'employers':
        table = 'v_results_employers_columns'

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM "+table)
    rawresults = cursor.fetchall()
    cursor.close()

    if respondent_strtype == 'employers':
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM v_results_employers_potreb_columns")
        rawresults_potreb = cursor.fetchall()
        cursor.close()
        return render(request, 'results/unloading.html',
                      {'rawresults': rawresults, 'rawresults_potreb': rawresults_potreb, 'respondent_strtype': respondent_strtype,
                       'respondent_name': respondent_name})

    return render(request, 'results/unloading.html',
                  {'rawresults': rawresults, 'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name})


def anketsresult(request, respondent_strtype):
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    cursor = connection.cursor()
    cursor.execute("SELECT respondent_id, status, mail, link_name FROM graduates_links INNER JOIN graduates_respondent ON graduates_links.respondent_type_id = graduates_respondent.respondent_type WHERE graduates_links.status=1 AND graduates_respondent.link_name = '"+respondent_strtype+"' ORDER BY graduates_links.id")
    rawresults = cursor.fetchall()
    cursor.close()
    return render(request, 'results/anketsresult.html',
                  {'rawresults': rawresults, 'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name})


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