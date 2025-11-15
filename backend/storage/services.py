"""
Storage services for file uploads to AWS S3.
"""
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging
import uuid
from datetime import timedelta

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for S3 file storage."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def upload_file(self, file, patient_id, record_id=None):
        """
        Upload file to S3.
        
        Args:
            file: Django UploadedFile object
            patient_id: Patient user ID
            record_id: Optional record ID
        
        Returns:
            dict with file_url, file_name, file_size, file_type
        """
        try:
            # Generate unique file key
            file_extension = file.name.split('.')[-1] if '.' in file.name else ''
            file_id = str(uuid.uuid4())
            file_key = f"documents/{patient_id}/{file_id}.{file_extension}" if file_extension else f"documents/{patient_id}/{file_id}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'ContentType': file.content_type,
                    'Metadata': {
                        'patient_id': str(patient_id),
                        'record_id': str(record_id) if record_id else '',
                    }
                }
            )
            
            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_key}"
            
            return {
                'file_url': file_url,
                'file_name': file.name,
                'file_size': file.size,
                'file_type': file.content_type,
                'file_key': file_key
            }
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            raise
    
    def get_presigned_url(self, file_key, expires_in=300):
        """
        Generate presigned URL for file access.
        
        Args:
            file_key: S3 object key
            expires_in: URL expiration time in seconds (default 5 minutes)
        
        Returns:
            Presigned URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise Exception(f"Failed to generate URL: {str(e)}")
    
    def delete_file(self, file_key):
        """
        Delete file from S3.
        
        Args:
            file_key: S3 object key
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")


# Global instance
s3_storage = S3StorageService()

