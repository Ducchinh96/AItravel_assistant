from django.db import models

class ChatTurn(models.Model):
    id = models.AutoField(primary_key=True)
    text_user = models.TextField()
    text_ai = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]  # lấy theo thứ tự hội thoại
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"#{self.id} - {self.text_user[:40]}..."


class Itinerary(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    details = models.JSONField()
    is_fixed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
