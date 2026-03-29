from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.dataset import DatasetProfile
from app.services.csv_ingestion import CSVIngestionError, read_csv_upload
from app.services.profiling_service import profile_dataset

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post(
    "/profile",
    response_model=DatasetProfile,
    status_code=status.HTTP_200_OK,
)
def upload_and_profile_dataset(file: UploadFile = File(...)) -> DatasetProfile:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV uploads are supported.",
        )

    try:
        dataframe = read_csv_upload(file)
    except CSVIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return profile_dataset(dataframe, dataset_name=file.filename)
