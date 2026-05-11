from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

# Re-export for convenience
DBSession = Depends(get_db)
