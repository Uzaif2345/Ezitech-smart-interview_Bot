import os
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import traceback
import uuid  # Import the uuid module

from utils.resume_parser import extract_text_from_pdf, parse_resume  # Import your actual parsing functions

router = APIRouter()

@router.post("/upload_resume")
async def upload_resume_route(file: UploadFile = File(...)):
    try:
        # Sanitize filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"  # Generate a unique filename
        file_location = os.path.join("uploads", unique_filename)  # Use os.path.join for safety
        os.makedirs("uploads", exist_ok=True)  # Ensure the uploads directory exists

        with open(file_location, "wb") as f:
            f.write(await file.read())

        try:
            text = extract_text_from_pdf(file_location)
            parsed = parse_resume(text)

            return {
                "message": "Resume parsed successfully.",
                "data": parsed
            }
        except ValueError as ve:
            print(f"[VALUE ERROR] {ve}")
            raise HTTPException(status_code=400, detail=f"Resume parsing failed: {ve}")
        except Exception as e:
            print(f"[PARSING ERROR] {e}")
            raise HTTPException(status_code=500, detail="Error during resume parsing.")
        finally:
            os.remove(file_location)  # Delete the temporary file

    except Exception as e:
        print(f"[GENERAL ERROR] {e}")
        raise HTTPException(status_code=500, detail="Internal server error while parsing resume.")