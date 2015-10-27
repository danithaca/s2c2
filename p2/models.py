from sitetree.models import TreeItemBase
from django.db import models


class TreeItem(TreeItemBase):
    fa_icon = models.CharField(blank=True)
    container = models.BooleanField(default=False)
