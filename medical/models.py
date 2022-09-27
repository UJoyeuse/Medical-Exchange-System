
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.
STATUS = [
    ("PENDING", "PENDING"),
    ("APPROVED", "APPROVED"),
    ("DENIED", "DENIED"),
    ("RETURNED", "RETURNED"),
]

class CustomUser(AbstractUser):
    phone_number = models.CharField(default='0780000000', max_length=20)

    class Meta:
        db_table = 'customuser'

    def __str__(self):
        return self.first_name + ' ' + self.last_name 


class Hospital(models.Model):
    leader = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=False)
    hospital_name = models.CharField(max_length=40, blank=True, unique=True)
    address = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'hospital'

    def __str__(self):
        return self.hospital_name


class Medicine(models.Model):
    name = models.CharField(max_length=25)
    manufacture_date=models.DateTimeField(null=True)
    expiry_date=models.DateTimeField(null=True)
    quantity = models.IntegerField()
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    class Meta:
        db_table = 'medicine'

    def __str__(self):
        return self.name

class Requests(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUS, default="PENDING")
    return_date=models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    hospital_requested = models.ForeignKey(Hospital,related_name='requested_hospital',on_delete=models.CASCADE)
    hospital_owner =  models.ForeignKey(Hospital,related_name='owner_hospital',on_delete=models.CASCADE)

    class Meta:
        db_table = 'request'

    def __int__(self):
        return self.medicine+ ' ' + self.hospital_requested+ ' ' +self.hospital_owner

class Approved(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUS, default="APPROVED")
    return_date=models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    hospital_requested = models.ForeignKey(Hospital,related_name='request_hospital',on_delete=models.CASCADE)
    hospital_approved =  models.ForeignKey(Hospital,related_name='approved_hospital',on_delete=models.CASCADE)

    class Meta:
        db_table = 'approved'

    def __str__(self):
        return self.medicine+ ' ' + self.hospital_requested+ ' ' +self.hospital_approved

class Returned(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUS, default="PENDING")
    return_date=models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    hospital_returned = models.ForeignKey(Hospital,related_name='returned_hospital',on_delete=models.CASCADE)
    hospital_received =  models.ForeignKey(Hospital,related_name='recieved_hospital',on_delete=models.CASCADE)

    class Meta:
        db_table = 'returned'

    def __int__(self):
        return self.medicine+ ' ' + self.hospital_returned+ ' ' +self.hospital_received