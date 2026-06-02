from fastapi import Depends, status, HTTPException, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from app import models
from ..schema import TicketResponse
from ..oauth2 import get_current_admin

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# view all tickets
# for users to see all their tickets
@router.get("", response_model=TicketResponse)
async def get_all_tickets(db: Session = Depends(get_db), business_name: str = "", department: str = "", priority: str = "", confidence: float = 0):
    # search ticket
    all_tickets = db.query(models.Tickets).filter(models.Tickets.owner.business_name == business_name).filter(models.Tickets.department == department).filter(models.Tickets.priority == priority).filter(models.Tickets.confidence == confidence).all()
        
    if all_tickets is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ticket available")
   
    return all_tickets

# get all tickets of a user
@router.get("/all_tickets/{user_id}", response_model=TicketResponse)
async def get_user_tickets(id: int, db: Session = Depends(get_db)):
    # search ticket
     
    tickets = db.query(models.Tickets).filter(models.Tickets.user_id == id).all
        
    if tickets is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
   
    return tickets

# get one ticket
@router.get("/{id}", response_model=TicketResponse)
async def get_one_ticket(
    id: int, 
    current_admin : Session = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ticket = db.query(models.Tickets).filter(models.Tickets.id == id).first()
    
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        
    
    if current_admin.role != "Admin":
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You do not have permission to view this ticket"
    )
    return ticket

