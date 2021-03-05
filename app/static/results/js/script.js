$(document).on("click", "#getreport", function(){
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    var resp = $(this).attr("respondent")

    var ugs = $('#ugs').val();
    ugs = ugs.join();

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

    let de = ($(".de").prop('checked') == true) ? 1 : 0;
    let cel = ($(".cel").prop('checked') == true) ? 1 : 0;
    let inv = ($(".inv").prop('checked') == true) ? 1 : 0;
    let de_checked = ( $('#de:checked').val() == 1 ) ? $('[for="de"]').text() : '';
    let cel_checked = ( $('#cel:checked').val() == 1 ) ? $('[for="cel"]').text() : '';
    let inv_checked = ( $('#inv:checked').val() == 1 ) ? $('[for="inv"]').text() : '';
    var dop_parameters = de_checked + ' | ' + cel_checked + ' | ' + inv_checked;

    $.ajax({
      type: "POST",
      url: "/results/ajaxgetreport/"+resp+"/",
      dataType: 'binary',
      xhrFields: {
        'responseType': 'blob'
      },
      data: {
        'regions': regions,
        'ugs': ugs,
        'de': de,
        'cel': cel,
        'inv': inv,
        'regions_checked': regions_checked,
        'ugs_checked': ugs_checked,
        'dop_parameters': dop_parameters,
        'razrez': $("#razrez").val(),
        csrfmiddlewaretoken: tok
      },
      success: function (res, status, xhr) {
                var link = document.createElement('a'),
                filename = 'report_'+resp+'.xls';
                link.href = URL.createObjectURL(res);
                link.download = filename;
                link.click();
                //$('.modal').modal('hide');
      }
    });
});


$('#select_all_regions').click(function() {
    $('#regions option').prop('selected', true);
});

$('#select_all_ugs').click(function() {
    $('#ugs option').prop('selected', true);
});