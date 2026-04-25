import uuid

from django.db import models


class Profession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profession_name = models.CharField(max_length=45)

    class Meta:
        db_table = "professions"


class Parent(models.Model):
    PARENT_TYPE = (("F", "Father"), ("M", "Mother"), ("G", "Guardian"), ("T", "Tuteur"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_name = models.CharField(max_length=60)
    parent_phone = models.CharField(max_length=15,null=True, blank=True)
    parent_email = models.EmailField(max_length=100, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.RESTRICT)
    parent_type = models.CharField(max_length=1, choices=PARENT_TYPE)
    is_alive = models.BooleanField(default=True)
    is_contact_person = models.BooleanField(default=False)

    class Meta:
        db_table = "parents"
