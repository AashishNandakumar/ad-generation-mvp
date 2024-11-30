from fastapi import UploadFile
import PyPDF2
import docx
from io import BytesIO


class FileProcessor:
    @staticmethod
    async def process_file(file: UploadFile) -> str:
        """Process uploaded file and extract text content."""
        content = await file.read()
        file_extension = file.filename.split(".")[-1].lower()

        if file_extension == "pdf":
            return await FileProcessor._process_pdf(content)
        elif file_extension == "docx":
            return await FileProcessor._process_docx(content)
        elif file_extension == "txt":
            return content.decode("utf-8")

        raise ValueError(f"Unsupported file type: {file_extension}")

    @staticmethod
    async def _process_pdf(content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
        finally:
            pdf_file.close()

    @staticmethod
    async def _process_docx(content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc_file = BytesIO(content)
            doc = docx.Document(doc_file)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Error processing DOCX: {str(e)}")
        finally:
            doc_file.close()
