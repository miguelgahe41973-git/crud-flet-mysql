-- ============================================
-- Script de creación de base de datos
-- Importar este archivo desde phpMyAdmin
-- (pestaña "Importar" o pegarlo en "SQL")
-- ============================================

CREATE DATABASE IF NOT EXISTS crud_flet
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crud_flet;

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL DEFAULT 0,
    cantidad INT NOT NULL DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Datos de ejemplo (opcional)
INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES
('Teclado mecánico', 'Switches azules, retroiluminado', 899.00, 15),
('Mouse inalámbrico', 'Sensor óptico 1600 DPI', 349.50, 30),
('Monitor 24"', 'Full HD, panel IPS', 3299.00, 8);
