from fastapi import Depends, HTTPException, APIRouter, status
from ..schema import HealthResponse, MetricsResponse
from ..load_model import model, vectorizer, label_encoder
from ..database import get_db
from sqlalchemy.orm import Session
from app import models
from ..oauth2 import get_current_admin, get_current_user
from sqlalchemy import func

router = APIRouter(
    prefix='/model',
    tags=["Models"]
)

@router.get("/health", response_model=HealthResponse)
def get_health():
    try:
        if model is not None and vectorizer is not None and label_encoder is not None:
            return {
                "status": "Healthy",
                "model_loaded": True,
                "vectorizer_loaded": True,
                "version": "1.0.0"
            }
            
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model files not found")
    
@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db), current_user: Session = Depends(get_current_user)):
    
    # if current_user.role != "Admin":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to perform action")
    
    metrics = db.query(
        func.count(models.Tickets.id),
        func.sum(models.Tickets.confidence),
        func.count(models.Tickets.latency),
        func.sum(models.Tickets.latency)
    ).first()

    all_tickets_count = int(metrics[0]) or 0
    all_confidence_sum = float(metrics[1]) or 0.0
    count_all_latencies = int(metrics[2]) or 0
    sum_total_latencies = float(metrics[3]) or 0.0

    if all_tickets_count > 0:
        clean_confidence = all_confidence_sum / all_tickets_count
    else:
        clean_confidence = 0.0

    if count_all_latencies > 0:
        clean_latency = sum_total_latencies / count_all_latencies
    else:
        clean_latency = 0.0

    distribution = db.query(
        models.Tickets.department,
        func.count(models.Tickets.id)
    ).group_by(models.Tickets.department).all()

    return {
    "total_tickets": all_tickets_count,
    "avg_confidence": round(clean_confidence, 2),
    "average_response_time_ms": round(clean_latency, 2),
    "model_version": "1.0.0",
    "routing_distribution": {row[0]: int(row[1]) for row in distribution}
}