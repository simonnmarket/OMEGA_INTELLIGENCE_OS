from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    report_type = Column(String, nullable=False)  # performance, risk, trading, etc.
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    parameters = Column(JSON)  # Store report generation parameters
    generated_at = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active, archived, deleted
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="reports")
    user = relationship("User", back_populates="reports")
    
    def to_dict(self):
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "user_id": self.user_id,
            "report_type": self.report_type,
            "title": self.title,
            "content": self.content,
            "parameters": self.parameters,
            "generated_at": self.generated_at.isoformat(),
            "status": self.status
        } 