-- Canonical schema for CUBRID benchmarks
-- Tables: kv, orders, order_items (per BENCHMARK_PLAN.md)

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS kv;

CREATE TABLE kv (
    id       INT PRIMARY KEY,
    k        VARCHAR(64) NOT NULL UNIQUE,
    v        VARCHAR(255) NOT NULL,
    pad      VARCHAR(512)
);

CREATE TABLE orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    total      DECIMAL(10,2) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_created_at ON orders (created_at);

CREATE TABLE order_items (
    order_id   INT NOT NULL,
    sku        VARCHAR(32) NOT NULL,
    qty        INT NOT NULL,
    price      DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, sku),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
