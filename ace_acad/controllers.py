# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.tools import html2plaintext
from odoo.addons.website_event.controllers.main import WebsiteEventController

class AcadControlelr(WebsiteEventController):
    @http.route([
                    '''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/registration/confirm'''],
                type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        Attendees = request.env['event.registration']
        registrations = self._process_registration_details(post)

        for registration in registrations:
            registration['event_id'] = event
            Attendees += Attendees.sudo().create(
                Attendees._prepare_attendee_values(registration))

        urls = event._get_event_resource_urls(Attendees.ids)
        return request.render("website_event.registration_complete", {
            'attendees': Attendees.sudo(),
            'event': event,
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url')
        })