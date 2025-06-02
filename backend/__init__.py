"""
LotusLynx Backend API
An e-commerce platform built with FastAPI

This package contains all backend components including:
- Database models and schemas
- API routes and endpoints
- Authentication and authorization
- Payment processing with Stripe
- Admin dashboard functionality
"""

__version__ = "1.0.0"
__author__ = "Pankaj Kushwaha"
__license__ = "MIT"
__copyright__ = "Copyright 2024 LotusLynx"

# Package metadata
from . import models
from . import schemas
from . import routers
from . import dependencies
from . import core

__all__ = [
    "models",
    "schemas",
    "routers",
    "dependencies",
    "core"
]

# API Information
API_VERSION = "v1"
API_TITLE = "LotusLynx API"
API_DESCRIPTION = "E-commerce Platform API with FastAPI"
API_PREFIX = "/api/v1"

# Package Configuration
DEBUG = False