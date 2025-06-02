# LotusLynx E-commerce Platform

A modern e-commerce platform built with FastAPI and React, featuring secure authentication, payment processing, and image management.

## Current Progress

- ✅ Backend API setup with FastAPI
- ✅ Database models and schemas
- ✅ User authentication with JWT (access/refresh tokens)
- ✅ Product management with image upload
- ✅ Stripe payment integration
- ✅ Role-based access control
- 🔄 Cart and Order system (In Progress)
- ⏳ Frontend development (Planned)

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **PostgreSQL**: Primary database
- **JWT**: Authentication tokens
- **Alembic**: Database migrations

### External Services
- **Stripe**: Payment processing
- **Cloudinary**: Image storage and optimization

### Development Tools
- **Python 3.10+**
- **Poetry/pip**: Dependency management
- **pytest**: Testing framework
- **uvicorn**: ASGI server

## Project Structure

```
lotuslynx/
│
├── .env                      # Environment variables
├── .gitignore                # Standard Python + frontend ignores
├── requirements.txt          # With dev dependencies separated
├── Dockerfile                # Multi-stage build
├── docker-compose.yml        # App + DB + Redis + Frontend
├── alembic.ini               # Migration config
│
├── backend/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI app (lifespan setup)
│   ├── database.py           # SQLAlchemy async/sync setup
│   ├── utils.py              # Miscellaneous helpers
│   │
│   ├── core/                 # Critical utilities
│   │   ├── __init__.py       # Exports config, auth
│   │   ├── auth.py           # JWT logic (access/refresh)
│   │   ├── config.py         # Pydantic settings
│   │   └── security.py       # OAuth2 schemes
│   │
│   ├── dependencies/         # Reusable FastAPI deps
│   │   ├── __init__.py       # Clean exports
│   │   ├── auth.py           # get_current_user
│   │   ├── roles.py          # require_admin/require_editor
│   │   ├── payments.py       # stripe_payment
│   │   └── database.py       # get_db (session)
│   │
│   ├── models/               # SQLAlchemy ORM
│   │   ├── __init__.py       # Exposes models
│   │   ├── user.py           # User, roles
│   │   ├── product.py        # Product, categories
│   │   ├── cart.py           # Cart, CartItem
│   │   └── order.py          # Order, OrderItem
│   │
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py       # Exposes schemas
│   │   ├── user.py           # UserCreate, UserResponse
│   │   ├── product.py        # Product CRUD schemas
│   │   ├── cart.py           # Cart operations
│   │   └── order.py          # Order workflows
│   │
│   ├── routers/              # API endpoints
│   │   ├── __init__.py       # Router aggregation
│   │   ├── auth.py           # /auth/*
│   │   ├── products.py       # /products/* (with Cloudinary)
│   │   ├── cart.py           # /cart/*
│   │   └── orders.py         # /orders/*
│   │
│   ├── services/             # External integrations
│   │   ├── __init__.py
│   │   ├── payment.py        # Stripe/PayPal
│   │   ├── email.py          # SMTP templates
│   │   └── cloudinary.py     # Image upload helpers
│   │
│   └── tests/                # Pytest
│       ├── __init__.py
│       ├── conftest.py       # Fixtures
│       ├── test_auth.py
│       └── test_products.py
│
├── frontend/                 # Static files
│   ├── static/               # Built assets (Vite/Webpack)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/            # Jinja2 templates
│       ├── base.html         # Layout
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── admin/
│           ├── dashboard.html
│           └── products.html
│
├── alembic/                  # Migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
└── scripts/                  # Deployment/DB
    ├── seed_db.py            # Test data
    └── backup_db.sh          # PostgreSQL dumps
```

## Features

### Implemented
- JWT Authentication with refresh tokens
- Role-based access control (Admin/Editor/User)
- Product management with image upload
- Secure payment processing with Stripe
- Cloudinary integration for image storage

### Planned
- Shopping cart functionality
- Order management
- User profiles
- Admin dashboard
- Email notifications
- React frontend
- Docker containerization

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lotuslynx.git
cd lotuslynx
```

2. Set up environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run development server:
```bash
uvicorn backend.main:app --reload
```

## Development Roadmap

1. **Phase 1** (Current)
   - Complete core backend functionality
   - Implement comprehensive testing
   - Document API endpoints

2. **Phase 2**
   - Develop React frontend
   - Add shopping cart
   - Implement order system

3. **Phase 3**
   - Add admin dashboard
   - Email integration
   - Performance optimization

4. **Phase 4**
   - Docker containerization
   - CI/CD setup
   - Production deployment

## Contributing

Currently, this is a personal project in development. Contributions might be welcome in the future.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Author

Pankaj Kushwaha - ([GitHub](https://github.com/pankaj085 "My GitHub"))