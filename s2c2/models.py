from django.db import models


class TemplateSettings(models.Model):
    template_base_date = models.DateField(blank=True, null=True, help_text='Pick a date of which the weekly schedule would be the template for automatic copy.')
    template_copy_ahead = models.CharField(default='none', max_length=10, choices=(
        ('none', 'None'),
        ('1week', '1 week ahead'),
        ('2week', '2 weeks ahead'),
        ('3week', '3 weeks ahead'),
        ('4week', '4 weeks ahead'),
    ), help_text='How much ahead to copy the template.')

    class Meta:
        abstract = True