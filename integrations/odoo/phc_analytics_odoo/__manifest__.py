# -*- coding: utf-8 -*-
# pyright: reportUnusedExpression=false
{
    "name": "PHC Analytics Integration",
    "version": "1.0.0",
    "summary": "PrestaShop ↔ Odoo integration with analytics-ready data pipeline",
    "description": """
PHC Analytics Odoo Module

- Installs cleanly in Odoo
- Acts as the integration anchor for PrestaShop sync
- Prepared for future extensions (models, services, scheduled jobs)
- Designed for analytics and BI consumption downstream
""",
    "author": "João Fonseca",
    "website": "https://github.com/jcsf2020/phc-analytics-portfolio",
    "license": "LGPL-3",
    "category": "Tools",
    "depends": [
        "base",
    ],
    "data": [
        # XML / CSV files go here when UI or models are added
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
