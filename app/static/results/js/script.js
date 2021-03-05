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

//    var ugs = '';
//    $( ".ugs" ).each(function( index ) {
//        if(this.checked){
//            ugs += "'"+$(this).val()+"',";
//        }
//    });
//    ugs = ugs.substr(0, ugs.length - 1);

    var de = 0;
    if($(".de").prop('checked') == true){
        de = 1;
    }
    var cel = 0;
    if($(".cel").prop('checked') == true){
        cel = 1;
    }
    var inv = 0;
    if($(".inv").prop('checked') == true){
        inv = 1;
    }

    var de_checked = '';
    if( $('#de:checked').val() == 1 ){
        de_checked = $('[for="de"]').text();
    }
    var cel_checked = '';
    if( $('#cel:checked').val() == 1 ){
        cel_checked = $('[for="cel"]').text();
    }
    var inv_checked = '';
    if( $('#inv:checked').val() == 1 ){
        inv_checked = $('[for="inv"]').text();
    }
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