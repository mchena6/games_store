# Games Store API - Backend

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

Backend API RESTful desarrollada para el proyecto "Games Store" (Ingeniería de Software). Esta API gestiona todo el catálogo de productos, autenticación de usuarios, carritos de compras, reseñas y procesamiento de órdenes.

## Características Principales

*   **Autenticación Segura:** Implementación de JSON Web Tokens (JWT) para sesiones sin estado.
*   **Catálogo Completo:** Gestión de Productos, Categorías, Marcas y Especificaciones Técnicas.
*   **Ecommerce Real:** Carrito de compras persistente con cálculos automáticos de subtotales, wishlist y sistema de órdenes (Checkout).
*   **Interacción de Usuarios:** Sistema de reseñas (1 a 5 estrellas) con cálculo automático de promedios para cada producto.
*   **Filtros Avanzados:** Búsquedas y filtrado dinámico integrado con `django-filter` (ej. por precio, marca, categoría).

## Tecnologías Usadas

*   **Framework Core:** Python 3.x, Django 5.x
*   **API Framework:** Django REST Framework (DRF)
*   **Autenticación:** SimpleJWT
*   **Documentación:** drf-spectacular (Swagger UI / OpenAPI 3)
*   **Gestor de Paquetes:** `uv`
*   **Base de Datos:** SQLite (Desarrollo) / [PostgreSQL en prod (NeonDB)]

## Requisitos Previos

Para correr este proyecto necesitas tener instalado:
*   Python 3.10+
*   [uv](https://github.com/astral-sh/uv) (Gestor de paquetes y entornos ultra rápido)
*   Git

## ⚙️ Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:mchena6/games_store.git
   cd games_store
   ```

2. **Crear el entorno virtual e instalar dependencias:**
   ```bash
   uv venv
   # Activar en Mac/Linux: source .venv/bin/activate
   uv pip install -r requirements.txt 
   ```

3. **Configurar Variables de Entorno:**
   Crea un archivo `.env` en la raíz del proyecto basándote en un `.env.example`

4. **Aplicar Migraciones:**
   ```bash
   uv run manage.py makemigrations
   uv run manage.py migrate
   ```

5. **Ejecutar el Servidor de Desarrollo:**
   ```bash
   uv run manage.py runserver
   ```
   La API estará disponible en `http://127.0.0.1:8000/`.

## 📡 Endpoints Habilitados

A continuación se detallan las rutas principales de la API. La URL base local es `http://127.0.0.1:8000/`.

### Autenticación y Usuarios
*   `POST /api/users/register/` - Registro de nuevos clientes.
*   `POST /api/token/` - Login (Obtener Access y Refresh Token).
*   `POST /api/token/refresh/` - Refrescar el Access Token.

### Catálogo (Públicos)
*   `GET /api/products/` - Listar productos (soporta paginación, filtros `?search=`, `?category=`, `?min_price=`).
*   `GET /api/products/{id}/` - Detalle de un producto.
*   `GET /api/categories/` - Listado de categorías.
*   `GET /api/brands/` - Listado de marcas.

### Carrito de Compras (Requiere Token)
*   `GET /api/carts/` - Ver carrito activo del usuario logueado.
*   `POST /api/carts/add-item/` - Agregar producto al carrito.
*   `POST /api/carts/{id}/incrementar/` - Sumar +1 a un ítem.
*   `POST /api/carts/{id}/decrementar/` - Restar -1 a un ítem.
*   `POST /api/carts/{id}/vaciar/` - Eliminar todos los ítems.

### Órdenes y Reseñas (Requiere Token)
*   `GET / POST /api/orders/` - Historial de compras y creación de una orden (Checkout).
*   `POST /api/orders/{id}/cancelar/` - Cancelar una orden pendiente.
*   `GET / POST /api/reviews/` - Leer o crear reseñas de productos.
*   `GET / POST /api/wishlist/` - Gestionar lista de deseos.

## Documentación Interactiva (Swagger)

La API cuenta con documentación autogenerada y testeable. Una vez que el servidor esté corriendo, puedes acceder a:
*   **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
*   **OpenAPI Schema:** `http://127.0.0.1:8000/api/schema/`

## Capturas de Pantalla

<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-30-19" src="https://github.com/user-attachments/assets/d6fff491-206c-41aa-bdb3-e4f4929376e3" />
<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-29-12" src="https://github.com/user-attachments/assets/4f4add58-3797-41ae-a82a-6dc89813d12e" />
<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-28-53" src="https://github.com/user-attachments/assets/0750f093-aee9-4af0-88f6-25f0434ca13c" />
<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-28-37" src="https://github.com/user-attachments/assets/2f23cd19-7896-4962-a262-21bf6df55b7f" />
<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-28-11" src="https://github.com/user-attachments/assets/1fc58c22-8cd4-46a8-a758-e7a82423c381" />
<img width="1366" height="768" alt="Captura de pantalla de 2026-11-05 23-27-57" src="https://github.com/user-attachments/assets/13430b81-94c3-47aa-a0c1-869a44ca5ced" />


## Equipo de Desarrollo

*   **Martin Chena** - (https://github.com/mchena6)
*   **Ibañez Ian** - (https://github.com/IanChoDK)
*   **Pereyra Franco** - (https://github.com/FrancoPereyra13)

---
*Proyecto desarrollado para la EFI de Ingeniería de Software.*
