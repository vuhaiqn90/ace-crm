odoo.define('app_web_superbar.SearchView', function (require) {
    "use strict";

    var SearchView = require('web.SearchView');
    var ControlPanel = require('web.ControlPanel');
    var Superbar = require('app_web_superbar.Superbar');
    var ListRenderer = require('web.ListRenderer');
    var KanbanRenderer = require('web.KanbanRenderer');
    var PivotRenderer = require('web.PivotRenderer');
    var GraphRenderer = require('web.GraphRenderer');
    var FormRenderer = require('web.FormRenderer');
    var CalendarRenderer = require('web.CalendarRenderer');
    var ActionManager = require('web.ActionManager');
    var data = require('web.data');
    var cur_sender;
    var last_sender;
    var cur_search;
    var last_search_view_id;
    var last_view_id;
    var last_view_type;
    var need_render;

    SearchView.include({
        init: function () {
            this._super.apply(this, arguments)
            var self = this;
            self.$superbar = undefined;
            //默认位置改为左边
            self.ztree_position = 'left';
            //代码设置 superbar domain
            var search_superbar_domain = {};
            _.each(self.dataset.context, function (value_, key) {
                var match = /^search_superbar_domain_(.*)$/.exec(key);
                if (match) {
                    search_superbar_domain[match[1]] = value_;
                }
            });

            var bar_data = this._prepare_bar_data();
            if (search_superbar_domain && JSON.stringify(search_superbar_domain) !== '{}')
                try {
                bar_data['search_superbar_domain'] = search_superbar_domain;
                } catch(e) {
                    ;
                }
            self.bar_data = bar_data;

            console.log('search data');
            console.log(self.bar_data);
        },
        start: function () {
            var self = this;
            cur_search = self;
            return $.when(self._super()).then(function () {
                need_render = true;
                if (cur_search && cur_search.$superbar)
                    try {
                        cur_search.$superbar.destroy();
                    } catch (e) {
                        cur_search.$superbar = null;
                        cur_search = null;
                        ;
                    }
                try {
                    last_search_view_id = self.action.search_view_id[0];
                } catch (e) {
                    last_search_view_id = null;
                }
                try {
                    last_view_type = self.action.views[0].type;
                } catch (e) {
                    last_view_type = null;
                }
            });
        },
        destroy: function () {
            if (this.$superbar)
                this.$superbar.destroy();
            this.$superbar = undefined;
            this._super.apply(this, arguments);
        },
        //扩展domain加上ztree等
        build_search_data: function () {
            data = this._super.apply(this, arguments);
            var bar_domain = [];
            if (this.$superbar && this.$superbar.bar_data && this.$superbar.bar_data.children.length) {
                $.each(this.$superbar.bar_data.children, function (i, field) {
                    if (field.attrs && field.attrs.ztree_selected_vals && field.tag.toLowerCase() == 'field') {
                        var vals = field.attrs.ztree_selected_vals;
                        //在odoo12里，可以用 child_of了，但是 odoo11有些问题，故全部用 in
                        bar_domain.push([field.attrs.name, 'in', vals]);
                    }
                });
                if (bar_domain.length)
                    data.domains.push(bar_domain);
            }
            return data;
        },
        renderSuperbar: function (sender) {
            var self = this;
            //不在主视图
            //如果视图不变，不处理
            if (sender==last_sender)
                need_render = false;
            last_sender = sender;
            if (!need_render)
                return false;
            //todo: 这里要再调试
            try {
                if (!sender.getParent().$el.hasClass('o_view_controller'))
                    return false;
            } catch (e) {
                ;
            }
            //one2many many2many 不显示
            // if (sender.getParent().$el.hasClass('o_field_one2many') || sender.getParent().$el.hasClass('o_field_many2many'))
            //     return false;

            //需要render就清理
            //没有数据就清理
            //如果不在允许的view_mode，不处理，默认只有 list, kanban
            if (!need_render || !self.bar_data || !self.bar_data.attrs.view_mode) {
                if (self.$superbar)
                    self.$superbar.destroy();
                return false;
            }
            var views = self.bar_data.attrs.view_mode.split(',');
            var viewTag = sender.arch.tag;
            //o的list要改为tree
            if (views.indexOf(viewTag) < 0)  {
                if (self.$superbar)
                    self.$superbar.destroy();
                return false;
            }
            if (self.$superbar)
                self.$superbar.destroy();
            //一旦viewType换了，处理渲染
            need_render = false;
            self.$superbar = new Superbar(self.bar_data, this, sender);
            //todo: 当popup时，位置不同
            self.$superbar.appendTo(sender.getParent().$el);
            if (self.bar_data.attrs.position)
                self.ztree_position = self.bar_data.attrs.position;
            sender.getParent().$el.css('display', 'flex');
            //只有当不是pivot时
            if (viewTag != 'pivot')
                sender.getParent().$el.children('div:first').css('flex', '1');
            if (self.ztree_position && self.ztree_position.toLowerCase() == 'right') {
                self.$superbar.$el.css('order', '2');
            } else {
                self.$superbar.$el.css('order', '-2');
                sender.getParent().$el.children('div:last').css('border-left', '0');
            }
        },
        _renderView: function () {
            this._super.apply(this, arguments)
        },
        _prepare_bar_data: function () {
            var arch = this.fields_view.arch;
            var res = null;
            if (arch.children && arch.children.length > 0)
                _.each(arch.children, function (item) {
                    if (item.tag.toLowerCase() == 'superbar') {
                        res = item;
                        if (res && res.children && res.children.length) {
                            //处理 invisible，包括 groups权限
                            for (var key in res.children) {
                                if (res.children[key].attrs.invisible)
                                    delete res.children.splice(key,1);
                                }
                        }
                        return false;
                    }
                });
            return res;
        }
    });

    KanbanRenderer.include({
        _renderView: function () {
            var result = this._super.apply(this, arguments);
            cur_sender = this;
            return result;
        }
    });

    ListRenderer.include({
        _renderView: function () {
            var result = this._super.apply(this, arguments);
            cur_sender = this;
            if (cur_search) {
                this.$('.table-responsive').css("overflow-x", "auto");
                //这里加条件，如果是 search_more 的弹出窗口才渲染 superbar，其它情况的 list由 ControlPanel 处理
                try {
                    var pop = cur_sender.getParent().getParent().getParent().$el;
                    if (pop.hasClass('o_field_many2one') || pop.hasClass('o_field_many2many'))
                        cur_search.renderSuperbar(this);
                } catch (e) {
                    ;
                }
            }
            return result;
        },
    });

    PivotRenderer.include({
        _render: function () {
            var result = this._super.apply(this, arguments);
            cur_sender = this;
            return result;
        },
    });

    GraphRenderer.include({
        _render: function () {
            var result = this._super.apply(this, arguments);
            cur_sender = this;
            return result;
        },
    });

    // FormRenderer.include({
    //     _renderView: function () {
    //         var result = this._super.apply(this, arguments);
    //         cur_sender = this;
    //         return result;
    //     }
    // });

    // CalendarRenderer.include({
    //     _renderView: function () {
    //         var result = this._super.apply(this, arguments);
    //         cur_sender = this;
    //         return result;
    //     }
    // });

    //在control_panel.js 中的_update_search_view处理，当无 isHidden 时重新渲染
    ControlPanel.include({
        _update_search_view: function (searchview, isHidden, groupable, enableTimeRangeMenu) {
            var self = this;
            need_render = true;
            if (!isHidden && searchview)
                searchview.renderSuperbar(cur_sender);

            this._super.apply(this, arguments);
        },
    });
    //odoo 12中没有viewManager,用此代替： action_manager_act_window.js  _onSwitchView
    //优化停用
    // ActionManager.include({
    //     _onSwitchView: function (ev) {
    //         //主要是给 need_render 赋值，判断是否需要重置，如果view换了，包括 viewtype 也换了，就要重新赋值
    //         need_render = true;
    //         var self = this;
    //         var act, view_id;
    //         try {
    //             for (act in self.actions) {
    //                 view_id = self.actions[act].view_id[0];
    //                 if (view_id)
    //                     break;
    //             }
    //         }   catch(e) {
    //             view_id = null;
    //         }
    //         if (view_id == last_view_id)
    //             need_render = false;
    //         else {
    //             need_render = true;
    //         }
    //         try {
    //             last_view_id = view_id;
    //         }   catch (e) {
    //             last_view_id = null;
    //         }
    //         try {
    //             last_search_view_id = search_view_id;
    //         }   catch (e) {
    //             last_search_view_id = null;
    //         }
    //         try {
    //             last_view_type = ev.data.view_type;
    //         }   catch (e) {
    //             last_view_type = null;
    //         }
    //         self._super.apply(this, arguments);
    //     },
    // });

});


