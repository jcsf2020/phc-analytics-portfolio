## Repository Structure (high level)

- `sql/` — SQL bootstrap and migrations
- `src/` — pipeline code (connectors, ingestion, transformations)
- `docker/` — local services
- `docker-compose*.yml` — reproducible environments
- `docs/` — architecture notes and runbooks

---

## Integrations

### Odoo ERP Integration (Addon)

This repository includes a dockerized **Odoo addon** provided as an example of
**ERP integration and deliverable packaging**.

The integration is intentionally **isolated from the core data pipeline**
to demonstrate good engineering practice:

- clear separation between analytics core and external systems
- reproducible integration via Docker Compose
- versioned source code, without committing binary release artifacts

Location in repository:

- `integrations/odoo/phc_analytics_odoo/` — Odoo addon source
- `integrations/odoo/docker-compose.odoo.yml` — reproducible Odoo environment

This integration is not required to run the analytics pipeline itself;
it exists to showcase real-world platform integration and delivery discipline.

---

## Local Run (Docker Compose)

### Start PostgreSQL locally

```bash
docker compose up -d db
```

---
