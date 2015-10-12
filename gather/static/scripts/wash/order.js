// tab切换
$(".nav li").click(function(){
    $(".nav li").removeClass("active");
    $(this).addClass("active");
    var belong = $(this).attr("value");
    var value = $("#wash_"+belong).attr("name");
    if(value != 'true'){
        get_show_info(belong);
    }else{
        $(".wash_div").css("display", "none");
        $("#wash_"+belong).css("display", "");
    }
});

// 获取tab下内容
function get_show_info(belong){
    var _data = {};
    $.ajax({
        type: 'get',
        dataType: "json",
        url: "/wash/show/",
        data: {'belong': belong},
        success: function(Data) {
            if (Data['status']) {
                $(".wash_div").css("display", "none");
                $("#wash_"+belong).css("display", "");
                $("#wash_"+belong).attr("name", "true");
                for(i=0;i<Data['result'].length;i++){
                    var d = Data['result'][i];
                    var html = "<div class='container-fluid' style='border-bottom:solid 1px #CCCCCC;margin-top:10px;'>"+
                                    "<div clss='row'>"+
                                        "<div class='col-xs-3 text-left'>"+
                                            "<a href='#'><img class='order-img' src='"+ d['photo'] +"' alt='...'></a>"+
                                        "</div>"+
                                        "<div class='col-xs-4'>"+
                                           "<h4 class='media-heading text-left'>"+ d['name'] +"</h4>"+
                                            "<label class='media-heading'>"+ d['belong'] +"</label>"+
                                            "<h4>"+
                                                "<label style='color:red'>￥</label><label class='media-heading'>"+ d['new_price'] +"</label>元("+ d['measure'] +")"+
                                            "</h4>"+
                                        "</div>"+
                                        "<div class='col-xs-5 text-right'>"+
                                            "<button type='button' class='btn btn-default btn-sm' style='margin-right:4px;' onclick='order_minus("+ d['id'] +")'>"+
                                              "<span class='glyphicon glyphicon-minus' aria-hidden='true'></span>"+
                                             " </button><label id='wash_count_"+ d['id'] +"'>"+ d['count']+"</label><button type='button' class='btn btn-default btn-sm add' style='margin-left:4px;' onclick='order_add("+ d['id'] +")'>"+
                                             "<span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button></div></div>";
                    $("#wash_"+belong).append(html);
                }
            } else {
                alert("error");
            }
        }
    });
};

// 数量增加一
function order_add(wash_id){
    update_order_ajax(wash_id, 'add')

    $("#order_count").css("display", "");
    $("#order_count").html(parseInt($("#order_count").html())+1);
    var wash_count = $("#wash_count_"+wash_id).html();
    $("#wash_count_"+wash_id).html(parseInt(wash_count)+1);
    price_sum();
}

// 数量减一
function order_minus(wash_id){
    var wash_count = parseInt($("#wash_count_"+wash_id).html());
    var order_count = parseInt($("#order_count").html());
    if(wash_count>0){
        $("#wash_count_"+wash_id).html(parseInt(wash_count)-1);
    }
    if (order_count-1==0){
        $("#order_count").css("display", "none");
        $("#order_count").html(parseInt($("#order_count").html())-1);
    }else if(order_count>0){
        $("#order_count").html(parseInt($("#order_count").html())-1);
    }

    if(wash_count > 0 && order_count>0){
        update_order_ajax(wash_id, 'minus')
    }
    price_sum();
}

// 购物车信息修改1
function update_order_json(d, key, flag){
    var _d = eval('('+d+')');
    if(_d[key] == undefined){
        _d[key] = '1';
    }else{
        if(flag){
           _d[key] = (parseInt(_d[key]) + 1).toString();
        }else{
           _d[key] = (parseInt(_d[key]) - 1).toString();
        }
    }
    var order_str = JSON.stringify(_d);
    $("#order_count_str").val(order_str);
}

// 购物车信息修改2
function update_order_ajax(key, flag){
    $.ajax({
        type: 'post',
        dataType: "json",
        url: "/wash/basket/update/",
        data: { key: key, flag: flag},
        success: function(Data) {
            // do sth
        }
    });
}

function price_sum(){
    var sum = 0;
    $("label[name='price']").each(function(){
        sum += parseInt($(this).html()) * parseInt($("#wash_count_"+$(this).attr("value")).html());
    });
    $("#price_total").html(sum).show();
}



