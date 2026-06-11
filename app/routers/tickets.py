from fastapi import Depends, status, HTTPException, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from app import models
from ..schema import CreateTicketRequest, TicketResponse
from ..oauth2 import get_current_user, get_current_admin
from app.load_model import model, label_encoder, vectorizer
import pandas as pd
import torch
from ..utils import generated_tags, generate_priority
import time
from app import models

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponse)
async def create_ticket(
    new_ticket: CreateTicketRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check if user exists
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to perform action")
    
    # turn request into a dataframe
    ticket_data = {
    "body": [new_ticket.body],
    "subject": [new_ticket.subject],
    "type": [new_ticket.type]
    }

    X = pd.DataFrame(ticket_data)
    
    # vectorize the data
    vectorized_data = vectorizer.transform(X)
    
    # turn data into tensors
    X_test = torch.from_numpy(vectorized_data).float()
    
    # start timer 
    start_time = time.perf_counter()
    # run inference
    model.eval()
    with torch.inference_mode():
        logits = model(X_test)
        # tuen them into probabilities using softmax
        preds = torch.argmax(torch.softmax(logits, dim=1)).item()
        probabilities = torch.softmax(logits, dim=1)
    confidence_value = float(round(torch.max(probabilities, dim=1).values.item(), 2))
    
    # get the predicted department using inverse transform
    encoder = label_encoder
    pred_department = encoder.inverse_transform([preds])[0]
    department = pred_department
    
    # generate tags
    full_text = new_ticket.subject + new_ticket.body
    tags, extracted_keywords, highest_severity = generated_tags(full_text)
    # get user's tier
    account_tier = user.account_tier
    priority = generate_priority(list(tags), account_tier)
    
    # end timer
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    ticket_response = {
        "user_id": user.id,
        "subject": new_ticket.subject,
        "body": new_ticket.body,
        "department": department,
        "confidence": confidence_value,
        "priority": priority,
        "tags": list(tags),
        "extracted_keywords": list(extracted_keywords),
        "status": "Queued",
        "latency": round(latency_ms)
    }
    
    try:
        ticket = models.Tickets(**ticket_response)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        return ticket
    
    except Exception as e:
        db.rollback()
        
        print(f"Error creating ticket: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred while creating your ticket",
        )
        
# for users to see all their tickets
@router.get("/all", response_model=list[TicketResponse])
async def get_user_tickets(current_user: models.User = Depends(get_current_user)):
    # search ticket
    all_tickets = current_user.incidents
    
    if current_user.id != all_tickets[0].user_id:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You do not have permission to view this ticket"
    )
        
    if all_tickets is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ticket available")
   
    return all_tickets

