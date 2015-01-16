 $("#big").change(function(){
    photo_name = $(this).val();
    if(photo_name.indexOf("png")||photo_name.indexOf("jpg")||photo_name.indexOf("jpeg")){
      $("#upload_form").submit();
    }else{
      alert("请上传png,jpg,jpeg格式的图片");
    }
  });

  $("#upload").click(function(){
    var top = $(".jcrop-holder div").css("top");
    var left = $(".jcrop-holder div").css("left");
    var width = $(".jcrop-holder div").css("width");
    var height = $(".jcrop-holder div").css("height");
    var crop = top + ":" + left + ":" + width + ":" + height;
    $("#crop").val(crop);
    $("#upload_form").submit();
  });