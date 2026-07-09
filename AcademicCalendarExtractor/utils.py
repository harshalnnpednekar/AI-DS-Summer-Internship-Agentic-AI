import pdfplumber
import fitz
import logging
import os

logger = logging.getLogger(__name__)

def extract_with_pdfplumber(pdf_path: str) -> str:
    extracted_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                logger.error(f"Empty PDF: {pdf_path} contains no pages.")
                return ""
                
            for i, page in enumerate(pdf.pages):
                try:
                    width = page.width
                    height = page.height
                    bbox = (0, height * 0.08, width, height * 0.92)
                    cropped_page = page.within_bbox(bbox)
                    
                    text = cropped_page.extract_text()
                    if text:
                        extracted_text.append(text)
                    
                    tables = cropped_page.extract_tables()
                    for table in tables:
                        for row in table:
                            row_text = "\t".join([str(cell).strip() if cell else "" for cell in row])
                            if row_text.strip():
                                extracted_text.append(row_text)
                    logger.info(f"Page {i+1} read successfully.")
                except Exception as e:
                    logger.error(f"Unreadable page {i+1} in {pdf_path} using pdfplumber: {e}")
                    
    except Exception as e:
        logger.error(f"Corrupted or invalid PDF {pdf_path} for pdfplumber: {e}")
        raise
                        
    return "\n".join(extracted_text)

def extract_with_pymupdf(pdf_path: str) -> str:
    extracted_text = []
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            logger.error(f"Empty PDF: {pdf_path} contains no pages.")
            return ""
            
        for i, page in enumerate(doc):
            try:
                rect = page.rect
                clip = fitz.Rect(0, rect.height * 0.08, rect.width, rect.height * 0.92)
                text = page.get_text("text", clip=clip)
                if text:
                    extracted_text.append(text)
                logger.info(f"Page {i+1} read successfully via PyMuPDF.")
            except Exception as e:
                logger.error(f"Unreadable page {i+1} in {pdf_path} using PyMuPDF: {e}")
                
        doc.close()
    except Exception as e:
        logger.error(f"Corrupted or invalid PDF {pdf_path} for PyMuPDF: {e}")
        raise
        
    return "\n".join(extracted_text)

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        raise FileNotFoundError(f"File not found: {pdf_path}")
        
    try:
        return extract_with_pdfplumber(pdf_path)
    except Exception:
        logger.warning(f"Falling back to PyMuPDF...")
        try:
            return extract_with_pymupdf(pdf_path)
        except Exception as fallback_e:
            logger.error(f"Both extractors failed for {pdf_path}. It might be severely corrupted.")
            raise RuntimeError(f"Failed to extract text from PDF.")
