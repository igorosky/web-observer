import uuid
from django.db import models
from users.models import User
class TrackedWebsite(models.Model):
    class Meta:
        db_table = "tracked_websites"

    siteId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    siteName = models.CharField(max_length=30, unique=True)
    siteUrl = models.TextField()
    siteDescription = models.TextField(max_length=300,null=False)
    createdAt = models.DateTimeField(auto_now_add=True)

# FK has _id
class UserTrackedWebsites(models.Model):
    class Meta:
        db_table = "user_tracked_websites"
        unique_together = ('user', 'website')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    addedAt = models.DateTimeField(auto_now_add=True)

    @classmethod
    def exists_site_for_user(cls, site_id, user_id):
        return cls.objects.filter(website_id=site_id, user_id=user_id).exists()
    @classmethod
    def get_site_id_user(cls,user_id):
        return cls.objects.get(user_id=user_id)


class TrackedElement(models.Model):
    class Meta:
        db_table = "tracked_elements"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE,unique=True)
    cssSelector = models.TextField()
    elementName = models.CharField(max_length=255)
    registeredAt = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_elemId_by_siteId(cls, site_id):
        return cls.objects.get(website_id=site_id).id


class ElementChange(models.Model):
    class Meta:
        db_table = "element_changes"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    element = models.ForeignKey(TrackedElement, on_delete=models.CASCADE)
    content = models.TextField()
    change = models.TextField(null=True)
    detectedAt = models.DateTimeField(auto_now_add=True)


class UserElementUpdate(models.Model):
    class Meta:
        db_table = "user_element_updates"
        indexes = [
            models.Index(fields=["user", "updateTime"], name="idx_user_updates_user_time")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(TrackedElement, on_delete=models.CASCADE)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    statusCode = models.CharField(max_length=100)
    updateTime = models.DateTimeField()