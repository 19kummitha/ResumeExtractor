from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
from app.database import get_db
from app.services.resume_parser import parse_resume_with_openai
from auth.auth import JWTBearer
router = APIRouter(dependencies=[Depends(JWTBearer())])

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    pdf = PdfReader(file.file)
    text = "\n".join([page.extract_text() or "" for page in pdf.pages])
    parsed_data = await parse_resume_with_openai(text)
    return parsed_data
