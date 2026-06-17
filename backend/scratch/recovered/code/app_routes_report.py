from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.report_service import report_service_instance
import uuid
from typing import Dict, Any
import os

router = APIRouter(prefix="/report", tags=["Report Generation"])

class ReportRequest(BaseModel):
    analysis_data: Dict[str, Any]

@router.post("/generate")
async def generate_report(request: ReportRequest):
    if not request.analysis_data:
        raise HTTPException(status_code=400, detail="Analysis data is required.")
    
    report_id = str(uuid.uuid4())
    
    json_path = report_service_instance.generate_json_report(request.analysis_data, report_id)
    excel_path = report_service_instance.generate_excel_report(request.analysis_data, report_id)
    pdf_path = report_service_instance.generate_pdf_report(request.analysis_data, report_id)
    
    return {
        "report_id": report_id,
        "json_url": f"/report/download/{report_id}?format=json",
        "excel_url": f"/report/download/{report_id}?format=xlsx",
        "pdf_url": f"/report/download/{report_id}?format=pdf"
    }

@router.get("/download/{report_id}")
async def download_report(report_id: str, format: str = "json"):
    from app.services.report_service import REPORTS_DIR
    
    filepath = os.path.join(REPORTS_DIR, f"{report_id}.{format}")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found.")
    
    return FileResponse(filepath, filename=f"report_{report_id}.{format}")
