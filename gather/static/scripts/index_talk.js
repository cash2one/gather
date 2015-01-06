$(".note-a").click(function(){
    note_id = $(this).attr("value");
    title = $(this).attr("name");
    $("#myModalLabel").html(title).show();
    $("#myModalLabel").attr("name", note_id);
    _data = {};
    _data['note_id'] = note_id;
    $.ajax({
        type: 'post',
        dataType: "json",
        url: '/comment/list/',
        data: _data,
        success: function(Data) {
          comment_html = '';
          for(i=0;i<Data.length;i++){
            comment_html = comment_html + "<div class='row note_comment'><div class='col-sm-note-1'><img src='/static/images/regist.jpg' alt='140*140' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" + Data[i]['created'] + "&nbsp;&nbsp;<a href=''>" + Data[i]['username'] +"</a></label><label class='text-right reply'><a href=''>#</a></label></div><p class='note-comment'>" + Data[i]['comment'] + "</p></div></div>"
          }
          $("#comment-body").html(comment_html).show();
        }
    });
  });

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
        comment_html = "<div class='row note_comment'><div class='col-sm-note-1'><img src='/static/images/regist.jpg' alt='140*140' style='width:40px;height:40px' class='img-rounded'/></div><div class='col-sm-note-11'><div class='note-info'><label class='pubtime'>" + Data['created'] + "&nbsp;&nbsp;<a href=''>" + Data['username'] +"</a></label><label class='text-right reply'><a href=''>#</a></label></div><p class='note-comment'>" + Data['comment'] + "</p></div></div>"
        $("#comment-body").html($("#comment-body").html() + comment_html).show();
      }
    });
  });