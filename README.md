# 🏛️ Programa Nacional de Registro y Preservación de Sitios Históricos

Trabajo Integrador – Proyecto de Software 2025  
Facultad de Informática – UNLP  

---

## 📖 Descripción del Proyecto

Este proyecto consiste en el desarrollo de una aplicación web destinada a centralizar la información de sitios históricos de distintas ciudades del país, permitiendo su gestión, visualización y consulta pública.

La solución se compone de:

- 🔐 Una **aplicación privada de administración** para editores y administradores.
- 🌎 Un **portal público** para que los usuarios puedan explorar los sitios históricos, dejar reseñas y marcar favoritos.
- 🔌 Una **API REST** que integra ambos sistemas.

El sistema permite:

- Registrar y gestionar sitios históricos con información geográfica.
- Asociar etiquetas (tags) a los sitios.
- Gestionar usuarios y roles.
- Moderar reseñas.
- Visualizar sitios en mapas interactivos.
- Exportar información en formato CSV.
- Implementar feature flags para control de funcionalidades.

El desarrollo se realiza en dos etapas, siguiendo el modelo MVC y aplicando buenas prácticas de ingeniería de software.

---

## 🎯 Objetivos Académicos

Este trabajo integrador tiene como finalidad:

- Aplicar conocimientos de Ingeniería de Software.
- Implementar una arquitectura web clásica con separación en capas.
- Desarrollar una API RESTful.
- Trabajar con bases de datos relacionales utilizando ORM.
- Implementar autenticación, autorización y manejo de sesiones.
- Integrar servicios externos (OAuth y mapas).
- Aplicar criterios de seguridad web (OWASP).
- Trabajar colaborativamente utilizando control de versiones.

---

## 🏗️ Arquitectura del Sistema

El sistema está dividido en tres grandes componentes:

### 1️⃣ Aplicación Privada (Administración)
- Gestión de sitios históricos (CRUD)
- Gestión de usuarios y roles
- Moderación de reseñas
- Gestión de tags
- Exportación de datos
- Feature Flags
- Historial de modificaciones

### 2️⃣ API REST
- Provee datos al portal público
- Maneja autenticación y autorización
- Expone endpoints para sitios, reseñas, usuarios y favoritos

### 3️⃣ Portal Público
- Listado y búsqueda avanzada de sitios
- Visualización en mapa interactivo
- Detalle completo de cada sitio
- Sistema de reseñas
- Login con Google (OAuth2)
- Perfil de usuario

---

## 🛠️ Tecnologías Utilizadas

### 🔹 Backend
- **Python 3.12**
- **Flask**
- **SQLAlchemy (ORM)**
- **PostgreSQL 16**
- **Flask-Session**
- **Poetry** (gestión de dependencias)
- **bcrypt** (hash de contraseñas)

### 🔹 Frontend Público
- **Vue.js 3**
- **JavaScript**
- **HTML5**
- **CSS3**
- Framework CSS (Bootstrap / Tailwind )

### 🔹 Mapas e Integraciones
- **Leaflet**
- **OpenStreetMap**
- **OAuth2 (Login con Google)**

### 🔹 Infraestructura
- **nginx**
- **MinIO** (almacenamiento de imágenes)
- Servidor Linux (Ubuntu)

### 🔹 Herramientas de Desarrollo
- **Git**
- **GitHub / GitLab**
- Entornos virtuales Python
- IDE de desarrollo
- Validadores HTML/CSS

---

## 🔐 Seguridad Implementada

- Autenticación manual (sin Flask-Login)
- Manejo seguro de sesiones
- Hash seguro de contraseñas
- Protección contra inyección SQL mediante SQLAlchemy
- Validación de datos en cliente y servidor
- Control de permisos basado en roles
- Consideración de vulnerabilidades OWASP (XSS, SQLi)


  
