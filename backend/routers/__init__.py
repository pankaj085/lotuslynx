from .auth_router import router as auth_router
from .product_router import router as product_router
# from .cart_router import router as cart_router
# from .order_router import router as order_router

# Export all routers
__all__ = [
    "auth_router",
    "product_router",
    # "cart_router",
    # "order_router"
]