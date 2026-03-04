CREATE TABLE IF NOT EXISTS sales_daily (
date date NOT NULL,
region text NOT NULL,
category text NOT NULL,
revenue numeric(12,2) NOT NULL,
orders integer NOT NULL,
created_at timestamptz NOT NULL DEFAULT now(),
PRIMARY KEY (date, region, category)
);