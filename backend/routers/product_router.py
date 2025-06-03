from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import stripe
from decimal import Decimal
import logging
from database import get_db

# Set up logger
logger = logging.getLogger(__name__)

# Dependencies
from dependencies import get_db, require_admin
from models.product import Product
from schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductUpdate,
    ProductWithPrice
)
from services.cloudinary import upload_to_cloudinary, delete_from_cloudinary, handle_product_image

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}}
)

# --------------------------------
# Public Routes
# --------------------------------

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, le=500, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    db: Session = Depends(get_db)
):
    """
    List all products with optional filters:
    - Pagination (skip/limit)
    - Category filter
    - Price range
    """
    query = db.query(Product)

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed product information by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

# --------------------------------
# Admin-Only Routes
# --------------------------------

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product (Admin only)"""
    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be positive"
        )

    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """Update product details (Admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.dict(exclude_unset=True)
    
    if 'price' in update_data and update_data['price'] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be positive"
        )

    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """Delete a product (Admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Handle image deletion
    handle_product_image(product)

    db.delete(product)
    db.commit()
    return None

# --------------------------------
# Image Management
# --------------------------------

@router.post(
    "/{product_id}/upload-image",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def upload_product_image(
    product_id: int,
    file: UploadFile = File(..., description="Image file (JPEG/PNG)"),
    db: Session = Depends(get_db)
):
    """Upload product image to Cloudinary (Admin only)"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete old image using helper function
    handle_product_image(product)

    # Upload new image
    image_url = upload_to_cloudinary(file, str(product_id))
    product.image_url.set(image_url) if hasattr(product.image_url, "set") else setattr(product, "image_url", image_url)
    db.commit()

    return {"image_url": image_url}

# --------------------------------
# Stripe Integration
# --------------------------------

@router.post("/{product_id}/create-payment-intent", response_model=ProductWithPrice)
def create_payment_intent(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Create Stripe PaymentIntent for checkout"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # Convert SQLAlchemy Column to Decimal for precise calculation
        price = Decimal(str(product.price))
        amount = int(price * 100)  # Convert to cents
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "product_id": str(product.id),
                "product_name": str(product.name)
            }
        )
        
        return {
            "product": product,
            "client_secret": intent.client_secret,
            "amount": amount
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid price format: {str(e)}"
        )
    except stripe.StripeError as e:
        # Get HTTP status from Stripe error or default to 400
        status_code = getattr(e, 'http_status', 400)
        # Get user message or fallback to error string
        error_message = getattr(e, 'user_message', str(e))
        raise HTTPException(
            status_code=status_code,
            detail=error_message
        )
    except Exception as e:
        # Log unexpected errors but don't expose details to client
        logger.error(f"Unexpected error in payment processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing the payment"
        )