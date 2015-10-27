
    $("#verify_code").click(function(){
        $(".alert").css("display", "none");
        $("#send_err").css("display", "none");
        var phone = $("#id_phone").val();
        if(isNaN(phone) || phone.length != 11){
            $("#send_err").html("手机号码格式错误");
            $("#send_err").css("display", "block");
        }else{
            var code = $("#code").val();
            $.ajax({
                type: 'get',
                dataType: "json",
                url: "/wash/check_code/",
                data: {'code': code},
                success: function(Data) {
                    if(Data){
                        $("#verify_code").addClass("disabled");
                        $("#verify_code").html("发送中,请稍等...");
                        $.ajax({
                            type: 'post',
                            dataType: "json",
                            url: "/wash/verify/",
                            data: {'phone': phone},
                            success: function(data) {
                                if(data['result']){
                                    $("#send_succ").css("display", "block");
                                    countDown(60);
                                    if(data['msg'] == 'login'){
                                        location.href = '/wash/';
                                    }
                                }else{
                                    $("#send_err").html(data['msg']);
                                    $("#send_err").css("display", "block");
                                }
                            },
                            error: function(){
                                $("#send_err").css("display", "block");
                            }
                        });
                    }else{
                        $("#send_err").html('图片验证码错误');
                        $("#send_err").css("display", "block");
                    }
                },
            });
        }
    });

    function changeVcode() {
        document.getElementById('valiCode').src = "/wash/code/" + '?randomNum=' + Math.random() * 1000;
    }

    function countDown(seconds) {
        var txt = ((seconds < 10) ? "0" + seconds : seconds);
        $("#verify_code").html(txt + "秒后重新获取").addClass('disabled').attr('disabled', true);
        timeId = setTimeout(function() {
            countDown(seconds);
        }, 1000);
        if (seconds < 1) {
            clearTimeout(timeId);
            $('#verify_code').text('重新获取验证码').removeClass('disabled').attr('disabled', false);
        }
        seconds = seconds - 1;
    }


