from typing import Generator
from sqlalchemy.orm import Session
from ..database import SessionLocal
def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Usage:
        @router.get("/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()