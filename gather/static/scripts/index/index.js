// 通过h2的value跳转
$("h2").click(function(){
    var name = $(this).attr("value");
    if(name == 'mood'){
        window.location.href = '/bookmark/note/';
    }else if(name == 'share'){
        window.location.href = '/share/';
    }else if(name == 'help'){
        window.location.href = '/help/';
    }else if(name == 'chat'){
        window.location.href = '/chat';
    }
});