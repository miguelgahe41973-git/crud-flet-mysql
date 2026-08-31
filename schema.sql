-- ============================================
-- Script de creación de base de datos
-- Importar este archivo desde phpMyAdmin
-- (pestaña "Importar" o pegarlo en "SQL")
-- ============================================

CREATE DATABASE IF NOT EXISTS crud_flet
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crud_flet;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    perfil ENUM('Administrador', 'Usuario', 'Invitado', 'Restringido') NOT NULL DEFAULT 'Usuario',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Usuario administrador de ejemplo
-- Usuario: admin   |   Contraseña: admin123
-- (¡Cámbiala después de tu primer login en un sistema real!)
INSERT INTO usuarios (username, password_hash, nombre, perfil) VALUES
('admin', '7e56d30214e51e9b9d6192b09e23d8b6$b7e832051527d4307835aa6e0b6ce113dec80a8473ccc6c18704c1c4aad2899f', 'Administrador', 'Administrador');

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL DEFAULT 0,
    cantidad INT NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Datos de ejemplo (opcional)
INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES
('Teclado mecánico', 'Switches azules, retroiluminado', 899.00, 15),
('Mouse inalámbrico', 'Sensor óptico 1600 DPI', 349.50, 30),
('Monitor 24"', 'Full HD, panel IPS', 3299.00, 8);
