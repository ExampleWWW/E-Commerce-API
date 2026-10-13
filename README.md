# 🛒 E-Commerce API

RESTful API для интернет-магазина на FastAPI с использованием PostgreSQL, Redis и Docker Compose.

---

## 🛠 Технологический стек

* **Язык программирования:** Python 3.11
* **Фреймворк и библиотеки:** FastAPI, Pydantic v2
* **База данных и ORM:** PostgreSQL 16, SQLModel / SQLAlchemy 2.0 (AsyncSession), Alembic
* **Хранилище в памяти:** Redis 7 (`redis.asyncio`) — хранение и расчет корзины
* **Аутентификация:** JWT (PyJWT), хеширование паролей `bcrypt`
* **Тестирование:** Pytest, pytest-asyncio, HTTPX (26 юнит и интеграционных тестов)
* **Инфраструктура:** Docker, Docker Compose

---

## 🏗 Архитектура и особенности

1. **Слои приложения:** `Endpoints -> Services -> Models & Schemas`.
2. **Асинхронность:** `async/await` стек для работы с I/O (БД и Redis).
3. **Авторизация:** JWT access-токены для защиты эндпоинтов.
4. **Корзина:** Хранение позиций корзины пользователя в Redis.
5. **Заказы:** Оформление заказов с блокировкой строк (`with_for_update`), списанием остатков со склада и очисткой корзины.
6. **Тесты:** Автоматические интеграционные и юнит-тесты с изолированными тестовыми БД и Redis.

---

## 🚀 Запуск проекта

### 1. Подготовка окружения
```bash
git clone https://github.com/ExampleWWW/E-Commerce-API.git
cd E-Commerce-API
cp .env.example .env
```

### 2. Запуск контейнеров
```bash
docker compose up -d --build
```

### 3. Применение миграций
```bash
docker compose exec app alembic upgrade head
```

Приложение будет доступно по адресу: **http://localhost:8000**

---

## 📚 Документация API

* **Swagger UI:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Тестирование

Для запуска тестов убедитесь, что тестовое окружение поднято (`docker compose up -d`), затем выполните:
```bash
pytest -v
```

## 📷 Скриншоты
<img width="1901" height="907" alt="image" src="https://github.com/user-attachments/assets/695c6364-9c5f-4088-89de-ee2ab55d764a" />
<img width="1917" height="906" alt="image" src="https://github.com/user-attachments/assets/0d9df751-eb68-4e88-b3a6-fe9c7a24853c" />
<img width="1897" height="311" alt="image" src="https://github.com/user-attachments/assets/ff8d7c2a-eb8e-4ae1-bfa0-7413cc3bb1f0" />
<img width="1144" height="617" alt="image" src="https://github.com/user-attachments/assets/5e8b9b8e-b5c0-43d3-907e-c0de13eee7c2" />

