$(document).on("click", "#getreport", function(){
    var resp = $(this).attr("respondent");
    data_chk = setchkparameters(resp,'excel');
    $.ajax({
      type: "POST",
      url: "/results/ajaxgetreport/"+resp+"/",
      dataType: 'binary',
      xhrFields: {
        'responseType': 'blob'
      },
      data: data_chk,
      success: function (res, status, xhr) {
                var link = document.createElement('a'),
                filename = 'report_'+resp+'_'+$("#type").val()+'.xls';
                link.href = URL.createObjectURL(res);
                link.download = filename;
                link.click();
                //$('.modal').modal('hide');
      }
    });
});

$(document).on("click", "#getgraphs", function(){
    var resp = $(this).attr("respondent");
    data_chk = setchkparameters(resp,'graph');
    $.ajax({
      type: "POST",
      url: "/results/ajaxgetreport/"+resp+"/",
      dataType: 'html',
      xhrFields: {
        //'responseType': 'blob'
      },
      data: data_chk,
      success: function (res, status, xhr) {
                //console.log(res);
                //$(".result").html(res);
                $("#divfilters").hide();
                $("#divgraphbody").html(res);
                $("#divgraphs").show();
                //var myWindow = window.open("", "_self");
                //myWindow.document.write(res);
//                var link = document.createElement('a'),
//                filename = 'report_'+resp+'_'+$("#type").val()+'.xls';
//                link.href = URL.createObjectURL(res);
//                link.download = filename;
//                link.click();
                //$('.modal').modal('hide');
      }
    });
});

$(document).on("click", "#btnbackfromgraph", function(){
    $("#graphcontent").detach();
    $("#divfilters").show();
    $("#divgraphs").hide()
});


$(document).on("click", "#select_profspec", function(){
    var resp = $(this).attr("respondent");
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    //$('#ugs option').prop('selected', true);
    $(this).after('<button type="button" class="small" id="select_ugps" respondent="'+resp+'">Выбрать УГПС</button>');
    $(this).hide();
    //$('#divchkugs').hide();
    $.ajax({
      type: "POST",
      url: "/results/ajaxgetprofspec/"+resp+"/",
      data: {
        typech: 'profspec',
        csrfmiddlewaretoken: tok
      },
      success: function (res) {
        $('#contentchek').html(res);
      }
    });
});

$(document).on("click", "#select_ugps", function(){
    //console.log('dfsdfd');
    //$('#divchkprofspec').detach();
    var resp = $(this).attr("respondent");
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    $(this).after('<button type="button" class="small" id="select_profspec" respondent="'+resp+'">Выбрать профессии/специальности</button>');
    $(this).hide();
    $.ajax({
      type: "POST",
      url: "/results/ajaxgetprofspec/"+resp+"/",
      data: {
        typech: 'ugs',
        csrfmiddlewaretoken: tok
      },
      success: function (res) {
        $('#contentchek').html(res);
      }
    });
});

$('#select_all_regions').click(function() {
    $('#regions option').prop('selected', true);
});

$(document).on("click", "#select_all_ugs", function(){
    $('#ugs option').prop('selected', true);
});

$(document).on("click", "#select_all_profspec", function(){
    $('#profspec option').prop('selected', true);
});

//Сбор параметров с формы:
function setchkparameters(resp,type_report) {
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    let razrez = ( type_report == 'graph' ) ? 'rf' : $("#razrez").val(); //для графиков всегда итоговый разрез данных
    let year = ( $('#year').length > 0 ) ? $("#year").val() : 'None';
    let formaob = ( $('#formaob').length > 0 ) ? $("#formaob").val() : 'None';
    let sex = ( $('#sex').length > 0 ) ? $("#sex").val() : 'None';
    let finance = ( $('#finance').length > 0 ) ? $("#finance").val() : 'None';
    var ugs = ($('#ugs').length > 0) ? $('#ugs').val().join() : '';
    //ugs = ugs.join();
    var profspec = ($('#profspec').length > 0) ? $('#profspec').val().join() : '';
    //profspec = profspec.join();
    var regions = $('#regions').val();
    regions = regions.join();
    var regions_checked = '';
    $('#regions :selected').each(function(i, sel){
        regions_checked += $(sel).text() + ', ';
    });
    regions_checked = 'Выбранные субъекты: ' + regions_checked.substr(0, regions_checked.length - 2);

    var ugs_checked = '';
    $('#ugs :selected').each(function(i, sel){
        ugs_checked += $(sel).text() + ', ';
    });
    ugs_checked = 'Выбранные УГПС: ' + ugs_checked.substr(0, ugs_checked.length - 2);

    var profspec_checked = '';
    $('#profspec :selected').each(function(i, sel){
        profspec_checked += $(sel).text() + ', ';
    });
    profspec_checked = 'Выбранные проф./спец.: ' + profspec_checked.substr(0, profspec_checked.length - 2);

    let de = ($(".de").prop('checked') == true) ? 1 : 0;
    let cel = ($(".cel").prop('checked') == true) ? 1 : 0;
    let inv = ($(".inv").prop('checked') == true) ? 1 : 0;
    let de_checked = ( $('#de:checked').val() == 1 ) ? $('[for="de"]').text() : '';
    let cel_checked = ( $('#cel:checked').val() == 1 ) ? $('[for="cel"]').text() : '';
    let inv_checked = ( $('#inv:checked').val() == 1 ) ? $('[for="inv"]').text() : '';
    var dop_parameters = de_checked + ' | ' + cel_checked + ' | ' + inv_checked;

    let year_checked = ( $('#year').length > 0 ) ? 'Год выпуска: '+$( "#year option:selected" ).text()+', ' : '';
    let finance_checked = ( $('#finance').length > 0 ) ? 'Источник финансирования обучения: '+$( "#finance option:selected" ).text()+', ' : '';
    let formaob_checked = 'Форма обучения: '+$( "#formaob option:selected" ).text()+', ';
    let sex_checked = 'Пол: '+$( "#sex option:selected" ).text();
    var chk_text = year_checked + formaob_checked + finance_checked + sex_checked

    data_chk = {
        'regions': regions,
        'ugs': ugs,
        'profspec': profspec,
        'de': de,
        'cel': cel,
        'inv': inv,
        'regions_checked': regions_checked,
        'ugs_checked': ugs_checked,
        'profspec_checked': profspec_checked,
        'dop_parameters': dop_parameters,
        'chk_text': chk_text,
        'razrez': razrez,
        'year': year,
        'finance': finance,
        'formaob': formaob,
        'sex': sex,
        'type': $("#type").val(),
        'type_report': type_report,
        csrfmiddlewaretoken: tok
      };
    return data_chk;
}