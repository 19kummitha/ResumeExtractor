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




# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from sqlalchemy.orm import Session
# from PyPDF2 import PdfReader
# import tempfile
# import os
# import cv2
# import numpy as np
# import pytesseract
# from pdf2image import convert_from_bytes
# from io import BytesIO
# import imghdr
# import logging
# import traceback

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# from app.database import get_db
# from app.services.resume_parser import parse_resume_with_openai
# from auth.auth import JWTBearer

# router = APIRouter(dependencies=[Depends(JWTBearer())])

# def extract_text_from_pdf(file_bytes):
#     """Extract text from PDF using PyPDF2, handles text-based PDFs"""
#     pdf = PdfReader(BytesIO(file_bytes))
#     text = "\n".join([page.extract_text() or "" for page in pdf.pages])
#     return text

# def has_extractable_text(file_bytes):
#     """Check if PDF has extractable text"""
#     try:
#         pdf = PdfReader(BytesIO(file_bytes))
#         for page in pdf.pages:
#             text = page.extract_text()
#             # If any page has a reasonable amount of text, consider it text-based
#             if text and len(text.strip()) > 100:  # Arbitrary threshold
#                 return True
#         return False
#     except Exception as e:
#         logger.warning(f"Error checking for extractable text: {str(e)}")
#         return False

# def extract_text_with_ocr(file_bytes):
#     """Extract text from image-based PDF using OCR"""
#     try:
#         logger.info("Starting OCR extraction from PDF")
#         # Convert PDF to images
#         with tempfile.TemporaryDirectory() as temp_dir:
#             # convert_from_bytes expects raw bytes, not BytesIO
#             logger.info(f"Converting PDF to images, bytes length: {len(file_bytes)}")
#             images = convert_from_bytes(file_bytes)
#             logger.info(f"Converted {len(images)} pages")
#             texts = []
            
#             for i, image in enumerate(images):
#                 try:
#                     # Save image to temp file
#                     image_path = os.path.join(temp_dir, f'page_{i}.png')
#                     image.save(image_path, 'PNG')
#                     logger.info(f"Saved page {i} to {image_path}")
                    
#                     # Read image with OpenCV
#                     img = cv2.imread(image_path)
#                     if img is None:
#                         logger.warning(f"OpenCV could not read image at {image_path}")
#                         continue
                    
#                     # Convert to grayscale
#                     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
#                     # Apply thresholding to enhance text
#                     _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
#                     # Extract text with pytesseract
#                     logger.info(f"Running OCR on page {i}")
#                     text = pytesseract.image_to_string(threshold)
#                     logger.info(f"OCR complete for page {i}, extracted {len(text)} characters")
#                     texts.append(text)
#                 except Exception as e:
#                     logger.error(f"Error processing page {i}: {str(e)}")
#                     logger.error(traceback.format_exc())
        
#         result = "\n".join(texts)
#         logger.info(f"Total extracted text: {len(result)} characters")
#         return result
#     except Exception as e:
#         logger.error(f"Error in OCR extraction: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise

# def extract_text_from_image(image_bytes):
#     """Extract text from image using OCR"""
#     try:
#         logger.info("Starting OCR extraction from image")
#         logger.info(f"Image bytes length: {len(image_bytes)}")
        
#         # Convert bytes to numpy array for OpenCV
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
#         if img is None:
#             logger.warning("OpenCV could not decode the image")
#             raise ValueError("Invalid image format or corrupted image data")
        
#         logger.info(f"Image decoded, shape: {img.shape}")
        
#         # Convert to grayscale
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
#         # Apply thresholding to enhance text
#         _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
#         # Extract text with pytesseract
#         logger.info("Running OCR on image")
#         text = pytesseract.image_to_string(threshold)
#         logger.info(f"OCR complete, extracted {len(text)} characters")
        
#         return text
#     except Exception as e:
#         logger.error(f"Error in image OCR extraction: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise

# def is_valid_image(file_content):
#     """Check if the file content is a valid image"""
#     image_type = imghdr.what(None, file_content)
#     return image_type is not None

# @router.post("/upload")
# async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     try:
#         # Validate file extension
#         file_ext = os.path.splitext(file.filename.lower())[1]
#         valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
#         if file_ext not in valid_extensions:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Unsupported file format. Please upload a PDF or image file ({', '.join(valid_extensions)})"
#             )
        
#         # Read file content into memory
#         file_content = await file.read()
#         logger.info(f"Received file: {file.filename}, size: {len(file_content)} bytes")
        
#         try:
#             file_ext = os.path.splitext(file.filename.lower())[1]
#             logger.info(f"File extension: {file_ext}")
            
#             # Process based on file type
#             if file_ext == '.pdf':
#                 # Try to handle potential PDF errors by attempting direct OCR if standard methods fail
#                 try:
#                     # First try standard PDF text extraction
#                     if has_extractable_text(file_content):
#                         logger.info("PDF has extractable text, using standard extraction")
#                         text = extract_text_from_pdf(file_content)
#                     else:
#                         logger.info("PDF doesn't have extractable text, using OCR")
#                         text = extract_text_with_ocr(file_content)
#                 except Exception as pdf_error:
#                     logger.error(f"PDF processing failed: {str(pdf_error)}")
#                     logger.info("Attempting to treat PDF as an image...")
                    
#                     # If the PDF is problematic, try using Poppler (pdf2image) to convert first page to image
#                     # and then apply OCR on that image
#                     try:
#                         with tempfile.TemporaryDirectory() as temp_dir:
#                             output_file = os.path.join(temp_dir, "pdf_first_page.png")
                            
#                             # Save PDF content to a temporary file
#                             temp_pdf = os.path.join(temp_dir, "temp.pdf")
#                             with open(temp_pdf, "wb") as f:
#                                 f.write(file_content)
                            
#                             # Try a different approach with pdf2image
#                             from pdf2image import convert_from_path
#                             logger.info(f"Trying to convert PDF from path: {temp_pdf}")
#                             images = convert_from_path(temp_pdf, first_page=1, last_page=1)
                            
#                             if images:
#                                 logger.info("Successfully extracted first page as image")
#                                 images[0].save(output_file, "PNG")
                                
#                                 # Now OCR the image
#                                 with open(output_file, "rb") as img_file:
#                                     img_bytes = img_file.read()
#                                     text = extract_text_from_image(img_bytes)
#                             else:
#                                 raise ValueError("No images extracted from PDF")
#                     except Exception as alternate_error:
#                         logger.error(f"Alternative PDF processing failed: {str(alternate_error)}")
#                         # If all approaches fail, raise the original error
#                         raise pdf_error
#             else:
#                 # For image files, use OCR directly
#                 if is_valid_image(file_content):
#                     logger.info("Processing as image file")
#                     text = extract_text_from_image(file_content)
#                 else:
#                     logger.warning("Not a valid image file")
#                     raise HTTPException(
#                         status_code=400,
#                         detail="The uploaded file appears to be corrupted or not a valid image format."
#                     )
#         except Exception as e:
#             # Handle PDF parsing errors
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Error processing PDF: {str(e)}. Please ensure the file is a valid PDF document."
#             )
        
#         # If still no significant text found, raise an error
#         if not text or len(text.strip()) < 50:  # Arbitrary minimum length
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Could not extract sufficient text from the PDF. Please ensure the document is readable."
#             )
        
#         # Process with OpenAI
#         try:
#             parsed_data = await parse_resume_with_openai(text)
#             return parsed_data
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Error parsing resume data: {str(e)}"
#             )
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         # Catch all other unexpected errors
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")