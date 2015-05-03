$("input").click(function(){
    var num = $(this).val();
    if(num == '3'){
        window.location.href = '/help/';
    }else if(num == '2'){
        window.location.href = '/share/';
    }else if(num == '1'){
        window.location.href = '/bookmark/note/';
    }
});