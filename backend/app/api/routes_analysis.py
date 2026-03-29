from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.dashboard import DashboardPayload
from app.services.csv_ingestion import CSVIngestionError, read_csv_upload
from app.services.report_generator import build_dashboard

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "/dashboard",
    response_model=DashboardPayload,
    status_code=status.HTTP_200_OK,
)
def analyze_dataset_to_dashboard(
    file: UploadFile = File(...),
    question: str = Form(...),
) -> DashboardPayload:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV uploads are supported.",
        )
    if not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A business question is required.",
        )

    try:
        dataframe = read_csv_upload(file)
    except CSVIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return build_dashboard(dataframe, dataset_name=file.filename, question=question)
