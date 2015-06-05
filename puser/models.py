from django.contrib.auth.models import User
from django.db import models
from image_cropping import ImageCropField, ImageRatioField
from localflavor.us.models import PhoneNumberField


class Info(models.Model):
    """
    The extended field for p2 Users.
    Authentication/authorization would be handled by user_account.
    """

    user = models.OneToOneField(User, primary_key=True)
    address = models.CharField(max_length=200, blank=True)
    phone = PhoneNumberField(blank=True)
    note = models.TextField(blank=True)

    picture_original = ImageCropField(upload_to='picture', blank=True, null=True)
    picture_cropping = ImageRatioField('picture_original', '200x200')

    from location.models import Area
    # user's home area. it doesn't necessarily mean the user will request/respond to this area only.
    area = models.ForeignKey(Area)

    def __str__(self):
        return self.user.get_full_name() or self.user.username