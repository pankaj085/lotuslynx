# backend/routers/products_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import cloudinary
import cloudinary.uploader
from datetime import datetime
import stripe

# Dependencies and Models
from dependencies import get_db, require_admin
from models.product import Product
from schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductUpdate,
    ProductWithPrice
)
from core.config import settings

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# --------------------------------
# Cloudinary Image Helpers
# --------------------------------

def upload_to_cloudinary(file: UploadFile, product_id: int) -> str:
    """Uploads image to Cloudinary with product-specific folder"""
    try:
        result = cloudinary.uploader.upload(
            file.file,
            public_id=f"product_{product_id}_{datetime.now().timestamp()}",
            folder=f"lotuslynx/products/{product_id}",
            quality="auto",
            fetch_format="auto",
            width=1200,
            crop="limit"
        )
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )

def delete_from_cloudinary(image_url: str) -> bool:
    """Deletes image from Cloudinary"""
    try:
        public_id = image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception:
        return False

# --------------------------------
# Public Product Routes
# --------------------------------

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """
    List products with filters:
    - Pagination (skip/limit)
    - Category filter
    - Price range
    """
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
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
    """Get product details by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# --------------------------------
# Admin-Only Product Routes
# --------------------------------

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """Create new product (Admin only)"""
    # Validate price
    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
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
    
    # Prevent price being set to 0 or negative
    if 'price' in update_data and update_data['price'] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
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
    """Delete a product and its associated image"""
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete image if exists
    image_url = str(product.image_url) if product.image_url is not None else None
    if image_url:
        delete_from_cloudinary(image_url)

    # Delete product
    db.delete(product)
    db.commit()
    return None

# --------------------------------
# Image Management Routes
# --------------------------------

@router.post("/{product_id}/upload-image")
async def upload_product_image(
    product_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """Upload product image to Cloudinary (Admin only)"""
    # Validate file exists and has content type
    if not file or not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file upload"
        )

    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )

    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Delete old image if exists
        if product.image_url is not None:  # Check for None using SQLAlchemy's way
            image_url = str(product.image_url)  # Convert Column to str
            delete_from_cloudinary(image_url)

        # Upload new image
        image_url = upload_to_cloudinary(file, product_id)
        setattr(product, 'image_url', image_url)  # Use setattr for SQLAlchemy
        db.commit()

        return {"image_url": image_url}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image upload: {str(e)}"
        )

# --------------------------------
# Stripe Payment Integration
# --------------------------------

@router.post("/{product_id}/create-payment-intent", response_model=ProductWithPrice)
def create_payment_intent(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Create Stripe PaymentIntent for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # Get the actual price value and convert to cents
        price_value = float(str(product.price))  # Convert Column to string first
        amount = int(price_value * 100)  # Convert to cents
        
        # Create payment intent with proper type conversions
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "product_id": str(product.id),
                "product_name": str(product.name)
            },
            description=f"Purchase of {str(product.name)}"
        )

        return {
            "product": product,
            "client_secret": payment_intent.client_secret,
            "amount": amount
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid price format: {str(e)}"
        )
    except stripe.StripeError as e:  # Changed from stripe.error.StripeError
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.user_message)
        )