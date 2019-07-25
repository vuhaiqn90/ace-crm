odoo.define('ace_crm_caresoft.embed_frame', function (require) {
"use strict";

var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

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
	    // $('.o_control_panel').hide();
        var self = this;
        this.$main_dashboard = QWeb.render( 'ace_crm_caresoft.embed_frame', {
            widget: self,
        });
        this.$el.append(this.$main_dashboard);
        $('.caresoft_embed_frame').parent().css('width', '100%');
    },
    reload: function () {
            window.location.href = this.href;
    },

});
core.action_registry.add('ace_crm_caresoft.embed_frame', CaresoftEmbedView);
return CaresoftEmbedView
});