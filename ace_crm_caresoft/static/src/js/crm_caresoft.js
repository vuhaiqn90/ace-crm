odoo.define('ace_crm_caresoft.embed_frame', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;


    var CaresoftEmbedView = AbstractAction.extend(ControlPanelMixin, {
        events: {
        },
        init: function(parent, context) {
            this._super(parent, context);
        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            return this._super().then(function() {
                self.render();
            });
        },
        render: function() {
            var self = this;
            this.$main_dashboard = QWeb.render( 'ace_crm_caresoft.embed_frame', {
                widget: self,
            });
            this.$el.append(this.$main_dashboard);

            setTimeout(
                function()
                {
                    $( ".o_control_panel" ).addClass( "o_hidden" );
                    $('.caresoft_embed_frame').height($('.o_content').height()-10);
                }, 500);
        },
        reload: function () {
            window.location.href = this.href;
        },

    });
    core.action_registry.add('ace_crm_caresoft.embed_frame', CaresoftEmbedView);
    return CaresoftEmbedView
});