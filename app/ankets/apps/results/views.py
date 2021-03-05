from django.shortcuts import render
from django.http import HttpResponse
from django.template.defaulttags import register
from django.db import connection
from graduates.models import Respondent
#from excel_response import ExcelResponse
import xlwt
import datetime
#from django.db.models import Max

#Пользовательские фильтры:
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

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
        #sql = 'SELECT ter, q71, COUNT(respondent_id) AS count_resp FROM v_results_graduates_columns GROUP BY ter, q71'
        sql = "SELECT ter, q71, SUM(count_resp) AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2) AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_trud))*100,2) ELSE 0.00 END AS d_trud_prof, CASE WHEN SUM(count_trud)!=0 THEN SUM(zp)/SUM(count_trud) ELSE 0 END AS zp FROM" \
              " (SELECT respondent_id, ter, q71, COUNT(respondent_id) AS count_resp, CASE WHEN(q91_zn = 1 OR q91_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN(q92_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q97 <> '') THEN q97::int ELSE 0 END AS zp  FROM v_results_graduates_columns GROUP BY respondent_id, ter, q71, q91_zn, q92_zn, q97) sq" \
              " GROUP BY ter, q71"
        sql_ugs = "SELECT kod_ugs, name_ugs FROM t_ugs INNER JOIN v_results_graduates_columns ON t_ugs.kod_ugs = v_results_graduates_columns.ugs ORDER BY kod_ugs"
    elif respondent_strtype == 'organizations':
        table = 'v_exit_1_oospo_rf'
        #sql = 'SELECT ter, q3, COUNT(respondent_id) AS count_resp FROM v_results_oospo_columns GROUP BY ter, q3'
        sql = "SELECT ter, q3, SUM(count_resp) AS count_resp, ROUND((SUM(count_trud)/SUM(count_resp))*100,2) AS d_trud, CASE WHEN SUM(count_trud)!=0 THEN ROUND((CAST(SUM(count_trud_prof) AS DEC(12,4))/SUM(count_trud))*100,2) ELSE 0.00 END AS d_trud_prof, CASE WHEN SUM(count_trud)!=0 THEN SUM(zp)/SUM(count_trud_with_zp) ELSE 0 END AS zp FROM" \
              "              (SELECT respondent_id, ter, q3, COUNT(respondent_id) AS count_resp, CASE WHEN(q18_zn = 1 OR q18_zn = 2) THEN 1 ELSE 0 END AS count_trud, CASE WHEN((q18_zn = 1 OR q18_zn = 2) AND q119 <> '') THEN 1 ELSE 0 END AS count_trud_with_zp, CASE WHEN(q111_zn = 1) THEN 1 ELSE 0 END AS count_trud_prof, CASE WHEN(q119 <> '') THEN q119::int ELSE 0 END AS zp FROM v_results_oospo_columns GROUP BY respondent_id, essence_id, ter, q3, q18_zn, q111_zn, q119 ORDER BY respondent_id) sq" \
              "              GROUP BY ter, q3"
        sql_ugs = "SELECT t_ugs.kod_ugs, t_ugs.name_ugs FROM t_ugs INNER JOIN v_results_oospo_columns ON t_ugs.kod_ugs = v_results_oospo_columns.kod_ugs ORDER BY kod_ugs"
    elif respondent_strtype == 'employers':
        table = 'v_exit_1_employers'
        sql = ''
        sql_ugs = "SELECT kod_ugs, name_ugs FROM t_ugs ORDER BY kod_ugs"
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

    return render(request, 'results/respondents.html',
                  {'count_all': count_all, 'regions': regions, 'ugs_dic': ugs_dic, 'respondent_strtype': respondent_strtype, 'respondent_name': respondent_name, 'raw_employment': raw_employment, 'raw_employment_types': raw_employment_types, 'raw_employment_prof': raw_employment_prof, 'raw_employment_regions': raw_employment_regions})


def exittables(request, respondent_strtype, ter):
    if ter == 0:
        return HttpResponse('Нет страницы')
    # else:
    #     return HttpResponse(ter)
    respondent_obj = Respondent.objects.get(link_name=respondent_strtype)
    respondent_name = respondent_obj.respondent_name
    cursor = connection.cursor()
    if respondent_strtype == 'graduates':
        #cursor.execute("SELECT * FROM v_exit_1_graduates")
        cursor.execute("SELECT name_ugs,"
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
                       " WHERE ter = "+str(ter)+" GROUP BY name_ugs"
                       " ORDER BY name_ugs")
    elif respondent_strtype == 'organizations':
        cursor.execute("SELECT v_characteristic_oospo.name_ugs AS name_ugs,"
                       " SUM(v_exit_1_oospo.gr1) AS gr1,"
                       " SUM(v_exit_1_oospo.gr2) AS gr2,"
                       " SUM(v_exit_1_oospo.gr3) AS gr3,"
                       " SUM(v_exit_1_oospo.gr4) AS gr4,"
                       " SUM(v_exit_1_oospo.gr5) AS gr5,"
                       " SUM(v_exit_1_oospo.gr6) AS gr6,"
                       " SUM(v_exit_1_oospo.gr7) AS gr7,"
                       " SUM(v_exit_1_oospo.gr8) AS gr8,"
                       " SUM(v_exit_1_oospo.gr9) AS gr9,"
                       " SUM(v_exit_1_oospo.gr10) AS gr10,"
                       " SUM(v_exit_1_oospo.gr11) AS gr11,"
                       " SUM(v_exit_1_oospo.gr12) AS gr12,"
                       " SUM(v_exit_1_oospo.gr13) AS gr13,"
                       " SUM(v_exit_1_oospo.gr14) AS gr14,"
                       " SUM(v_exit_1_oospo.gr15) AS gr15"
                       " FROM v_exit_1_oospo INNER JOIN v_characteristic_oospo ON v_exit_1_oospo.name_agregate = v_characteristic_oospo.respondent_id AND v_exit_1_oospo.essence_id = v_characteristic_oospo.essence_id"
                       " WHERE ter = "+str(ter)+""
                       " GROUP BY name_ugs")
    elif respondent_strtype == 'employers':
        return HttpResponse('Нет выходных таблиц по данной группе респондентов')
    rawresults = cursor.fetchall()
    cursor.close()
    results = rawresults
    return render(request, 'results/exittables.html',
                  {'respondent_strtype': respondent_strtype, 'results': results, 'respondent_name': respondent_name})



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
    razrez = request.POST.get('razrez')
    de = ' AND dem_exam = 1 ' if request.POST.get('de') == '1' else ''
    cel = ' AND celevoe = 1 ' if request.POST.get('cel') == '1' else ''
    inv = ' AND ovz_inv = 1 ' if request.POST.get('inv') == '1' else ''
    if regions == '' or ugs == '':
        return HttpResponse("don't set parameters")
    if respondent_strtype == 'graduates':
        #sql = "SELECT * FROM v_results_graduates_columns WHERE ter IN("+regions+")"
        sql = "SELECT "+razrez+"," \
                       " SUM(gr1) AS gr1," \
                       " SUM(gr2) AS gr2," \
                       " SUM(gr3) AS gr3," \
                       " SUM(gr4) AS gr4," \
                       " SUM(gr5) AS gr5," \
                       " SUM(gr6) AS gr6," \
                       " SUM(gr7) AS gr7," \
                       " SUM(gr8) AS gr8," \
                       " SUM(gr9) AS gr9," \
                       " SUM(gr10) AS gr10," \
                       " SUM(gr11) AS gr11," \
                       " SUM(gr12) AS gr12," \
                       " SUM(gr13) AS gr13," \
                       " SUM(gr14) AS gr14," \
                       " SUM(gr15) AS gr15" \
                       " FROM v_exit_1_graduates INNER JOIN v_characteristic_graduates ON v_exit_1_graduates.respondent_id = v_characteristic_graduates.respondent_id" \
                       " WHERE ter IN("+regions+") AND kod_ugs IN("+ugs+") "+de+" "+cel+"  "+inv+"  GROUP BY "+razrez+"" \
                       " ORDER BY "+razrez+""
        #return HttpResponse(sql)
    elif respondent_strtype == 'organizations':
        sql = "SELECT "+razrez+"," \
                       " SUM(v_exit_1_oospo.gr1) AS gr1," \
                       " SUM(v_exit_1_oospo.gr2) AS gr2," \
                       " SUM(v_exit_1_oospo.gr3) AS gr3," \
                       " SUM(v_exit_1_oospo.gr4) AS gr4," \
                       " SUM(v_exit_1_oospo.gr5) AS gr5," \
                       " SUM(v_exit_1_oospo.gr6) AS gr6," \
                       " SUM(v_exit_1_oospo.gr7) AS gr7," \
                       " SUM(v_exit_1_oospo.gr8) AS gr8," \
                       " SUM(v_exit_1_oospo.gr9) AS gr9," \
                       " SUM(v_exit_1_oospo.gr10) AS gr10," \
                       " SUM(v_exit_1_oospo.gr11) AS gr11," \
                       " SUM(v_exit_1_oospo.gr12) AS gr12," \
                       " SUM(v_exit_1_oospo.gr13) AS gr13," \
                       " SUM(v_exit_1_oospo.gr14) AS gr14," \
                       " SUM(v_exit_1_oospo.gr15) AS gr15" \
                       " FROM v_exit_1_oospo INNER JOIN v_characteristic_oospo ON v_exit_1_oospo.name_agregate = v_characteristic_oospo.respondent_id AND v_exit_1_oospo.essence_id = v_characteristic_oospo.essence_id" \
                       " WHERE ter IN("+regions+") AND kod_ugs IN("+ugs+") "+de+" "+cel+"  "+inv+"  GROUP BY "+razrez+"" \
                       " ORDER BY "+razrez+""
        #return HttpResponse(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

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
    style.alignment.wrap = 1 #переносить по словам
    ws.write_merge(0, 1, 0, 0, '', style)
    ws.write_merge(0, 1, 1, 1, 'Всего, чел.', style)
    ws.write_merge(0, 0, 2, 9, 'Трудоустроены, чел.', style)
    ws.write_merge(0, 0, 10, 11, 'Трудоустроены из гр.2, чел.', style)
    ws.write_merge(0, 1, 12, 12, 'Продолжили обучение в проф. обр. организациях', style)
    ws.write_merge(0, 1, 13, 13, 'Призваны в ряды Вооруженных Сил Российской Федерации', style)
    ws.write_merge(0, 1, 14, 14, 'Находятся в отпуске по уходу за ребенком', style)
    ws.write_merge(0, 1, 15, 15, 'Не трудоустроены (в т. ч. находятся на учете в службе занятости в качестве безработных)', style)
    ws.write(1, 2, 'Всего', style)
    ws.write(1, 3, 'из них по профессии/специальности', style)
    ws.write(1, 4, 'По найму', style)
    ws.write(1, 5, 'из них по профессии/специальности', style)
    ws.write(1, 6, 'ИП', style)
    ws.write(1, 7, 'из них по профессии/специальности', style)
    ws.write(1, 8, 'Самозанятые', style)
    ws.write(1, 9, 'из них по профессии/специальности', style)
    ws.write(1, 10, 'в регионах с постоянной регистрацией', style)
    ws.write(1, 11, 'в регионах, не связанных с местом постоянной регистрации', style)
    for nc in range(16):
        ws.write(2, nc, nc, style)
        ws.col(nc).width = int(23 * 260)
    font_style = xlwt.XFStyle()
    row_num = 2
    for row in results:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
    #return HttpResponse(results)
    #return render(request, 'results/exittables.html',
    #              {'respondent_strtype': respondent_strtype, 'results': results, 'respondent_name': "В-----"})