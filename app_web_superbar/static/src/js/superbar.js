odoo.define('app_web_superbar.Superbar', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var SuperbarToggle = require('app_web_superbar.SuperbarToggle');
    var zTreeWrap = require('app_web_widget_ztree.zTree');
    var zTree = zTreeWrap.zTree;
    var Domain = require('web.Domain');
    var _t = core._t;
    var qweb = core.qweb;

// 显示superbar
    var Superbar = Widget.extend({
        template: 'App.Superbar',
        custom_events: {},
        events: {
            'click .panel-title': function (e) {
                $(e.target).parent().toggleClass('active');
                $(e.target).parent().next().toggleClass('collapse');
            },
            'click .a_clear_ztree': function (e) {
                var self = this;
                var index = $(e.target)[0].dataset.ztree_index;
                self.zTrees[index].$zTree.cancelSelectedNode();
                self.bar_data.children[index].attrs.ztree_selected_id = null;
                self.bar_data.children[index].attrs.ztree_selected_vals = null;
                self.search_view.bar_data = self.bar_data;
                $(e.target).addClass('o_hidden');
                if (self.search_view)
                    return self.search_view.do_search();
            },
            'click .ztree_search .o_checkbox input': function (e) {
                //每次点击要清除select
                //todo: 做个取节点函数，关键点击重算
                var self = this;
                var index = $(e.target)[0].dataset.ztree_index;

                if ($(e.target).children('input').prop('checked')) {
                    $(e.target).children('input').prop('checked', false);
                }
                else {
                    $(e.target).children('input').prop('checked', true);
                }

                self.bar_data.children[index].attrs.ztree_with_sub_node = $(e.target).prop('checked');
                var treeId = self.zTrees[index].ztree_id;
                var ids = self.setTreeSearchData(treeId, 'id', self.bar_data.children[index].attrs.ztree_with_sub_node);
                self.bar_data.children[index].attrs.ztree_selected_vals = ids;
                if (self.search_view) {
                    return self.search_view.do_search();
                }
            },
        },
        bar_domain: [],

        //bar_data: init, parent: searchview, sender: list/kanban/...
        init: function (bar_data, parent, sender) {
            this._super.apply(this, arguments);
            this.search_view = parent;
            console.log('bar data');
            console.log(bar_data);
            if (bar_data && bar_data.children && bar_data.children.length) {
                for (var key in bar_data.children) {
                    if (bar_data.children[key].tag.toLowerCase() == "field") {
                        var field = parent.fields[bar_data.children[key].attrs.name];
                        //加index，为后续引用值
                        bar_data.children[key].ztree_index = key;
                        //默认widget为 ztree_search
                        if (!parent.fields[bar_data.children[key].attrs.widget])
                            bar_data.children[key].attrs.widget = "ztree_search";
                        //默认包含子数据
                        bar_data.children[key].attrs.ztree_with_sub_node = true;
                        //增加字段类型
                        bar_data.children[key].attrs.type = field.type;
                        //增加字段名
                        bar_data.children[key].attrs.string = field.string;
                        //如果没有指定Model，则增加模型名
                        if (!parent.fields[bar_data.children[key].attrs.model])
                            bar_data.children[key].attrs.model = field.relation;
                        //如果是固定列表，selection
                        if (field.type === 'selection') {
                            bar_data.children[key].attrs.selection = field.selection;
                            bar_data.children[key].attrs.ztree_with_sub_node = false;
                        }
                        //todo: 如果没有指定parent_key，则增加父字段名
                    }
                }
            }
            this.bar_data = bar_data;
            this.zTrees = new Array();
        },
        start: function () {
            this._super.apply(this, arguments);
            var self = this;

            if (self.bar_data)
                self.buildField();

            self.renderToggle()
        },
        renderToggle: function () {
            $(".a-superbar-toggle").empty();
            if (self.SuperbarToggle)
                self.SuperbarToggle.destroy();
            setTimeout(function () {
                self.SuperbarToggle = new SuperbarToggle(this);
                self.SuperbarToggle.appendTo($(".a-superbar-toggle"));
            }, 200);
        },
        destroy: function () {
            $(".a-superbar-toggle").empty();
            if (this.SuperbarToggle)
                this.SuperbarToggle.destroy();
            this._super.apply(this, arguments);
        },
        // public
        // todo: 实现odoo search view内的当前过滤显示参考 search_view.js select_completion,
        // 主要是 search_view 中 searchquery.add 后 trigger reset, 再 render  FacetView
        // todo: 学习Backbone 实现构建query，search_menus.js 中 commit_search
        buildField: function () {
            //todo: 暂时不管domain，后续要加自动 domain
            var self = this;
            var allow_fields = ['many2one', 'many2many', 'selection'];
            var field;
            self.zTrees = [];
            var setting = {};

            self.$(".ztree_search").each(function (index, element) {
                field = self.bar_data.children[index];
                //只支持m2o,m2m,select
                if (allow_fields.indexOf(field.attrs.type) < 0)
                    return true;
                //select 处理
                var znodes = [];
                var keyName = 'id';
                if (field.attrs.selection && field.attrs.selection.length) {
                    keyName = 'title';
                    $.each(field.attrs.selection, function (index, s) {
                        znodes.push({
                            id: index,
                            name: s[1],
                            title: s[0],
                            value: s[0],
                        })
                    })
                }

                setting = {
                    callback: {
                        onClick: function (event, treeId, treeNode, clickFlag) {
                            self.$el.find(".a_clear_ztree").eq(index).removeClass('o_hidden');

                            self.bar_data.children[index].attrs.ztree_selected_id = treeNode.id;
                            var vals = self.setTreeSearchData(treeId, keyName, self.bar_data.children[index].attrs.ztree_with_sub_node);
                            self.bar_data.children[index].attrs.ztree_selected_vals = vals;
                            self.search_view.bar_data = self.bar_data;
                            if (self.search_view)
                                return self.search_view.do_search();
                        }
                    }
                };
                if (field.attrs.widget.toLowerCase() == "ztree_search") {
                    var ztree_domain = [];
                    // 处理 search_superbar_domain，形如： {group_id: "[('root_sale', '=', 72)]"}
                    var domain_str = '';
                    if (self.bar_data.search_superbar_domain)
                        $.each(self.bar_data.search_superbar_domain, function (key, value) {
                            if (key === field.attrs.name) {
                                domain_str = value;
                                return false;
                            }
                        })
                    if (field.attrs.domain)
                        domain_str += field.attrs.domain;
                    domain_str = domain_str.replace('][',',');

                    if (domain_str && domain_str.length)
                        ztree_domain= Domain.prototype.stringToArray(domain_str);

                    var ztree_context = field.attrs.context;
                    var $ztree = new zTree(
                        setting,
                        {
                            zNodes: znodes,
                            ztree_model: field.attrs.model,
                            limit: field.attrs.limit,
                            ztree_field: field.attrs.name,
                            ztree_parent_key: field.attrs.parent_key,
                            ztree_root_id: field.attrs.root_id,
                            ztree_domain: ztree_domain,
                            ztree_context: eval('(' + field.attrs.context +')'),
                            ztree_expend_level: field.attrs.level,
                            ztree_selected_id: field.attrs.ztree_selected_id,
                            ztree_with_sub_node: field.attrs.ztree_with_sub_node,
                            ztree_index: index,
                            ztree_type: 'bar',
                        }
                    )
                    self.zTrees[index] = $ztree;
                    $ztree.appendTo(element);
                }
            })
        },
        getChildNodes: function getChildNodes(treeId, treeNode) {
            //得到下级 node id数组
            var $tree = $.fn.zTree.getZTreeObj(treeId);
            var childNodes = $tree.transformToArray(treeNode);
            var nodes = new Array();
            var i;
            for (i = 0; i < childNodes.length; i++) {
                nodes[i] = childNodes[i].id;
            }
            return nodes;
        },
        setTreeSearchData: function getChildNodes(treeId, keyName, withChild) {
            var self = this;
            var $tree = $.fn.zTree.getZTreeObj(treeId);
            var vals = [];
            var children;
            $.each($tree.getSelectedNodes(), function (i, node) {
                if (withChild)
                //注意，取每一个选中节点的所有子节点，只有m2o有child，故此处只处理id即可
                    children = self.getChildNodes(treeId, node);
                else
                    children = node[keyName];
                vals = vals.concat(children);
            });

            return vals;
        }

    });

    return Superbar;
});
