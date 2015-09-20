/**
 * Created by huangzhongjian on 15/7/27.
 */


(function(){
    window.WL = WL || {};
    WL.utils = WL.utils || {};

    WL.utils.tips = function(text, showFooter){
        var str = '<div class="am-modal am-modal-alert" tabindex="-1" id="my-alert">'
         + '<div class="am-modal-dialog">'
         + '<div class="am-modal-bd">'
         +  text
         + '</div>';
        if(showFooter !== false){
            str += '<div class="am-modal-footer">'
            + '<span class="am-modal-btn">确定</span></div></div></div>';
        }
        var $elem = $(str).appendTo('body');
        $elem.modal();
    }
})();