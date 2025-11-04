"""Dashboard routes for role-based analytics and overviews."""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.lead import Lead, LeadStatus
from ...models.user import User, UserRole
from ...models.assignment import LeadAssignment
from ...utils.auth import get_current_active_user, require_role


router = APIRouter()


@router.get("/sales-rep")
def get_sales_rep_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SALES_REP])),
) -> Dict:
    """Get dashboard data for sales rep - their own leads and stats."""
    
    # Get leads created by this sales rep
    my_leads = db.query(Lead).filter(Lead.created_by == current_user.id).all()
    
    # Calculate statistics
    total_leads = len(my_leads)
    hot_leads = sum(1 for l in my_leads if l.classification == "hot")
    warm_leads = sum(1 for l in my_leads if l.classification == "warm")
    cold_leads = sum(1 for l in my_leads if l.classification == "cold")
    
    avg_score = sum(l.current_score for l in my_leads) / total_leads if total_leads > 0 else 0
    
    # Status breakdown
    status_counts = {}
    for status in LeadStatus:
        status_counts[status.value] = sum(1 for l in my_leads if l.status == status)
    
    # Recent leads (last 10)
    recent_leads = sorted(my_leads, key=lambda x: x.created_at, reverse=True)[:10]
    
    return {
        "user": {
            "id": str(current_user.id),
            "name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role.value
        },
        "statistics": {
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "warm_leads": warm_leads,
            "cold_leads": cold_leads,
            "average_score": round(avg_score, 2),
            "status_breakdown": status_counts
        },
        "recent_leads": [
            {
                "id": str(lead.id),
                "name": lead.name,
                "email": lead.email,
                "score": lead.current_score,
                "classification": lead.classification,
                "status": lead.status.value,
                "created_at": lead.created_at.isoformat()
            }
            for lead in recent_leads
        ]
    }


@router.get("/manager")
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN])),
) -> Dict:
    """Get dashboard data for manager - overview of all sales reps."""
    
    # Get all sales reps
    sales_reps = db.query(User).filter(User.role == UserRole.SALES_REP).all()
    
    # Get stats for each sales rep
    rep_stats = []
    for rep in sales_reps:
        rep_leads = db.query(Lead).filter(Lead.created_by == rep.id).all()
        
        total = len(rep_leads)
        hot = sum(1 for l in rep_leads if l.classification == "hot")
        warm = sum(1 for l in rep_leads if l.classification == "warm")
        cold = sum(1 for l in rep_leads if l.classification == "cold")
        avg_score = sum(l.current_score for l in rep_leads) / total if total > 0 else 0
        
        rep_stats.append({
            "rep": {
                "id": str(rep.id),
                "name": rep.full_name,
                "email": rep.email,
                "username": rep.username
            },
            "statistics": {
                "total_leads": total,
                "hot_leads": hot,
                "warm_leads": warm,
                "cold_leads": cold,
                "average_score": round(avg_score, 2)
            }
        })
    
    # Overall team statistics
    all_leads = db.query(Lead).all()
    team_total = len(all_leads)
    team_hot = sum(1 for l in all_leads if l.classification == "hot")
    team_warm = sum(1 for l in all_leads if l.classification == "warm")
    team_cold = sum(1 for l in all_leads if l.classification == "cold")
    team_avg_score = sum(l.current_score for l in all_leads) / team_total if team_total > 0 else 0
    
    return {
        "manager": {
            "id": str(current_user.id),
            "name": current_user.full_name,
            "email": current_user.email
        },
        "team_statistics": {
            "total_sales_reps": len(sales_reps),
            "total_leads": team_total,
            "hot_leads": team_hot,
            "warm_leads": team_warm,
            "cold_leads": team_cold,
            "average_score": round(team_avg_score, 2)
        },
        "sales_reps": rep_stats
    }


@router.get("/owner")
def get_owner_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
) -> Dict:
    """Get dashboard data for owner - full system overview with all analytics."""
    
    # Get all users
    all_users = db.query(User).all()
    sales_reps = [u for u in all_users if u.role == UserRole.SALES_REP]
    managers = [u for u in all_users if u.role == UserRole.MANAGER]
    
    # Get all leads
    all_leads = db.query(Lead).all()
    
    # Overall statistics
    total_leads = len(all_leads)
    hot_leads = sum(1 for l in all_leads if l.classification == "hot")
    warm_leads = sum(1 for l in all_leads if l.classification == "warm")
    cold_leads = sum(1 for l in all_leads if l.classification == "cold")
    avg_score = sum(l.current_score for l in all_leads) / total_leads if total_leads > 0 else 0
    
    # Status breakdown
    status_counts = {}
    for status in LeadStatus:
        status_counts[status.value] = sum(1 for l in all_leads if l.status == status)
    
    # Source breakdown
    source_counts = {}
    for lead in all_leads:
        source = lead.source or "unknown"
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Top performing sales reps
    rep_performance = []
    for rep in sales_reps:
        rep_leads = db.query(Lead).filter(Lead.created_by == rep.id).all()
        if rep_leads:
            rep_avg = sum(l.current_score for l in rep_leads) / len(rep_leads)
            rep_hot = sum(1 for l in rep_leads if l.classification == "hot")
            rep_stats = {
                "rep": {
                    "id": str(rep.id),
                    "name": rep.full_name,
                    "email": rep.email
                },
                "total_leads": len(rep_leads),
                "hot_leads": rep_hot,
                "average_score": round(rep_avg, 2),
                "conversion_rate": round((rep_hot / len(rep_leads)) * 100, 2) if rep_leads else 0
            }
            rep_performance.append(rep_stats)
    
    # Sort by average score
    rep_performance.sort(key=lambda x: x["average_score"], reverse=True)
    
    # Recent activity (last 20 leads)
    recent_leads = sorted(all_leads, key=lambda x: x.created_at, reverse=True)[:20]
    
    return {
        "owner": {
            "id": str(current_user.id),
            "name": current_user.full_name,
            "email": current_user.email
        },
        "system_statistics": {
            "total_users": len(all_users),
            "sales_reps": len(sales_reps),
            "managers": len(managers),
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "warm_leads": warm_leads,
            "cold_leads": cold_leads,
            "average_score": round(avg_score, 2),
            "status_breakdown": status_counts,
            "source_breakdown": source_counts
        },
        "top_performers": rep_performance[:10],  # Top 10
        "recent_leads": [
            {
                "id": str(lead.id),
                "name": lead.name,
                "email": lead.email,
                "score": lead.current_score,
                "classification": lead.classification,
                "status": lead.status.value,
                "source": lead.source,
                "created_by": str(lead.created_by) if lead.created_by else None,
                "created_at": lead.created_at.isoformat()
            }
            for lead in recent_leads
        ]
    }


@router.get("/sales-rep/leads")
def get_sales_rep_leads(
    page: int = 1,
    per_page: int = 25,
    sort: str = "score",
    classification: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SALES_REP])),
) -> Dict:
    """Get paginated leads table for sales rep dashboard."""
    
    query = db.query(Lead).filter(Lead.created_by == current_user.id)
    
    # Filter by classification
    if classification and classification != "all":
        query = query.filter(Lead.classification == classification)
    
    # Sorting
    if sort == "score":
        query = query.order_by(desc(Lead.current_score))
    elif sort == "date":
        query = query.order_by(desc(Lead.created_at))
    elif sort == "name":
        query = query.order_by(Lead.name)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * per_page
    leads = query.offset(offset).limit(per_page).all()
    
    return {
        "leads": [
            {
                "id": str(lead.id),
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source,
                "location": lead.location,
                "score": lead.current_score,
                "classification": lead.classification,
                "status": lead.status.value,
                "created_at": lead.created_at.isoformat(),
                "updated_at": lead.updated_at.isoformat()
            }
            for lead in leads
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

