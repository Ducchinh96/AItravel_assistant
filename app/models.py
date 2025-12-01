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
    
    
class Destination(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)  # Address or city name
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

