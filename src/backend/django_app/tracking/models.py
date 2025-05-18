import uuid
from django.db import models
from users.models import User
class TrackedWebsite(models.Model):
    class Meta:
        db_table = "tracked_websites"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserTrackedWebsites(models.Model):
    class Meta:
        db_table = "user_tracked_websites"
        unique_together = ('user', 'website')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


class TrackedElement(models.Model):
    class Meta:
        db_table = "tracked_elements"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    css_selector = models.TextField()
    element_name = models.CharField(max_length=255)
    registered_at = models.DateTimeField(auto_now_add=True)


class ElementChange(models.Model):
    class Meta:
        db_table = "element_changes"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    element = models.ForeignKey(TrackedElement, on_delete=models.CASCADE)
    content = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)


class UserElementUpdate(models.Model):
    class Meta:
        db_table = "user_element_updates"
        indexes = [
            models.Index(fields=["user", "update_time"], name="idx_user_updates_user_time")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(TrackedElement, on_delete=models.CASCADE)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    update_time = models.DateTimeField()