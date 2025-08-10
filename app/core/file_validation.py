from fastapi import HTTPException, UploadFile
from typing import List, Optional
import magic
import os

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB default
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB for images
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB for documents

# Allowed MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml"
]

ALLOWED_DOCUMENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv"
]

ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"],
    "all": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".doc", ".docx", 
            ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"]
}


class FileValidator:
    """
    Validates uploaded files for size, type, and content
    """
    
    @staticmethod
    def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> None:
        """
        Validate file size
        
        Args:
            file: Uploaded file
            max_size: Maximum allowed size in bytes
            
        Raises:
            HTTPException: If file is too large
        """
        # Read file to get size (this loads it into memory)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024:.1f} MB"
            )
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> None:
        """
        Validate file extension
        
        Args:
            filename: Name of the file
            allowed_extensions: List of allowed extensions
            
        Raises:
            HTTPException: If extension is not allowed
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
    
    @staticmethod
    def validate_mime_type(file: UploadFile, allowed_types: List[str]) -> None:
        """
        Validate file MIME type using python-magic
        
        Args:
            file: Uploaded file
            allowed_types: List of allowed MIME types
            
        Raises:
            HTTPException: If MIME type is not allowed
        """
        # Read first 2048 bytes for magic number detection
        file_header = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer
        
        # Detect MIME type
        mime = magic.from_buffer(file_header, mime=True)
        
        if mime not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File content type not allowed. Detected: {mime}"
            )
    
    @staticmethod
    def validate_image(file: UploadFile) -> None:
        """
        Validate image file
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        FileValidator.validate_file_size(file, MAX_IMAGE_SIZE)
        FileValidator.validate_file_extension(file.filename, ALLOWED_EXTENSIONS["image"])
        FileValidator.validate_mime_type(file, ALLOWED_IMAGE_TYPES)
    
    @staticmethod
    def validate_document(file: UploadFile) -> None:
        """
        Validate document file
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        FileValidator.validate_file_size(file, MAX_DOCUMENT_SIZE)
        FileValidator.validate_file_extension(file.filename, ALLOWED_EXTENSIONS["document"])
        FileValidator.validate_mime_type(file, ALLOWED_DOCUMENT_TYPES)
    
    @staticmethod
    def validate_file(file: UploadFile, file_type: str = "all") -> None:
        """
        Validate any file based on type
        
        Args:
            file: Uploaded file
            file_type: Type of file ("image", "document", "all")
            
        Raises:
            HTTPException: If validation fails
        """
        if file_type == "image":
            FileValidator.validate_image(file)
        elif file_type == "document":
            FileValidator.validate_document(file)
        else:
            # General validation
            FileValidator.validate_file_size(file)
            FileValidator.validate_file_extension(file.filename, ALLOWED_EXTENSIONS["all"])
            allowed_types = ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES
            FileValidator.validate_mime_type(file, allowed_types)


# Convenience functions
def validate_upload(file: UploadFile, file_type: str = "all") -> None:
    """
    Convenience function to validate uploaded file
    
    Args:
        file: Uploaded file
        file_type: Type of file ("image", "document", "all")
        
    Raises:
        HTTPException: If validation fails
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    FileValidator.validate_file(file, file_type)