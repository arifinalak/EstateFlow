-- Run this file in MySQL to set up the database
-- mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS realestate;
USE realestate;

-- USERS (all roles: admin, agent, buyer, investor)
CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role     ENUM('admin','agent','buyer','investor') DEFAULT 'buyer',
    created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PROPERTIES
CREATE TABLE IF NOT EXISTS properties (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    price       DECIMAL(12,2),
    city        VARCHAR(100),
    bedrooms    INT DEFAULT 0,
    bathrooms   INT DEFAULT 0,
    area        DECIMAL(10,2),
    property_type VARCHAR(30) DEFAULT 'apartment',
    image_path  VARCHAR(255),
    status      ENUM('available','sold','rented') DEFAULT 'available',
    agent_id    INT,
    created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE SET NULL
);

-- SAVED LISTINGS (buyer feature)
CREATE TABLE IF NOT EXISTS saved_listings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    property_id INT NOT NULL,
    saved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_save (user_id, property_id),
    FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- LEADS / CRM
CREATE TABLE IF NOT EXISTS leads (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    name     VARCHAR(100),
    email    VARCHAR(100),
    phone    VARCHAR(30),
    status   ENUM('new','contacted','qualified','closed') DEFAULT 'new',
    notes    TEXT,
    created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- BUYER INQUIRIES (buyer -> property agent)
CREATE TABLE IF NOT EXISTS inquiries (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    buyer_id    INT NOT NULL,
    agent_id    INT NOT NULL,
    message     TEXT NOT NULL,
    agent_message TEXT,
    status      ENUM('new','in_progress','completed','replied','closed') DEFAULT 'new',
    created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id)    REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (agent_id)    REFERENCES users(id)      ON DELETE CASCADE
);

-- INVESTOR PORTFOLIO
CREATE TABLE IF NOT EXISTS portfolio (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    investor_id    INT NOT NULL,
    property_name  VARCHAR(200),
    purchase_price DECIMAL(12,2),
    current_value  DECIMAL(12,2),
    monthly_income DECIMAL(10,2),
    added_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── SAMPLE DATA ──────────────────────────────────────────────────────────────
-- Passwords stored as plain text for demo (use hashing in production!)
INSERT INTO users (name, email, password, role) VALUES
('Md. Rashed Chowdhury', 'admin@demo.com',    'admin123',    'admin'),
('Arifa Rahman',         'agent@demo.com',    'agent123',    'agent'),
('Sumaiya Islam',        'buyer@demo.com',    'buyer123',    'buyer'),
('Tanvir Hasan',         'investor@demo.com', 'investor123', 'investor');

INSERT INTO properties (title, description, price, city, bedrooms, bathrooms, area, property_type, image_path, status, agent_id) VALUES
('Dhanmondi Shanti Apartment', 'Shohorer majhe sundor baranda shoho 2 bedroom apartment.', 250000, 'Dhaka', 2, 1, 900, 'apartment', 'lakeview-house.jpg', 'available', 2),
('Uttara Paribarik Villa',     'Bagan shoho 5 bedroom er proshosto villa, poribarer jonno ideal.', 850000, 'Dhaka', 5, 3, 3500, 'villa', 'pride-villa.jpg', 'available', 2),
('Mirpur Cozy Studio',         'University area r kache chhoto o aramdayok studio flat.', 95000, 'Dhaka', 1, 1, 450, 'studio', 'cozy-studio-apartment.jpg', 'available', 2),
('Motijheel Corporate Office', 'Byabshar jonno premium office space, location khub bhalo.', 500000, 'Dhaka', 0, 2, 2000, 'office', 'corporate-house.jpeg', 'available', 2),
('Gulshan Prime Land',         'Abashik ba banijjik unnoyoner jonno prime location er jomi.', 650000, 'Dhaka', 0, 0, 2400, 'land', 'gulshan-land.jpg', 'available', 2),
('Gulshan Lakeview Banglow',   'Laker pase niribili poribesh e 3 bedroom banglow bari.', 320000, 'Narayanganj', 3, 2, 1500, 'bungalow', 'banglow.jpg', 'available', 2);
