$(document).on("click", "#getreport", function(){
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    var resp = $(this).attr("respondent")

    var ugs = $('#ugs').val();
    ugs = ugs.join();

    var regions = $('#regions').val();
    regions = regions.join();

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