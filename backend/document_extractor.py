import PyPDF2
import io
import docx

def _extract_text_from_pdf(pdf_bytes):
    """Extracts text from PDF bytes."""
    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def _extract_text_from_docx(docx_bytes):
    """Extracts text from a DOCX file bytes."""
    try:
        docx_stream = io.BytesIO(docx_bytes)
        document = docx.Document(docx_stream)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return None

def extract_text(file_bytes, filename):
    """Extracts text from a file based on its extension."""
    if filename.lower().endswith('.pdf'):
        return _extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith('.docx'):
        return _extract_text_from_docx(file_bytes)
    else:
        print(f"Unsupported file type: {filename}")
        return None
