
$(".chosen-select").chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});

$('.modal').on('shown.bs.modal', function () {
     $('.chosen-select', this).chosen('destroy').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
     $(".modal-body").children(".nodata").remove();
     $("span").css("color", "#555");
     $(".questionselement").css("color", "#555");
     $(".questionselement").removeClass('red_placeholder')
});


$('.mask-phone').mask('+7 (999) 999-99-99');
$('.mask-date').mask('99.99.9999');


function checkRequered(classfor) {
    var nosubmit = 0
    $("span").css("color", "#555");
    $(".questionselement").css("color", "#555");
    classfor.removeClass('red_placeholder')
    $(".nodata").remove();
    classfor.each(function(i,elem) {
    //console.log("id: "+$(this).attr("id")+" val: "+$(this).val());
        if( $(this).attr("req") == 1 && ( $(this).val() == 0 || $(this).val() == '' || $(this).val() == null)){
            var idelement = $(this).attr("id");
            nosubmit = 1
            if( $("#"+idelement+"_chosen") ){
                $("#"+idelement+"_chosen").find("span").css("color", "red");
            }
            if( $(this).get(0).tagName == 'INPUT' ){
                 $(this).addClass("red_placeholder");
                 $(this).css("color", "red");
            }
        }
    });
    //console.log("__________________________________");
    return nosubmit;
}

$(document).on("click", "#btnAddEssence", function(){
    //console.log(checkRequered());
    var idmodalplace = $(this).attr("block_num");
    ee = $("#addEssenseModal_"+idmodalplace).find(".questionselement");
    //console.log(ee);
    if( checkRequered(ee) == 0){

        var el = $('.modal-body[block_num="'+idmodalplace+'"]').children(".questionselement");
        var essnum;
        //if( $("button").is(".essance") ){
        if( $('button[modalplace="'+idmodalplace+'"]') ){
            //essnum = $(".essance").length+1;
            essnum = $('button[modalplace="'+idmodalplace+'"]').length+1;
        }else{
            essnum = 1;
        }
        esselement = '';
        $('#essanceplace_'+idmodalplace+"").append('<button modalplace="'+idmodalplace+'" title="'+essnum+'" id="spanessance_'+essnum+'" type="button" class="btn btn-secondary btn-lg essance" style="margin:5px;" disabled><i class="fas fa-user-graduate fas-lg"></i></button>');
        el.each(function( index ) {
            $("#spanessance_"+essnum+"").append('<input type="hidden" name="essance_'+idmodalplace+'_'+essnum+'_'+$(this).attr('id')+'" value="'+$(this).val()+'" />');
            $(this).val("");
        });
        $(".nodata").remove();
        $('.modal').modal('hide');
    }else{
        $(".modal-body").append('<div class="alert alert-danger nodata" role="alert" style="margin-top:25px;">Заполнены не все обязательные поля!</div>');
    }

});


$(document).on("click", "#btnsave", function(){
    var respondent_id = $("#anketform").attr("action").split("/");
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
      type: "POST",
      url: "/graduates/ajaxsave/"+respondent_id[3]+"/",
      data: {
        'form': $("#anketform").serialize(),
        csrfmiddlewaretoken: tok
      },
      success: function (res) {
        $("#anketform").after('<div class="alert alert-light" role="alert" style="margin-top:25px;">Промежуточные данные сохранены: '+res+'</div>');
      }
    });
});


$(document).on("click", "#btnsubmit", function(){
    ii = $(".mainelement")
    if( checkRequered(ii) == 0){
        $("#anketform").submit();
    }else{
        $("#btnsubmit").after('<div class="alert alert-danger nodata" role="alert" style="margin-top:25px;">Заполнены не все обязательные поля!</div>');
    }
});

$(document).on("change", ".chosen-select", function(){
    if( $("div").is(".nodata") ){
        var idelement = $(this).attr("id");
        $("#"+idelement+"_chosen").find("span").css("color", "#555");
    }
});

$(document).on("change", ".questionselement", function(){
    if( $("div").is(".nodata") ){
        var idelement = $(this).attr("id");
        $("#"+idelement+"").css("color", "#555");
    }
});

/*$(document).on("click", "#btnsubmit", function(){
    if( $("button").is(".essance") ){
        $(".ecsubdiv").each(function( index ) {
            var idel = $(this).attr("id").split("_");
            var x = $(this).find('.essance').attr("id");
            if( !x ){
                console.log("уничтожить"+"#addEssenseModal_"+idel[1]+"");
                $("#addEssenseModal_"+idel[1]+"").remove();
            }
        });
    }else{
        $(".modal").remove();
    }
    $("#anketform").submit();
});*/

