from fastapi import Depends, status, HTTPException, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from app import models
from ..schema import TicketResponse
from ..oauth2 import get_current_admin

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# view all tickets
@router.get(
    "",
    response_model=list[TicketResponse],
)
async def get_all_tickets(
    current_user: models.Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    business_name: str = "",
    department: str = "",
    priority: str = "",
    confidence: float = 0
):

    if current_user is None or current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform action",
        )

    all_tickets = (
        db.query(models.Tickets)
        .join(models.Tickets.owner)
        .filter(models.User.business_name.contains(business_name))
        .filter(models.Tickets.department.contains(department))
        .filter(models.Tickets.priority.contains(priority))
        .filter(models.Tickets.confidence == confidence if confidence > 0 else True)
    ).all()

    if all_tickets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No ticket available"
        )

    return all_tickets


# admin get all tickets of a user
@router.get("/user_tickets/{user_id}", response_model=list[TicketResponse])
async def get_user_tickets(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.Admin = Depends(get_current_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    all_tickets = user.incidents
    
    if current_user is None or current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform action",
        )
    # search user

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if all_tickets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ticket found for this user",
        )

    return all_tickets


# get one ticket
@router.get("/{id}", response_model=TicketResponse)
async def get_one_ticket(
    id: int,
    current_admin: models.Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket = db.query(models.Tickets).filter(models.Tickets.id == id).first()
    
    if current_admin is None or current_admin.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket",
        )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    return ticket
