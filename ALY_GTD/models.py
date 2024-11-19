from datetime import timezone
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    roles = models.CharField(max_length=100, blank=True, null=True)
    role2 = models.CharField(max_length=100, blank=True, null=True)
    def str(self):
        return self.username


class XXGTD_VEHICLE_INFO(models.Model):
    STATUS_CHOICES = (
        ('draft', 'draft'),
        ('modification', 'Modification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('Pending for Approval','Pending for Approval')
    )
   

    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    FLEET_CREATION_DATE = models.DateField(null=True, blank=True)
    VIN_NO = models.CharField(max_length=100, null=True, blank=True)
    MANUFACTURER = models.CharField(max_length=100, null=True, blank=True)
    MODEL = models.CharField(max_length=100, null=True, blank=True)
    VEHICLE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    COLOR = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    FLEET_SUB_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    ENGINE_NO = models.CharField(max_length=100, null=True, blank=True)
    MODEL_YEAR = models.CharField(max_length=100, null=True, blank=True)
    COUNTRY_OF_ORIGIN = models.CharField(max_length=100, null=True, blank=True)
    SEATING_CAPACITY = models.CharField(max_length=100, null=True, blank=True)
    TONNAGE = models.CharField(max_length=100, null=True, blank=True)
    GROSS_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    EMPTY_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    PURCHASE_VALUE_AED = models.CharField(max_length=100, null=True, blank=True)
    COMMENTS = models.CharField(max_length=100, null=True, blank=True)
    STATUS = models.CharField(max_length=100, null=True, blank=True, choices=STATUS_CHOICES,default='Pending for Approval')
    ApplicationUsage = models.CharField(max_length=100, null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    
    VehiclePurchaseDoc=models.TextField(null=True, blank=True)
     
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_VEHICLE_INFO'
        
    @classmethod
    def get_next_header_id(cls):
        next_id = str(SequenceManager.get_next_number())
        print(f"Generated next header ID: {next_id}")
        return next_id

    
    def save(self, *args, **kwargs):
        generate_fleet_control_number = kwargs.pop('generate_fleet_control_number', True)
        print(f"Saving XXGTD_VEHICLE_INFO: HEADER_ID={self.HEADER_ID}, FLEET_CONTROL_NO={self.FLEET_CONTROL_NO}")
        
        if not self.HEADER_ID:
            self.HEADER_ID = kwargs.pop('new_header_id', None) or self.get_next_header_id()
            if generate_fleet_control_number:
                self.FLEET_CONTROL_NO = f"AY-{self.HEADER_ID}"
            print(f"Generated new HEADER_ID and FLEET_CONTROL_NO: {self.HEADER_ID}, {self.FLEET_CONTROL_NO}")
        elif not self.FLEET_CONTROL_NO and generate_fleet_control_number:
            self.FLEET_CONTROL_NO = f"AY-{self.HEADER_ID}"
        
        super().save(*args, **kwargs)
        print(f"Saved XXGTD_VEHICLE_INFO: HEADER_ID={self.HEADER_ID}, FLEET_CONTROL_NO={self.FLEET_CONTROL_NO}")

   
    def create_action_history(self, user, action_performed, process_status, doc_status):
        CustomUser = AbstractUser()

        XXALY_GTD_ACTION_HISTORY.objects.create(
            APPLICATION_ID=str(self.id),  # Convert to string to ensure compatibility
            APPL_NUMBER=self.FLEET_CONTROL_NO,
            REQUEST_TYPE='FLEET_MASTER',  # Changed from 'FLEET' to match your API
            REQUEST_NUMBER=self.FLEET_CONTROL_NO,  # Added this field
            PROCESS_STATUS=process_status,
            DOC_STATUS=doc_status,
            RESPONSE_DATE=timezone.now().date(),  # Use .date() to match your API
            RESPONDED_BY=CustomUser.username,  # Use the passed user object
            RESPONDER_ROLE=CustomUser.roles,  # Use the passed user object
            RESPONSE_COMMENTS=self.COMMENTS,  # Added this field
            ACTION_PERFORMED=action_performed,
            NEXT_RESP="APPROVER" if CustomUser and CustomUser.roles == "REQUESTOR" else "REQUESTOR",
       
            CREATED_BY=CustomUser.username,  # Use the passed user object
            CREATION_DATE=timezone.now().date(),  # Use .date() to match your API
            LAST_UPDATED_BY=CustomUser.username,  # Use the passed user object
            LAST_UPDATE_DATE=timezone.now().date(),  # Use .date() to match your API
          
     
    
            )
        
class XXGTD_COMMERCIAL_PLATE_INFO(models.Model):
    STATUS_CHOICES = (
        ('draft', 'draft'),
        ('modification', 'Modification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('Pending for Approval','Pending for Approval')
    )

    HEADER_ID = models.CharField(max_length=200, null=True, blank=True)
    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    COMM_PLATE_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_PLATE_DATE = models.DateField(null=True, blank=True)
    COMM_PLATE_CATEGORY = models.CharField(max_length=200, null=True, blank=True)
    CP_ISSUED_AUTHORITY = models.CharField(max_length=200, null=True, blank=True)
    CP_VEHICLE_TYPE = models.CharField(max_length=200, null=True, blank=True)
    CP_COLOR = models.CharField(max_length=200, null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=200, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=200, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=200, null=True, blank=True)
    ACTION = models.CharField(max_length=200, null=True, blank=True)
    RECORD_STATUS = models.CharField(max_length=200, null=True, blank=True)
    STATUS = models.CharField(max_length=200, null=True, blank=True)
    COMMENTS = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_COMMERCIAL_PLATE_INFO'
    
   
    
    @classmethod
    def get_next_header_id(cls):
        next_id = str(SequenceManager.get_next_number())
        print(f"Generated next header ID: {next_id}")
        return next_id

    
    def save(self, *args, **kwargs):
        generate_commercial_control_number = kwargs.pop('generate_commercial_control_number', True)
        print(f"Saving XXGTD_COMMERCIAL_PLATE_INFO: HEADER_ID={self.HEADER_ID}, COMM_CONTROL_NO={self.COMM_CONTROL_NO}")
        
        if not self.HEADER_ID:
            self.HEADER_ID = kwargs.pop('new_header_id', None) or self.get_next_header_id()
            if generate_commercial_control_number:
                self.COMM_CONTROL_NO = f"AY-{self.HEADER_ID}"
            print(f"Generated new HEADER_ID and COMM_CONTROL_NO: {self.HEADER_ID}, {self.COMM_CONTROL_NO}")
        elif not self.COMM_CONTROL_NO and generate_commercial_control_number:
            self.COMM_CONTROL_NO = f"AY-{self.HEADER_ID}"
        
        super().save(*args, **kwargs)
        print(f"Saved XXGTD_COMMERCIAL_PLATE_INFO: HEADER_ID={self.HEADER_ID}, COMM_CONTROL_NO={self.COMM_CONTROL_NO}")

        
        
        
    def create_action_history(self, user, action_performed, process_status, doc_status):
        CustomUser = AbstractUser()

        XXALY_GTD_ACTION_HISTORY.objects.create(
            APPLICATION_ID=str(self.id),
            APPL_NUMBER=self.COMM_CONTROL_NO,
            REQUEST_TYPE='COMMERCIAL MASTER',
            REQUEST_NUMBER=self.COMM_CONTROL_NO,
            PROCESS_STATUS=process_status,
            DOC_STATUS=doc_status,
            RESPONSE_DATE=timezone.now().date(),
            RESPONDED_BY=CustomUser.username,
            RESPONDER_ROLE=CustomUser.roles,
            RESPONSE_COMMENTS=self.COMMENTS,
            ACTION_PERFORMED=action_performed,
            NEXT_RESP="APPROVER" if CustomUser and CustomUser.roles == "REQUESTOR" else "REQUESTOR",
            CREATED_BY=CustomUser.username,
            CREATION_DATE=timezone.now().date(),
            LAST_UPDATED_BY=CustomUser.username,
            LAST_UPDATE_DATE=timezone.now().date(),
        )

from django.db import transaction, IntegrityError

class SequenceManager(models.Model):
    last_used_number = models.IntegerField(default=99999)

    @classmethod
    def get_next_number(cls):
        with transaction.atomic():
            instance = cls.objects.select_for_update().get(pk=1)
            next_number = instance.last_used_number + 1
            print(f"SequenceManager: Incrementing from {instance.last_used_number} to {next_number}")
            instance.last_used_number = next_number
            instance.save()
            return next_number

    @classmethod
    def initialize(cls):
        cls.objects.get_or_create(pk=1, defaults={'last_used_number': 99999})

    
class XXGTD_INSURANCE_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    INS_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='insurances', null=True, blank=True)
    commercial_master = models.ForeignKey(XXGTD_COMMERCIAL_PLATE_INFO, on_delete=models.CASCADE, related_name='insurances', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    
    INSURANCE_COMPANY = models.CharField(max_length=100, null=True, blank=True)
    POLICY_NO = models.CharField(max_length=100, null=True, blank=True)
    POLICY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_START_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_MOT_INS = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    Process = models.CharField(max_length=200, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    
    
    InsurancePolicAattachment = models.TextField(null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        db_table = 'XXGTD_INSURANCE_INFO'
    def __str__(self):
        if self.FLEET_CONTROL_NO:
            return f"Insurance for Fleet {self.FLEET_CONTROL_NO}"
        elif self.COMM_CONTROL_NO:
            return f"Insurance for Commercial {self.COMM_CONTROL_NO}"
        return "Insurance"


class XXGTD_REGISTRATION_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    REG_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='registration', null=True, blank=True)
    commercial_master = models.ForeignKey(XXGTD_COMMERCIAL_PLATE_INFO, on_delete=models.CASCADE, related_name='registration', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    EMIRATES_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTERED_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REG_COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO1 = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_REG = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    RegCardAttachment =  models.TextField(null=True, blank=True)
    Process = models.CharField(max_length=200, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_REGISTRATION_INFO'


    def __str__(self):
        if self.FLEET_CONTROL_NO:
            return f"Registration for Fleet {self.FLEET_CONTROL_NO}"
        elif self.COMM_CONTROL_NO:
            return f"Registration for Commercial {self.COMM_CONTROL_NO}"
        return "Registration"



class XXGTD_ROAD_TOLL_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    RT_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='roadtoll', null=True, blank=True)
    commercial_master = models.ForeignKey(XXGTD_COMMERCIAL_PLATE_INFO, on_delete=models.CASCADE, related_name='roadtoll', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    TOLL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=100, null=True, blank=True)
    TAG_NO = models.CharField(max_length=100, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE= models.DateField(null=True, blank=True)
    CURRENT_STATUS = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    RoadtollAttachments =  models.TextField(null=True, blank=True)
    Process = models.CharField(max_length=200, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_ROAD_TOLL_INFO'
    def __str__(self):
        if self.FLEET_CONTROL_NO:
            return f"Roadtoll for Fleet {self.FLEET_CONTROL_NO}"
        elif self.COMM_CONTROL_NO:
            return f"Roadtoll for Commercial {self.COMM_CONTROL_NO}"
        return "Roadtoll"



class XXGTD_ALLOCATION_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    ALLOC_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='allocation', null=True, blank=True)
    commercial_master = models.ForeignKey(XXGTD_COMMERCIAL_PLATE_INFO, on_delete=models.CASCADE, related_name='allocation', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    DIVISION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_LOCATION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    APPICATION_USAGE = models.CharField(max_length=100, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    attachment = models.TextField(null=True, blank=True)
    Process = models.CharField(max_length=200, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    

    EMPLOYEE_NO = models.IntegerField(null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=100, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=100, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=20, null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    ALLOCATION_END_DATE = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_ALLOCATION_INFO'
        
    def __str__(self):
        if self.FLEET_CONTROL_NO:
            return f"Allocation for Fleet {self.FLEET_CONTROL_NO}"
        elif self.COMM_CONTROL_NO:
            return f"Allocation for Commercial {self.COMM_CONTROL_NO}"
        return "Allocation"
   

class XXGTD_PARKING_PERMIT(models.Model):
 
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    
    PERMIT_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='permits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    PERMIT_TYPE = models.CharField(max_length=100, null=True, blank=True)
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    ISSUING_AUTHORITY = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_NO = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_DATE = models.DateField(null=True, blank=True)
    PERMIT_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_PERMIT = models.CharField(max_length=100, null=True, blank=True)
    PermitColor = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    PermitAattachment = models.TextField(null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'XXGTD_PARKING_PERMIT'
        
        
    def __str__(self):
        return f"Permits for {self.fleet_master.FLEET_CONTROL_NO}"

class XXGTD_GPS_TRACKING_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
       
        ('Rectification', 'Rectification')
    )
    
    GT_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='gps')
    GPS_DEVICE_NO = models.CharField(max_length=100, null=True, blank=True)
    GPS_INSTALLATION_DATE = models.DateField(null=True, blank=True)
    GPS_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    GpsAattachment =  models.TextField(null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    
   
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'XXGTD_GPS_TRACKING_INFO'

    def __str__(self):
        return f"GPS for {self.fleet_master.FLEET_CONTROL_NO}"

class XXGTD_FUEL_INFO(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    FUEL_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='fuel')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    FUEL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    MONTHLY_FUEL_LIMIT = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_NO = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_DATE = models.DateField(null=True, blank=True)
    FUEL_DOC_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_FUEL_DOC = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    FuelDocumentAttachment =  models.TextField(null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    

    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)



    class Meta:
        db_table = 'XXGTD_FUEL_INFO'
    def __str__(self):
        return f"Fuel for {self.fleet_master.FLEET_CONTROL_NO}"


class XXGTD_DRIVER_ASSIGNMENT(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    ASGN_LINE_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='driver')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    EMPLOYEE_NO = models.CharField(max_length=100, null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=100, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=100, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=20, null=True, blank=True)
    ASSIGNMENT_DATE = models.DateField(null=True, blank=True)
    TRAFFIC_CODE_NO = models.CharField(max_length=50, null=True, blank=True)
    DRIVING_LICENSE_NO = models.CharField(max_length=50, null=True, blank=True)
    LICENSE_TYPE = models.CharField(max_length=50, null=True, blank=True)
    PLACE_OF_ISSUE = models.CharField(max_length=100, null=True, blank=True)
    LICENSE_EXPIRY_DATE = models.DateField(null=True, blank=True)
    GPS_TAG_NO = models.CharField(max_length=50, null=True, blank=True)
    GPS_TAG_ASSIGN_DATE = models.DateField(null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=200, null=True, blank=True)
    DriverAttachments =  models.TextField(null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    

    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    ASSIGNMENT_END_DATE = models.DateField(null=True, blank=True)


    class Meta:
        db_table = 'XXGTD_DRIVER_ASSIGNMENT'
    def __str__(self):
        return f"Driver {self.EmployeeName} for {self.fleet_master.FLEET_CONTROL_NO}"
 
class Attachment(models.Model):
    fleet_master = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    file = models.FileField(upload_to='attachments/')
    upload_date = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    attachment_type = models.CharField(max_length=50,null=True, blank=True)
    FleetNumber = models.CharField(max_length=200, null=True, blank=True)
    uploaded_by= models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'Attachment'

    def __str__(self):
        return f"Attachment for {self.fleet_master.FLEET_CONTROL_NO if self.fleet_master else 'Unknown'} - {self.attachment_type}"

class XXALY_GTD_AUDIT_T(models.Model):
    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    
    FLEET_CONTROL_NO = models.CharField(max_length=50, null=True, blank=True)
    FLEET_CREATION_DATE =models.DateField(null=True, blank=True)
    VIN_NO = models.CharField(max_length=240, null=True, blank=True)
    MANUFACTURER = models.CharField(max_length=240, null=True, blank=True)
    MODEL = models.CharField(max_length=240, null=True, blank=True)
    VEHICLE_TYPE = models.CharField(max_length=240, null=True, blank=True)
    COLOR = models.CharField(max_length=240, null=True, blank=True)
    FLEET_CATEGORY = models.CharField(max_length=240, null=True, blank=True)
    FLEET_SUB_CATEGORY = models.CharField(max_length=240, null=True, blank=True)
    ENGINE_NO = models.CharField(max_length=240, null=True, blank=True)
    MODEL_YEAR = models.BigIntegerField(null=True, blank=True)
    COUNTRY_OF_ORIGIN = models.CharField(max_length=240, null=True, blank=True)
    SEATING_CAPACITY = models.CharField(max_length=50, null=True, blank=True)
    TONNAGE = models.CharField(max_length=240, null=True, blank=True)
    GROSS_WEIGHT_KG = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    EMPTY_WEIGHT_KG = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    PURCHASE_VALUE_AED = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    FLEET_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    INSURANCE_COMPANY = models.CharField(max_length=240, null=True, blank=True)
    POLICY_NO = models.CharField(max_length=240, null=True, blank=True)
    POLICY_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    POLICY_INSUR_EXPIRY_DATE = models.DateField(null=True, blank=True)
    INSUR_CURRENT_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    REGISTRATION_NO = models.CharField(max_length=240, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REGISTERED_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    EMIRATES_TRF_FILE_NO = models.CharField(max_length=240, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=240, null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    REG_COMPANY_NAME = models.CharField(max_length=240, null=True, blank=True)
    
    REGISTRATION_STATUS = models.CharField(max_length=240, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=240, null=True, blank=True)
    
    FUEL_TYPE = models.CharField(max_length=240, null=True, blank=True)
    MONTHLY_FUEL_LIMIT = models.CharField(max_length=240, null=True, blank=True)
    FUEL_SERVICE_TYPE = models.CharField(max_length=240, null=True, blank=True)
    FUEL_SERVICE_PROVIDER = models.CharField(max_length=240, null=True, blank=True)
    FUEL_DOCUMENT_NO = models.CharField(max_length=240, null=True, blank=True)
    FUEL_DOCUMENT_DATE = models.DateField(null=True, blank=True)
    FUEL_DOC_EXPIRY_DATE = models.DateField(null=True, blank=True)
    FUEL_DOC_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    TOLL_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    TOLL_TYPE = models.CharField(max_length=240, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=240, null=True, blank=True)
    TAG_NO = models.CharField(max_length=240, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE = models.DateField(null=True, blank=True)
    TOLL_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    PERMIT_TYPE = models.CharField(max_length=240, null=True, blank=True)
    PARKING_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    PARKING_AUTHORITY = models.CharField(max_length=240, null=True, blank=True)
    PERMIT_NO = models.CharField(max_length=240, null=True, blank=True)
    PERMIT_DATE = models.DateField(null=True, blank=True)
    PERMIT_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PARKING_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    LOADING_PERMIT_TYPE = models.CharField(max_length=240, null=True, blank=True)
    LOADING_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    LOADING_AUTHORITY = models.CharField(max_length=240, null=True, blank=True)
    LOADING_PERMIT_NO = models.CharField(max_length=240, null=True, blank=True)
    LOADING_PERMIT_DATE = models.DateField(null=True, blank=True)
    LOADING_EXP_DATE = models.DateField(null=True, blank=True)
    LOADING_STATUS = models.CharField(max_length=240, null=True, blank=True)
    ROAD_PERMIT_TYPE = models.CharField(max_length=240, null=True, blank=True)
    ROAD_PERMIT_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    ROAD_ISSUE_AUTHORITY = models.CharField(max_length=240, null=True, blank=True)
    ROAD_PERMIT_NO = models.CharField(max_length=240, null=True, blank=True)
    ROAD_PERMIT_DATE = models.DateField(null=True, blank=True)
    ROAD_PERMIT_EXP_DATE = models.DateField(null=True, blank=True)
    ROAD_PERMIT_STATUS = models.CharField(max_length=240, null=True, blank=True)
    BRAND_PERMIT_TYPE = models.CharField(max_length=240, null=True, blank=True)
    BRAND_PERMIT_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    BRAND_ISSUE_AUTHORITY = models.CharField(max_length=240, null=True, blank=True)
    BRAND_PERMIT_NO = models.CharField(max_length=240, null=True, blank=True)
    BRAND_PERMIT_DATE = models.DateField(null=True, blank=True)
    BRAND_PERMIT_EXP_DATE = models.DateField(null=True, blank=True)
    BRAND_STATUS = models.CharField(max_length=240, null=True, blank=True)
    
    GPS_DEVICE_NO = models.CharField(max_length=240, null=True, blank=True)
    GPS_INSTALLATION_DATE = models.DateField(null=True, blank=True)
    GPS_SERVICE_PROVIDER = models.CharField(max_length=240, null=True, blank=True)
   
    COMPANY_NAME = models.CharField(max_length=240, null=True, blank=True)
    DIVISION = models.CharField(max_length=240, null=True, blank=True)
    OPERATING_LOCATION = models.CharField(max_length=240, null=True, blank=True)
    OPERATING_EMIRATES = models.CharField(max_length=240, null=True, blank=True)
    APPICATION_USAGE = models.CharField(max_length=240, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    
    
    EMPLOYEE_NO = models.CharField(max_length=240, null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=240, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=240, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=50, null=True, blank=True)
    ASSIGNMENT_DATE = models.DateField(null=True, blank=True)
    ASSIGNMENT_END_DATE = models.DateField(null=True, blank=True)
    TRAFFIC_CODE_NO = models.CharField(max_length=240, null=True, blank=True)
    DRIVING_LICENSE_NO = models.CharField(max_length=240, null=True, blank=True)
    LICENSE_TYPE = models.CharField(max_length=240, null=True, blank=True)
    PLACE_OF_ISSUE = models.CharField(max_length=240, null=True, blank=True)
    LICENSE_EXPIRY_DATE = models.DateField(null=True, blank=True)
    GPS_TAG_NO = models.CharField(max_length=240, null=True, blank=True)
    GPS_TAG_ASSIGN_DATE = models.DateField(null=True, blank=True)
    
    ASSET_NO = models.BigIntegerField(null=True, blank=True)
    ASSET_REG_DATE = models.DateField(null=True, blank=True)
    LATEST_BOOK_VALUE = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    BOOK_VALUE_DATE = models.DateField(null=True, blank=True)
    
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    CREATION_DATE = models.DateField(null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    REGISTRATION_NO1 = models.CharField(max_length=240, null=True, blank=True)
    RECORD_STATUS = models.CharField(max_length=240, null=True, blank=True)
    VEH_COMPANY = models.CharField(max_length=240, null=True, blank=True)
    COMMENTS = models.CharField(max_length=4000, null=True, blank=True)
    ALLOCATION_END_DATE = models.DateField(null=True, blank=True)
    INS_START_DATE = models.DateField(null=True, blank=True)
    
    INS_LINE_ID = models.ForeignKey('XXGTD_INSURANCE_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_insurance', db_column='INS_LINE_ID')
    REG_LINE_ID = models.ForeignKey('XXGTD_REGISTRATION_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_registration', db_column='REG_LINE_ID')
    ALLOC_LINE_ID = models.ForeignKey('XXGTD_ALLOCATION_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_allocation', db_column='ALLOC_LINE_ID')
    RD_LINE_ID = models.ForeignKey('XXGTD_PARKING_PERMIT', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_rd', db_column='RD_LINE_ID')
    
    FUEL_LINE_ID = models.ForeignKey('XXGTD_FUEL_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_fuel', db_column='FUEL_LINE_ID')
    RT_LINE_ID = models.ForeignKey('XXGTD_ROAD_TOLL_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_roadtoll', db_column='RT_LINE_ID')
    PERMIT_LINE_ID = models.ForeignKey('XXGTD_PARKING_PERMIT', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_permit', db_column='PERMIT_LINE_ID')
    LOADING_LINE_ID = models.ForeignKey('XXGTD_PARKING_PERMIT', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_loading', db_column='LOADING_LINE_ID')
    
    GT_LINE_ID = models.ForeignKey('XXGTD_GPS_TRACKING_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_gps', db_column='GT_LINE_ID')
    
    ASGN_LINE_ID = models.ForeignKey('XXGTD_DRIVER_ASSIGNMENT', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_driver', db_column='ASGN_LINE_ID')
    ASSET_LINE_ID = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'XXALY_GTD_AUDIT_T'

    def __str__(self):
        return f"Audit Entry {self.SEQ_ID}"


class XXGTD_VEHICLE_AUDIT(models.Model):
    FLEET_MASTER = models.ForeignKey(XXGTD_VEHICLE_INFO, on_delete=models.CASCADE, related_name='vehicle_audits',null=True, blank=True,)
    
    FLEET_AUDIT_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID') 
    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=100, null=True, blank=True,editable=False)
    FLEET_CREATION_DATE = models.DateField(null=True, blank=True)
    VIN_NO = models.CharField(max_length=100, null=True, blank=True)
    MANUFACTURER = models.CharField(max_length=100, null=True, blank=True)
    MODEL = models.CharField(max_length=100, null=True, blank=True)
    VEHICLE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    COLOR = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    FLEET_SUB_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    ENGINE_NO = models.CharField(max_length=100, null=True, blank=True)
    MODEL_YEAR = models.CharField(max_length=100, null=True, blank=True)
    COUNTRY_OF_ORIGIN = models.CharField(max_length=100, null=True, blank=True)
    SEATING_CAPACITY = models.CharField(max_length=100, null=True, blank=True)
    TONNAGE = models.CharField(max_length=100, null=True, blank=True)
    GROSS_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    EMPTY_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    PURCHASE_VALUE_AED = models.CharField(max_length=100, null=True, blank=True)
    COMMENTS = models.CharField(max_length=100, null=True, blank=True)
    STATUS = models.CharField(max_length=100, null=True, blank=True,default='Pending for Approval')
    ApplicationUsage = models.CharField(max_length=100, null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True,editable=False)
    
    VehiclePurchaseDoc=models.TextField(null=True, blank=True)
     
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)


    class Meta:
        db_table = 'XXGTD_VEHICLE_AUDIT'

    def __str__(self):
        return f"Vehicle Audit: {self.FLEET_CONTROL_NO}"


class XXGTD_INSUR_AUDIT(models.Model):
    PROCESS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('Approved', 'Approved'),
        ('Rectification', 'Rectification')
    )
    INSUR_AUDIT_ID= models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
   
    INS_LINE_ID = models.ForeignKey(XXGTD_INSURANCE_INFO, on_delete=models.CASCADE, to_field='INS_LINE_ID', db_column='INS_LINE_ID', related_name='insur_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    
    INSURANCE_COMPANY = models.CharField(max_length=100, null=True, blank=True)
    POLICY_NO = models.CharField(max_length=100, null=True, blank=True)
    
    POLICY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_START_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_MOT_INS = models.CharField(max_length=100, null=True, blank=True)
    
    FLEET_PROCESS = models.CharField(max_length=200,null=True, choices=PROCESS_CHOICES, default='Pending for Approval', blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    PROCESS=models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_INSUR_AUDIT'

    def __str__(self):
        return f"Insurance Audit: {self.INSUR_AUDIT_ID}"


class XXGTD_REGIS_AUDIT(models.Model):
    REG_AUDIT_ID =models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    REG_LINE_ID = models.ForeignKey(XXGTD_REGISTRATION_INFO, on_delete=models.CASCADE, to_field='REG_LINE_ID', db_column='REG_LINE_ID', related_name='reg_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    
    EMIRATES_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTERED_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REG_COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO1 = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_REG = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True, default='Pending for Approval', blank=True)

    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    PROCESS=models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_REGIS_AUDIT'


class XXGTD_PARK_PERMIT_AUDIT(models.Model):
    PP_AUDIT_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    PERMIT_LINE_ID = models.ForeignKey(XXGTD_PARKING_PERMIT, on_delete=models.CASCADE, to_field='PERMIT_LINE_ID', db_column='PERMIT_LINE_ID', related_name='permit_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_TYPE = models.CharField(max_length=100, null=True, blank=True)
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    ISSUING_AUTHORITY = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_NO = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_DATE = models.DateField(null=True, blank=True)
    PERMIT_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_PERMIT = models.CharField(max_length=100, null=True, blank=True)
    PermitColor = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200,null=True, default='Pending for Approval', blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
   
    class Meta:
        db_table = 'XXGTD_PARK_PERMIT_AUDIT'

    def __str__(self):
        return f"Permit Audit {self.PP_AUDIT_ID}"



class XXGTD_FUEL_AUDIT(models.Model):
    FUEL_AUDIT_ID=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    FUEL_LINE_ID= models.ForeignKey(XXGTD_FUEL_INFO, on_delete=models.CASCADE, to_field='FUEL_LINE_ID', db_column='FUEL_LINE_ID', related_name='fuel_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)

    FUEL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    MONTHLY_FUEL_LIMIT = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_NO = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_DATE = models.DateField(null=True, blank=True)
    FUEL_DOC_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_FUEL_DOC = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True, default='Pending for Approval', blank=True)


    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_FUEL_AUDIT'

class XXGTD_GPS_TRACKING_AUDIT(models.Model):
    GPS_AUDIT_ID =models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    GT_LINE_ID= models.ForeignKey(XXGTD_GPS_TRACKING_INFO, on_delete=models.CASCADE, to_field='GT_LINE_ID', db_column='GT_LINE_ID', related_name='gps_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    GPS_DEVICE_NO = models.CharField(max_length=100, null=True, blank=True)
    GPS_INSTALLATION_DATE = models.DateField(null=True, blank=True)
    GPS_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True, default='Pending for Approval', blank=True)
    
   
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_GPS_TRACKING_AUDIT'

class XXGTD_ALLOCATION_AUDIT(models.Model):
    FT_ALLOC_ID=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    ALLOC_LINE_ID= models.ForeignKey(XXGTD_ALLOCATION_INFO, on_delete=models.CASCADE, to_field='ALLOC_LINE_ID', db_column='ALLOC_LINE_ID', related_name='allo_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
   
    COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    DIVISION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_LOCATION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    APPICATION_USAGE = models.CharField(max_length=100, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    ALLOCATION_END_DATE=models.DateField(null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200,null=True,  default='Pending for Approval', blank=True)


    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    PROCESS=models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_FLEET_ALLOC_AUDIT'

class XXGTD_DRIVER_ASSIG_AUDIT(models.Model):
    DA_AUDIT_ID =models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    ASGN_LINE_ID= models.ForeignKey(XXGTD_DRIVER_ASSIGNMENT, on_delete=models.CASCADE, to_field='ASGN_LINE_ID', db_column='ASGN_LINE_ID', related_name='driver_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    EMPLOYEE_NO = models.IntegerField(null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=100, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=100, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=20, null=True, blank=True)
    ASSIGNMENT_DATE = models.DateField(null=True, blank=True)
    ASSIGNMENT_END_DATE = models.DateField(null=True, blank=True)
    TRAFFIC_CODE_NO = models.CharField(max_length=50, null=True, blank=True)
    DRIVING_LICENSE_NO = models.CharField(max_length=50, null=True, blank=True)
    LICENSE_TYPE = models.CharField(max_length=50, null=True, blank=True)
    PLACE_OF_ISSUE = models.CharField(max_length=100, null=True, blank=True)
    LICENSE_EXPIRY_DATE = models.DateField(null=True, blank=True)
    GPS_TAG_NO = models.CharField(max_length=50, null=True, blank=True)
    GPS_TAG_ASSIGN_DATE = models.DateField(null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200,null=True, default='Pending for Approval', blank=True)


    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_DRIVER_ASSIG_AUDIT'

class XXGTD_ROAD_TOLL_AUDIT(models.Model):
    RT_AUDIT_ID =models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    RT_LINE_ID= models.ForeignKey(XXGTD_ROAD_TOLL_INFO, on_delete=models.CASCADE, to_field='RT_LINE_ID', db_column='RT_LINE_ID', related_name='roadtoll_audits')
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    
    
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    TOLL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=100, null=True, blank=True)
    TAG_NO = models.CharField(max_length=100, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE = models.DateField(null=True, blank=True)
    CURRENT_STATUS = models.CharField(max_length=100, null=True, blank=True)
    FLEET_PROCESS = models.CharField(max_length=200, null=True,default='Pending for Approval', blank=True)

    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    PROCESS=models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_ROAD_TOLL_AUDIT'




class XXALY_GTD_LOOKUP_MASTER (models.Model):
    MEANING = models.CharField(max_length=200,null=True, blank=True)
    LOOKUP_NAME = models.CharField(max_length=200,null=True, blank=True)
    ACTIVE=models.CharField(max_length=200,null=True, blank=True)
    START_DATE=models.DateField(null=True, blank=True)
    END_DATE=models.DateField(null=True, blank=True)
    CREATION_DATE=models.DateField(null=True, blank=True)
    CREATED_BY=models.CharField(max_length=200,null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=200,null=True, blank=True)
    DISPLAY_TO_ADMIN=models.CharField(max_length=200,null=True, blank=True)
    DISPLAY_TO_USER=models.CharField(max_length=200,null=True, blank=True)
    class Meta:
        db_table = 'XXALY_GTD_LOOKUP_MASTER'



class XXALY_GTD_LOOKUP_DETAIL (models.Model):
    LOOKUP_CODE = models.CharField(max_length=200,null=True, blank=True)
    LOOKUP_VALUE = models.CharField(max_length=200,null=True, blank=True)
    ACTIVE = models.CharField(max_length=200,null=True, blank=True)      
    START_DATE =  models.DateField(null=True, blank=True)
    END_DATE  =   models.DateField(null=True, blank=True)
    CREATION_DATE  = models.DateField(null=True, blank=True)
    CREATED_BY       = models.CharField(max_length=200,null=True, blank=True)
    LAST_UPDATE_DATE  = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY    = models.CharField(max_length=200,null=True, blank=True)
    LOOKUP_SHORT_CODE  = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE_CATEGORY  = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE1          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE2         = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE3         = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE4          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE5          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE6          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE7          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE8          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE9          = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE10         = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE11        = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE12         = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE13        = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE14         = models.CharField(max_length=200,null=True, blank=True)
    ATTRIBUTE15         = models.CharField(max_length=200,null=True, blank=True)
    MEANING             = models.CharField(max_length=200,null=True, blank=True)
    LOOKUP_NAME       = models.CharField(max_length=200,null=True, blank=True)

    class Meta:
        db_table = 'XXALY_GTD_LOOKUP_DETAIL'







class XXGTD_TRAFFIC_FILE_MASTER(models.Model):
    TRAFFIC_FILE_ID=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    TRAFFIC_FILE_NO = models.CharField(max_length=250,null=True, blank=True)
    COMPANY_NAME = models.CharField(max_length=250, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=250, null=True, blank=True)
    EMIRATES = models.CharField(max_length=50, null=True, blank=True)
    FEDERAL_TRAFFIC_FILE_NO = models.CharField(max_length=250,null=True, blank=True)
    SALIK_ACCOUNT_NO = models.CharField(max_length=250,null=True, blank=True)
    CREATION_DATE = models.DateField(null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    RECORD_STATUS = models.CharField(max_length=240, null=True, blank=True)
    STATUS = models.CharField(max_length=50, null=True, blank=True)
    COMMENTS = models.CharField(max_length=4000, null=True, blank=True)
    NO_OF_VEHICLES = models.IntegerField(null=True, blank=True,default=0)

    class Meta:
        db_table = 'XXGTD_TRAFFIC_FILE_MASTER'

    def __str__(self):
        return f"Traffic File {self.traffic_file_no}"





class CommercialAttachment(models.Model):
    commercial_master = models.ForeignKey(XXGTD_COMMERCIAL_PLATE_INFO, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to='commercial_attachments/')
    upload_date = models.DateField(auto_now_add=True, null=True, blank=True)
    attachment_type = models.CharField(max_length=50, null=True, blank=True)
    CommercialNumber = models.CharField(max_length=200, null=True, blank=True)
    uploaded_by = models.CharField(max_length=200, null=True, blank=True)

    def _str_(self):
        return f"Attachment for {self.commercial_master.CommercialNumber if self.commercial_master else 'Unknown'} - {self.attachment_type}"
    class Meta:
        db_table = 'CommercialAttachment'


# class SharedControlNumber(models.Model):
    
#     last_number = models.IntegerField(default=100000)
#     last_header_number = models.IntegerField(default=100000)

#     @classmethod
#     def get_next_number(cls, HEADER_ID=None):
#         if HEADER_ID:
#             return f'AY-{HEADER_ID}'
#         else:
#             instance, created = cls.objects.get_or_create(pk=1)
#             instance.last_number += 1
#             instance.save()
#             return f'AY-{instance.last_number}'


#     @classmethod
#     def get_next_header_number(cls):
#         instance, created = cls.objects.get_or_create(pk=1)
#         current_number = instance.last_header_number
#         instance.last_header_number += 1
#         instance.save()
#         return str(current_number)


class ApprovalRequest(models.Model):
    REQUEST_TYPES = (
        ('FLEET', 'Fleet Master'),
        ('COMMERCIAL', 'Commercial Master'),
        ('TRAFFIC', 'Traffic File Master'),
    )
   
    STATUS_CHOICES = (
        ('Pending for Approval', 'Pending for Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    request_number = models.CharField(max_length=150, unique=True)
    application_number = models.CharField(max_length=150, default='',blank=True,null=True)  # Added default value
    company_name = models.CharField(max_length=100,blank=True,null=True)
    request_type = models.CharField(max_length=150, choices=REQUEST_TYPES,blank=True,null=True)
    request_details = models.CharField(max_length=150, default='Modified',blank=True,null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending for Approval',blank=True,null=True)
    creation_date = models.DateField(auto_now_add=True,blank=True,null=True)
    last_update_date = models.DateField(auto_now=True,blank=True,null=True)
    comments = models.TextField(max_length=200, blank=True, null=True)
    
    responded_by = models.CharField(max_length=150, blank=True, null=True)
    response_role = models.CharField(max_length=50, default='',blank=True,null=True)  # Added default value
    action = models.CharField(max_length=100, default='',blank=True,null=True)  # Added default value
   
    fleet_master = models.ForeignKey('XXGTD_VEHICLE_INFO', on_delete=models.CASCADE, null=True, blank=True)
    commercial_master = models.ForeignKey('XXGTD_COMMERCIAL_PLATE_INFO', on_delete=models.CASCADE, null=True, blank=True)
    traffic_file_master = models.ForeignKey('XXGTD_TRAFFIC_FILE_MASTER', on_delete=models.CASCADE, null=True, blank=True)

    def _str_(self):
        return f"{self.request_type} - {self.request_number}"
    
    def create_action_history(self, CustomUser, action_performed):
        CustomUser = AbstractUser()
        
        XXALY_GTD_ACTION_HISTORY.objects.create(
            APPLICATION_ID=str(self.id),
            APPL_NUMBER=self.request_number,
            REQUEST_TYPE=self.request_type,
            REQUEST_NUMBER=self.request_number,
            PROCESS_STATUS=self.status,
            DOC_STATUS=self.status,
            RESPONSE_DATE=timezone.now(),
            RESPONDED_BY=CustomUser.username if CustomUser else "System",
            RESPONDER_ROLE=CustomUser.roles if CustomUser else "System",
            RESPONSE_COMMENTS=self.comments,
            ACTION_PERFORMED=action_performed,
            CREATED_BY=CustomUser.username if CustomUser else "System",
            CREATION_DATE=self.creation_date.date(),
            LAST_UPDATED_BY=CustomUser.username if CustomUser else "System",
            LAST_UPDATE_DATE=self.last_update_date.date(),
            NEXT_RESP="APPROVER" if CustomUser and CustomUser.roles == "REQUESTOR" else "REQUESTOR"
        )
        
   

class XXALY_GTD_ACTION_HISTORY(models.Model):

    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    APPLICATION_ID = models.CharField (max_length=100 ,blank=True,null=True,)
    APPL_NUMBER   = models.CharField (max_length=100 ,blank=True,null=True,)
    REQUEST_TYPE    = models.CharField(max_length=100 ,blank=True,null=True,)
    REQUEST_NUMBER    = models.CharField (max_length=100 ,blank=True,null=True,)
    PROCESS_STATUS     = models.CharField (max_length=100 ,blank=True,null=True,)
    DOC_STATUS         = models.CharField (max_length=100 ,blank=True,null=True,)
    RESPONSE_DATE      = models.DateField(null=True, blank=True)
    RESPONDED_BY        = models.CharField (max_length=100 ,blank=True,null=True,)
    RESPONDER_ROLE      = models.CharField (max_length=100 ,blank=True,null=True,)
    RESPONSE_COMMENTS   = models.CharField (max_length=100 ,blank=True,null=True,)
    ACTION_PERFORMED    = models.CharField (max_length=100 ,blank=True,null=True,)
    ERROR_MISTAKE_FLAG  = models.CharField (max_length=100 ,blank=True,null=True,)
    NEED_INFO_FLAG     = models.CharField (max_length=100 ,blank=True,null=True,)
    NEXT_RESP           = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE_CATEGORY  = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE1          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE2          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE3          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE4          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE5          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE6          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE7          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE8          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE9          = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE10         = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE11         = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE12         = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE13         = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE14         = models.CharField (max_length=100 ,blank=True,null=True,)
    ATTRIBUTE15         = models.CharField (max_length=100 ,blank=True,null=True,)
    CREATED_BY          = models.CharField (max_length=100 ,blank=True,null=True,)
    CREATION_DATE       = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY     = models.CharField (max_length=100 ,blank=True,null=True,)
    LAST_UPDATE_DATE    = models.DateField(null=True, blank=True)
    
  
    class Meta:
        db_table = 'XXALY_GTD_ACTION_HISTORY'


class XXALY_GTD_DATA_COMPARE_T(models.Model):
    
    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    COLUMN_NAME = models.CharField(max_length=240, null=True, blank=True)
    ACTUAL_COLUMN_NAME = models.CharField(max_length=240, null=True, blank=True)
    COLUMN_VALUE1 = models.CharField(max_length=240, null=True, blank=True)
    COLUMN_VALUE2 = models.CharField(max_length=240, null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True)
    CREATED_BY = models.CharField(max_length=50, null=True, blank=True)
    TABLE_NAME = models.CharField(max_length=240, null=True, blank=True)
    LINE_ID = models.CharField(max_length=240, null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'XXALY_GTD_DATA_COMPARE_T'
        verbose_name = 'GTD Data Compare'
        verbose_name_plural = 'GTD Data Compares'

    def __str__(self):
        return f"{self.TABLE_NAME} - {self.COLUMN_NAME}"
    

class XXALY_GTD_DATA_COMPARE_HIST(models.Model):
    
    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    COLUMN_NAME = models.CharField(max_length=240, null=True, blank=True)
    ACTUAL_COLUMN_NAME = models.CharField(max_length=240, null=True, blank=True)
    COLUMN_VALUE1 = models.CharField(max_length=240, null=True, blank=True)
    COLUMN_VALUE2 = models.CharField(max_length=240, null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True)
    CREATED_BY = models.CharField(max_length=50, null=True, blank=True)
    TABLE_NAME = models.CharField(max_length=240, null=True, blank=True)
    LINE_ID = models.CharField(max_length=240, null=True, blank=True)
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'XXALY_GTD_DATA_COMPARE_HIST'
        verbose_name = 'GTD Data Compare History'
        verbose_name_plural = 'GTD Data Compares History'

    def __str__(self):
        return f"{self.TABLE_NAME} - {self.COLUMN_NAME}"
    
    

class XXGTD_COMM_DETAIL_AUDIT(models.Model):
    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    
 
    HEADER_ID = models.CharField(max_length=200, null=True, blank=True)
    
    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)
    COMM_PLATE_NO =models.CharField(max_length=200, null=True, blank=True)
    COMM_PLATE_DATE = models.DateField(null=True, blank=True)
    COMM_PLATE_CATEGORY =models.CharField(max_length=200, null=True, blank=True)
    CP_ISSUED_AUTHORITY =models.CharField(max_length=200, null=True, blank=True)
    CP_VEHICLE_TYPE =models.CharField(max_length=200, null=True, blank=True)
    CP_COLOR =models.CharField(max_length=200, null=True, blank=True)
    STATUS = models.CharField(max_length=50, null=True, blank=True)
    
    INSURANCE_COMPANY =models.CharField(max_length=200, null=True, blank=True)
    POLICY_NO =models.CharField(max_length=200, null=True, blank=True)
    POLICY_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PLATE_INSURANCE_EXPIRY_DATE = models.DateField(null=True, blank=True)
    INSURANCE_STATUS =models.CharField(max_length=200, null=True, blank=True)
    
    REGISTRATION_NO =models.CharField(max_length=200, null=True, blank=True)
    REGISTRATION_NO1 =models.CharField(max_length=200, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REGISTERED_EMIRATES =models.CharField(max_length=200, null=True, blank=True)
    EMIRATES_TRF_FILE_NO =  models.CharField(max_length=100, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    REG_COMPANY_NAME =models.CharField(max_length=200, null=True, blank=True)
    REG_STATUS =models.CharField(max_length=200, null=True, blank=True)
    TRADE_LICENSE_NO =  models.CharField(max_length=100, null=True, blank=True)
    
    EMIRATES =models.CharField(max_length=200, null=True, blank=True)
    TOLL_TYPE =models.CharField(max_length=200, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=50, null=True, blank=True)
    TAG_NO = models.CharField(max_length=50, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE = models.DateField(null=True, blank=True)
    TOLL_STATUS =models.CharField(max_length=200, null=True, blank=True)
    
    
    COMPANY_NAME =models.CharField(max_length=200, null=True, blank=True)
    DIVISION =models.CharField(max_length=200, null=True, blank=True)
    OPERATING_LOCATION =models.CharField(max_length=200, null=True, blank=True)
    OPERATING_EMIRATES =models.CharField(max_length=200, null=True, blank=True)
    APPICATION_USAGE =models.CharField(max_length=200, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    ALLOCATION_END_DATE= models.DateField(null=True, blank=True)
    EMPLOYEE_NO =  models.CharField(max_length=100, null=True, blank=True)
    EMPLOYEE_NAME =models.CharField(max_length=200, null=True, blank=True)
    DESIGNATION =models.CharField(max_length=200, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=50, null=True, blank=True)
    
    
    ACTION_CODE = models.CharField(max_length=1)
    ACTION = models.CharField(max_length=50, null=True, blank=True)
    CREATION_DATE = models.DateField(null=True, blank=True)
    CREATED_BY =models.CharField(max_length=200, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE1 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE2 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE3 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE4 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE5 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE6 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE7 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE8 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE9 =models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE10 =models.CharField(max_length=200, null=True, blank=True)
    INS_LINE_ID = models.ForeignKey('XXGTD_INSURANCE_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='comm_detail_audit_insurance', db_column='INS_LINE_ID ')
    REG_LINE_ID = models.ForeignKey('XXGTD_REGISTRATION_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='comm_detail_audit_registration', db_column='REG_LINE_ID ')
    ALLOC_LINE_ID = models.ForeignKey('XXGTD_ALLOCATION_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='comm_detail_audit_allocation', db_column='ALLOC_LINE_ID')
    RT_LINE_ID = models.ForeignKey('XXGTD_ROAD_TOLL_INFO', on_delete=models.SET_NULL, null=True, blank=True, related_name='comm_detail_audit_roadtoll', db_column='RT_LINE_ID ')

    COMM_CONTROL_NO = models.CharField(max_length=50, null=True, blank=True)
    COMMENTS = models.CharField(max_length=4000)
    COMM_COMPANY =models.CharField(max_length=200, null=True, blank=True)
    INS_START_DATE = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_COMM_DETAIL_AUDIT'




class XXGTD_CPI_AUDIT(models.Model):
    
    CP_AUDIT_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID') 
    COMM_PLATE_NO =  models.CharField(max_length=50, null=True, blank=True)
    COMM_PLATE_DATE = models.DateField(null=True, blank=True)
    COMM_PLATE_CATEGORY = models.CharField(max_length=200, null=True, blank=True)
    CP_ISSUED_AUTHORITY = models.CharField(max_length=200, null=True, blank=True)
    CP_VEHICLE_TYPE = models.CharField(max_length=200, null=True, blank=True)
    CP_COLOR = models.CharField(max_length=200, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION =  models.CharField(max_length=50, null=True, blank=True)
    RECORD_STATUS = models.CharField(max_length=200, null=True, blank=True)
    CREATION_DATE = models.DateField(null=True, blank=True)
    CREATED_BY = models.CharField(max_length=200, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=200, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=200, null=True, blank=True)
    STATUS =  models.CharField(max_length=50, null=True, blank=True)
    COMM_CONTROL_NO =  models.CharField(max_length=50, null=True, blank=True)
    COMMENTS =models.CharField(max_length=40000, null=True, blank=True)
    HEADER_ID = models.CharField(max_length=200, null=True, blank=True)
    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_CPI_AUDIT'


class REVERT_APPROVES(models.Model):
    HEADER_ID = models.CharField(max_length=100)
    APPROVED_DATE = models.DateTimeField(auto_now=True)

    # XXGTD_VEHICLE_INFO fields
    FM_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    FM_TABLE_NAME = models.CharField(max_length=100, default='XXGTD_VEHICLE_INFO')
    COMPANY_NAME = models.CharField(max_length=200, null=True, blank=True)
    FLEET_CONTROL_NO = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CREATION_DATE = models.DateField(null=True, blank=True)
    VIN_NO = models.CharField(max_length=100, null=True, blank=True)
    MANUFACTURER = models.CharField(max_length=100, null=True, blank=True)
    MODEL = models.CharField(max_length=100, null=True, blank=True)
    VEHICLE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    COLOR = models.CharField(max_length=100, null=True, blank=True)
    FLEET_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    FLEET_SUB_CATEGORY = models.CharField(max_length=100, null=True, blank=True)
    ENGINE_NO = models.CharField(max_length=100, null=True, blank=True)
    MODEL_YEAR = models.CharField(max_length=100, null=True, blank=True)
    COUNTRY_OF_ORIGIN = models.CharField(max_length=100, null=True, blank=True)
    SEATING_CAPACITY = models.CharField(max_length=100, null=True, blank=True)
    TONNAGE = models.CharField(max_length=100, null=True, blank=True)
    GROSS_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    EMPTY_WEIGHT_KG = models.CharField(max_length=100, null=True, blank=True)
    PURCHASE_VALUE_AED = models.CharField(max_length=100, null=True, blank=True)
    COMMENTS = models.CharField(max_length=100, null=True, blank=True)
    STATUS = models.CharField(max_length=100, null=True, blank=True)
    ApplicationUsage = models.CharField(max_length=100, null=True, blank=True)

    # Insurance fields
    INS_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    INS_TABLE_NAME = models.CharField(max_length=100, default='Insurance')
    INSURANCE_COMPANY = models.CharField(max_length=100, null=True, blank=True)
    POLICY_NO = models.CharField(max_length=100, null=True, blank=True)
    POLICY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_START_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_MOT_INS = models.CharField(max_length=100, null=True, blank=True)

    # Registration fields
    REG_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    REG_TABLE_NAME = models.CharField(max_length=100, default='Registration')
    EMIRATES_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTERED_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REG_COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO1 = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_REG = models.CharField(max_length=100, null=True, blank=True)

    # Roadtoll fields
    RT_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    RT_TABLE_NAME = models.CharField(max_length=100, default='Roadtoll')
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    TOLL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=100, null=True, blank=True)
    TAG_NO = models.CharField(max_length=100, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE= models.DateField(null=True, blank=True)
    CURRENT_STATUS = models.CharField(max_length=100, null=True, blank=True)

    # Fuel fields
    FUEL_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    FUEL_TABLE_NAME = models.CharField(max_length=100, default='Fuel')
    FUEL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    MONTHLY_FUEL_LIMIT = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_TYPE = models.CharField(max_length=100, null=True, blank=True)
    FUEL_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_NO = models.CharField(max_length=100, null=True, blank=True)
    FUEL_DOCUMENT_DATE = models.DateField(null=True, blank=True)
    FUEL_DOC_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_FUEL_DOC = models.CharField(max_length=100, null=True, blank=True)

    # Permits fields
    PERMIT_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_TABLE_NAME = models.CharField(max_length=100, default='Permits')
    PERMIT_TYPE = models.CharField(max_length=100, null=True, blank=True)
    ISSUING_AUTHORITY = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_NO = models.CharField(max_length=100, null=True, blank=True)
    PERMIT_DATE = models.DateField(null=True, blank=True)
    PERMIT_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_PERMIT = models.CharField(max_length=100, null=True, blank=True)
    PermitColor = models.CharField(max_length=100, null=True, blank=True)

    # GPS fields
    GT_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    GT_TABLE_NAME = models.CharField(max_length=100, default='Gps')
    GPS_DEVICE_NO = models.CharField(max_length=100, null=True, blank=True)
    GPS_INSTALLATION_DATE = models.DateField(null=True, blank=True)
    GPS_SERVICE_PROVIDER = models.CharField(max_length=100, null=True, blank=True)

    # Driver fields
    ASGN_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    ASGN_TABLE_NAME = models.CharField(max_length=100, default='Driver')
    EMPLOYEE_NO = models.CharField(max_length=100, null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=100, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=100, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=20, null=True, blank=True)
    ASSIGNMENT_DATE = models.DateField(null=True, blank=True)
    TRAFFIC_CODE_NO = models.CharField(max_length=50, null=True, blank=True)
    DRIVING_LICENSE_NO = models.CharField(max_length=50, null=True, blank=True)
    LICENSE_TYPE = models.CharField(max_length=50, null=True, blank=True)
    PLACE_OF_ISSUE = models.CharField(max_length=100, null=True, blank=True)
    LICENSE_EXPIRY_DATE = models.DateField(null=True, blank=True)
    GPS_TAG_NO = models.CharField(max_length=50, null=True, blank=True)
    GPS_TAG_ASSIGN_DATE = models.DateField(null=True, blank=True)
    ASSIGNMENT_END_DATE = models.DateField(null=True, blank=True)

    # Allocation fields
    ALLOC_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    ALLOC_TABLE_NAME = models.CharField(max_length=100, default='Allocation')
    COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    DIVISION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_LOCATION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    APPICATION_USAGE = models.CharField(max_length=100, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    ALLOCATION_END_DATE = models.DateField(null=True, blank=True)

    


class REVERT_COMMERCIAL_APPROVES(models.Model):
    HEADER_ID = models.CharField(max_length=100)
    APPROVED_DATE = models.DateTimeField(auto_now=True)

    # XXGTD_VEHICLE_INFO fields
    CM_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    CM_TABLE_NAME = models.CharField(max_length=100, default='CommercialMaster')
    COMPANY_NAME      = models.CharField(max_length=200, null=True, blank=True)
    COMM_CONTROL_NO  = models.CharField(max_length=100, null=True, blank=True,  editable=False)
    COMM_PLATE_NO = models.CharField(max_length=200, null=True, blank=True)
    COMM_PLATE_DATE  = models.DateField(null=True, blank=True)
    COMM_PLATE_CATEGORY = models.CharField(max_length=200, null=True, blank=True)
    CP_ISSUED_AUTHORITY = models.CharField(max_length=200, null=True, blank=True)
    CP_VEHICLE_TYPE  = models.CharField(max_length=200, null=True, blank=True)
    CP_COLOR   = models.CharField(max_length=200, null=True, blank=True)
    
    STATUS = models.CharField(max_length=100, null=True, blank=True)
    
    
    
    
  
    # Insurance fields
    INS_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    INS_TABLE_NAME = models.CharField(max_length=100, default='Insurance')
    INSURANCE_COMPANY = models.CharField(max_length=100, null=True, blank=True)
    POLICY_NO = models.CharField(max_length=100, null=True, blank=True)
    POLICY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_START_DATE = models.DateField(null=True, blank=True)
    POLICY_EXPIRY_DATE = models.DateField(null=True, blank=True)
    PLTS_INS_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_MOT_INS = models.CharField(max_length=100, null=True, blank=True)

    # Registration fields
    REG_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    REG_TABLE_NAME = models.CharField(max_length=100, default='Registration')
    EMIRATES_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTERED_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    FEDERAL_TRF_FILE_NO = models.CharField(max_length=100, null=True, blank=True)
    REG_COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    TRADE_LICENSE_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO1 = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_NO = models.CharField(max_length=100, null=True, blank=True)
    REGISTRATION_DATE = models.DateField(null=True, blank=True)
    REG_EXPIRY_DATE = models.DateField(null=True, blank=True)
    CUR_STAT_REG = models.CharField(max_length=100, null=True, blank=True)

    # Roadtoll fields
    RT_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    RT_TABLE_NAME = models.CharField(max_length=100, default='Roadtoll')
    EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    TOLL_TYPE = models.CharField(max_length=100, null=True, blank=True)
    ACCOUNT_NO = models.CharField(max_length=100, null=True, blank=True)
    TAG_NO = models.CharField(max_length=100, null=True, blank=True)
    ACTIVATION_DATE = models.DateField(null=True, blank=True)
    ACTIVATION_END_DATE= models.DateField(null=True, blank=True)
    CURRENT_STATUS = models.CharField(max_length=100, null=True, blank=True)

   

    # Allocation fields
    ALLOC_LINE_ID = models.CharField(max_length=100, null=True, blank=True)
    ALLOC_TABLE_NAME = models.CharField(max_length=100, default='Allocation')
    COMPANY_NAME = models.CharField(max_length=100, null=True, blank=True)
    DIVISION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_LOCATION = models.CharField(max_length=100, null=True, blank=True)
    OPERATING_EMIRATES = models.CharField(max_length=100, null=True, blank=True)
    APPICATION_USAGE = models.CharField(max_length=100, null=True, blank=True)
    ALLOCATION_DATE = models.DateField(null=True, blank=True)
    ALLOCATION_END_DATE = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('HEADER_ID', 'CM_LINE_ID', 'INS_LINE_ID', 'REG_LINE_ID', 'RT_LINE_ID', 'ALLOC_LINE_ID')


class XXGTDAssetAssignment(models.Model):
    
    ASSET_LINE_ID = models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')
    
    HEADER_ID = models.CharField(max_length=100, null=True, blank=True)
    ASSET_NO = models.BigIntegerField(null=True, blank=True)
    ASSET_REG_DATE = models.DateField(null=True, blank=True)
    LATEST_BOOK_VALUE = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    BOOK_VALUE_DATE = models.DateField(null=True, blank=True)
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)
    ACTION_CODE = models.CharField(max_length=1, null=True, blank=True)
    ACTION = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_ASSET_ASSIGNMENT'

    def _str_(self):
        return f"Asset Assignment {self.ASSET_NO}"


from django.db import models

class XXALY_FA_ASSET_GTD_V(models.Model):
    asset_id = models.BigIntegerField(primary_key=True)  # Unique identifier for the asset
    asset_number = models.CharField(max_length=200, unique=True)  # Unique asset number
    tag_number = models.CharField(max_length=200, blank=True, null=True)  # Tag for identification
    description = models.CharField(max_length=80,blank=True, null=True)  # Asset description
    manufacturer_name = models.CharField(max_length=360, blank=True, null=True)  # Manufacturer details
    serial_number = models.CharField(max_length=35, blank=True, null=True)  # Serial number of the asset
    model_number = models.CharField(max_length=40, blank=True, null=True)  # Model number of the asset
    major_category = models.CharField(max_length=30,blank=True, null=True)  # Broad asset classification
    sub_category = models.CharField(max_length=30, blank=True, null=True)  # Specific asset classification
    book_type_code = models.CharField(max_length=200,blank=True, null=True)  # Financial book type
    date_placed_in_service = models.DateField(blank=True, null=True)  # Date when the asset was placed into service
    deprn_method_code = models.CharField(max_length=200,blank=True, null=True)  # Depreciation method
    life_in_months = models.PositiveIntegerField(blank=True, null=True)  # Useful life in months
    nbv = models.DecimalField(max_digits=200, decimal_places=2, blank=True, null=True)  # Net book value
    dep_run_date = models.DateField(blank=True, null=True)  # Last depreciation run date
    cost = models.DecimalField(max_digits=200, decimal_places=2,blank=True,null=True)  # Cost of the asset
    salvage_value = models.DecimalField(max_digits=200, decimal_places=2, blank=True, null=True)  # Salvage value
    adjusted_rate = models.DecimalField(max_digits=200, decimal_places=5, blank=True, null=True)  # Adjusted rate for depreciation
    production_capacity = models.PositiveIntegerField(blank=True, null=True)  # Production capacity of the asset


    class  Meta:
        db_table ='XXALY_FA_ASSET_GTD_V'
    def __str__(self):
        return f"{self.asset_number} - {self.description}"

    


class XXGDT_PAYABLE_INV_DETS_V(models.Model):
    ORG_IDNUMBER = models.BigIntegerField(primary_key=True)  # Organization identifier
    INVOICE_IDNUMBE = models.BigIntegerField(blank=True, null=True)  # Invoice identifier
    INVOICE_NUMVARCHAR2 = models.CharField(max_length=250, unique=True,blank=True, null=True)  # Unique invoice number
    INVOICE_DATEDATE = models.DateField(blank=True, null=True)  # Date of the invoice
    GL_DATEDATE = models.DateField(blank=True, null=True)  # General ledger date
    INVOICE_AMOUNTNUMBER = models.DecimalField(max_digits=200, decimal_places=2,blank=True, null=True)  # Invoice amount
    INVOICE_STATUSVARCHAR2 = models.CharField(max_length=200,blank=True, null=True)  # Status of the invoice
    LINE_DESCRIPTIONVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Line item description
    SERIAL_NUMBERVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Serial number (e.g., item serial number)
    REGISTRATIONNOVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Registration number
    CATEGORYVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Invoice category
    SUBCATEGORYVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Invoice subcategory
    COST_TYPEVARCHAR2 = models.CharField(max_length=240, blank=True, null=True)  # Cost type (e.g., fixed, variable)

    def __str__(self):
        return f"Invoice {self.INVOICE_NUMVARCHAR2} - {self.INVOICE_STATUSVARCHAR2}"

    class Meta:
        db_table = 'XXGDT_PAYABLE_INV_DETS_V'
        verbose_name = "Payable Invoice Detail"
        verbose_name_plural = "Payable Invoice Details"
        indexes = [
            models.Index(fields=['ORG_IDNUMBER']),
            models.Index(fields=['INVOICE_IDNUMBE']),
            models.Index(fields=['INVOICE_STATUSVARCHAR2']),
        ]
        unique_together = ('ORG_IDNUMBER', 'INVOICE_NUMVARCHAR2')
    
    
class XXGTDFleetExpenseUpload(models.Model):
    SEQ_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    SERIAL_NUMBER = models.CharField(max_length=240, null=True, blank=True)
    EXPENSE_DATE = models.DateField(null=True, blank=True)
    COST_TYPE = models.CharField(max_length=240, null=True, blank=True)
    CATEGORY = models.CharField(max_length=240, null=True, blank=True)
    SUB_CATEGORY = models.CharField(max_length=240, null=True, blank=True)
    VEHICLE_REG_NO = models.CharField(max_length=50, null=True, blank=True)
    AMOUNT = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    REMARKS = models.TextField(max_length=4000, null=True, blank=True)
    
    CREATION_DATE = models.DateField(auto_now_add=True, null=True, blank=True)
    CREATED_BY = models.CharField(max_length=240, null=True, blank=True)
    LAST_UPDATE_DATE = models.DateField(auto_now=True, null=True, blank=True)
    LAST_UPDATED_BY = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE1 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE2 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE3 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE4 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE5 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE6 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE7 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE8 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE9 = models.CharField(max_length=240, null=True, blank=True)
    ATTRIBUTE10 = models.CharField(max_length=240, null=True, blank=True)

    class Meta:
        db_table = 'XXGTD_FLEET_EXPENSE_UPLOAD'

    def _str_(self):
        return f"Fleet Expense Upload {self.SERIAL_NUMBER}"
    
    
    

class XXGTDTfmAudit(models.Model):
    TFM_AUDIT_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    TRAFFIC_FILE_NO = models.BigIntegerField(db_column='TRAFFIC_FILE_NO', blank=True, null=True, )
    COMPANY_NAME = models.CharField(max_length=250, db_column='COMPANY_NAME', blank=True, null=True, )
    TRADE_LICENSE_NO = models.CharField(max_length=250, db_column='TRADE_LICENSE_NO', blank=True, null=True, )
    EMIRATES = models.CharField(max_length=50, db_column='EMIRATES', blank=True, null=True, )
    FEDERAL_TRAFFIC_FILE_NO = models.BigIntegerField(db_column='FEDERAL_TRAFFIC_FILE_NO', blank=True, null=True, )
    SALIK_ACCOUNT_NO = models.BigIntegerField(db_column='SALIK_ACCOUNT_NO', blank=True, null=True, )
    ACTION_CODE = models.CharField(max_length=1, db_column='ACTION_CODE', blank=True, null=True, )
    ACTION = models.CharField(max_length=50, db_column='ACTION', blank=True, null=True, )
    RECORD_STATUS = models.CharField(max_length=240, db_column='RECORD_STATUS', blank=True, null=True, )
    CREATION_DATE = models.DateField(db_column='CREATION_DATE', blank=True, null=True, )
    CREATED_BY = models.CharField(max_length=240, db_column='CREATED_BY', blank=True, null=True, )
    LAST_UPDATE_DATE = models.DateField(db_column='LAST_UPDATE_DATE', blank=True, null=True, )
    LAST_UPDATED_BY = models.CharField(max_length=240, db_column='LAST_UPDATED_BY', blank=True, null=True, )
    ATTRIBUTE1 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE1')
    ATTRIBUTE2 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE2')
    ATTRIBUTE3 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE3')
    ATTRIBUTE4 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE4')
    ATTRIBUTE5 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE5')
    ATTRIBUTE6 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE6')
    ATTRIBUTE7 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE7')
    ATTRIBUTE8 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE8')
    ATTRIBUTE9 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE9')
    ATTRIBUTE10 = models.CharField(max_length=240, blank=True, null=True, db_column='ATTRIBUTE10')
    STATUS = models.CharField(max_length=50, db_column='STATUS')
    COMMENTS = models.TextField(blank=True, null=True, db_column='COMMENTS')

    class Meta:
        db_table = 'XXGTD_TFM_AUDIT'

    def __str__(self):
        return f"Audit ID: {self.TFM_AUDIT_ID}"



class XXGTDRIVERINFO(models.Model):
    DRIVER_INFO_ID = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    EMPLOYEE_NO = models.CharField(max_length=100, null=True, blank=True)
    EMPLOYEE_NAME = models.CharField(max_length=100, null=True, blank=True)
    DESIGNATION = models.CharField(max_length=100, null=True, blank=True)
    CONTACT_NUMBER = models.CharField(max_length=20, null=True, blank=True)
    CREATION_DATE = models.DateField(db_column='CREATION_DATE', blank=True, null=True, )
    CREATED_BY = models.CharField(max_length=240, db_column='CREATED_BY', blank=True, null=True, )


    class Meta:
        db_table = 'XXGTD_DRIVER_INFO'

    def __str__(self):
        return f"DRIVERINFO ID: {self.DRIVER_INFO_ID}"