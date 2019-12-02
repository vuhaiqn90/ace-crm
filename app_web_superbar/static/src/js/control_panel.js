odoo.define('app_web_superbar.ControlPanel', function (require) {

    var ControlPanel = require('web.ControlPanel');
    ControlPanel.include({
        _render_breadcrumbs: function (breadcrumbs) {
            var self = this;
            var res = self._super.apply(this, arguments);
            // res = "<div class=\"a-superbar-toggle btn-group ml8\"/>" + res;
            return res;
        },
    });
})
