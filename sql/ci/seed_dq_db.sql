-- Seed database for CI Data Quality checks (self-contained).
-- Goal: create minimal schemas/tables + minimal rows so DQ checks can run deterministically.

begin;

-- Schemas used by the project
create schema if not exists analytics;

-- 1) dim_customer (minimal subset of columns required by DQ checks)
create table if not exists analytics.dim_customer (
  customer_sk   bigserial primary key,
  customer_nk   text not null,
  is_current    boolean not null default true,
  valid_from    timestamptz not null default now(),
  valid_to      timestamptz null
);

-- Ensure uniqueness for current record per NK (matches SCD2 intent)
create unique index if not exists uq_dim_customer_current_nk
on analytics.dim_customer (btrim(customer_nk))
where is_current = true;

-- 2) fact_orders (columns used by FK check)
create table if not exists analytics.fact_orders (
  order_id     text not null,
  customer_id  text null,
  order_date   timestamp null,
  total_paid   numeric null,
  order_state  text null,
  source       text null
);

-- 3) dim_date (based on the real schema you inspected)
create table if not exists analytics.dim_date (
  date_id          date primary key,
  date_key         integer not null,
  year             smallint not null,
  quarter          smallint not null,
  month            smallint not null,
  day              smallint not null,
  iso_year         smallint not null,
  iso_week         smallint not null,
  day_of_week      smallint not null,
  month_name       text not null,
  day_name         text not null,
  is_weekend       boolean not null,
  is_month_start   boolean not null,
  is_month_end     boolean not null,
  is_quarter_start boolean not null,
  is_quarter_end   boolean not null,
  is_year_start    boolean not null,
  is_year_end      boolean not null
);

-- Minimal deterministic data (enough to PASS your current DQ rules)

-- dim_customer: include one current customer NK
insert into analytics.dim_customer (customer_nk, is_current, valid_from, valid_to)
values ('42', true, now(), null)
on conflict do nothing;

-- fact_orders: reference an existing customer NK and avoid invalid empty strings
insert into analytics.fact_orders (order_id, customer_id, order_date, total_paid, order_state, source)
values ('1001', '42', '2024-01-15 10:32:00', 129.90, 'paid', 'prestashop')
on conflict do nothing;

-- dim_date: include one date row, unique and not null (aligned with your schema)
insert into analytics.dim_date (
  date_id, date_key, year, quarter, month, day, iso_year, iso_week, day_of_week,
  month_name, day_name, is_weekend,
  is_month_start, is_month_end, is_quarter_start, is_quarter_end, is_year_start, is_year_end
) values (
  date '2024-01-15', 20240115, 2024, 1, 1, 15, 2024, 3, 1,
  'January', 'Monday', false,
  false, false, false, false, false, false
)
on conflict do nothing;

commit;
