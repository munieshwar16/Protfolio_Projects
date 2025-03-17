# services/__init__.py
"""
Services module for the AI content creation pipeline.
Provides storage and other infrastructure services.
"""

# Import this way to avoid circular imports
from .minio_storage_service import MinioStorageService

__all__ = ['MinioStorageService']