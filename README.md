<<<<<<< HEAD

# decision-support-system

=======

# Maintenance Fund Allocation CDSS Backend

Production-ready FastAPI backend scaffold for a Computerized Decision Support System used in property management maintenance fund allocation.

## Stack

- FastAPI
- SQLAlchemy 2.x
- MySQL via PyMySQL
- JWT authentication
- Role-based access control for Admin and Property Manager users

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set strong credentials/secrets.
4. Create the MySQL database named in `MYSQL_DATABASE`.
5. Run database migrations:

```powershell
alembic upgrade head
```

6. Start the API:

```powershell
uvicorn app.main:app --reload
```

The API documentation will be available at `http://127.0.0.1:8000/docs`.

## Initial Admin

After the database is configured, create an admin user:

```powershell
python scripts/create_admin.py admin@example.com "StrongPassword123!"
```

## Key Endpoints

- `POST /api/v1/auth/login` - issue JWT access token
- `GET /api/v1/users/me` - current authenticated user
- `POST /api/v1/users/` - admin-only user creation
- `GET /api/v1/maintenance-allocations/summary` - admin and property manager access
- `POST /api/v1/maintenance-allocations/recommend` - admin and property manager access
  > > > > > > >
