## 📦 Product Inventory Management System

A full-stack inventory management application built with FastAPI, React, and PostgreSQL, fully containerized using Docker.

This project demonstrates scalable backend architecture, modern frontend design, database modeling, and full-stack integration using best practices.
This system allows businesses to manage products, categories, stock levels, and pricing with a clean, modern interface.
<hr>

### Live Features

* ✅ Create, update, soft delete products
* ✅ Server-side pagination
* ✅ Server-side sorting
* ✅ Search by ID, name, or description
* ✅ Dynamic category filtering
* ✅ Unique product name validation
* ✅ Soft delete (historical data preserved)
* ✅ Inventory quantity tracking
* ✅ Modern responsive UI
* ✅ Dockerized full-stack setup
* ✅ Persistent PostgreSQL storage
  
<hr>

### 🛠 Tech Stack
#### 🔹Backend

* FastAPI
* SQLAlchemy (ORM)
* PostgreSQL
* Pydantic
* Uvicorn
* Custom Exception Handling
* CORS Middleware
* Layered Architecture (Routes -> Services -> DB)

#### 🔹Frontend

* React
* Axios
* React Icons
* Custom CSS
* State-driven UI updates

#### 🔹DevOps

* Docker
* Docker Compose
* Named Volume for DB persistence

### 📂Project Structure

```bash
Product-Inventory/
│
├── alembic/
│   ├── versions
│   ├── env.py
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── schemas/
│   ├── db/
│   ├── tests/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── swagger.YAML
├── alembic.ini
├── entrypoint.sh
├── package.json
└── README.md
```
### 🐳 Run With Docker (Recommended)
##### Prerequisites
* Docker
* Docker Compose

##### Start the Application
```
docker compose up --build
```
##### Access the Application

Frontend:
```
http://localhost:3000
```
Backend:
```
http://localhost:8000
```
API Documentation:
```
http://localhost:8000/docs
```
##### Stop Containers (Data Persists)
```
docker compose down
```
⚠️ Do NOT use -v unless you want to reset the database.

##### Reset Database (Optional)
```
docker compose down -v
```
##### Database Persistence
PostgreSQL data is stored in a Docker named volume:
```
postgres_data
```
Data remains intact across container restarts.

### ⚙️Installation & Manual Setup
#### Clone the Repository
```
git clone https://github.com/DeepthiPavurala/product-inventory.git

cd product-inventory
```
#### 🔹Backend Setup
Create Virtual Environment
```
python -m venv venv
source venv/bin/activate  # Mac/Linux
```
Install Dependencies
```
pip install -r requirements.txt
```
Create .env File

Create a file named .env in the root directory:
```
DATABASE_URL=postgresql://username:password@localhost:5432/inventory_db
```
Run Backend Server
```
uvicorn app.main:app --reload
```
Backend runs at:
```
http://localhost:8000
```
API Docs available at:
```
http://localhost:8000/docs
```
#### 🔹Frontend Setup
```
cd frontend
npm install
npm start
```
Frontend runs at:
```
http://localhost:3000
```
##### 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET    | `/api/v1/products` | List products (pagination, sorting, filtering) |
| GET    | `/api/v1/products/categories` | Fetch unique categories |
| POST   | `/api/v1/products` | Create product |
| PATCH  | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Soft delete product |

<img width="1609" height="937" alt="Screenshot 2026-02-26 at 18 22 15" src="https://github.com/user-attachments/assets/177c44f3-98fe-42be-ae58-7133f940a1e1" />


##### 🔎Backend Capabilities

* Pagination via page & limit
* Sorting via sort_by & sort_order
* Search via search
* Category filtering via category
* Unique product name constraint
* Soft delete using is_active
* Custom exception handling for validation

### 🧠 Architecture Overview
```mermaid
graph TD
    A[Client: React] --> B[FastAPI Routes]
    B --> C[Service Layer]
    C --> D[SQLAlchemy ORM]
    D --> E[(PostgreSQL)]

    style A fill:#61DAFB,stroke:#333,stroke-width:2px
    style B fill:#05998B,stroke:#fff,stroke-width:2px,color:#fff
    style E fill:#336791,stroke:#fff,stroke-width:2px,color:#fff
```

##### Design Decisions

* Soft delete preserves historical integrity.
* Server-side pagination improves scalability.
* Business logic separated into service layer.
* Clean exception handling for maintainability.
* Dockerized architecture for portability and deployment.

#### 🔐Environment Variables

For local development copy .env.example and rename it to .env and replace username and password with your postgres credentials
```
DATABASE_URL=postgresql://username:password@localhost:5432/inventory_db
```
For Docker usage, environment variables are handled automatically via docker-compose.yml.
#### 📈Future Improvements

* JWT Authentication
* Role-based access control
* Low-stock alerts
* Inventory analytics dashboard
* CI/CD pipeline
* Cloud deployment (Render / Railway / AWS)

#### 📸Screenshots

<img width="1781" height="1099" alt="Screenshot 2026-02-26 at 18 37 17" src="https://github.com/user-attachments/assets/9f0a13f4-c252-4b81-ab7f-12d9a0b70cfc" />

<img width="1782" height="1111" alt="Screenshot 2026-02-26 at 18 37 30" src="https://github.com/user-attachments/assets/899ba3dd-118c-4f65-9669-df1e7a44b626" />


### 👩‍💻Author

<b>Deepthi</b>

Full Stack Developer | Data Engineer | Analytics Engineer

#### Why This Project Matters

This project demonstrates:
* RESTful API design
* Database modeling with constraints
* Backend scalability principles
* Modern frontend state management
* Full-stack integration
* Docker-based deployment
* Clean, maintainable architecture

## Test organization

The test suite is organized by testing style so different levels of confidence can run independently:

- `tests/unit/` - isolated service/helper tests with mocks, including mocked SMTP email alerts.
- `tests/integration/` - in-process FastAPI tests using a temporary SQLite database and mocked external boundaries.
- `tests/equivalence/` - equivalence partitioning tests for valid and invalid product/stock inputs.
- `tests/boundary/` - boundary value tests for price, quantity, and low-stock alert thresholds.
- `tests/test_products.py` - Docker-backed end-to-end backend tests using the Docker orchestrator.

Useful commands:

```bash
PYTEST_SKIP_DOCKER=1 pipenv run pytest -m "unit or integration or equivalence or boundary"
pipenv run pytest -m docker
```

The stock adjustment endpoint is available at the shared route builder path `api_routes.product_stock(product_id)` and maps to `PATCH /api/v1/products/{product_id}/stock`.

---

### ✅ Testing Setup

The project now supports multiple test types without requiring Docker for every run.

#### Install Python dependencies

Using `pip`:

```bash
python -m pip install -r requirements.txt
```

Using `pipenv`:

```bash
pip install pipenv
pipenv install --dev
```

#### Run local tests without Docker

These tests use FastAPI `TestClient`, an in-memory SQLite database, and mocks for Stripe/email behavior:

```bash
pytest -q
```

or with Pipenv:

```bash
pipenv run test
```

Expected result:

```text
25 passed, 5 skipped
```

The skipped tests are Docker-backed end-to-end tests. They are skipped by default so a clean local environment can run unit, integration, equivalence, and boundary tests without Docker.

#### Run Docker-backed tests

Docker tests use the Python Docker SDK and the centralized Docker orchestrator under `tests/docker_orchestrator.py`.

```bash
pytest -q --run-docker -m docker
```

or with Pipenv:

```bash
pipenv run test-docker
```

#### Test organization

```text
tests/
├── config.py                 # centralized test configuration
├── helpers.py                # reusable test data builders
├── utils.py                  # generic HTTP/test utilities
├── docker_orchestrator.py    # all Docker SDK lifecycle logic
├── unit/                     # service-level unit tests with mocks
├── integration/              # in-process API tests
├── equivalence/              # equivalence partition tests
├── boundary/                 # boundary value tests
└── test_products.py          # Docker-backed end-to-end tests
```

#### Mocking scenarios covered

* Stripe checkout session creation is mocked; no real Stripe API call is made.
* Low-stock email behavior is mocked; no real SMTP call is made.
* Product stock boundary behavior is tested at quantities above, at, and below the low-stock threshold.

### Docker SDK test orchestration

Docker-backed tests use `tests/docker_orchestrator.py`. The class name is `DockerOrchestrator`, and that class directly creates the Python Docker SDK client with `docker.from_env()`. There is no separate `DockerClient` wrapper class and no `docker compose` shell command inside pytest.

```python
from tests.docker_orchestrator import DockerOrchestrator

orchestrator = DockerOrchestrator(backend_config)
orchestrator.start()  # internally uses docker.from_env()
```
