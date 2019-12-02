# -*- coding: utf-8 -*-
import logging
import os

from lxml import etree

from odoo import api, models, tools, SUPERUSER_ID
from odoo.tools import view_validation
from odoo.tools.view_validation import _relaxng_cache

_logger = logging.getLogger(__name__)

def relaxng_app(view_type):
    """ Return a validator for the given view type, or None. """
    ADDONS_PATH = tools.config['addons_path']
    if view_type not in _relaxng_cache:
        # 先判断 search 和 tree
        if (view_type == 'search'):
            folder = 'app_web_superbar'
        elif (view_type == 'tree'):
            folder = 'app_web_tree_bgcolor'
        else:
            folder = 'base'
        _file = '%s/rng/%s_view.rng' % (folder, view_type)
        _logger.info("superbar rng file: %s" % _file)
        try:
            with tools.file_open(_file) as frng:
                try:
                    relaxng_doc = etree.parse(frng)
                    _relaxng_cache[view_type] = etree.RelaxNG(relaxng_doc)
                except Exception:
                    _logger.exception('%s Failed to load RelaxNG XML schema for views validation' % _file)
                    _relaxng_cache[view_type] = None
        except Exception:
            # 出错时到base找
            _file = 'base/rng/%s_view.rng' % (view_type)
            with tools.file_open(os.path.join(_file)) as frng:
                try:
                    relaxng_doc = etree.parse(frng)
                    _relaxng_cache[view_type] = etree.RelaxNG(relaxng_doc)
                except Exception:
                    _logger.exception('%s Failed to load RelaxNG XML schema for views validation' % _file)
                    _relaxng_cache[view_type] = None
    return _relaxng_cache[view_type]



class View(models.Model):
    _inherit = 'ir.ui.view'

    def __init__(self, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)
        view_validation.relaxng = relaxng_app
