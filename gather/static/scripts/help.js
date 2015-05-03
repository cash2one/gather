  $("#map").css('height', window.screen.availHeight - 90);
  $("#map").css('width', window.screen.availWidth);
  $(".help-search").css('margin-bottom', window.screen.availHeight * 0.7);
  $(".help-search").css('margin-left', window.screen.availWidth * 0.8);

  var map = new BMap.Map("map");

  // 进入时焦点位置；第一次进入为默认，其他为发布拜托后位置
  var init_x = parseFloat($("#init_x").val());
  var init_y = parseFloat($("#init_y").val());
  map.centerAndZoom(new BMap.Point(init_x, init_y), 15);

  window.onload = get_location;
  function get_location(){
      // 获取所有拜托的位置
      $.ajax({
          url: '/help/points/',
          type: 'GET',
          dataType: 'json',
          success: function(Data) {
              if(Data['result']){
                  var json_data = Data['points'];
                  var pointArray = new Array();
                  for(var i=0;i<json_data.length;i++){
                      var marker = new BMap.Marker(new BMap.Point(json_data[i][0], json_data[i][1])); // 创建点
                      map.addOverlay(marker);    //增加点
                      pointArray[i] = new BMap.Point(json_data[i][0], json_data[i][1]);
                      marker.addEventListener("click", show_help_info);
                  }
                  //让所有点在视野范围内
                  map.setViewport(pointArray);
              }
          }
      })
      .fail(function() {
          alert("获取地点加载失败, 请刷新");
      });
  }

  /*
   * 显示帮助详细信息
   */
  function show_help_info(e){
    var p = e.target.getPosition();
    var x = p.lng;
    var y = p.lat;
    var _data = {};
    _data['x'] = x;
    _data['y'] = y;
    $.ajax({
        url: '/help/list/',
        type: 'GET',
        dataType: 'json',
        data: _data,
        success: function(Data){
            if(Data['result']){
              if(Data['is_single']){
                $("#help_longitude").html("经度" + Data['longitude']);
                $("#help_latitude").html("维度" + Data['latitude']);
                $("#help_title").html(Data['title']);
                $("#help_content").html(Data['content']);
                $("#help_remark").html(Data['remark']);
                $("#help_connect_method").html(Data['connect_method']);
                $("#help_cancel_time").html(Data['cancel_time']);
                $("#helpModal").removeClass('fade').addClass('show');
              }else{
                var help_head = "<ul class='list-group'>";
                var help_tail = "</ul>";
                var help_body = "";
                for(var i=0;i<Data['helps'].length;i++){
                    var title =  Data['helps'][i]['title'];
                    if (title.length > 10){
                      title = title.substring(0, 10) + "...";
                    }
                    help_body = help_body + "<li class='list-group-item'>" + title + "</li>";
                }
                $("#help_body").html(help_head + help_body + help_tail);
                $("#helpModal").removeClass('fade').addClass('show');
              }
            }else{
                alert("拜托详情错误, 请刷新");
            }
        }
    });
  }

  /*
   * 放大缩小的标尺
   */ 
  var top_left_control = new BMap.ScaleControl({anchor: BMAP_ANCHOR_TOP_LEFT});// 左上角，添加比例尺
  var top_left_navigation = new BMap.NavigationControl();  //左上角，添加默认缩放平移控件
  //添加控件和比例尺
  map.addControl(top_left_control);        
  map.addControl(top_left_navigation);     

  /*
   *  添加定位控件
   */ 
  var geolocationControl = new BMap.GeolocationControl();
  map.addControl(geolocationControl);

  /*
   * 点击事件
   */
  function showInfo(e){
      $("#x").html("经度" + e.point.lng)
      $("#y").html("维度" + e.point.lat)

      $("#longitude").val(e.point.lng)
      $("#latitude").val(e.point.lat)

      $("#x_bottom").html("经度" + e.point.lng)
      $("#y_bottom").html("维度" + e.point.lat)

      $("#help_btn").removeAttr('disabled');
      $("#help_btn").html('发起拜托');
  }
  map.addEventListener("click", showInfo);

  /*
   * 地图地点搜索
   */
  // 百度地图API功能
  function G(id) {
      return document.getElementById(id);
  }

  var ac = new BMap.Autocomplete(    //建立一个自动完成的对象
      {"input" : "suggestId"
      ,"location" : map
  });

  ac.addEventListener("onhighlight", function(e) {  //鼠标放在下拉列表上的事件
  var str = "";
      var _value = e.fromitem.value;
      var value = "";
      if (e.fromitem.index > -1) {
          value = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
      }    
      str = "FromItem<br />index = " + e.fromitem.index + "<br />value = " + value;
      
      value = "";
      if (e.toitem.index > -1) {
          _value = e.toitem.value;
          value = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
      }    
      str += "<br />ToItem<br />index = " + e.toitem.index + "<br />value = " + value;
      G("searchResultPanel").innerHTML = str;
  });

  var myValue;
  ac.addEventListener("onconfirm", function(e) {    //鼠标点击下拉列表后的事件
  var _value = e.item.value;
      myValue = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
      G("searchResultPanel").innerHTML ="onconfirm<br />index = " + e.item.index + "<br />myValue = " + myValue;
      
      setPlace();
  });

  function setPlace(){
      map.clearOverlays();    //清除地图上所有覆盖物
      function myFun(){
          var pp = local.getResults().getPoi(0).point;    //获取第一个智能搜索的结果
          map.centerAndZoom(pp, 18);
          map.addOverlay(new BMap.Marker(pp));    //添加标注
      }
      var local = new BMap.LocalSearch(map, { //智能搜索
        onSearchComplete: myFun
      });
      local.search(myValue);
  }

  /* 
   * bootstrap modal 关闭按钮, 隐藏modal
   */
   $(".close_btn").click(function(){
      $(".modal").removeClass('show').addClass('fade');
   });
