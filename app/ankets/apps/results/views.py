from django.shortcuts import render
from django.http import HttpResponse
from django.template.defaulttags import register
from django.db import connection
from graduates.models import Respondent
from graduates.models import Spravochnik
#from excel_response import ExcelResponse
import xlwt
import datetime
import random
import numpy as np
#from django.db.models import Max

#Пользовательские фильтры:
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_list(list, key):
    return list[key]

# @register.filter
# def hash(h, key):
#     return h[key]
#
# @register.filter
# def get_max_index(dictionary_data):
#     #max_arr = {'max_value': max(dictionary_data), 'max_index': dictionary_data.index(max(dictionary_data))}
#     return int(dictionary_data.index(max(dictionary_data)))

@register.filter
def get_max_label(dictionary, key):
    index = int(dictionary.get('data').index(max(dictionary.get('data'))))
    label = dictionary.get('labels')[index]
    max_val = max(dictionary.get('data'))
    d = {'max_label': label, 'max_val': max_val}
    return d.get(key)

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
    res = []
    res_1 = []
    res_2 = []
    res_3 = []
    labels = []
    ter = []
    for value in rawresults:
        labels.append(value[0])
        res_1.append(int(value[1]))
        res_2.append(int(value[2]))
        res_3.append(int(value[3]))
        res.append(int(value[4]))
        ter.append(int(value[5]))
    raw_sub = {'data': res, 'data_1': res_1, 'data_2': res_2, 'data_3': res_3, 'labels': labels, 'ter': ter}

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
        q_for_count = '71'
        icon = 'fa-user-graduate'
        table = 'v_exit_1_graduates_rf'
        table_trudprof = 'v_graph_trudprof_graduates'
        #sql = 'SELECT ter, q71, COUNT(respondent_id) AS count_resp FROM v_results_graduates_columns GROUP BY ter, q71'
        sql = "SELECT ter, q71, SUM(count_resp) AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2) AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_resp))*100,2) ELSE 0.00 END AS d_trud_prof, CASE WHEN SUM(count_trud)!=0 THEN SUM(zp)/SUM(count_trud) ELSE 0 END AS zp FROM" \
              " (SELECT respondent_id, ter, q71, COUNT(respondent_id) AS count_resp, CASE WHEN(q91_zn = 1 OR q91_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN(q92_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q97 <> '') THEN q97::int ELSE 0 END AS zp  FROM v_results_graduates_columns GROUP BY respondent_id, ter, q71, q91_zn, q92_zn, q97) sq" \
              " GROUP BY ter, q71"
        sql_ugs = "SELECT kod_ugs, name_ugs FROM t_ugs INNER JOIN v_results_graduates_columns ON t_ugs.kod_ugs = v_results_graduates_columns.ugs ORDER BY kod_ugs"
        sql_ugs_data = "SELECT name_ugs, SUM(count_resp):: bigint AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2):: bigint AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_trud))*100,2) ELSE 0.00 END :: bigint AS d_trud_prof, CASE WHEN SUM(count_trud)!=0 THEN SUM(zp)/SUM(count_trud) ELSE 0 END AS zp FROM" \
                       "               (SELECT respondent_id, t_ugs.kod_ugs || ' - ' || t_ugs.name_ugs AS name_ugs, COUNT(respondent_id) AS count_resp, CASE WHEN(q91_zn = 1 OR q91_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN(q92_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q97 <> '') THEN q97::int ELSE 0 END AS zp  FROM v_results_graduates_columns LEFT JOIN t_ugs ON v_results_graduates_columns.ugs = t_ugs.kod_ugs GROUP BY respondent_id, t_ugs.kod_ugs, t_ugs.name_ugs, q91_zn, q92_zn, q97) sq" \
                       "              GROUP BY name_ugs"
    elif respondent_strtype == 'organizations':
        q_for_count = '3'
        icon = 'fa-university' #4.6 сек.
        table = 'v_exit_1_oospo_rf'
        table_trudprof = 'v_graph_trudprof_oospo' #1.9 сек.
        #sql = 'SELECT ter, q3, COUNT(respondent_id) AS count_resp FROM v_results_oospo_columns GROUP BY ter, q3'
        sql = "SELECT ter, q3, SUM(count_resp) AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2) AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_resp))*100,2) ELSE 0.00 END AS d_trud_prof, CASE WHEN SUM(count_trud)!=0 THEN SUM(zp)/SUM(count_trud_with_zp) ELSE 0 END AS zp FROM" \
              "              (SELECT respondent_id, ter, q3, COUNT(respondent_id) AS count_resp, CASE WHEN(q18_zn = 1 OR q18_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN((q18_zn = 1 OR q18_zn = 2) AND q119 <> '') THEN 1 ELSE 0 END AS count_trud_with_zp, CASE WHEN(q111_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q119 <> '') THEN q119::int ELSE 0 END AS zp FROM v_results_oospo_columns GROUP BY respondent_id, essence_id, ter, q3, q18_zn, q111_zn, q119 ORDER BY respondent_id) sq" \
              "              GROUP BY ter, q3"
        sql_ugs = "SELECT t_ugs.kod_ugs, t_ugs.name_ugs FROM t_ugs INNER JOIN v_results_oospo_columns ON t_ugs.kod_ugs = v_results_oospo_columns.kod_ugs ORDER BY kod_ugs"
        sql_ugs_data = "SELECT name_ugs, SUM(count_resp) :: bigint AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2) :: bigint AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_trud))*100,2) ELSE 0.00 END :: bigint AS d_trud_prof, CASE WHEN SUM(count_trud_with_zp)!=0 THEN SUM(zp)/SUM(count_trud_with_zp) ELSE 0 END AS zp FROM" \
                       "     (SELECT respondent_id, t_ugs.kod_ugs || ' - ' || t_ugs.name_ugs AS name_ugs, COUNT(respondent_id) AS count_resp, CASE WHEN(q18_zn = 1 OR q18_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN((q18_zn = 1 OR q18_zn = 2) AND q119 <> '') THEN 1 ELSE 0 END AS count_trud_with_zp, CASE WHEN(q111_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q119 <> '') THEN q119::int ELSE 0 END AS zp FROM v_results_oospo_columns LEFT JOIN t_ugs ON v_results_oospo_columns.kod_ugs = t_ugs.kod_ugs GROUP BY respondent_id, t_ugs.kod_ugs, t_ugs.name_ugs, essence_id, q18_zn, q111_zn, q119 ORDER BY respondent_id) sq" \
                       "     GROUP BY name_ugs"
    elif respondent_strtype == 'employers':
        q_for_count = '30'
        icon ='fa-briefcase'
        table = 'v_exit_1_employers'
        table_trudprof = ''
        sql = ''
        sql_ugs = "SELECT kod_ugs, name_ugs FROM t_ugs ORDER BY kod_ugs"
        sql_ugs_data = ""
        #return HttpResponse("<a href='/results/ankets/employers/'>Анкеты</a>")
        return render(request, 'results/respondents.html',
                      {'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name})

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(respondent_id) AS qount_answer FROM graduates_result "
                   "    WHERE graduates_result.question_number_id = "+q_for_count+" ")
    res = cursor.fetchone()
    cursor.close()
    raw_count_resp = {'data': res[0], 'icon': icon}

    #Объединённый запрос:
    # cursor = connection.cursor()
    # cursor.execute("SELECT 1 AS type, unnest(ARRAY['Трудоустроены', 'Продолжили обучение', 'Призваны в ряды Вооруженных Сил', 'Находятся в отпуске по уходу за ребенком', 'Не трудоустроены']) ,"
    #                "                    unnest(ARRAY[gr2, gr12, gr13, gr14, gr15])"
    #                "       FROM	"+table+""
    #                " UNION"
    #                " SELECT 2 AS type, unnest(ARRAY['По профессии/специальности', 'Не по профессии/специальности']) ,"
    #                "                    unnest(ARRAY[gr3, gr2-gr3])"
    #                "       FROM	"+table+""
    #                " UNION"
    #                " SELECT 3 AS type, unnest(ARRAY['В регионах с постоянной регистрацией', 'В регионах, не связанных с местом постоянной регистрации']) ,"
    #                "                    unnest(ARRAY[gr10, gr11])"
    #                "       FROM	"+table+""
    #                "                   ORDER BY type	")
    # rawresults = cursor.fetchall()
    # cursor.close()
    # res = []
    # labels = []
    # dic1 = []
    # for value in rawresults:
    #     #labels.append(value[1])
    #     dic1.append({value[0]: {'data': int(value[2]), 'labels': value[1]}})
    #     #dic[value[0]] = res
    # dic = dic1




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
    # cursor.execute("SELECT"
    #                " unnest(ARRAY['По найму', 'ИП', 'Самозанятые']) ,"
    #                " unnest(ARRAY[gr4, gr6, gr8])"
    #                " FROM "+table)
    cursor.execute("SELECT * FROM "+table_trudprof+ " ORDER BY zn_all desc")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    res_prof = []
    res_noprof = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(int(value[1]))
        res_prof.append(int(value[2]))
        res_noprof.append(int(value[3]))
    raw_employment_types = {'data': res, 'data_prof': res_prof, 'data_noprof': res_noprof, 'labels': labels}

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

    cursor = connection.cursor()
    cursor.execute(sql_ugs)
    rawresults = cursor.fetchall()
    cursor.close()
    ugs_dic = {}
    for value in rawresults:
        ugs_dic[value[0]] = {'kod_ugs': value[0], 'name_ugs': value[1]}

    cursor = connection.cursor()
    cursor.execute(sql)
    rawresults = cursor.fetchall()
    cursor.close()
    regions = {}
    count_all = 0
    for value in rawresults:
        count_all = count_all + value[2]
        regions[value[0]] = {'ter': value[0], 'name': value[1], 'count': value[2], 'd_trud': value[3], 'd_trud_prof': value[4], 'zp': value[5]}

    cursor = connection.cursor()
    cursor.execute(sql_ugs_data)
    rawresults = cursor.fetchall()
    cursor.close()
    ugs_data = []
    labels = []
    count_resp = []
    for value in rawresults:
        count_resp.append(value[1])
    #Экспоненциальное распределение для вычисления радиуса на графике типа bubble:
    count_resp = np.array(count_resp)
    count_resp = count_resp / count_resp.max(axis=0)
    i = 0
    for value in rawresults:
        color = 'rgba('+str(random.randint(0, 255))+','+str(random.randint(0, 255))+','+str(random.randint(0, 255))+','+'0.5)'
        labels.append(value[0])
        rr = count_resp[i]*10
        i += 1
        ugs_data.append({'label': value[0], 'data': [{'x': value[2], 'y': value[4], 'r': rr}], 'backgroundColor': color})
    raw_ugs_data = ugs_data

    return render(request, 'results/respondents.html',
                  {'count_all': count_all, 'raw_count_resp': raw_count_resp, 'regions': regions, 'ugs_dic': ugs_dic, 'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name, 'raw_employment': raw_employment, 'raw_employment_types': raw_employment_types, 'raw_employment_prof': raw_employment_prof, 'raw_employment_regions': raw_employment_regions, 'raw_ugs_data': raw_ugs_data})


def exittables(request, respondent_strtype, ter):
    if ter == 0:
        return HttpResponse('Нет страницы')
    # else:
    #     return HttpResponse(ter)
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    spravochnik_obj = Spravochnik.objects.get(spravochnik_kod=ter)
    region_name = spravochnik_obj.spravochnik_name
    cursor = connection.cursor()
    if respondent_strtype == 'graduates':
        table = 'v_exit_1_graduates'
        tbl_char = 'v_characteristic_graduates'
        #cursor.execute("SELECT * FROM v_exit_1_graduates")
        # cursor.execute("SELECT name_ugs,"
        #                " SUM(gr1) AS gr1,"
        #                " SUM(gr2) AS gr2,"
        #                " SUM(gr3) AS gr3,"
        #                " SUM(gr4) AS gr4,"
        #                " SUM(gr5) AS gr5,"
        #                " SUM(gr6) AS gr6,"
        #                " SUM(gr7) AS gr7,"
        #                " SUM(gr8) AS gr8,"
        #                " SUM(gr9) AS gr9,"
        #                " SUM(gr10) AS gr10,"
        #                " SUM(gr11) AS gr11,"
        #                " SUM(gr12) AS gr12,"
        #                " SUM(gr13) AS gr13,"
        #                " SUM(gr14) AS gr14,"
        #                " SUM(gr15) AS gr15"
        #                " FROM v_exit_1_graduates INNER JOIN v_characteristic_graduates ON v_exit_1_graduates.respondent_id = v_characteristic_graduates.respondent_id"
        #                " WHERE ter = "+str(ter)+" GROUP BY name_ugs"
        #                " ORDER BY name_ugs")
    elif respondent_strtype == 'organizations':
        table = 'v_exit_1_oospo'
        tbl_char = 'v_characteristic_oospo'
        # cursor.execute("SELECT v_characteristic_oospo.name_ugs AS name_ugs,"
        #                " SUM(v_exit_1_oospo.gr1) AS gr1,"
        #                " SUM(v_exit_1_oospo.gr2) AS gr2,"
        #                " SUM(v_exit_1_oospo.gr3) AS gr3,"
        #                " SUM(v_exit_1_oospo.gr4) AS gr4,"
        #                " SUM(v_exit_1_oospo.gr5) AS gr5,"
        #                " SUM(v_exit_1_oospo.gr6) AS gr6,"
        #                " SUM(v_exit_1_oospo.gr7) AS gr7,"
        #                " SUM(v_exit_1_oospo.gr8) AS gr8,"
        #                " SUM(v_exit_1_oospo.gr9) AS gr9,"
        #                " SUM(v_exit_1_oospo.gr10) AS gr10,"
        #                " SUM(v_exit_1_oospo.gr11) AS gr11,"
        #                " SUM(v_exit_1_oospo.gr12) AS gr12,"
        #                " SUM(v_exit_1_oospo.gr13) AS gr13,"
        #                " SUM(v_exit_1_oospo.gr14) AS gr14,"
        #                " SUM(v_exit_1_oospo.gr15) AS gr15"
        #                " FROM v_exit_1_oospo INNER JOIN v_characteristic_oospo ON v_exit_1_oospo.name_agregate = v_characteristic_oospo.respondent_id AND v_exit_1_oospo.essence_id = v_characteristic_oospo.essence_id"
        #                " WHERE ter = "+str(ter)+""
        #                " GROUP BY name_ugs")
    elif respondent_strtype == 'employers':
        return HttpResponse('Нет выходных таблиц по данной группе респондентов')
    # rawresults = cursor.fetchall()
    # cursor.close()
    # results = rawresults
    cursor = connection.cursor()
    sql = "  SELECT ter," \
          "  unnest(ARRAY['Трудоустроены', 'Продолжили обучение', 'Призваны в ряды Вооруженных Сил', 'Находятся в отпуске по уходу за ребенком', 'Не трудоустроены']) ," \
          "  unnest(ARRAY[sum(gr2), sum(gr12), sum(gr13), sum(gr14), sum(gr15)])" \
          "  FROM "+table+" " \
          "  INNER JOIN "+tbl_char+" ON "+table+".respondent_id = "+tbl_char+".respondent_id" \
          "  WHERE ter = "+str(ter)+" GROUP BY 1"
    #return HttpResponse(sql)
    cursor.execute(sql)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[1])
        res.append(int(value[2]))
    raw_employment = {'data': res, 'labels': labels}
    return render(request, 'results/exittables.html',
                  {'respondent_strtype': respondent_strtype, 'raw_employment': raw_employment, 'respondent_name': respondent_name, 'region_name': region_name})



def unloading(request, respondent_strtype):
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    #respondent_name = respondent_obj.respondent_name

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+respondent_strtype+now+'.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(respondent_strtype)

    style = xlwt.easyxf('font: bold off, color black;\
                         borders: top_color black, bottom_color black, right_color black, left_color black,\
                                  left thin, right thin, top thin, bottom thin;\
                         pattern: pattern solid, fore_color white;\
                         align: vert centre, horiz centre')
    style.alignment.wrap = 1 #переносить по словам

    if respondent_strtype == 'graduates':
        sql = 'SELECT respondent_id, q70, q120, q77, q71, q73, q75, q76, q78, q79, q80, q82, q112, q83, q85, q91, q121, q72, q110, q92, q95, q96, q97, q98, q99, q100, q101, q102, q103, q104 FROM v_results_graduates_columns'
        ws.write_merge(0, 1, 0, 0, 'id', style)
        ws.write_merge(0, 0, 1, 7, 'Общие сведения', style) #с 1 по 7 вправо
        ws.write_merge(0, 0, 8, 14, 'Образование', style)  #c 8 по 14 вправо
        ws.write_merge(0, 0, 15, 16, 'Факт занятости', style)
        ws.write_merge(0, 0, 17, 22, 'Для продолживших работать или трудоустроившихся (на первое место работы) после завершения обученияи', style)
        ws.write_merge(0, 0, 23, 25, 'Для трудоустроившихся выпускников ПОО, обучавшихся по договору о целевом обучении', style)
        ws.write_merge(0, 0, 26, 28, 'Для трудоустроившихся выпускников ПОО, завершивших ГИА с использованием ДЭ', style)
        ws.write_merge(0, 1, 29, 29, 'Вообще не искал работу по профессии (специальности) полученной в профессиональной образовательной организации', style)
        ws.write(1, 1, 'Наименование профессиональной образовательной организации, реализующей образовательные программ среднего профессионального образования, в которой Вы обучались', style)
        ws.write(1, 2, 'Субъект РФ, на территории которого Вы обучались', style)
        ws.write(1, 3, 'Тип образовательной организации', style)
        ws.write(1, 4, 'Место Вашей постоянной регистрации', style)
        ws.write(1, 5, 'Пол', style)
        ws.write(1, 6, 'Возраст, лет', style)
        ws.write(1, 7, 'Отношение к одной из льготных категорий', style)
        ws.write(1, 8, 'Код/Наименование профессии (специальности) по диплому', style)
        ws.write(1, 9, 'Форма обучения', style)
        ws.write(1, 10, 'Обучение было за счет', style)
        ws.write(1, 11, 'Завершения государственной итоговой аттестации с использованием демонстрационного экзамена', style)
        ws.write(1, 12, 'Укажите балл государственной итоговой аттестации с использованием демонстрационного экзамена', style)
        ws.write(1, 13, 'Обучался (обучалась) на основании договора о целевом обучении', style)
        ws.write(1, 14, 'Год выпуска', style)
        ws.write(1, 15, 'Факт занятости после завершения обучения', style)
        ws.write(1, 16, 'Планируете ли Вы продолжать обучение без прерывания трудовой деятельности', style)
        ws.write(1, 17, 'Субъект Российской Федерации, в котором Вы смогли впервые трудоустроится в течение года, после завершения обучения в профессиональной образовательной организации', style)
        ws.write(1, 18, 'Трудоустроен как', style)
        ws.write(1, 19, 'Факт трудоустройства по профессии (специальности)', style)
        ws.write(1, 20, '«Число месяцев» – в течение которых велся поиск работы; «0» – для продолживших работать', style)
        ws.write(1, 21, 'Наименование профессии/должности', style)
        ws.write(1, 22, 'Среднемесячная заработная плата, руб.', style)
        ws.write(1, 23, 'Факт трудоустройства в организацию, записанную в договоре о целевом обучении, после завершения обучения', style)
        ws.write(1, 24, 'Укажите причины трудоустройства в другой организации', style)
        ws.write(1, 25, 'Наименование профессии/должности', style)
        ws.write(1, 26, 'Повлияло ли на трудоустройство сдача государственной итоговой аттестации с использованием демонстрационного экзамена', style)
        ws.write(1, 27, 'Заинтересованность работодателя в выпускниках, сдавших  государственную итоговую аттестацию с использованием демонстрационного экзамена (Ваше мнение)', style)
        ws.write(1, 28, 'Завершение государственной итоговой аттестации с использованием демонстрационного экзамена дает более качественную оценку подготовки обучающегося в профессиональной образовательной организации (Ваше мнение)', style)
        for nc in range(30):
            ws.write(2, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
    elif respondent_strtype == 'organizations':
        sql = 'SELECT respondent_id, essence_id, q3, q4, q5, q6, q7, q8, q113, q114, q29, q26, q19, q9, q115, q10, q116, q11, q18, q117, q109, q118, q111, q27, q119, q25 FROM v_results_oospo_columns'
        ws.write_merge(0, 1, 0, 0, 'id', style)
        ws.write_merge(0, 1, 1, 1, '№ п/п', style)
        ws.write_merge(0, 0, 2, 6, 'Общие сведения', style)
        ws.write_merge(0, 0, 7, 9, 'Численность выпускников на конец 2018/2019 учебного года', style)
        ws.write_merge(0, 0, 10, 25, 'Классификация выпускников ПОО на конец 2018/2019 учебного года', style)
        ws.write(1, 2, 'Субъект Российской Федерации, на территории которого расположена организация, либо филиал', style)
        ws.write(1, 3, 'Наименование головной организации', style)
        ws.write(1, 4, 'Ответственный за заполнение анкеты', style)
        ws.write(1, 5, 'E-mail', style)
        ws.write(1, 6, 'Контактный телефон', style)
        ws.write(1, 7, 'Очной формы обучения', style)
        ws.write(1, 8, 'Заочной формы обучения', style)
        ws.write(1, 9, 'Очно-заочной формы обучения', style)
        ws.write(1, 10, 'Пол', style)
        ws.write(1, 11, 'Относится к лицам с ОВЗ или детям-инвалидам', style)
        ws.write(1, 12, 'Субъект Российской Федерации, в котором выпускник имеет постоянную регистрацию', style)
        ws.write(1, 13, 'Код/наименование профессии (специальности)', style)
        ws.write(1, 14, 'Форма обучения', style)
        ws.write(1, 15, 'Завершил(а) государственную итоговую аттестацию с использованием демонстрационного экзамена', style)
        ws.write(1, 16, 'Укажите балл демонстрационного экзамена', style)
        ws.write(1, 17, 'Обучался(обучалась) на основании договора о целевом обучении', style)
        ws.write(1, 18, 'Факт занятости в течение года после завершения обучения', style)
        ws.write(1, 19, 'Субъект Российской Федерации, в котором трудоустроился выпускник', style)
        ws.write(1, 20, 'Название должности (по предоставленной информации от выпускника)', style)
        ws.write(1, 21, 'Работает как', style)
        ws.write(1, 22, 'Факт трудоустройства по профессии/специальности, полученной в образовательной организации', style)
        ws.write(1, 23, 'Дата трудоустройства (заполняется при наличии данных)', style)
        ws.write(1, 24, 'Среднемесячная заработная плата, руб. (заполняется при наличии данных)', style)
        ws.write(1, 25, 'Соответствие места трудоустройства выпускника (обучавшегося на основании договора о целевом обучении) организации, указанной в договоре на целевое обучение', style)
        for nc in range(26):
            ws.write(2, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
    elif respondent_strtype == 'employers':
        sql = 'SELECT * FROM v_results_employers_columns'
        ws.write_merge(0, 1, 0, 0, 'id', style)
        ws.write_merge(0, 1, 1, 1, '№ п/п', style)
        ws.write_merge(0, 0, 2, 8, 'Общие сведения', style)
        ws.write_merge(0, 0, 9, 23, 'Численность выпускников на конец 2018/2019 учебного года', style)
        ws.write(1, 2, 'Субъект Российской Федерации', style)
        ws.write(1, 3, 'Наименование предприятия/организации', style)
        ws.write(1, 4, 'Ответственный за заполнение анкеты', style)
        ws.write(1, 5, 'E-mail', style)
        ws.write(1, 6, 'Контактный телефон', style)
        ws.write(1, 7, 'Основной ОКВЭД предприятия/организации', style)
        ws.write(1, 8, 'Дополнительные ОКВЭДы предприятия/организации (не обязательно)', style)
        ws.write(1, 9, 'Код/наименование профессии (специальности) по диплому', style)
        ws.write(1, 10, 'Год выпуска', style)
        ws.write(1, 11, 'Завершил(а) государственную итоговую аттестацию с использованием демонстрационного экзамена (если нет данных поле остается не заполненным)', style)
        ws.write(1, 12, 'Принят(принята) на основании договора о целевом обучении', style)
        ws.write(1, 13, 'Место постоянной регистрации совпадает с местом трудоустройства', style)
        ws.write(1, 14, 'В случае трудоустройства в другом регионе укажите регион постоянной регистрации', style)
        ws.write(1, 15, 'Трудоустроен впервые', style)
        ws.write(1, 16, 'Название должности, согласно штатного расписания', style)
        ws.write(1, 17, 'Код профессии по ОКПДТР', style)
        ws.write(1, 18, 'Код профессии по ОКЗ', style)
        ws.write(1, 19, 'Дата зачисления в штат', style)
        ws.write(1, 20, 'Дата увольнения (если уволен', style)
        ws.write(1, 21, 'Средняя сумма выплат в месяц (начисленная), руб.', style)
        ws.write(1, 22, 'Относится к лицам с ОВЗ или инвалидам', style)
        ws.write(1, 23, 'Пол', style)
        for nc in range(24):
            ws.write(2, nc, nc, style)
            ws.col(nc).width = int(23 * 260)

    cursor = connection.cursor()
    #cursor.execute("SELECT * FROM "+table)
    cursor.execute(sql)
    rawresults = cursor.fetchall()
    cursor.close()

    ws.row(0).height_mismatch = True
    ws.row(0).height = 50 * 10
    ws.row(1).height_mismatch = True
    ws.row(1).height = 200 * 10

    row_num = 2
    font_style = xlwt.XFStyle()
    for row in rawresults:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    if respondent_strtype == 'employers':
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM v_results_employers_potreb_columns")
        rawresults_potreb = cursor.fetchall()
        cursor.close()
        ws_potreb = wb.add_sheet(respondent_strtype+'_потребность')
        ws_potreb.write_merge(0, 1, 0, 0, 'id', style)
        ws_potreb.write_merge(0, 1, 1, 1, '№ п/п', style)
        ws_potreb.write_merge(0, 0, 2, 8, 'Общие сведения', style)
        ws_potreb.write_merge(0, 0, 9, 16, 'Прогнозная потребность предприятия/организации в выпускниках образовательных организаций, реализующих образовательные программы среднего профессионального образования, в возрасте до 30 лет на ближайшие 2–3 года', style)
        ws_potreb.write(1, 2, 'Субъект Российской Федерации', style)
        ws_potreb.write(1, 3, 'Наименование предприятия/организации', style)
        ws_potreb.write(1, 4, 'Ответственный за заполнение анкеты', style)
        ws_potreb.write(1, 5, 'E-mail', style)
        ws_potreb.write(1, 6, 'Контактный телефон', style)
        ws_potreb.write(1, 7, 'Основной ОКВЭД предприятия/организации', style)
        ws_potreb.write(1, 8, 'Дополнительные ОКВЭДы предприятия/организации (не обязательно)', style)
        ws_potreb.write(1, 9, 'Код профессии по ОКПДТР', style)
        ws_potreb.write(1, 10, 'Код профессии по ОКЗ', style)
        ws_potreb.write(1, 11, 'Наличие приоритета для кандидатов, завершивших государственную итоговую аттестацию использованием демонстрационного экзамена', style)
        ws_potreb.write(1, 12, 'Заключение с профессиональной образовательной организацией договора о целевом обучении', style)
        ws_potreb.write(1, 13, 'Предполагаемая средняя заработная плата в месяц, руб.', style)
        ws_potreb.write(1, 14, 'Требуемый уровень профессионального образования (ППКРС или ППССЗ)', style)
        ws_potreb.write(1, 15, 'Планируете ли Вы нанимать работников с ОВЗ или инвалидов?', style)
        ws_potreb.write(1, 16, 'Пол (в каких специалистах существует большая потребность предприятия/организации?)', style)
        for nc in range(17):
            ws_potreb.write(2, nc, nc, style)
            ws_potreb.col(nc).width = int(23 * 260)
        ws_potreb.row(0).height_mismatch = True
        ws_potreb.row(0).height = 50 * 10
        ws_potreb.row(1).height_mismatch = True
        ws_potreb.row(1).height = 200 * 10
        row_num_potreb = 2
        for row_potreb in rawresults_potreb:
            row_num_potreb += 1
            for col_num_potreb in range(len(row_potreb)):
                ws_potreb.write(row_num_potreb, col_num_potreb, row_potreb[col_num_potreb], font_style)

    wb.save(response)
    return response
    #return ExcelResponse(rawresults, respondent_strtype+'_'+now)
    #return render(request, 'results/unloading.html',
    #              {'rawresults': rawresults, 'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name})



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


def ajaxgetreport(request, respondent_strtype):
    regions = request.POST.get('regions')
    ugs = request.POST.get('ugs')
    profspec = request.POST.get('profspec')
    razrez = request.POST.get('razrez')
    typeq = request.POST.get('type')
    type_report = request.POST.get('type_report')
    regions_checked = request.POST.get('regions_checked')
    ugs_checked = request.POST.get('ugs_checked')
    profspec_checked = request.POST.get('profspec_checked')
    dop_parameters = request.POST.get('dop_parameters')
    chk_text = request.POST.get('chk_text')
    de = ' AND dem_exam = 1 ' if request.POST.get('de') == '1' else ''
    cel = ' AND celevoe = 1 ' if request.POST.get('cel') == '1' else ''
    inv = ' AND ovz_inv = 1 ' if request.POST.get('inv') == '1' else ''
    year = " AND yearv = '"+request.POST.get('year')+"' " if (request.POST.get('year') != 'None' and request.POST.get('year') != 'all') else ''
    finance = " AND finance = '"+request.POST.get('finance')+"' " if (request.POST.get('finance') != 'None' and request.POST.get('finance') != 'all') else ''
    formaob = " AND formaob = "+request.POST.get('formaob')+" " if (request.POST.get('formaob') != 'None' and request.POST.get('formaob') != 'all') else ''
    sex = " AND sex = "+request.POST.get('sex')+" " if (request.POST.get('sex') != 'None' and request.POST.get('sex') != 'all') else ''
    typeoo = " AND typeoo = "+request.POST.get('typeoo')+" " if (request.POST.get('typeoo') != 'None' and request.POST.get('typeoo') != 'all') else ''
    golfil = " AND golfil = "+request.POST.get('golfil')+" " if (request.POST.get('golfil') != 'None' and request.POST.get('golfil') != 'all') else ''
    ugs_str = " AND kod_ugs IN("+ugs+")" if ugs != '' else ''
    profspec_str = " AND dic_val IN("+profspec+")" if profspec != '' else ''
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    #return HttpResponse(ugs_checked)
    if regions == '' or (ugs == '' and profspec == ''):
        return HttpResponse("don't set parameters")
        #return results
    checked = profspec_checked if ugs == '' else ugs_checked
    if type_report == 'excel':
        results = getdataforexcel(respondent_strtype, typeq, year, finance, razrez, regions, ugs_str, profspec_str, de,
                                  cel, inv, formaob, sex, typeoo, golfil)
        #return HttpResponse(results)
        return getexcelhead(typeq, respondent_strtype, regions_checked, checked, dop_parameters, chk_text, results)

    elif type_report == 'graph':
        results = getdataforgraph(respondent_strtype, typeq, year, finance, razrez, regions, ugs_str, profspec_str, de,
                                  cel, inv, formaob, sex, typeoo, golfil)
        #return HttpResponse(results)
        # if( len(results.get('raw_employment')) < 1 and results.get('raw_employment_regions') < 1 ):
        #     return HttpResponse("Нет данных согласно выбранным фильтрам")
        return render(request, 'results/graphs.html',
                      {'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name, 'raw_employment': results.get('raw_employment'), 'raw_employment_spec': results.get('raw_employment_spec'), 'raw_employment_regions': results.get('raw_employment_regions'), 'raw_employment_types': results.get('raw_employment_types'), 'regions_checked': regions_checked, 'checked': checked, 'dop_parameters': dop_parameters, 'chk_text': chk_text})

def ajaxgetprofspec(request, respondent_strtype):
    typech = request.POST.get('typech')
    #это для выпускников, для ОО надо отдельно сделать запрос:
    if respondent_strtype == 'graduates':
        if typech == 'profspec':
            sql = "SELECT 		graduates_result.result_result AS dic_val, " \
                      "            graduates_spravochnik.spravochnik_name AS name_spec " \
                      "           FROM (graduates_result " \
                      "             JOIN graduates_spravochnik ON ((graduates_result.result_result = graduates_spravochnik.spravochnik_kod))) " \
                      "          WHERE ((graduates_result.respondent_type_id = 1) AND (graduates_result.question_number_id = 78) AND (graduates_spravochnik.spravochnik_number = 2)) " \
                      "          GROUP BY graduates_spravochnik.spravochnik_name, graduates_result.essence_id, graduates_result.question_number_id, graduates_result.result_result " \
                      "          ORDER BY graduates_spravochnik.spravochnik_name "
            html = 'checkprofspec'
        elif typech == 'ugs':
            sql = "SELECT kod_ugs, kod_ugs||' - '||name_ugs AS name_ugs FROM t_ugs INNER JOIN v_results_graduates_columns ON t_ugs.kod_ugs = v_results_graduates_columns.ugs ORDER BY kod_ugs"
            html = 'checkugs'
    elif respondent_strtype == 'organizations':
        if typech == 'profspec':
            sql = "SELECT 		graduates_result.result_result AS dic_val, " \
                      "            graduates_spravochnik.spravochnik_name AS name_spec " \
                      "           FROM (graduates_result " \
                      "             JOIN graduates_spravochnik ON ((graduates_result.result_result = graduates_spravochnik.spravochnik_kod))) " \
                      "          WHERE ((graduates_result.respondent_type_id = 3) AND (graduates_result.question_number_id = 9) AND (graduates_spravochnik.spravochnik_number = 2)) " \
                      "          GROUP BY graduates_spravochnik.spravochnik_name, graduates_result.essence_id, graduates_result.question_number_id, graduates_result.result_result " \
                      "          ORDER BY graduates_spravochnik.spravochnik_name "
            html = 'checkprofspec'
        elif typech == 'ugs':
            sql = "SELECT t_ugs.kod_ugs, t_ugs.kod_ugs||' - '||t_ugs.name_ugs AS name_ugs FROM t_ugs INNER JOIN v_results_oospo_columns ON t_ugs.kod_ugs = v_results_oospo_columns.kod_ugs ORDER BY t_ugs.kod_ugs"
            html = 'checkugs'
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    profspec_dic = {}
    for value in results:
        profspec_dic[value[0]] = {'kod': value[0], 'name': value[1]}
    #return HttpResponse(ugs_dic)
    return render(request, 'results/'+html+'.html',
                  {'profspec_dic': profspec_dic})


def getdataforgraph(respondent_strtype, typeq, year, finance, razrez, regions, ugs_str, profspec_str, de, cel, inv, formaob, sex, typeoo, golfil):
    if respondent_strtype == 'graduates':
        table = 'v_exit_1_graduates'
        tbl_char = 'v_characteristic_graduates'
    elif respondent_strtype == 'organizations':
        table = 'v_exit_1_oospo'
        tbl_char = 'v_characteristic_oospo'
    elif respondent_strtype == 'employers':
        return HttpResponse('Нет выходных таблиц по данной группе респондентов')
    cursor = connection.cursor()
    sql = "  SELECT " \
          "  unnest(ARRAY['Трудоустроены', 'Продолжили обучение', 'Призваны в ряды Вооруженных Сил', 'Находятся в отпуске по уходу за ребенком', 'Не трудоустроены']) ," \
          "  unnest(ARRAY[ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr14) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr15) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr16) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr17) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2)])" \
          "  FROM "+table+" " \
          "  INNER JOIN "+tbl_char+" ON "+table+".respondent_id = "+tbl_char+".respondent_id" \
          "  WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" "
    #return HttpResponse(sql)
    cursor.execute(sql)
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(float(value[1]))
    raw_employment = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['По специальности', 'Не по специальности']) ,"
                   " unnest(ARRAY[ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST((SUM(gr2)-SUM(gr3)) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2)])"
                   " FROM "+table+" "
                   "  INNER JOIN "+tbl_char+" ON "+table+".respondent_id = "+tbl_char+".respondent_id"
                   "  WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" ")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(float(value[1]))
    raw_employment_spec = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['В регионах с постоянной регистрацией', 'В регионах, не связанных с местом постоянной регистрации']) ,"
                   " unnest(ARRAY[ROUND(CAST(SUM(gr10) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr12) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2)])"
                   " FROM "+table+" "
                   "  INNER JOIN "+tbl_char+" ON "+table+".respondent_id = "+tbl_char+".respondent_id"
                   "  WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" ")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(float(value[1]))
    raw_employment_regions = {'data': res, 'labels': labels}

    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " unnest(ARRAY['По найму', 'ИП', 'Самозанятые']) ,"
                   " unnest(ARRAY[ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2), ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2)])"
                   " FROM "+table+" "
                   "  INNER JOIN "+tbl_char+" ON "+table+".respondent_id = "+tbl_char+".respondent_id"
                   "  WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" ")
    rawresults = cursor.fetchall()
    cursor.close()
    res = []
    labels = []
    for value in rawresults:
        labels.append(value[0])
        res.append(float(value[1]))
    raw_employment_types = {'data': res, 'labels': labels}

    raw = {'raw_employment': raw_employment, 'raw_employment_regions': raw_employment_regions, 'raw_employment_types': raw_employment_types, 'raw_employment_spec': raw_employment_spec}
    return raw



def getdataforexcel(respondent_strtype, typeq, year, finance, razrez, regions, ugs_str, profspec_str, de, cel, inv, formaob, sex, typeoo, golfil):
    if razrez == 'rf':
        razrez = "'Итого'"
    if respondent_strtype == 'graduates':
        tbl = 'v_exit_'+typeq[1]+'_graduates'
        tbl_char = 'v_characteristic_graduates'
        dopon = ''
    elif respondent_strtype == 'organizations':
        tbl = 'v_exit_'+typeq[1]+'_oospo'
        tbl_char = 'v_characteristic_oospo'
        dopon = ' AND '+tbl+'.essence_id = '+tbl_char+'.essence_id '
    if typeq == 'v1':
        sql = "SELECT "+razrez+"," \
                       " ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr2," \
                       " ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr3," \
                       " ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr4," \
                       " ROUND(CAST(SUM(gr5) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr5," \
                       " ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr6," \
                       " ROUND(CAST(SUM(gr7) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr7," \
                       " ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr8," \
                       " ROUND(CAST(SUM(gr9) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr9," \
                       " ROUND(CAST(SUM(gr10) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr10," \
                       " ROUND(CAST(SUM(gr11) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr11," \
                       " ROUND(CAST(SUM(gr12) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr12," \
                       " ROUND(CAST(SUM(gr13) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr13," \
                       " ROUND(CAST(SUM(gr14) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr14," \
                       " ROUND(CAST(SUM(gr15) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr15," \
                       " ROUND(CAST(SUM(gr16) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr16," \
                       " ROUND(CAST(SUM(gr17) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr17," \
                       " ROUND(CAST(SUM(gr18) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr18" \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    if typeq == 'v2':
        sql = "SELECT "+razrez+"," \
                       " ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr2," \
                       " ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr3," \
                       " ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr4," \
                       " ROUND(CAST(SUM(gr5) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr5," \
                       " ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr6," \
                       " ROUND(CAST(SUM(gr7) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr7," \
                       " ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr8," \
                       " ROUND(CAST(SUM(gr9) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr9," \
                       " ROUND(CAST(SUM(gr10) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr10," \
                       " ROUND(CAST(SUM(gr11) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr11," \
                       " ROUND(CAST(SUM(gr12) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr12," \
                       " ROUND(CAST(SUM(gr13) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr13," \
                       " ROUND(CAST(SUM(gr14) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr14," \
                       " ROUND(CAST(SUM(gr15) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr15," \
                       " ROUND(CAST(SUM(gr16) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr16," \
                       " ROUND(CAST(SUM(gr17) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr17," \
                       " ROUND(CAST(SUM(gr18) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr18, " \
                       " ROUND(CAST(SUM(gr19) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr19" \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    if typeq == 'v3':
        sql = "SELECT "+razrez+"," \
                       " ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr2," \
                       " ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr3," \
                       " ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr4," \
                       " ROUND(CAST(SUM(gr5) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr5," \
                       " ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr6," \
                       " ROUND(CAST(SUM(gr7) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr7," \
                       " ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr8," \
                       " ROUND(CAST(SUM(gr9) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr9," \
                       " ROUND(CAST(SUM(gr10) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr10," \
                       " ROUND(CAST(SUM(gr11) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr11," \
                       " ROUND(CAST(SUM(gr12) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr12" \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    if typeq == 'v4':
        sql = "SELECT "+razrez+"," \
                       " ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr2," \
                       " ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr3," \
                       " ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr4," \
                       " ROUND(CAST(SUM(gr5) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr5," \
                       " ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr6," \
                       " ROUND(CAST(SUM(gr7) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr7," \
                       " ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr8," \
                       " ROUND(CAST(SUM(gr9) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr9 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    elif typeq == 'v5':
        sql = "SELECT " + razrez + "," \
                       " SUM(gr1)/SUM(qount) AS gr1," \
                       " SUM(gr2)/SUM(qount) AS gr2," \
                       " SUM(gr3)/SUM(qount) AS gr3," \
                       " SUM(gr4)/SUM(qount) AS gr4," \
                       " SUM(gr5)/SUM(qount) AS gr5," \
                       " SUM(gr6)/SUM(qount) AS gr6," \
                       " SUM(gr7)/SUM(qount) AS gr7," \
                       " SUM(gr8)/SUM(qount) AS gr8," \
                       " SUM(gr9)/SUM(qount) AS gr9," \
                       " SUM(gr10)/SUM(qount) AS gr10 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN(" + regions + ") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" " + de + " " + cel + "  " + inv + " "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    elif typeq == 'v6':
        sql = "SELECT " + razrez + "," \
                       " "+tbl+".respondent_id, " \
                       " SUM(gr1)/SUM(qount) AS gr1," \
                       " SUM(gr2)/SUM(qount) AS gr2 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN(" + regions + ") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" " + de + " " + cel + "  " + inv + " "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1, "+tbl+".respondent_id" \
                       " ORDER BY 1, gr1 desc "
        #return HttpResponse(sql)
    elif typeq == 'v7':
        sql = "SELECT " + razrez + "," \
                       " SUM(gr1)/SUM(qount) AS gr1," \
                       " SUM(gr2)/SUM(qount) AS gr2," \
                       " SUM(gr3)/SUM(qount) AS gr3," \
                       " SUM(gr4)/SUM(qount) AS gr4," \
                       " SUM(gr5)/SUM(qount) AS gr5," \
                       " SUM(gr6)/SUM(qount) AS gr6," \
                       " SUM(gr7)/SUM(qount) AS gr7," \
                       " SUM(gr8)/SUM(qount) AS gr8 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN(" + regions + ") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" " + de + " " + cel + "  " + inv + " "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    if typeq == 'v8':
        sql = "SELECT "+razrez+"," \
                       " ROUND(CAST(SUM(gr2) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr2," \
                       " ROUND(CAST(SUM(gr3) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr3," \
                       " ROUND(CAST(SUM(gr4) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr4," \
                       " ROUND(CAST(SUM(gr5) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr5," \
                       " ROUND(CAST(SUM(gr6) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr6," \
                       " ROUND(CAST(SUM(gr7) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr7," \
                       " ROUND(CAST(SUM(gr8) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr8," \
                       " ROUND(CAST(SUM(gr9) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr9, " \
                       " ROUND(CAST(SUM(gr10) AS DEC(12,4))/CAST(SUM(gr1) AS DEC(12,4))*100,2) AS gr10 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN("+regions+") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" "+de+" "+cel+" "+inv+" "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    elif typeq == 'v9':
        sql = "SELECT " + razrez + "," \
                       " SUM(gr1)/SUM(qount) AS gr1," \
                       " SUM(gr2)/SUM(qount) AS gr2 " \
                       " FROM "+tbl+" INNER JOIN "+tbl_char+" ON "+tbl+".respondent_id = "+tbl_char+".respondent_id "+dopon+" " \
                       " WHERE ter IN(" + regions + ") "+ugs_str+" "+profspec_str+" "+year+" "+finance+" " + de + " " + cel + "  " + inv + " "+formaob+" "+sex+" "+typeoo+" "+golfil+" GROUP BY 1" \
                       " ORDER BY 1"
        #return HttpResponse(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results



def getexcelhead(typeq,respondent_strtype,regions_checked,checked,dop_parameters,chk_text,results):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + respondent_strtype + now + '.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(respondent_strtype)
    style = xlwt.easyxf('font: bold off, color black;\
                         borders: top_color black, bottom_color black, right_color black, left_color black,\
                                  left thin, right thin, top thin, bottom thin;\
                         pattern: pattern solid, fore_color white;\
                         align: vert centre, horiz centre')
    style.alignment.wrap = 1  # переносить по словам
    ws.write(0, 0, chk_text)
    ws.write(1, 0, regions_checked)
    ws.write(2, 0, checked)
    ws.write(3, 0, dop_parameters)
    if typeq == 'v1':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 4, 1, 8, 'Трудоустроены, %', style)
        ws.write_merge(4, 4, 9, 12, 'Трудоустроены из гр.2, %', style)
        ws.write_merge(4, 5, 13, 13, 'Продолжили обучение в проф. обр. организациях, %', style)
        ws.write_merge(4, 5, 14, 14, 'Призваны в ряды Вооруженных Сил Российской Федерации, %', style)
        ws.write_merge(4, 5, 15, 15, 'Находятся в отпуске по уходу за ребенком, %', style)
        ws.write_merge(4, 5, 16, 16,
                       'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных), %', style)
        ws.write_merge(4, 5, 17, 17, 'из них зарегистрированы на бирже труда, %', style)
        ws.write(5, 1, 'Всего', style)
        ws.write(5, 2, 'из них по профессии/специальности', style)
        ws.write(5, 3, 'По найму', style)
        ws.write(5, 4, 'из них по профессии/специальности', style)
        ws.write(5, 5, 'ИП', style)
        ws.write(5, 6, 'из них по профессии/специальности', style)
        ws.write(5, 7, 'Самозанятые', style)
        ws.write(5, 8, 'из них по профессии/специальности', style)
        ws.write(5, 9, 'в регионах с постоянной регистрацией', style)
        ws.write(5, 10, 'из них по профессии/специальности', style)
        ws.write(5, 11, 'в регионах, не связанных с местом постоянной регистрации', style)
        ws.write(5, 12, 'из них по профессии/специальности', style)
        for nc in range(18):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v2':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 5, 1, 1, 'Завершили ГИА с исп. ДЭ (относительно всех опрошенных), %', style)
        ws.write_merge(4, 4, 2, 9, 'Трудоустроены, %', style)
        ws.write_merge(4, 4, 10, 11, 'Трудоустроены из гр.2, %', style)
        ws.write_merge(4, 4, 12, 13, 'Трудоустроены по профессии (специальности), из графы 3, %', style)
        ws.write_merge(4, 5, 14, 14, 'Продолжили обучение в проф. обр. организациях, %', style)
        ws.write_merge(4, 5, 15, 15, 'Призваны в ряды Вооруженных Сил Российской Федерации, %', style)
        ws.write_merge(4, 5, 16, 16, 'Находятся в отпуске по уходу за ребенком, %', style)
        ws.write_merge(4, 5, 17, 17,
                       'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных), %', style)
        ws.write_merge(4, 5, 18, 18, 'из них зарегистрированы на бирже труда, %', style)
        ws.write(5, 2, 'Всего', style)
        ws.write(5, 3, 'из них по профессии/специальности', style)
        ws.write(5, 4, 'По найму', style)
        ws.write(5, 5, 'из них по профессии/специальности', style)
        ws.write(5, 6, 'ИП', style)
        ws.write(5, 7, 'из них по профессии/специальности', style)
        ws.write(5, 8, 'Самозанятые', style)
        ws.write(5, 9, 'из них по профессии/специальности', style)
        ws.write(5, 10, 'в регионах с постоянной регистрацией', style)
        ws.write(5, 11, 'в регионах, не связанных с местом постоянной регистрации', style)
        ws.write(5, 12, 'в регионах с постоянной регистрацией', style)
        ws.write(5, 13, 'в регионах, не связанных с местом постоянной регистрации', style)
        for nc in range(19):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v3':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 5, 1, 1, 'Обучались на основании договора о целевом обучении (относительно всех опрошенных), %', style)
        ws.write_merge(4, 4, 2, 5, 'Трудоустроены, %', style)
        ws.write_merge(4, 4, 6, 7, 'Трудоустроены (из графы 2), %', style)
        ws.write_merge(4, 4, 8, 9, 'Трудоустроены по профессии (специальности), %', style)
        ws.write_merge(4, 5, 10, 10, 'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных), %', style)
        ws.write_merge(4, 5, 11, 11, 'из них зарегистрированы на бирже труда, %', style)
        ws.write(5, 2, 'всего', style)
        ws.write(5, 3, 'по профессии (специальности) в организации указанные в договоре о целевом обучении', style)
        ws.write(5, 4, 'по профессии (специальности) в организации отличные от указанных в договоре о целевом обучении', style)
        ws.write(5, 5, 'не по профессии (специальности)', style)
        ws.write(5, 6, 'в субъектах с постоянной регистрацией', style)
        ws.write(5, 7, 'в субъектах, не связанных с местом постоянной регистрации', style)
        ws.write(5, 8, 'в субъектах с постоянной регистрацией', style)
        ws.write(5, 9, 'в субъектах, не связанных с местом постоянной регистрации', style)
        for nc in range(12):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v4':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 5, 1, 1, 'Доля выпускников, не участвовавших в ДЭ и не обучавшихся на основании договора о целевом обучении (относительно всех опрошенных), %', style)
        ws.write_merge(4, 4, 2, 4, 'Трудоустроены, %', style)
        ws.write_merge(4, 4, 5, 7, 'Трудоустроены по профессии (специальности), %', style)
        ws.write_merge(4, 5, 8, 8, 'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных), %', style)
        ws.write(5, 2, 'всего', style)
        ws.write(5, 3, 'из них в субъектах с постоянной регистрацией', style)
        ws.write(5, 4, 'из них в субъектах, не связанных с местом постоянной регистрации', style)
        ws.write(5, 5, 'всего', style)
        ws.write(5, 6, 'из них в субъектах с постоянной регистрацией', style)
        ws.write(5, 7, 'из них в субъектах, не связанных с местом постоянной регистрации', style)
        for nc in range(9):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v5':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 5, 1, 1, 'Трудоустроившимся (в общем)', style)
        ws.write_merge(4, 4, 2, 4, 'Трудоустроившимся по профессиям (специальностям)', style)
        ws.write_merge(4, 4, 5, 7, 'Завершившим государственную итоговую аттестацию с использованием демонстрационного экзамена и трудоустроившимся по профессии (специальности)', style)
        ws.write_merge(4, 4, 8, 10, 'Обучавшимся на основании договора о целевом обучении и трудоустроившихся по профессии (специальности)', style)
        ws.write(5, 2, 'По найму', style)
        ws.write(5, 3, 'ИП', style)
        ws.write(5, 4, 'Самозанятые', style)
        ws.write(5, 5, 'По найму', style)
        ws.write(5, 6, 'ИП', style)
        ws.write(5, 7, 'Самозанятые', style)
        ws.write(5, 8, 'По найму', style)
        ws.write(5, 9, 'ИП', style)
        ws.write(5, 10, 'Самозанятые', style)
        for nc in range(11):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v6':
        ws.write(4, 0, '', style)
        ws.write(4, 1, 'id выпускника', style)
        ws.write(4, 2, 'Бал ГИА с использованием ДЭ, балл', style)
        ws.write(4, 3, 'Средняя сумма выплат в месяц', style)
        for nc in range(4):
            ws.write(5, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 5
    if typeq == 'v7':
        ws.write(4, 0, '', style)
        ws.write(4, 1, 'В общем', style)
        ws.write(4, 2, 'из них по проф.(/спец.)', style)
        ws.write(4, 3, 'Для завершивших ГИА без использования ДЭ и не обучавшихся по договорам о целевом обучении', style)
        ws.write(4, 4, 'из них по проф.(/спец.)', style)
        ws.write(4, 5, 'Для завершивших ГИА с использованием ДЭ', style)
        ws.write(4, 6, 'из них по проф.(/спец.)', style)
        ws.write(4, 7, 'Для обучавшихся на основании договора о целевом обучении', style)
        ws.write(4, 8, 'из них по проф.(/спец.)', style)
        for nc in range(9):
            ws.write(5, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 5
    if typeq == 'v8':
        ws.write_merge(4, 5, 0, 0, '', style)
        ws.write_merge(4, 4, 1, 7, 'Трудоустроены, %', style)
        ws.write_merge(4, 5, 8, 8, 'Продолжили обучение в проф. обр. организациях, %', style)
        ws.write_merge(4, 5, 9, 9, 'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных), %', style)
        ws.write(5, 1, 'Всего', style)
        ws.write(5, 2, 'из них (из графы 2) по профессии/специальности', style)
        ws.write(5, 3, 'из них (из графы 2) не по профессии/специальности', style)
        ws.write(5, 4, 'По найму', style)
        ws.write(5, 5, 'ИП', style)
        ws.write(5, 6, 'Самозанятые', style)
        ws.write(5, 7, 'Завершившие ГИА с использованием ДЭ', style)
        for nc in range(10):
            ws.write(6, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 6
    if typeq == 'v9':
        ws.write(4, 0, '', style)
        ws.write(4, 1, 'Трудоустроившемуся (в общем)', style)
        ws.write(4, 2, 'Трудоустроившемуся по профессии (специальности)', style)
        for nc in range(3):
            ws.write(5, nc, nc, style)
            ws.col(nc).width = int(23 * 260)
        row_num = 5
    font_style = xlwt.XFStyle()

    for row in results:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response