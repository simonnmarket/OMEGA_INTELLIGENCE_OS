from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.report import Report
from app.models.portfolio import Portfolio
from app.services.report_generator import ReportGenerator
from app.schemas.report import ReportCreate, ReportResponse
from app.core.security import get_current_user

router = APIRouter()

@router.post("/portfolios/{portfolio_id}/reports", response_model=ReportResponse)
async def generate_report(
    portfolio_id: int,
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate a new report for a portfolio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    report_generator = ReportGenerator(portfolio_id, db)
    
    if report_type == "performance":
        report_data = report_generator.generate_performance_report(start_date, end_date)
    elif report_type == "trading":
        report_data = report_generator.generate_trading_report(start_date, end_date)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report type"
        )
    
    report = Report(
        portfolio_id=portfolio_id,
        user_id=current_user.id,
        report_type=report_data["report_type"],
        title=report_data["title"],
        content=report_data["content"],
        parameters=report_data["parameters"],
        generated_at=datetime.utcnow()
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report.to_dict()

@router.get("/portfolios/{portfolio_id}/reports", response_model=List[ReportResponse])
async def get_reports(
    portfolio_id: int,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all reports for a portfolio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    query = db.query(Report).filter(
        Report.portfolio_id == portfolio_id,
        Report.status == "active"
    )
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(Report.generated_at.desc()).all()
    
    return [report.to_dict() for report in reports]

@router.get("/portfolios/{portfolio_id}/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    portfolio_id: int,
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific report.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.portfolio_id == portfolio_id,
        Report.status == "active"
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report.to_dict()

@router.delete("/portfolios/{portfolio_id}/reports/{report_id}")
async def delete_report(
    portfolio_id: int,
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a report (soft delete).
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.portfolio_id == portfolio_id,
        Report.status == "active"
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.status = "deleted"
    db.commit()
    
    return {"message": "Report deleted successfully"}

@router.post("/portfolios/{portfolio_id}/reports/{report_id}/regenerate")
async def regenerate_report(
    portfolio_id: int,
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Regenerate a report with updated data.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    old_report = db.query(Report).filter(
        Report.id == report_id,
        Report.portfolio_id == portfolio_id
    ).first()
    
    if not old_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report_generator = ReportGenerator(portfolio_id, db)
    start_date = datetime.fromisoformat(old_report.parameters["start_date"])
    end_date = datetime.fromisoformat(old_report.parameters["end_date"])
    
    if old_report.report_type == "performance":
        report_data = report_generator.generate_performance_report(start_date, end_date)
    elif old_report.report_type == "trading":
        report_data = report_generator.generate_trading_report(start_date, end_date)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report type"
        )
    
    old_report.content = report_data["content"]
    old_report.generated_at = datetime.utcnow()
    db.commit()
    
    return old_report.to_dict() 