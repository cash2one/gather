/*
 * 回复评论
 */
 function answer_comment(obj){
    var comment_obj = $(obj).parent().parent().find('a.commenter').first();
    var placeholder = "回复" + comment_obj.html() + ":";
    $("#comment_content").attr('placeholder', placeholder);
    $("#say").attr("name", "answer:" + $(obj).attr('name'));
    $("#comment_content").focus();
 }

/*
 * 显示评论
 */
 function show_comments(){
    _data = {};
    _data['note_id'] = $(".note-a").attr("value");
    $.ajax({
        type: 'post',
        dataType: "json",
        url: '/comment/list/',
        data: _data,
        success: function(Data) {
          comment_html = '';
          reply_html = '';
          $("#read_sum").html(Data['read_sum']).show();
          $("#heart").attr('value', Data['id']);
          $("#heart").html("&nbsp;" + Data['heart']).show();
          if(parseInt(Data['heart']) > 0){
            $("#heart").css('color', 'red');
          }else{
            $("#heart").css('color', '');
          }
          $("#note_url").attr("src", Data['url']);
          $("#note_created").html(Data['created']).show();
          $("#myModalLabel").html(Data['title']).show();
          $("#myModalLabel").attr("name", Data['id']);
          for(var i=0;i<Data['comments'].length;i++){
              for(var a=0;a<Data['comments'][i]['replys'].length;a++){
                var reply = Data['comments'][i]['replys'][a];
                reply_html = reply_html + "<div style='border-top:1px solid #eee;margin-bottom:5px;'><div class='row top5'><div class='col-sm-note-1'><img src='" +
                reply['url'] + "' alt='-_-' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><label class='reply'>" + 
                reply['comment'] + "</label><br><label class='reply-pubtime'>" + 
                reply['created'] + "&nbsp;&nbsp;<a href='javascript:;' class='commenter'>413761980@qq.com</a></label><label class='text-right reply'><a href='javascript:;' name=" +
                Data['comments'][i]['id'] + " onclick='answer_comment(this)'>&nbsp;回复</a></label></div></div></div>";
              }
              comment_html = comment_html + "<div class='row note_comment'><div class='col-sm-note-1'><img src='" +
                Data['comments'][i]['url'] + "' alt='-_-' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" +
                Data['comments'][i]['created'] + "&nbsp;&nbsp;<a href='javascript:;' class='commenter'>" + 
                Data['comments'][i]['username'] +"</a></label><label class='text-right reply'><a href='javascript:;' name='"+ 
                Data['comments'][i]['id'] +"' onclick='answer_comment(this)'>回复</a></label></div><p class='note-comment'>" + 
                Data['comments'][i]['comment'] + "</p>" + reply_html + "</div></div>";
              reply_html = '';
          }
          $("#comment-body").html(comment_html).show();
        }
      });
     $("#comment_content").val("");
     $("#say").attr("name", "comment:" + _data['note_id']);
 }

/*
 * ajax请求显示评论
 */
  $(".note-a").click(function(){
    //点击时间后显示评论
    show_comments();
  });

  /*
   * 发表评论
   */
  $("#say").click(function(){
    var say_name = $(this).attr("name").split(':');
    var comment_type = say_name[0];
    // 回复评论获取评论id, 发表评论获取标题id, id保存在say得name中
    note_id = say_name[1];
    comment = $("#comment_content").val();
    _data = {};
    _data['note_id'] = note_id;
    _data['comment'] = comment;
    $.ajax({
      type: 'post',
      dataType: "json",
      url: '/comment/add/',
      data: _data,
      success: function(Data) {
        if(comment_type == 'comment'){
          if(Data){
            comment_html = "<div class='row note_comment'><div class='col-sm-note-1'><img src='" + 
            Data['url'] + "' alt='140*140' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" + 
            Data['created'] + "&nbsp;&nbsp;<a href='javascript:;'' class='commenter'>" + 
            Data['username'] +"</a></label><label class='text-right reply'><a href='javascript:;' name='" + 
            Data['id'] + "' onclick='answer_comment(this)'>回复</a></label></div><p class='note-comment'>" + 
            Data['comment'] + "</p></div></div>";
            $("#comment-body").html($("#comment-body").html() + comment_html).show();
          }else{
            $("#myModal").css("display", "none");
            $("#login").removeClass('fade').addClass('show');
          }
        }else{
          // 回复评论后刷新评论
          $("#comment-body").html('').show();
          show_comments();
        }
      }
    });
     $("#comment_content").val("");
     // 重置name为node_id
     $("#say").attr("name", "comment:" + $("#myModalLabel").attr("name"));
     $("#say").attr('placeholder', '');
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
          $("#myModal").css("display", "none");
          $("#login").removeClass('fade').addClass('show');
        }
      }
    });
  });

 /*
  * 提示登录框关闭
  */

  $("#login_close1, #login_close2").click(function(){    
    $("#login").removeClass('show').addClass('fade');
  });

