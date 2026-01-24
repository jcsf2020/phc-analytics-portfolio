# -*- coding: utf-8 -*-
# PHC Analytics Odoo addon
#
# Minimal bootstrap module.
# Purpose:
# - Allow Odoo to detect and install the addon
# - Explicitly expose extension points (models, views, services)
# - Keep Ruff / linters clean and intentional

from . import models

__all__ = ["models"]
