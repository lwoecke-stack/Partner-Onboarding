"""Report generation and export routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.api.dependencies import DBSession
from app.services.report_service import ReportService
from app.services.export_service import ExportService
from app.services.backup_service import BackupService

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])


@router.post("/{lead_id}/all")
def generate_all_reports(lead_id: int, db: DBSession):
    svc = ReportService(db)
    try:
        reports = svc.generate_all_reports(lead_id)
        return {k: str(v) for k, v in reports.items()}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{lead_id}/history")
def download_history_report(lead_id: int, db: DBSession):
    svc = ReportService(db)
    try:
        path = svc.generate_history_report(lead_id)
        return FileResponse(str(path), media_type="application/pdf", filename=path.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{lead_id}/eligibility")
def download_eligibility_report(lead_id: int, db: DBSession):
    svc = ReportService(db)
    try:
        path = svc.generate_eligibility_report(lead_id)
        return FileResponse(str(path), media_type="application/pdf", filename=path.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{lead_id}/damex")
def download_damex_report(lead_id: int, db: DBSession):
    svc = ReportService(db)
    try:
        path = svc.generate_damex_report(lead_id)
        return FileResponse(str(path), media_type="application/pdf", filename=path.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{lead_id}/compliance")
def download_compliance_report(lead_id: int, db: DBSession):
    svc = ReportService(db)
    try:
        path = svc.generate_compliance_report(lead_id)
        return FileResponse(str(path), media_type="application/pdf", filename=path.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/export/csv")
def export_csv(db: DBSession):
    svc = ExportService(db)
    path = svc.export_csv()
    return {"path": str(path)}


@router.post("/export/json")
def export_json(db: DBSession):
    svc = ExportService(db)
    path = svc.export_json()
    return {"path": str(path)}


@router.post("/export/xlsx")
def export_xlsx(db: DBSession):
    svc = ExportService(db)
    path = svc.export_xlsx()
    return {"path": str(path)}


@router.post("/backup")
def create_backup():
    svc = BackupService()
    path = svc.create_backup("manual-api")
    return {"path": str(path)}


@router.get("/backup/list")
def list_backups():
    svc = BackupService()
    backups = svc.list_backups()
    return {"backups": [str(b) for b in backups], "count": len(backups)}
