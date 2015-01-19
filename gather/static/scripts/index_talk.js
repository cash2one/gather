/*
 * 显示评论
 */
$(".note-a").click(function(){
    _data = {};
    _data['note_id'] = $(this).attr("value");
    $.ajax({
        type: 'post',
        dataType: "json",
        url: '/comment/list/',
        data: _data,
        success: function(Data) {
          comment_html = '';
          $("#read_sum").html(Data['read_sum']).show();
          $("#heart").attr('value', Data['id']);
          $("#heart").html("&nbsp;" + Data['heart']).show();
          if(parseInt(Data['heart'])>0){
            $("#heart").css('color', 'red');
          }else{
            $("#heart").css('color', '');
          }
          $("#thumb_down").attr('value', Data['id']);
          $("#thumb_down").html("&nbsp;" + Data['thumb_down']).show();
          $("#myModalLabel").html(Data['title']).show();
          $("#myModalLabel").attr("name", Data['id']);
          for(i=0;i<Data['comments'].length;i++){
            comment_html = comment_html + "<div class='row note_comment'><div class='col-sm-note-1'><img src='" + Data['comments'][i]['url'] + "' alt='140*140' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" + Data['comments'][i]['created'] + "&nbsp;&nbsp;<a href=''>" + Data['comments'][i]['username'] +"</a></label><label class='text-right reply'><a href=''>#</a></label></div><p class='note-comment'>" + Data['comments'][i]['comment'] + "</p></div></div>"
          }
          $("#comment-body").html(comment_html).show();
        }
      });
     $("#comment_content").val("");
  });

  /*
   * 发表评论
   */
  $("#say").click(function(){
    comment = $("#comment_content").val();
    note_id = $("#myModalLabel").attr("name");
    _data = {};
    _data['note_id'] = note_id;
    _data['comment'] = comment;
    $.ajax({
      type: 'post',
      dataType: "json",
      url: '/comment/add/',
      data: _data,
      success: function(Data) {
        if(Data){
          comment_html = "<div class='row note_comment'><div class='col-sm-note-1'><img src='" + Data['url'] + "' alt='140*140' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" + Data['created'] + "&nbsp;&nbsp;<a href=''>" + Data['username'] +"</a></label><label class='text-right reply'><a href=''>#</a></label></div><p class='note-comment'>" + Data['comment'] + "</p></div></div>"
          $("#comment-body").html($("#comment-body").html() + comment_html).show();
        }else{
          $("#login").removeClass('fade').addClass('show');
        }
      }
    });
     $("#comment_content").val("");
  });

/*
 * 喜欢
 */
  $("#heart").click(function(){
    _data = {};
    _data['note_id'] = $(this).attr("value");
    $.ajax({
      type: 'post',
      dataType: "json",
      url: '/note/heart/',
      data: _data,
      success: function(Data) {
        if(Data['result']){
          if(Data['sign']){
            heart_sum = parseInt($("#heart").html().substring(6)) + 1;
            $("#heart").css('color', 'red');
            $("#heart").html('&nbsp;' + heart_sum);
          }else{
            heart_sum = parseInt($("#heart").html().substring(6)) - 1;
            $("#heart").css('color', '');
            $("#heart").html('&nbsp;' + heart_sum);
            
          }
        }else{
          $("#login").removeClass('fade').addClass('show');
        }
      }
    });
  })

 /*
  * 提示登录框关闭
  */ 
  $("#login_close1, #login_close2").click(function(){
    $("#login").removeClass('show').addClass('fade');
  })