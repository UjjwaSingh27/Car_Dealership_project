# SQL Commands & Inserts — Smart Car Dealership

All SQL statements needed to create and populate the `car_dealership_real` database from scratch.

---

## Step 1 — Create the Database

```sql
CREATE DATABASE IF NOT EXISTS car_dealership_real;
USE car_dealership_real;
```

---

## Step 2 — Create Tables

```sql
-- =============================================
-- USERS
-- Stores admin and customer accounts
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INT          NOT NULL AUTO_INCREMENT,
    username      VARCHAR(50)  NOT NULL,
    password      VARCHAR(255) NOT NULL,
    fname         VARCHAR(50)  DEFAULT NULL,
    lname         VARCHAR(50)  DEFAULT NULL,
    role          ENUM('admin','customer') DEFAULT 'customer',
    created_at    TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY    username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- CARS
-- Main inventory table — vin is the vehicle ID
-- =============================================
CREATE TABLE IF NOT EXISTS cars (
    vin            VARCHAR(17) NOT NULL,
    make           VARCHAR(50)  DEFAULT NULL,
    model          VARCHAR(50)  DEFAULT NULL,
    year           INT          DEFAULT NULL,
    selling_price  DECIMAL(15,2) DEFAULT NULL,
    cost_price     DECIMAL(15,2) DEFAULT NULL,
    status         ENUM('Available','Sold','Maintenance') DEFAULT 'Available',
    image_path     VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (vin),
    CONSTRAINT chk_min_price CHECK (selling_price >= 1000.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- CAR_SPECIFICATIONS
-- Technical details — linked 1:1 to cars via vin
-- =============================================
CREATE TABLE IF NOT EXISTS car_specifications (
    vin           VARCHAR(17) NOT NULL,
    fuel_type     ENUM('Petrol','Diesel','Electric','Hybrid') DEFAULT NULL,
    transmission  ENUM('Manual','Automatic') DEFAULT NULL,
    mileage       INT          DEFAULT NULL,
    color         VARCHAR(20)  DEFAULT NULL,
    PRIMARY KEY (vin),
    CONSTRAINT car_specifications_ibfk_1
        FOREIGN KEY (vin) REFERENCES cars (vin) ON DELETE CASCADE,
    CONSTRAINT chk_positive_mileage CHECK (mileage >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- TRANSACTIONS
-- Records every payment attempt
-- =============================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id       VARCHAR(100) NOT NULL,
    user_id              INT          DEFAULT NULL,
    vin                  VARCHAR(17) DEFAULT NULL,
    payment_method       ENUM('Card','UPI','Bank Transfer') DEFAULT NULL,
    amount               DECIMAL(10,2) DEFAULT NULL,
    transaction_status   ENUM('Success','Failed','Processing') DEFAULT 'Processing',
    transaction_date     TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    KEY user_id (user_id),
    KEY vin (vin),
    CONSTRAINT transactions_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT transactions_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- SALES
-- Finalized ownership records
-- =============================================
CREATE TABLE IF NOT EXISTS sales (
    sale_id         INT          NOT NULL AUTO_INCREMENT,
    transaction_id  VARCHAR(100) NOT NULL,
    sale_date       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sale_id),
    UNIQUE KEY transaction_id (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- SALE_DETAILS
-- Stores sale price and buyer info after verification
-- =============================================
CREATE TABLE IF NOT EXISTS sale_details (
    transaction_id     VARCHAR(100) NOT NULL,
    user_id            INT          DEFAULT NULL,
    vin                VARCHAR(17)  DEFAULT NULL,
    final_sale_price   DECIMAL(10,2) DEFAULT NULL,
    PRIMARY KEY (transaction_id),
    KEY user_id (user_id),
    KEY vin (vin),
    CONSTRAINT sale_details_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT sale_details_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- WISHLIST
-- Tracks which user saved which car (4NF normalized)
-- =============================================
CREATE TABLE IF NOT EXISTS wishlist (
    user_id  INT         NOT NULL,
    vin      VARCHAR(17) NOT NULL,
    PRIMARY KEY (user_id, vin),
    KEY vin (vin),
    CONSTRAINT wishlist_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT wishlist_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- WISHLIST_ENTRIES
-- Stores timestamp when a car was added to wishlist
-- =============================================
CREATE TABLE IF NOT EXISTS wishlist_entries (
    wishlist_id  INT         NOT NULL AUTO_INCREMENT,
    user_id      INT         NOT NULL,
    vin          VARCHAR(17) NOT NULL,
    added_at     TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (wishlist_id),
    KEY user_id (user_id),
    KEY vin (vin),
    CONSTRAINT wishlist_entries_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT wishlist_entries_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- TEST_DRIVES
-- Records which user test-drove which car
-- =============================================
CREATE TABLE IF NOT EXISTS test_drives (
    user_id  INT         NOT NULL,
    vin      VARCHAR(17) NOT NULL,
    PRIMARY KEY (user_id, vin),
    KEY vin (vin),
    CONSTRAINT test_drives_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT test_drives_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- TEST_DRIVE_SCHEDULES
-- Stores booked test drive slots with date/status
-- =============================================
CREATE TABLE IF NOT EXISTS test_drive_schedules (
    drive_id        INT          NOT NULL AUTO_INCREMENT,
    user_id        INT          NOT NULL,
    vin            VARCHAR(17)  NOT NULL,
    scheduled_date DATETIME     DEFAULT NULL,
    status         ENUM('Pending','Completed','Cancelled') DEFAULT 'Pending',
    PRIMARY KEY (drive_id),
    KEY user_id (user_id),
    KEY vin (vin),
    CONSTRAINT test_drive_schedules_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT test_drive_schedules_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- MAINTENANCE_RECORDS
-- Service history for each car
-- =============================================
CREATE TABLE IF NOT EXISTS maintenance_records (
    record_id     INT          NOT NULL AUTO_INCREMENT,
    vin           VARCHAR(17)  DEFAULT NULL,
    service_type  ENUM('Cleaning','Repair','Oil Change','General Inspection') DEFAULT NULL,
    service_date  DATE         DEFAULT NULL,
    cost          DECIMAL(10,2) DEFAULT NULL,
    description   TEXT,
    performed_by  VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (record_id),
    KEY vin (vin),
    CONSTRAINT maintenance_records_ibfk_1 FOREIGN KEY (vin) REFERENCES cars (vin) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- REFUNDS
-- Records of reversals for finalized sales
-- =============================================
CREATE TABLE IF NOT EXISTS refunds (
    refund_id       INT          NOT NULL AUTO_INCREMENT,
    sale_id         INT          DEFAULT NULL,
    refund_amount   DECIMAL(10,2) DEFAULT NULL,
    refund_reason   TEXT,
    refund_status   ENUM('Initiated','Completed') DEFAULT 'Initiated',
    processed_at    TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (refund_id),
    KEY sale_id (sale_id),
    CONSTRAINT refunds_ibfk_1 FOREIGN KEY (sale_id) REFERENCES sales (sale_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- ADMIN_LOGS
-- Security audit trail for admin actions
-- =============================================
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id             INT         NOT NULL AUTO_INCREMENT,
    admin_id           INT         DEFAULT NULL,
    action_performed   TEXT,
    action_date        TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY admin_id (admin_id),
    CONSTRAINT admin_logs_ibfk_1 FOREIGN KEY (admin_id) REFERENCES users (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- TRANSACTION_VERIFICATION
-- Admin approval records for transactions
-- =============================================
CREATE TABLE IF NOT EXISTS transaction_verification (
    verified_by_admin_id  INT         NOT NULL,
    transaction_id         VARCHAR(100) NOT NULL,
    verification_status   ENUM('Pending','Verified','Rejected') DEFAULT NULL,
    PRIMARY KEY (verified_by_admin_id, transaction_id),
    KEY transaction_id (transaction_id),
    CONSTRAINT transaction_verification_ibfk_1
        FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- TRANSACTIONVERIFICATION
-- Separate verification timestamp log
-- =============================================
CREATE TABLE IF NOT EXISTS transactionverification (
    verification_id   INT         NOT NULL AUTO_INCREMENT,
    transaction_id   VARCHAR(100) DEFAULT NULL,
    verification_date TIMESTAMP   NULL DEFAULT NULL,
    PRIMARY KEY (verification_id),
    KEY transaction_id (transaction_id),
    CONSTRAINT transactionverification_ibfk_1
        FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

```sql
-- =============================================
-- REVIEWS
-- Customer reviews and ratings for cars
-- =============================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id    INT         NOT NULL AUTO_INCREMENT,
    user_id      INT         NOT NULL,
    vin          VARCHAR(17) NOT NULL,
    rating       TINYINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT,
    created_at   TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (review_id),
    KEY user_id (user_id),
    KEY vin (vin),
    CONSTRAINT reviews_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT reviews_ibfk_2 FOREIGN KEY (vin) REFERENCES cars (vin) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

---

## Step 3 — Insert Users

Passwords must be hashed using Werkzeug before inserting. Use the hash script separately.

```sql
INSERT INTO users (user_id, username, password, fname, lname, role, created_at) VALUES
(1, 'Aadith_admin',  '<hashed>', 'Aadith', 'Geeth Mohan', 'admin',  '2026-04-08 13:50:02'),
(2, 'Ujjwal_admin',  '<hashed>', 'Ujjwal', 'Pratap Singh', 'admin',  '2026-04-08 13:50:02'),
(3, 'rahul_customer','<hashed>', 'Rahul', 'Kumar',        'customer','2026-04-08 13:50:02'),
(4, 'priya_v',      '<hashed>', 'Priya', 'Verma',        'customer','2026-04-08 13:50:02');
```

---

## Step 4 — Insert Sample Cars (Representative Rows)

Full dataset of 202 cars is available in `DBMS_SQL_INFO/car_dealership_real_cars.sql`.

```sql
INSERT INTO cars (vin, make, model, year, selling_price, cost_price, status, image_path) VALUES
('0001','Mercedes-Benz','300 SLR',1955,370000.00,114400000.00,'Available','mercedes-benz_300_slr.jpg'),
('0002','Ferrari','250 GTO',1962,660000.00,38400000.00,'Sold','ferrari_250_gto.jpg'),
('0003','Ferrari','335 S',1957,31500000.00,28000000.00,'Available','ferrari_335_s.jpg'),
('0011','Lamborghini','Revuelto',2024,540000.00,480000.00,'Available','lamborghini_revuelto.jpg'),
('0051','Toyota','Corolla',2026,20700.00,18400.00,'Available','toyota_corolla.jpg'),
('0083','Tesla','Model 3',2025,35100.00,31200.00,'Available','tesla_model_3.jpg');
```

---

## Step 5 — Insert Car Specifications

Full data in `DBMS_SQL_INFO/car_dealership_real_car_specifications.sql`.

```sql
INSERT INTO car_specifications (vin, fuel_type, transmission, mileage, color) VALUES
('0001','Petrol','Manual',8,'Blue'),
('0002','Petrol','Manual',11,'Silver'),
('0003','Petrol','Manual',18,'Yellow'),
('0011','Electric','Automatic',329,'Red'),
('0051','Hybrid','Automatic',27,'Black'),
('0083','Diesel','Automatic',17,'Grey');
```

---

## Step 6 — Insert Transactions

```sql
INSERT INTO transactions (transaction_id, user_id, vin, payment_method, amount, transaction_status, transaction_date) VALUES
('TXN_1002',    4, '0002', 'UPI',           65000.00,  'Success',    '2026-04-16 22:45:26'),
('TXN_2001',    3, '0002', 'Card',          65000.00,  'Success',    '2026-04-16 22:59:57'),
('TXN_9901',    3, '0003', 'Bank Transfer', 90000.00,  'Success',    '2026-04-08 14:01:47'),
('TXN_9902',    4, '0001', 'UPI',          35000.00,  'Processing', '2026-04-08 14:01:47'),
('TXN_9903',    3, '0002', 'Card',          65000.00,  'Failed',     '2026-04-08 14:01:47'),
('TXN_TEST_DUMMY',3,'0004','Card',        18000000.00, 'Success',    '2026-04-08 14:29:48');
```

---

## Step 7 — Insert Sales & Sale Details

```sql
INSERT INTO sales (sale_id, transaction_id, sale_date) VALUES
(1, 'TXN_9901',       '2026-04-08 19:32:40'),
(2, 'TXN_9902',       '2026-04-08 19:32:40'),
(3, 'TXN_TEST_DUMMY', '2026-04-08 19:58:03'),
(4, 'TXN_1002',       '2026-04-17 04:15:26');

INSERT INTO sale_details (transaction_id, user_id, vin, final_sale_price) VALUES
('TXN_1002',       4, '0002',  65000.00),
('TXN_9901',       3, '0003',  90000.00),
('TXN_9902',       4, '0001',  35000.00),
('TXN_TEST_DUMMY', 3, '0002', 48000000.00);
```

---

## Step 8 — Insert Maintenance Records

```sql
INSERT INTO maintenance_records (record_id, vin, service_type, service_date, cost, description, performed_by) VALUES
(1, '0004', 'Repair',           '2026-02-10', 500.00, 'Brake pad replacement and sensor check',   'Hyundai Services Ltd.'),
(2, '0002', 'Oil Change',       '2026-02-15', 150.00, 'Regular oil and filter change',           'BMW Service Center'),
(3, '0005', 'Cleaning',         '2026-02-20',  80.00, 'Interior and exterior detailing',          'Premium Auto Clean'),
(4, '0008', 'Repair',           '2026-03-01',2500.00, 'Suspension bushings replacement',          'Bugatti Authorized Service'),
(5, '0011', 'General Inspection','2026-03-05',100.00, 'Pre-purchase inspection',                'Lamborghini Certified Inspector'),
(6, '0017', 'Oil Change',       '2026-03-10', 120.00, 'Full synthetic oil change',                'Lexus Service Center');
```

---

## Step 9 — Insert Wishlist & Wishlist Entries

```sql
INSERT INTO wishlist (user_id, vin) VALUES
(4, '0001'),
(3, '0003'),
(4, '0004');

INSERT INTO wishlist_entries (wishlist_id, user_id, vin, added_at) VALUES
(1, 3, '0003', '2026-04-08 14:03:57'),
(2, 4, '0004', '2026-04-08 14:03:57'),
(3, 4, '0001', '2026-04-08 14:14:05');
```

---

## Step 10 — Insert Test Drives & Schedules

```sql
INSERT INTO test_drives (user_id, vin) VALUES
(4, '0001'),
(3, '0003'),
(3, '0004');

INSERT INTO test_drive_schedules (drive_id, user_id, vin, scheduled_date, status) VALUES
(1, 3, '0003', '2026-03-01 10:30:00', 'Pending'),
(2, 4, '0001', '2026-02-28 14:00:00', 'Completed'),
(3, 3, '0004', '2026-04-15 10:00:00', 'Pending');
```

---

## Step 11 — Insert Admin Logs

```sql
INSERT INTO admin_logs (log_id, admin_id, action_performed, action_date) VALUES
(1, 1, 'Updated selling price for Tesla Model S',    '2026-04-08 14:04:18'),
(2, 1, 'Verified Transaction TXN_9901',             '2026-04-08 14:04:18'),
(3, 2, 'Added new inventory: Hyundai Creta',         '2026-04-08 14:04:18'),
(4, 1, 'Transaction TXN_9902 marked as Rejected',   '2026-04-08 14:24:04'),
(5, 1, 'ALERT: Test VIN 9999 priced at 500000.00',   '2026-04-08 14:37:30'),
(6, 1, 'Verified Transaction TXN_9902',              '2026-04-16 22:54:23');
```

---

## Step 12 — Insert Refunds

```sql
INSERT INTO refunds (refund_id, sale_id, refund_amount, refund_reason, refund_status, processed_at) VALUES
(1, 1, 90000.00, 'Customer requested cancellation before delivery', 'Initiated', '2026-04-08 14:03:04');
```

---

## Step 13 — Insert Transaction Verification

```sql
INSERT INTO transaction_verification (verified_by_admin_id, transaction_id, verification_status) VALUES
(1, 'TXN_9901', 'Verified'),
(1, 'TXN_9902', 'Verified');

INSERT INTO transactionverification (verification_id, transaction_id, verification_date) VALUES
(1, 'TXN_9901', '2026-01-27 18:30:00'),
(2, 'TXN_9902', '2026-04-08 14:24:04'),
(3, 'TXN_9902', '2026-04-16 22:54:23');
```

---

## Step 14 — Create Views

```sql
-- Profit analysis: final sale price vs cost price
CREATE VIEW sales_dashboard AS
SELECT
    s.sale_id,
    s.sale_date,
    sd.final_sale_price,
    CONCAT(u.fname, ' ', u.lname) AS buyer_name,
    CONCAT(c.year, ' ', c.make, ' ', c.model) AS car_name,
    c.cost_price,
    (sd.final_sale_price - c.cost_price) AS profit
FROM sales s
JOIN sale_details sd ON s.transaction_id = sd.transaction_id
JOIN users u ON sd.user_id = u.user_id
JOIN cars c ON sd.vin = c.vin;
```

```sql
-- Per-customer activity summary
CREATE VIEW customer_activity AS
SELECT
    u.user_id,
    CONCAT(u.fname, ' ', u.lname) AS customer_name,
    COUNT(DISTINCT t.transaction_id) AS total_transactions,
    COUNT(DISTINCT w.vin) AS wishlist_count,
    COUNT(DISTINCT td.vin) AS test_drives
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
LEFT JOIN wishlist w ON u.user_id = w.user_id
LEFT JOIN test_drives td ON u.user_id = td.user_id
WHERE u.role = 'customer'
GROUP BY u.user_id, u.fname, u.lname;
```

```sql
-- Maintenance history for cars in service
CREATE VIEW maintenance_status AS
SELECT
    c.vin,
    c.make,
    c.model,
    c.year,
    mr.service_type,
    mr.service_date,
    mr.cost,
    mr.performed_by
FROM cars c
JOIN maintenance_records mr ON c.vin = mr.vin;
```

---

## Step 15 — Create Triggers

```sql
DELIMITER $$

-- Automatically mark a car as Sold once its transaction is verified
CREATE TRIGGER after_verification_update
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    IF NEW.transaction_status = 'Success' THEN
        UPDATE cars SET status = 'Sold' WHERE vin = NEW.vin;
    END IF;
END$$

-- Log a new maintenance record in admin_logs
CREATE TRIGGER after_maintenance_insert
AFTER INSERT ON maintenance_records
FOR EACH ROW
BEGIN
    INSERT INTO admin_logs (admin_id, action_performed)
    VALUES (1, CONCAT('Maintenance recorded for VIN ', NEW.vin, ': ', NEW.service_type));
END$$

DELIMITER ;
```

---

## Step 16 — Password Hashing (One-Time Setup)

Run this in Python before inserting users:

```python
import pymysql
from werkzeug.security import generate_password_hash

conn = pymysql.connect(
    host='localhost', user='root',
    password='Admin1234!', database='car_dealership_real'
)
cur = conn.cursor()

users = [
    (1, 'Aadith_admin',   'adminPass123'),
    (2, 'Ujjwal_admin',   'adminPass456'),
    (3, 'rahul_customer', 'custPass789'),
    (4, 'priya_v',        'priyaPass321'),
]

for uid, username, password in users:
    hashed = generate_password_hash(password)
    cur.execute(
        'UPDATE users SET password = %s WHERE user_id = %s',
        (hashed, uid)
    )
    print(f'Hashed: {username}')

conn.commit()
conn.close()
print('All passwords hashed.')
```
