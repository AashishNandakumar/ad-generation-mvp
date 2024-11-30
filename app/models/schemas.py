from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


# class InputFile(BaseModel):
#     content: str
#     file_type: FileType


class AdGenerationRequest(BaseModel):
    guidelines: str
    brand_metadata: str
    campaign_details: str
    region: str
    design_plan: str


class GeneratedAd(BaseModel):
    image_urls: List[str] | Any
    metadata: dict
