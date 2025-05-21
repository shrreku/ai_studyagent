import os
# import textract
from PyPDF2 import PdfReader
from fastapi import HTTPException

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a given file (PDF, TXT, DOCX).
    """
    try:
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif extension == ".docx":
            # textract handles .docx and other formats
            # It might require external dependencies like antiword for .doc or tesseract for images
            # Ensure these are installed if those formats are needed.
            # For .docx, it typically uses python-docx.
            # byte_string = textract.process(file_path)
            # return byte_string.decode('utf-8')
            raise HTTPException(status_code=501, detail=".docx parsing is temporarily disabled.")
        else:
            # Fallback for other types if textract supports them, or raise error
            # try:
            #     byte_string = textract.process(file_path)
            #     return byte_string.decode('utf-8')
            # except Exception as e:
            #     raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}. Error: {e}")
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}.")

    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Error processing file {os.path.basename(file_path)}: {e}")