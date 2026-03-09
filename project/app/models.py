from django.db import models
from django.contrib.auth.models import User


class ResearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_name = models.CharField(max_length=255)
    summary = models.TextField()
    extracted_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pdf_name