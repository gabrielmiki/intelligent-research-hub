from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class Summary(models.Model):
    # 1. Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 2. User Relationship (The "user_id")
    # We use settings.AUTH_USER_MODEL instead of 'auth.User' for flexibility
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, # If user is deleted, delete their summaries
        related_name='summaries'  # Allows access via user.summaries.all()
    )

    # 3. Task Tracking
    # Crucial for debugging: "Which Celery process handled this?"
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    # 4. Data Fields
    url = models.URLField()
    status = models.CharField(
        max_length=20, 
        choices=[
            ('PENDING', 'Pending'), 
            ('PROCESSING', 'Processing'), 
            ('COMPLETED', 'Completed'), 
            ('FAILED', 'Failed')
        ],
        default='PENDING',
        db_index=True # <--- Optimization: Makes filtering by status faster
    )
    
    # 5. Content
    # Storing input_content is great for debugging (seeing what the AI saw)
    input_content = models.TextField(blank=True, null=True) 
    output_summary = models.TextField(blank=True, null=True) 
    
    # 6. Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Default ordering: newest first

    def __str__(self):
        return f"{self.url} ({self.status})"

class CustomUser(AbstractUser):
    # You can add custom fields here whenever you want!

    def __str__(self):
        return self.username