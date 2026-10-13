# 🛒 E-Commerce API

Высоконагруженный асинхронный RESTful API для интернет-магазина, построенный на фреймворке **FastAPI** с использованием **PostgreSQL**, **Redis** и **Docker Compose**.

---

## 🛠 Технологический стек

* **Framework:** Python 3.12, FastAPI, Pydantic v2
* **Database & ORM:** PostgreSQL, SQLModel / SQLAlchemy 2.0 (AsyncSession), Alembic
* **In-Memory Storage:** Redis (Async via `redis.asyncio`) — для быстрого хранения и перерасчета корзины
* **Authentication:** JWT (PyJWT), хеширование паролей via `bcrypt`
* **Testing:** Pytest, pytest-asyncio, HTTPX (Unit & Integration tests)
* **Infrastructure & Environment:** Docker, Docker Compose

---

## 🏗 Архитектура и ключевые особенности

1. **Разделение слоев:** `Endpoints (Controllers) -> Services -> Models & Schemas (DTO)`.
2. **Асинхронность (Async/Await):** Полностью асинхронный I/O стек от веб-сервера до запросов к БД и Redis.
3. **Безопасность:** Регистрация, аутентификация через JWT access-токены, защита эндпоинтов.
4. **Управление корзиной:** Хранение и оперативный перерасчет позиций корзины в памяти Redis.
5. **Атомарность заказов:** Оформление заказов со списанием остатков на складе (`product.stock`), защитой от Race Condition (`with_for_update`) и автоочисткой корзины в Redis.
6. **Покрытие тестами:** Изолированная среда тестирования с подменой зависимостей (`dependency_overrides`) и автоочисткой базы и Redis.

---

## 🚀 Быстрый запуск

### 1. Клонирование репозитория и настройка переменных
```bash
git clone [https://github.com/ExampleWWW/E-Commerce-API.git](https://github.com/ExampleWWW/E-Commerce-API.git)
cd E-Commerce-API
cp .env.example .env
