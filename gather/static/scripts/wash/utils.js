/**
 * Created by huangzhongjian on 15/7/4.
 */


(function () {
    var WL = window.WL = window.WL || {};

    var utils = WL.utils = WL.utils || {};

    utils.dateFormat = function (date, fmt) { //author: meizz
        var o = {
            "M+": date.getMonth() + 1, //月份
            "d+": date.getDate(), //日
            "h+": date.getHours(), //小时
            "m+": date.getMinutes(), //分
            "s+": date.getSeconds(), //秒
            "q+": Math.floor((date.getMonth() + 3) / 3), //季度
            "S" : date.getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    };

    utils.getUrlParam = function (key) {
        var re = new RegExp('[?|&]' + key + '=(.*?)(&|#|$)', 'i'),
            r = this.urlParam().match(re);
        return r && decodeURIComponent(r[1]) || null;
    };


    utils.urlParam = function () {
        return location.href.indexOf('#!') === -1 ? location.search : (location.hash.split('?').length <= 1 ? '' : ('?' + location.hash.split('?')[1]));
    };

})();