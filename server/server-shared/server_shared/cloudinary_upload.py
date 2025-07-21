"""
CloudinaryUploader class to handle file and video uploads to Cloudinary.
It supports configuring public ID, cache invalidation, and overwrite options.
"""

import logging

from typing import Optional, Union, Dict, Any
import cloudinary
import cloudinary.uploader


class CloudinaryUploader:
    """
    A class to encapsulate Cloudinary file and video upload functionality.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize and configure Cloudinary credentials.

        :param cloud_name: Your Cloudinary cloud name.
        :param api_key: Your Cloudinary API key.
        :param api_secret: Your Cloudinary API secret.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing CloudinaryUploader with cloud_name: %s", cloud_name)
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

    def upload_file(
        self,
        file_path: str,
        public_id: Optional[str] = None,
        overwrite: Optional[bool] = None,
        invalidate: Optional[bool] = None
    ) -> Union[Dict[str, Any], None]:
        """
        Uploads a file (image/document) to Cloudinary.

        :param file_path: The local path to the file.
        :param public_id: Optional public ID for the file.
        :param overwrite: Overwrite existing file if true.
        :param invalidate: Invalidate cached copies if true.
        :return: Upload response dict or error.
        """
        
        response = cloudinary.uploader.upload(
            file_path,
            public_id=public_id,
            overwrite=overwrite,
            invalidate=invalidate,
            resource_type='auto'
        )
        return response

    def upload_video(
        self,
        file_path: str,
        public_id: Optional[str] = None,
        overwrite: Optional[bool] = None,
        invalidate: Optional[bool] = None
    ) -> Union[Dict[str, Any], None]:
        """
        Uploads a video file to Cloudinary.

        :param file_path: The local path to the video file.
        :param public_id: Optional public ID for the video.
        :param overwrite: Overwrite existing video if true.
        :param invalidate: Invalidate cached copies if true.
        :return: Upload response dict or error.
        """
        response = cloudinary.uploader.upload(
            file_path,
            public_id=public_id,
            overwrite=overwrite,
            invalidate=invalidate,
            chunk_size=50000,
            resource_type='video'
        )
        return response
