odoo.define('app_web_superbar.SuperbarToggle', function (require) {
    "use strict";

    var Widget = require('web.Widget');

    var SuperbarToggle = Widget.extend({
        template: 'App.SuperbarToggle',
        events: {
            'click button': function (event) {
                this.toggle_superbar();
                if ($('.a-superbar').hasClass('o_hidden')) {
                    this.$("button").removeClass('active');
                    this.$("button").removeClass('fa-chevron-down');
                    this.$("button").addClass('fa-chevron-right');
                } else {
                    this.$("button").addClass('active');
                    this.$("button").addClass('fa-chevron-down');
                    this.$("button").removeClass('fa-chevron-right');
                }
            },
        },
        init: function (sender) {
            this._super.apply(this, arguments);
        },
        willStart: function () {
            var def = function(){
                $(".a-superbar-toggle").empty();
            };
            return $.when(this._super.apply(this, arguments), def);
        },
        toggle_superbar: function () {
            $('.a-superbar').toggleClass('o_hidden');
        },
        destroy: function () {
            this.$el.empty();
        },
    });

    // core.action_registry.add('app_web_superbar.SuperbarToggle', SuperbarToggle);
    return SuperbarToggle;
});

