import sys, json
import xml.etree.ElementTree as ET
from src.phc_analytics.transformations import prestashop_normalize as n

KEY = "76ALF2PZ4Z2TKIIHCWL43SRJC63329Z1"
BASE = "https://teste234.pcbyte.pt/api"

def fetch(path):
    import subprocess
    cmd = ["curl","-sS","-u",f"{KEY}:", f"{BASE}{path}"]
    return subprocess.check_output(cmd, text=True)

def parse_one(root, path):
    node = root.find(path)
    return node

def txt(node, tag):
    el = node.find("./" + tag) if node is not None else None
    return (el.text or "").strip() if el is not None and el.text else None

def txt_i18n(parent, tag):
    el = parent.find("./" + tag)
    if el is None:
        return None
    # i18n: <name><language id="1">...</language></name>
    lang = el.find("./language")
    if lang is not None and lang.text:
        return lang.text.strip()
    return (el.text or "").strip() if el.text else None

# 1) Customers
xml = fetch("/customers?display=full&limit=1")
root = ET.fromstring(xml)
c = root.find(".//customer")
raw_customers = {"customers":[{"id":txt(c,"id"),"email":txt(c,"email"),"firstname":txt(c,"firstname"),"lastname":txt(c,"lastname"),"active":txt(c,"active"),"date_add":txt(c,"date_add"),"date_upd":txt(c,"date_upd")}]}
out_customers = n.normalize_customers(raw_customers)

# 2) Products
xml = fetch("/products?display=full&limit=1")
root = ET.fromstring(xml)
p = root.find(".//product")
raw_products = {"products":[{"id":txt(p,"id"),"reference":txt(p,"reference"),"name":txt_i18n(p,"name"),"active":txt(p,"active"),"price":txt(p,"price"),"date_add":txt(p,"date_add"),"date_upd":txt(p,"date_upd")}]}
out_products = n.normalize_products(raw_products)

# 3) Orders + Lines
xml = fetch("/orders?display=full&limit=1&sort=%5Bid_DESC%5D")
root = ET.fromstring(xml)
o = root.find(".//order")
raw_orders = {"orders":[{"id":txt(o,"id"),"id_customer":txt(o,"id_customer"),"current_state":txt(o,"current_state"),"total_paid":txt(o,"total_paid"),"date_add":txt(o,"date_add"),"date_upd":txt(o,"date_upd")}]}
out_orders = n.normalize_orders(raw_orders)

rows = []
for r in root.findall(".//order/associations/order_rows/order_row"):
    rows.append({"product_id":txt(r,"product_id"),"product_quantity":txt(r,"product_quantity"),"unit_price_tax_excl":txt(r,"unit_price_tax_excl") or txt(r,"product_price")})
raw_lines = {"orders":[{"id":txt(o,"id"),"associations":{"order_rows":rows}}]}
out_lines = n.normalize_order_lines(raw_lines)

print("CUSTOMERS:", json.dumps(out_customers, ensure_ascii=False, indent=2))
print("PRODUCTS:", json.dumps(out_products, ensure_ascii=False, indent=2))
print("ORDERS:", json.dumps(out_orders, ensure_ascii=False, indent=2))
print("ORDER_LINES:", json.dumps(out_lines, ensure_ascii=False, indent=2))
