$(".chosen-select").chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});

//$(".modal-body").children(".chosen-select").chosen("destroy");
$(".modal-body").children(".chosen-container").css("display","none");


$('.modal').on('shown.bs.modal', function () {
     $(".chosen-select", this).chosen("destroy").chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
     //для 48 вопроса:
     $('.ajax').chosen("destroy").chosen({no_results_text: "Не найдено: "});
     $(".modal-body").children(".nodata").remove();
     $("span").css("color", "#555");
     $(".questionselement").css("color", "#555");
     $(".questionselement").removeClass('red_placeholder');
});


$('.mask-phone').mask('+7 (999) 999-99-99');
$('.mask-date').mask('99.99.9999');


function checkLocalInterconnection(){
    if( $("#essencequestion_13").val() == "2" && $("#essencequestion_14").val() == "2" && $("#essencequestion_15").val() == "2" ){
        $("#essencequestion_18").attr("req","1");
    }else{
        $("#essencequestion_18").attr("req","0");
    }

    if( $("#essencequestion_18").val() == "1"){
        $("#essencequestion_19").attr("req","1");
        $("#freequestion_109").attr("req","1");
        $("#essencequestion_22").attr("req","1");
        $("#essencequestion_23").attr("req","1");
        $("#essencequestion_24").attr("req","1");
        $("#essencequestion_25").attr("req","1");
    }else{
        $("#essencequestion_19").attr("req","0");
        $("#freequestion_109").attr("req","0");
        $("#essencequestion_22").attr("req","0");
        $("#essencequestion_23").attr("req","0");
        $("#essencequestion_24").attr("req","0");
        $("#essencequestion_25").attr("req","0");
    }
}


var timer;
   //$(document).on("keyup", '#'+$(".ajax").attr("id")+'_chosen .chosen-search-input', function(){
   $(document).on("keyup", '.chosen-search-input', function(){
    var parentdiv = $(this).parents('div.chosen-container').attr('id');
    var idselect = parentdiv.split('_');
    idselect = idselect[0]+"_"+idselect[1];
       //var usertext = $('#essencequestion_48_chosen').find('.no-results').find("span").text();
       //var usertext = $('#essencequestion_48_chosen .no-results span').text();
       //var usertext = $('#'+$(".ajax").attr("id")+'_chosen .chosen-search-input').val();
    if($('#'+idselect).hasClass("ajax")){
       var usertext = $(this).val();
       var modela = $('#'+idselect).attr("modela");
       window.clearTimeout(timer);
       $('li.no-results').empty();
       if (usertext.length > 3) {
           timer = setTimeout(function () {
                var respondent_id = $("#anketform").attr("action").split("/");
                $.ajax({
                  type: "POST",
                  url: "/"+respondent_id[1]+"/ajaxgetprofession/"+respondent_id[3]+"/",
                  data: {
                    'userval': usertext,
                    'modela': modela,
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                  },
                  beforeSend: function(){
                  },
                  success: function (res) {
                    if(res.length > 0){
                        $('option.findoptions_'+idselect).remove();
                        $('li.no-results').empty();
                        $.each(res, function(i, item) {
                            var doai = i+1;
                            $('#'+idselect+'').append('<option class="fop findoptions_'+idselect+'" title="'+item.fields.name_okpdtr+'" value="'+item.fields.kod_okpdtr+'">'+item.fields.name_okpdtr+'</option>');
                            $('#'+parentdiv+' .chosen-results').append('<li class="active-result" data-option-array-index="'+doai+'" title="'+item.fields.name_okpdtr+'">'+item.fields.name_okpdtr+'</li>');
                        });
                        $('#'+idselect+'').trigger("chosen:updated");
                        $('#'+parentdiv+' .chosen-search-input').val(usertext);
                    }else{
                        $('li.no-results').text("Не найдено");
                    }
                  }
                });
           }, 1000);
       }
    }
   });



function checkLocalOne(element){
    if( element.attr("id") == "essencequestion_13" || element.attr("id") == "essencequestion_14" || element.attr("id") == "essencequestion_15" ){
            $("#essencequestion_18").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#essencequestion_19").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#freequestion_109").removeAttr('disabled');
            $("#essencequestion_22").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#essencequestion_23").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#essencequestion_24").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#essencequestion_25").removeAttr('disabled').chosen({no_results_text: "Не найдено: ", disable_search_threshold: 10});
            $("#freequestion_27").removeAttr('disabled');
        if( $("#essencequestion_13").val() == "1" || $("#essencequestion_14").val() == "1" || $("#essencequestion_15").val() == "1" ){
            $("#essencequestion_18").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#essencequestion_19").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#freequestion_109").attr('disabled', 'disabled');
            $("#essencequestion_22").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#essencequestion_23").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#essencequestion_24").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#essencequestion_25").chosen("destroy").attr('disabled', 'disabled').val("");
            $("#freequestion_27").attr('disabled', 'disabled');
        }
    }

    if( $("#essencequestion_48").val() !== null && $("#essencequestion_48").val() != 0){
        $("#essencequestion_49").attr("req","0");
        $("#essencequestion_49").chosen("destroy").attr('disabled', 'disabled').val("");
    }else{
        $("#essencequestion_49").removeAttr('disabled').chosen({no_results_text: "Не найдено: "});
        $("#essencequestion_49").attr("req","1");
    }
    if( $("#essencequestion_49").val() !== null && $("#essencequestion_49").val() != 0){
        $("#essencequestion_48").attr("req","0");
        $("#essencequestion_48").chosen("destroy").attr('disabled', 'disabled').val("");
    }else{
        $("#essencequestion_48").removeAttr('disabled').chosen({no_results_text: "Не найдено: "});
        $("#essencequestion_48").attr("req","1");
    }
    if( $("#essencequestion_59").val() !== null && $("#essencequestion_59").val() != 0){
        $("#essencequestion_107").attr("req","0");
        $("#essencequestion_107").chosen("destroy").attr('disabled', 'disabled').val("");
    }else{
        $("#essencequestion_107").removeAttr('disabled').chosen({no_results_text: "Не найдено: "});
        $("#essencequestion_107").attr("req","1");
    }
    if( $("#essencequestion_107").val() !== null && $("#essencequestion_107").val() != 0){
        $("#essencequestion_59").attr("req","0");
        $("#essencequestion_59").chosen("destroy").attr('disabled', 'disabled').val("");
    }else{
        $("#essencequestion_59").removeAttr('disabled').chosen({no_results_text: "Не найдено: "});
        $("#essencequestion_59").attr("req","1");
    }


}


function checkRequered(classfor) {
    var nosubmit = 0
    $("span").css("color", "#555");
    $(".questionselement").css("color", "#555");
    classfor.removeClass('red_placeholder')
    $(".nodata").remove();
    classfor.each(function(i,elem) {
    //console.log("id: "+$(this).attr("id")+" val: "+$(this).val());
        if( $(this).attr("req") == 1 && ( ($(this).val() == 0 && $(this).hasClass("chosen-select") ) || $(this).val() == '' || $(this).val() == null)){
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

function checkValue(element){
    $("#novalidvalue_"+element.attr("id")).remove();
    element.css("color", "#555");
    if( element.attr("type") == "number" ){
        if( (Number(element.attr("max")) < Number(element.val())) || (Number(element.attr("min")) > Number(element.val())) ){
            $(element).after('<small id="novalidvalue_'+element.attr("id")+'" class="text-danger">Введите значение в диапазоне от '+element.attr("min")+' до '+element.attr("max")+'</small>');
            $(element).css("color", "red");
        }
    }
    if( element.attr("type") == "email" ){
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if(re.test(element.val().toLowerCase()) == false){
            $(element).after('<small id="novalidvalue_'+element.attr("id")+'" class="text-danger">Введите корректный адрес электронной почты</small>');
            $(element).css("color", "red");
        }
    }
}


$(document).on("click", ".valcleaner", function(){
    //console.log($(this).attr("id"));
    $("#essencequestion_"+$(this).attr("id")).val(0);
    //$("ul.chosen-results").empty();
    //$("option.fop").remove();
    $("#essencequestion_"+$(this).attr("id")).trigger("chosen:updated");
    checkLocalOne($(this));
});


$(document).on("click", "#btnAddEssence", function(){
    checkLocalInterconnection();
    var idmodalplace = $(this).attr("block_num");
    ee = $("#addEssenseModal_"+idmodalplace).find(".questionselement");
    if( checkRequered(ee) == 0 ){
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
        $('#essanceplace_'+idmodalplace+"").append('<button modalplace="'+idmodalplace+'" title="'+essnum+'" id="spanessance_'+essnum+'" type="button" class="btn btn-secondary btn-lg essance" style="display:none;margin:5px;" disabled><i class="fas fa-user-graduate fas-lg"></i></button>');
        $('#essanceplace_'+idmodalplace+"").children(".countessances").remove();
        $('#essanceplace_'+idmodalplace+"").append('<div class="countessances"><mark>Добавлено: '+essnum+'</mark></div>');
        el.each(function( index ) {
            $("#spanessance_"+essnum+"").after('<input type="hidden" name="essance_'+idmodalplace+'_'+essnum+'_'+$(this).attr('id')+'" value="'+$(this).val()+'" />');
            $(this).val("");
            $(this).removeAttr('disabled');
        });
        $("ul.chosen-results").empty();
        $("option.fop").remove();
        $(".nodata").remove();
        $('.modal').modal('hide');
    }else{
        $(".alert").remove();
        $(".modal-body").append('<div class="alert alert-danger nodata" role="alert" style="margin-top:25px;"><i class="fas fa-exclamation-triangle"></i> Заполнены не все обязательные поля!</div>');
    }
});


$(document).on("click", "#btnsave", function(){
    var respondent_id = $("#anketform").attr("action").split("/");
    var tok = $('input[name=csrfmiddlewaretoken]').val();
    $.ajax({
      type: "POST",
      url: "/"+respondent_id[1]+"/ajaxsave/"+respondent_id[3]+"/",
      data: {
        'form': $("#anketform").serialize(),
        csrfmiddlewaretoken: tok
      },
      success: function (res) {
        $(".alert").remove();
        $("#anketform").after('<div class="alert alert-info" role="alert" style="margin-top:25px;"><i class="fas fa-info"></i> Промежуточные данные сохранены: '+res+'</div>');
      }
    });
});


$(document).on("click", "#btnsubmit", function(){
    ii = $(".mainelement")
    if( checkRequered(ii) == 0){
        $("#anketform").submit();
    }else{
        $(".alert").remove();
        $("#btnsubmit").after('<div class="alert alert-danger nodata" role="alert" style="margin-top:25px;"><i class="fas fa-exclamation-triangle"></i> Заполнены не все обязательные поля!</div>');
    }
});

$(document).on("change", ".chosen-select", function(){
    if( $("div").is(".nodata") ){
        var idelement = $(this).attr("id");
        $("#"+idelement+"_chosen").find("span").css("color", "#555");
    }
});

$(document).on("change", ".questionselement", function(){
    checkLocalOne($(this));
    if( $("div").is(".nodata") ){
        var idelement = $(this).attr("id");
        $("#"+idelement+"").css("color", "#555");
    }
});

$(document).on("change", ".mainelement", function(){
    checkValue($(this));
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

