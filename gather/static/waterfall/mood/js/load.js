$("#loading").click(function () {
    var page_num = $("#page_num").val();
    var _data = {};
    _data['page'] = page_num;
    $("#loading").html("加载中...");
    $("#loading").addClass('disabled');
    $.ajax({
      url: '/share/photo/more/',
      type: 'GET',
      dataType: 'json',
      data: _data,
      success: function(Data) {
          var html = "";
          if(Data['result']){
            for(var i=0;i<Data['data'].length;i++){
                var obj = Data['data'][i];
                var url = obj['photo'];
                var title = obj['title'];
                html += "<li><figure><img src='/media/"+ url +"' alt='加载中...'/><figcaption><p>"+ title +"</p></figcaption></figure></li>"
            }
            $(".grid").append(html);
            $("#loading").html("加载更多");
            $("#loading").removeClass('disabled');
            $("#page_num").val(Data['page_num']);
          }else{
            $("#loading").html("没有更多的数据");
            $("#loading").addClass('disabled');
          }
      }
    });
});