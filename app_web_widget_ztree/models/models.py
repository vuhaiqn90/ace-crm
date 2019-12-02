# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class BaseModelExtend(models.AbstractModel):
    _name = 'basemodel.extend'

    @api.model_cr
    def _register_hook(self):
        '''
        Register method in BaseModel
        type: bar是在superbar中，field是在form中
        '''

        @api.model
        def search_ztree(self, domain=None, context=None, parent_key=None, root_id=None, expend_level=None, limit=None, order=None, type=None):
            try:
                limit = int(limit)
            except Exception as e:
                limit = 16
            try:
                expend_level = int(expend_level)
            except Exception as e:
                expend_level = 2

            # 返回 id, name, value, pId, title, value
            def ztree(x):
                y = {}
                p = parent_key
                pid = False
                if p and x.get(p):
                    pid = x[p]
                    if pid:
                        pid = pid[0]
                y['id'] = x['id']
                # if type and type == 'bar':
                #     y['name'] = x['name']
                # else:
                #     y['name'] = x['display_name']
                if x.get('name'):
                    y['name'] = x['name']
                else:
                    y['name'] = x['display_name']

                y['value'] = x['name']
                y['title'] = x['display_name']
                y['pId'] = pid
                return y

            # 递归展开指定级别，即设定open
            def getLevel(node, nodes, level=1):
                if not node.get("pId"):
                    level = 1
                else:
                    try:
                        level = level + getLevel(nodes[node.get("pId")], nodes)
                    except Exception as e:
                        level = 1
                return level

            fields = ['id', 'name', 'display_name']
            # todo: 检查 root_id 的处理
            if parent_key:
                fields.append(parent_key)
                if root_id:
                    r = self.search_read([('id', '=', root_id)], ['parent_path'], limit=1)
                    path = r[0]['parent_path']
                    domain += [('parent_path', '=like', path + '%')]

            records = self.search_read(domain or [], fields, 0, limit=limit or False, order=order or False)

            if not records:
                return []

            result = records
            res = map(ztree, result)

            if len(result) <= 1:
                return result

            # reorder read, index: dict,  res: list
            index = {vals['id']: vals for vals in res}
            for key in index:
                index[key]["level"] = getLevel(index[key], index, 1)
                if index[key]["level"] <= expend_level:
                    index[key]["open"] = True
                else:
                    index[key]["open"] = False

            res = [index[record["id"]] for record in records if record["id"] in index]
            return res

        models.BaseModel.search_ztree = search_ztree
        return super(BaseModelExtend, self)._register_hook()
