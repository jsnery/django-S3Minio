# MinIO Utility for Django

This module was developed to facilitate the integration of Django projects with MinIO, using boto3. It offers a simple interface for uploading, deleting, generating authenticated URLs, and manipulating images (conversion to WEBP) in MinIO buckets.

## Features

  - Upload files to MinIO.
  - Delete files from MinIO.
  - Generate authenticated URLs for temporary download.
  - Convert images to WEBP format.
  - Generate valid filenames for images.

## Installation Requirements

Execute in the terminal:

```
pip install django boto3 django-storages Pillow
```

## Configuration

### 1\. Environment Variables

Before using the module, configure the following environment variables in your system or `.env` file:

  - `MINIO_ACCESS_KEY`: MinIO access key.
  - `MINIO_SECRET_KEY`: MinIO secret key.
  - `MINIO_BUCKET_NAME`: Name of the bucket in MinIO.
  - `MINIO_ENDPOINT_URL`: MinIO endpoint URL.

### 2\. Configuration in Django's `settings.py`

Add the following settings to your `settings.py` file:

```python
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')

AWS_S3_ENDPOINT_URL = os.getenv('MINIO_ENDPOINT_URL')
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}".rstrip('/')

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

MEDIA_URL = f"{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'temp/media')
```

## Usage with Django Models

This utility was designed for direct use in Django Models. To work correctly, it is necessary to:

  - Have a `created_at` field in your model **before** the image field.
  - Use the `generate_image_filename` method in the `upload_to` parameter of the image field.
  - Implement the `save`, `delete` methods and a property to get the image URL, as shown in the example below.

### Example of use in Model

```python
from django.db import models
from utils.s3_minio import S3Minio, generate_image_filename
from django.conf import settings

s3 = S3Minio(
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    access_key_id=settings.AWS_ACCESS_KEY_ID,
    secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
)

class Example(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=generate_image_filename, null=True, blank=True)

    def save(self, *args, **kwargs):
        s3.webp_converter(self.image)
        super(Example, self).save(*args, **kwargs)
        s3.upload(self.image.name)
        
    def delete(self, *args, **kwargs):
        s3.delete(self.image.name)
        super(Example, self).delete(*args, **kwargs)
        
    @property
    def get_image(self):
        return s3.get_url(self.image.name)

class Example2(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    image_1 = models.ImageField(upload_to=generate_image_filename, null=True, blank=True)
    image_2 = models.ImageField(upload_to=generate_image_filename, null=True, blank=True)

    def save(self, *args, **kwargs):
        s3.webp_converter(self.image_1, self.image_2)
        super(Example2, self).save(*args, **kwargs)
        s3.upload(self.image_1.name, self.image_2.name)
        
    def delete(self, *args, **kwargs):
        s3.delete(self.image_1.name, self.image_2.name)
        super(Example2, self).delete(*args, **kwargs)
        
    @property
    def get_image_1(self):
        return s3.get_url(self.image_1.name)

    @property
    def get_image_2(self):
        return s3.get_url(self.image_2.name)
```

> **Note:**
> The `created_at` field must come before the image field in the model, as the generated filename depends on the creation timestamp.

## Example of direct use

```python
from utils.s3_minio import S3Minio


s3 = S3Minio(
    endpoint_url='endpoint_url',
    access_key_id='access_key_id',
    secret_access_key='secret_access_key',
    bucket_name='bucket_name',
)
s3.upload('path/to/file.jpg')
url = s3.get_url('path/to/file.jpg')
s3.delete('path/to/file.jpg')
```

## About

  - Made for Django projects.
  - Uses boto3, Pillow, and django-storages.
  - Organize your files and images in MinIO simply and efficiently.
