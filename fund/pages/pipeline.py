# your_app/pipeline.py
from urllib.request import urlopen
from django.core.files.base import ContentFile
from .models import CustomUser

def save_profile_picture(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        if response.get('picture'):
            # Get Facebook profile picture
            picture_url = f"https://graph.facebook.com/{response['id']}/picture?type=large"
            
            try:
                # Download the image
                image_response = urlopen(picture_url)
                user.profile_picture.save(
                    f"{user.id}_facebook.jpg",
                    ContentFile(image_response.read()),
                    save=True
                )
            except Exception as e:
                # Silently fail if we can't get the picture
                pass