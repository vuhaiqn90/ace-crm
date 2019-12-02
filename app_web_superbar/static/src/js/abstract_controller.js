odoo.define('app_web_superbar.AbstractController', function (require) {
"use strict";
//调整向导的位置
var AbstractController = require('web.AbstractController');
var ajax = require('web.ajax');

AbstractController.include({
    _renderBanner: function () {
        var self=this;
        return $.when(self._super()).then(function () {
            if (self.bannerRoute !== undefined) {
                self.$el.children("div:eq(2)").prepend(self._$banner);
            }
        });

        // if (this.bannerRoute !== undefined) {
        //     var self = this;
        //     return this.dp
        //         .add(this._rpc({route: this.bannerRoute}))
        //         .then(function (response) {
        //             if (!response.html) {
        //                 self.$el.removeClass('o_has_banner');
        //                 return $.when();
        //             }
        //             self.$el.addClass('o_has_banner');
        //             var $banner = $(response.html);
        //             // we should only display one banner at a time
        //             if (self._$banner && self._$banner.remove) {
        //                 self._$banner.remove();
        //             }
        //             // Css and js are moved to <head>
        //             var defs = [];
        //             $('link[rel="stylesheet"]', $banner).each(function (i, link) {
        //                 defs.push(ajax.loadCSS(link.href));
        //                 link.remove();
        //             });
        //             $('script[type="text/javascript"]', $banner).each(function (i, js) {
        //                 defs.push(ajax.loadJS(js.src));
        //                 js.remove();
        //             });
        //             return $.when.apply($, defs).then(function () {
        //                 $banner.prependTo(self.$el.children("div:first"));
        //                 self._$banner = $banner;
        //             });
        //         });
        // }
        // return $.when();
    },

});

});
