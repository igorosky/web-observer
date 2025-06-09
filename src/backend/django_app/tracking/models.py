import uuid
from dataclasses import dataclass
from django.db import models
from users.models import User
class TrackedWebsite(models.Model):
    class Meta:
        db_table = "tracked_websites"
        indexes = [
            models.Index(fields=["siteName"],name="idx_site_name")
        ]
    class Type(models.TextChoices):
        HTML = 'html', 'HTML'
        JSON = 'json', 'JSON'
        IMAGE = 'image', 'image'


    siteId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    siteName = models.CharField(max_length=30)
    siteUrl = models.TextField()
    siteDescription = models.TextField(max_length=900,null=False)
    siteType = models.CharField(choices=Type,default=Type.HTML)
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
    selector = models.TextField()
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
    textChange = models.TextField(null=True)
    imageChangeUrl = models.CharField(null=True)
    detectedAt = models.DateTimeField(auto_now_add=True)

class UserElementUpdate(models.Model):
    class Meta:
        db_table = "user_element_updates"
        indexes = [
            models.Index(fields=["user", "updateTime"], name="idx_user_updates_user_time"),
            models.Index(fields=["website"],name="idx_website")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(TrackedElement, on_delete=models.CASCADE)
    website = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE)
    statusCode = models.CharField(max_length=100)
    updateTime = models.DateTimeField()
    error = models.TextField(null=True) # check in other places

class Observer(models.Model):
    class Meta:
        db_table = "observers"

    id = models.AutoField(primary_key=True)
    site = models.ForeignKey(TrackedWebsite, on_delete=models.CASCADE,unique=True)
    hash = models.CharField(null=True)

class ObserverInfo(models.Model):
    class Meta:
        db_table = "observers_info"

    observer = models.ForeignKey(Observer,primary_key=True,on_delete=models.CASCADE)
    info = models.JSONField(default=dict)


class GotifyInfo(models.Model):
    class Meta:
        db_table = 'gotify_info'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField(unique=True, null=False, blank=False)
    token = models.TextField(null=False, blank=False)
    updateTime = models.DateTimeField(auto_now_add=True)

