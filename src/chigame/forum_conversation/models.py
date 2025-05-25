from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
