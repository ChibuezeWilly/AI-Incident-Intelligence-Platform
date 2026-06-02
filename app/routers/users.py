from fastapi import Depends, status, HTTPException, APIRouter
from ..schema import UserDetails, AllUsers
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import hash_password
from app import oauth2
from app import models

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("", response_model=list[AllUsers])
async def get_users(db: Session = Depends(get_db), current_user: Session = Depends(oauth2.get_current_admin)):
    # check if user is an admin before running
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to perform action")
    
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to perform action")
    else:
        users = db.query(models.User).all()
        if users is None:
            return []
        else:
            return users
    
# for users to see their account details
@router.get("/profile", response_model=UserDetails)
async def get_user(current_user: Session = Depends(oauth2.get_current_user)):
    # search user
    if current_user is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    return {
        "user": current_user,
        "tickets": current_user.incidents
    }
    
    
@router.get("/{id}", response_model=UserDetails)
async def get_one_user(id: int, current_admin: Session = Depends(oauth2.get_current_admin), db: Session = Depends(get_db)):
    # search user
    user = db.query(models.User).filter(models.User.id == id).first()
        
    if user is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    return {
        "user": user,
        "tickets": user.incidents if user.incidents is not None else []
    }
    