'''
S3Minio Class
===================

This class is designed to manage file operations with MinIO, a high-performance
object storage system. It provides methods for uploading, deleting, and generating
presigned URLs for files stored in MinIO. Additionally, it includes functionality
to convert images to the WEBP format and generate valid filenames for saving images.

Dependencies
-------------------
- boto3: AWS SDK for Python, used to interact with MinIO.
- PIL (Pillow): Python Imaging Library, used for image processing.
- re: Regular expression operations.
- os: Provides a way of using operating system-dependent functionality.
- random: Used to generate random numbers.
- shutil: High-level file operations.
-------------------
# -*- coding: utf-8 -*-
'''
import re
import os
import random
import shutil
from io import BytesIO

import boto3
from PIL import Image


class S3Minio:
    '''
    Class to manage uploading, downloading, and deleting files in MinIO.
    
    Attributes:
        - s3: S3 client configured to connect to MinIO.
        
    Methods:
        - upload: Uploads files to MinIO.
        - delete: Deletes files from MinIO.
        - get_url: Generates a presigned URL to access files in MinIO.
        - webp_converter: Converts images to WEBP format.
        - image_save: Generates a valid filename for saving images.
    '''
    def __init__(self, endpoint_url, access_key_id, secret_access_key, bucket_name):
        print(
            f"Initializing S3Minio with endpoint: {endpoint_url}, "
            f"access_key_id: {access_key_id}, "
            f"secret_access_key: {secret_access_key}, "
            f"bucket_name: {bucket_name}"
        )
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        self.s3_bucket_name = bucket_name

    def upload(self, *args):
        '''
        Uploads files to MinIO.

        :param args: List of files to be uploaded.
        :param kwargs: Additional arguments.
        :return: True if the upload is successful, False otherwise.
        '''
        for i in args:
            path = i
            file_direct = f"temp/media/{path}"

            try:
                print(f"Uploading {file_direct} to MinIO...")
                try:
                    print(
                        f"File {file_direct}\n",
                        f"exists: {os.path.exists(file_direct)}\n",
                        f"Bucket: {self.s3_bucket_name}\n",
                        f"Path: {path}",
                    )
                    self.s3.upload_file(file_direct, self.s3_bucket_name, path)
                    print(f"File {file_direct} uploaded successfully to MinIO.")
                except Exception as exc:
                    raise ValueError(f"Upload Error: {exc}") from exc

                # Remove the file from the local directory
                os.remove(file_direct)

                dir_local = os.path.dirname(file_direct)
                if os.path.exists(dir_local) and not os.listdir(dir_local):
                    shutil.rmtree(dir_local)

                return True

            except Exception as exc:
                raise ValueError(f"Upload Error: {exc}") from exc

    def delete(self, *args):
        '''
        Deletes files from MinIO.
        
        :param args: List of files to be deleted.
        :param kwargs: Additional arguments.
        :return: True if deletion is successful, False otherwise.
        '''
        for i in args:
            path = i

            try:
                self.s3.delete_object(Bucket=self.s3_bucket_name, Key=path)
                return True

            except Exception as exc:
                raise ValueError(f"Delete Error: {exc}") from exc

    def get_url(self, path):
        '''
        Generates a presigned URL to access files in MinIO.
        
        :param path: Path to the file in MinIO.
        :return: Presigned URL or None if the file does not exist.
        '''
        bucket_name = self.s3_bucket_name

        try:
            # Verifica se o arquivo existe no bucket
            self.s3.head_object(Bucket=bucket_name, Key=path)

            # Gera a URL autenticada
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': path},
                ExpiresIn=3600
            )

            return url

        except self.s3.exceptions.ClientError:
            return None

    def webp_converter(self, *args):    # Exclusive to Django models
        '''
        Converts images to WEBP format and renames them.
        
        :param args: List of image files to be converted.
        :param kwargs: Additional arguments.
        :return: Converted image content or None if an error occurs.
        '''
        try:
            from django.core.files.base import ContentFile  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError("Convert Error (Exclusive to Django models) | pip install django django-storages") from exc

        for image in args:
            try:
                img = Image.open(image)
                img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, "WEBP", quality=75)

                # Rename the image
                extensions = [".jpg", ".jpeg", ".png", ".svg", ".gif"]
                for e in extensions:
                    try:
                        if e in image.name:
                            image.name = image.name.replace(e, ".webp")
                            break
                    except Exception as exc:
                        raise ValueError("Converter Error (Exclusive to Django models) | pip install django django-storages") from exc

                return ContentFile(buffer.getvalue())

            except Exception as exc:
                raise ValueError("Converter Error (Exclusive to Django models) | pip install django") from exc


def generate_image_filename(instance, filename):    # Exclusive to Django models
    '''
    Generates a valid filename for saving images.
    
    :param instance: Model instance.
    :param filename: Original filename.
    :return: Formatted filename.
    '''
    def get_valid_filename(filename):
        '''
        Generates a valid filename by removing special characters and spaces.
        '''
        filename = str(filename).strip().replace(' ', '_')
        return re.sub(r'[^A-Za-z0-9._-]', '', filename)

    random_number = random.randint(1000, 9999)
    file_ext = filename.split(".")[-1]
    class_name = instance.__class__.__name__
    timestamped_name = instance.created_at.strftime("%Y-%m-%d-%H-%M-%S-%F")
    valid_filename = get_valid_filename(f"{timestamped_name}-{random_number}.{file_ext}")

    return f"{class_name}/{timestamped_name}/{valid_filename}"
