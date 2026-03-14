# ERP Billing System - Backend

## Prerequisites

- Python 3.11+
- PostgreSQL 13+
- `pip` / `venv`

## Environment variables

Create a `.env` file inside the `backend/` directory with at least:

```env
SECRET_KEY="change-this-to-a-random-long-string"
DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/billing_db"

# CORS (comma-separated list for frontend origins)
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Invoice PDFs
INVOICE_PDF_DIR="generated_invoices"

# SMTP for invoice emails
SMTP_HOST="smtp.your-provider.com"
SMTP_PORT=587
SMTP_USER="smtp-username"
SMTP_PASSWORD="smtp-password"
SMTP_FROM_EMAIL="billing@yourcompany.com"
SMTP_USE_TLS=true
```

## Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Database migrations (Alembic)

Alembic is configured to use the SQLAlchemy models from `app.models`.

### Create initial migration

From the `backend/` directory, run:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Apply migrations

Whenever the models change and a new migration is created:

```bash
alembic upgrade head
```

## Running the backend (local)

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### API documentation

Open the interactive docs in your browser:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key features

- JWT authentication (`/api/v1/auth`)
- Clients, services, invoices, payments (`/api/v1/...`)
- Automatic invoice numbering (format: `INV-YYYY-0001` per company per year)
- Invoice PDF generation using WeasyPrint (stored under `INVOICE_PDF_DIR`, path saved in `invoices.pdf_path`)
- Invoice email sending with PDF attachment (via `/api/v1/invoices/{invoice_id}/send-email`)
- Dashboard metrics under `/api/v1/dashboard`

## Frontend (React + Vite)

### Environment variables

Create a `.env` file inside the `frontend/` directory:

```env
VITE_API_BASE_URL="http://localhost:8000"
```

### Install dependencies and run

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Database seed data

After running migrations, you can populate initial data (company, currency, GST tax rate, admin user, sample service) from the `backend/` directory:

```bash
cd backend
python -m app.db.seed_data
```

An admin user `admin@example.com` with password `admin123` will be created if it does not exist.

## Running the full system locally

1. **Backend**

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open `http://localhost:5173` in your browser to use the ERP Billing UI and `http://localhost:8000/docs` for API testing.

## Running with Docker (full stack)

1. Build and start all services from the project root:

   ```bash
   docker-compose up --build
   ```

   This will start:

   - `db`: PostgreSQL
   - `backend`: FastAPI app on port `8000`
   - `frontend`: Nginx serving the React build on port `5173`

2. Apply migrations inside the backend container (first run only):

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. Seed initial data:

   ```bash
   docker-compose exec backend python -m app.db.seed_data
   ```

4. Access the system:

   - UI: `http://localhost:5173`
   - API docs: `http://localhost:8000/docs`



