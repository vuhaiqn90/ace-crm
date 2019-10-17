{
    "name": "Odoo Tours Cancellation",
    "version": "12.0",
    'author': 'Pragmatic Techsoft Pvt. Ltd.',
    "website": "http://www.pragtech.co.in",
    "description": """Tours Cancellation""",
    "depends": ["base", "tour_travel"],
    "category": "Generic Modules",
    "data": [
        "wizard/refund_payment_journal_entry.xml",
        "views/tour_cancellation_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    "active": False,
    'license': 'OPL-1',
}
