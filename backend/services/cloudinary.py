import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from core.config import settings
import logging
from models.product import Product

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_to_cloudinary(file, product_id: str) -> str:
    """
    Upload file to Cloudinary and return the URL
    """
    try:
        # Upload file to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder="products",  # Organize images in a folder
            public_id=f"product_{product_id}",  # Set custom public ID
            overwrite=True,  # Override if image exists
            resource_type="auto"  # Auto-detect file type
        )
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

def delete_from_cloudinary(image_url: str) -> bool:
    """
    Delete image from Cloudinary using the URL
    Returns True if successful, False otherwise
    """
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/public_id
        public_id = image_url.split("/")[-1].split(".")[0]
        
        # Delete the image
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        # Log error but don't raise exception as this is cleanup
        print(f"Failed to delete image from Cloudinary: {str(e)}")
        return False

def handle_product_image(product: Product) -> bool:
    """
    Helper function to handle product image deletion
    
    Args:
        product (Product): Product model instance with image_url
        
    Returns:
        bool: True if deletion was successful or no image existed
    """
    if product.image_url is not None:
        try:
            image_url = str(product.image_url)
            success = delete_from_cloudinary(image_url)
            if not success:
                logging.error(f"Failed to delete image for product {product.id}")
                return False
            return True
        except Exception as e:
            logging.error(f"Error handling product image: {str(e)}")
            return False
    return True