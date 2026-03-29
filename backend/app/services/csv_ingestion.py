from __future__ import annotations

from io import BytesIO

import pandas as pd
from fastapi import UploadFile


class CSVIngestionError(ValueError):
    """Raised when uploaded CSV data cannot be parsed reliably."""


def read_csv_upload(upload: UploadFile) -> pd.DataFrame:
    raw_bytes = upload.file.read()
    if not raw_bytes:
        raise CSVIngestionError("The uploaded file is empty.")

    try:
        dataframe = pd.read_csv(BytesIO(raw_bytes))
    except Exception as exc:  # pragma: no cover - pandas error shapes vary
        raise CSVIngestionError("The uploaded file could not be parsed as CSV.") from exc

    if dataframe.empty:
        raise CSVIngestionError("The uploaded CSV does not contain any rows.")

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    return dataframe
