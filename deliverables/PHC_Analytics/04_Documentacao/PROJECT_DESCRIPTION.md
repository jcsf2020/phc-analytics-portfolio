# PHC Analytics — Data Engineering & BI Project

## Project Summary
End-to-end data analytics project designed to simulate a real-world ERP analytics scenario.
The project covers data modeling, KPI generation and interactive dashboards, following
best practices in data engineering and business intelligence.

All data used is mock/synthetic and the project is fully reproducible.

---

## Architecture Overview
The solution follows a layered approach:

- Data Generation: Python + Pandas (mock ERP data)
- Data Modeling: Star schema (facts and dimensions)
- Analytics Layer: KPI computation and aggregations
- Presentation Layer: Streamlit dashboard

---

## Data Model
Star schema composed of:

Fact table:
- fact_venda — sales transactions

Dimension tables:
- dim_cliente
- dim_artigo
- dim_vendedor
- dim_tempo

This structure allows scalable analytical queries and mirrors
typical enterprise data warehouse designs.

---

## KPIs Implemented
- Monthly revenue
- Monthly margin (%)
- Average ticket
- Top customers by revenue
- Inactive customers (no activity > 180 days)
- Top products by revenue
- Top products by margin

All KPIs are exported as CSV and consumed by the dashboard layer.

---

## Dashboard
Interactive Streamlit application with three main views:

- Overview — global business KPIs
- Customers — customer performance and inactivity
- Products — sales and margin analysis

The dashboard is designed to be easily connected to real databases
in future iterations.

---

## Tech Stack
- Python
- Pandas
- Streamlit
- Jupyter Notebook
- Git

---

## Portfolio Goals
This project demonstrates practical skills in:

- Data modeling (star schema)
- Analytical thinking and KPI design
- Data pipeline structuring
- Dashboard development
- Reproducible data engineering workflows