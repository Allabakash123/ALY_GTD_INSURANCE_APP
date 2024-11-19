

import json
import os
import re
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Form, File, NinjaAPI, Schema
from ninja.files import UploadedFile
from typing import Any, Dict, List, Optional, Union
from datetime import date, datetime

from django.apps import apps
from requests import Response

from .models import REVERT_APPROVES, REVERT_COMMERCIAL_APPROVES, XXALY_GTD_ACTION_HISTORY, XXALY_GTD_AUDIT_T, XXALY_GTD_DATA_COMPARE_HIST, XXALY_GTD_DATA_COMPARE_T, XXALY_GTD_LOOKUP_DETAIL, XXALY_GTD_LOOKUP_MASTER, XXGTD_CPI_AUDIT, XXGTD_TRAFFIC_FILE_MASTER, XXGTD_ALLOCATION_INFO, ApprovalRequest, Attachment, CommercialAttachment, XXGTD_COMMERCIAL_PLATE_INFO, XXGTD_DRIVER_ASSIGNMENT, XXGTD_VEHICLE_INFO, XXGTD_FUEL_INFO, XXGTD_INSURANCE_INFO, XXGTD_PARKING_PERMIT, XXGTD_GPS_TRACKING_INFO, XXGTD_REGISTRATION_INFO, XXGTD_ROAD_TOLL_INFO, SharedControlNumber, XXGTD_COMM_DETAIL_AUDIT, XXGTD_DRIVER_ASSIG_AUDIT, XXGTD_ALLOCATION_AUDIT, XXGTD_FUEL_AUDIT, XXGTD_GPS_TRACKING_AUDIT, XXGTD_INSUR_AUDIT, XXGTD_PARK_PERMIT_AUDIT, XXGTD_REGIS_AUDIT, XXGTD_ROAD_TOLL_AUDIT, XXGTD_VEHICLE_AUDIT
from django.db.models import Q

    
from django.db.models.functions import Cast
from django.db.models import TextField

   
    
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ninja import NinjaAPI, Form, File
from ninja.files import UploadedFile
from typing import List, Optional


class InsuranceSchema(Schema):
    INSURANCE_COMPANY: str
    POLICY_NO: str
    POLICY_DATE: date
    PLTS_INS_START_DATE: date
    POLICY_EXPIRY_DATE: date
    PLTS_INS_EXPIRY_DATE: date
    CUR_STAT_MOT_INS: str
    InsurancePolicAattachment: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class PermitsSchema(Schema):
    PERMIT_TYPE: str
    EMIRATES: str
    ISSUING_AUTHORITY: str
    PERMIT_NO: str
    PERMIT_DATE: date
    PERMIT_EXPIRY_DATE: date
    CUR_STAT_PERMIT: str
    PermitAattachment: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class GpsSchema(Schema):
    GPS_DEVICE_NO: str
    GPS_INSTALLATION_DATE: date
    GPS_SERVICE_PROVIDER: str
    GpsAattachment: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class RegistrationSchema(Schema):
    EMIRATES_TRF_FILE_NO: str
    REGISTERED_EMIRATES: str
    FEDERAL_TRF_FILE_NO: str
    REG_COMPANY_NAME: str
    TRADE_LICENSE_NO: str
    REGISTRATION_NO1: str
    REGISTRATION_NO: str
    REGISTRATION_DATE: date
    REG_EXPIRY_DATE: date
    CUR_STAT_REG: str
    RegCardAttachment: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None


class FuelSchema(Schema):
    FUEL_TYPE: str
    MONTHLY_FUEL_LIMIT: str
    FUEL_SERVICE_TYPE: str
    FUEL_SERVICE_PROVIDER: str
    FUEL_DOCUMENT_NO: str
    FUEL_DOCUMENT_DATE: date
    FUEL_DOC_EXPIRY_DATE: date
    CUR_STAT_FUEL_DOC: str
    FuelDocumentAttachment: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class FleetMasterSchema(Schema):
    COMPANY_NAME: Optional[str] = None
    FLEET_CONTROL_NO: Optional[str] = None
    FLEET_CREATION_DATE: Optional[date] = None
    VIN_NO: Optional[str] = None
    MANUFACTURER: Optional[str] = None
    MODEL: Optional[str] = None
    VEHICLE_TYPE: Optional[str] = None
    COLOR: Optional[str] = None
    FLEET_CATEGORY: Optional[str] = None
    FLEET_SUB_CATEGORY: Optional[str] = None
    ENGINE_NO: Optional[str] = None
    MODEL_YEAR: Optional[str] = None
    COUNTRY_OF_ORIGIN: Optional[str] = None
    SEATING_CAPACITY: Optional[Union[str,int]] = None
    TONNAGE: Optional[float] = None
    GROSS_WEIGHT_KG: Optional[float] = None
    EMPTY_WEIGHT_KG: Optional[float] = None
    PURCHASE_VALUE_AED: Optional[float] = None
    COMMENTS: Optional[str] = None
    STATUS: Optional[str] = "Pending for Approval"
    ApplicationUsage: Optional[str] = None
    VehiclePurchaseDoc: Optional[str] = None
    HEADER_ID:Optional[str]=None
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    
    

class RoadtollSchema(Schema):
    EMIRATES: str
    TOLL_TYPE: str
    ACCOUNT_NO: str
    TAG_NO: str
    ACTIVATION_DATE: date
    CURRENT_STATUS: str
    ACTIVATION_END_DATE:str
    RoadtollAttachments: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    
class DriverSchema(Schema):
    EMPLOYEE_NAME: str
    DESIGNATION: str
    CONTACT_NUMBER: str
    ASSIGNMENT_DATE: date
    TRAFFIC_CODE_NO: str
    DRIVING_LICENSE_NO: str
    LICENSE_TYPE: str
    PLACE_OF_ISSUE: str
    LICENSE_EXPIRY_DATE: date
    GPS_TAG_NO: str
    GPS_TAG_ASSIGN_DATE: date
    DriverAttachments: str
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    
class AllocationSchema(Schema):
    COMPANY_NAME: str
    DIVISION: str
    OPERATING_LOCATION: str
    OPERATING_EMIRATES: str
    APPICATION_USAGE: str
    ALLOCATION_DATE: date
    ALLOCATION_END_DATE:str
    attachment: Optional[str] = None
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None


class FleetMasterResponse(Schema):
    message: str
    fleet_master: Optional[FleetMasterSchema] = None


api = NinjaAPI()

def update_fleet_master_status(fleet_master):
    fleet_master.STATUS = XXGTD_VEHICLE_INFO.DEFAULT_STATUS
    fleet_master.save()

def get_existing_attachments(fleet_master, attachment_type):
    return set(Attachment.objects.filter(
        fleet_master=fleet_master,
        attachment_type=attachment_type
    ).values_list('file', flat=True))


def move_to_history_and_cleanup(header_id, tracked_changes):
    print(f"Starting move_to_history_and_cleanup for HEADER_ID: {header_id}")

    try:
        with transaction.atomic():
            existing_records = XXALY_GTD_DATA_COMPARE_T.objects.filter(HEADER_ID=header_id)

            if tracked_changes:
                history_objects = [
                    XXALY_GTD_DATA_COMPARE_HIST(
                        COLUMN_NAME=record.COLUMN_NAME,
                        ACTUAL_COLUMN_NAME=record.ACTUAL_COLUMN_NAME,
                        COLUMN_VALUE1=record.COLUMN_VALUE1,
                        COLUMN_VALUE2=record.COLUMN_VALUE2,
                        CREATED_BY=record.CREATED_BY,
                        TABLE_NAME=record.TABLE_NAME,
                        LINE_ID=record.LINE_ID,
                        HEADER_ID=record.HEADER_ID
                    ) for record in existing_records
                ]

                if history_objects:
                    XXALY_GTD_DATA_COMPARE_HIST.objects.bulk_create(history_objects)
                    print(f"Moved {len(history_objects)} records to history")

                deleted_count = existing_records.delete()
                print(f"Deleted {deleted_count[0]} old records from XXALY_GTD_DATA_COMPARE_T")

            new_compare_objects = [XXALY_GTD_DATA_COMPARE_T(**change) for change in tracked_changes]
            XXALY_GTD_DATA_COMPARE_T.objects.bulk_create(new_compare_objects)
            print(f"Created {len(new_compare_objects)} new records in XXALY_GTD_DATA_COMPARE_T")

    except Exception as e:
        print(f"Error in move_to_history_and_cleanup: {str(e)}")
        raise

    print(f"Finished move_to_history_and_cleanup for HEADER_ID: {header_id}")

def track_changes(old_obj, new_data, tracked_fields, table_name, current_user, header_id):
    changes = []
    for field in tracked_fields:
        old_value = getattr(old_obj, field, None)
        new_value = new_data.get(field)
        
        if new_value is not None and str(old_value) != str(new_value):
            changes.append({
                'COLUMN_NAME': field,
                'ACTUAL_COLUMN_NAME': field,
                'COLUMN_VALUE1': str(old_value) if old_value is not None else '',
                'COLUMN_VALUE2': str(new_value),
                'CREATED_BY': current_user,
                'TABLE_NAME': table_name,
                'LINE_ID': str(old_obj.INS_LINE_ID if hasattr(old_obj, 'INS_LINE_ID') else 
                    old_obj.REG_LINE_ID if hasattr(old_obj, 'REG_LINE_ID') else 
                    old_obj.RT_LINE_ID if hasattr(old_obj, 'RT_LINE_ID') else 
                    old_obj.ALLOC_LINE_ID if hasattr(old_obj, 'ALLOC_LINE_ID') else
                    old_obj.PERMIT_LINE_ID if hasattr(old_obj, 'PERMIT_LINE_ID') else 
                    old_obj.GT_LINE_ID if hasattr(old_obj, 'GT_LINE_ID') else 
                    old_obj.FUEL_LINE_ID if hasattr(old_obj, 'FUEL_LINE_ID') else 
                    old_obj.ASGN_LINE_ID if hasattr(old_obj, 'ASGN_LINE_ID') else 

                    old_obj.id),

                'HEADER_ID': header_id
            })
    return changes

@api.post("/fleet-master", response=FleetMasterResponse)
def create_or_update_fleet_master(
    request,
    COMPANY_NAME: Optional[str] = Form(None),
    FLEET_CONTROL_NO: Optional[str] = Form(None),
    FLEET_CREATION_DATE: Optional[date] = Form(None),
    VIN_NO: Optional[str] = Form(None),
    MANUFACTURER: Optional[str] = Form(None),
    MODEL: Optional[str] = Form(None),
    VEHICLE_TYPE: Optional[str] = Form(None),
    COLOR: Optional[str] = Form(None),
    FLEET_CATEGORY: Optional[str] = Form(None),
    FLEET_SUB_CATEGORY: Optional[str] = Form(None),
    ENGINE_NO: Optional[str] = Form(None),
    MODEL_YEAR: Optional[str] = Form(None),
    COUNTRY_OF_ORIGIN: Optional[str] = Form(None),
    SEATING_CAPACITY: Optional[Union[str,int]] = Form(None),
    TONNAGE: Optional[float] = Form(None),
    GROSS_WEIGHT_KG: Optional[float] = Form(None),
    EMPTY_WEIGHT_KG: Optional[float] = Form(None),
    PURCHASE_VALUE_AED: Optional[float] = Form(None),
    COMMENTS: Optional[str] = Form(None),
    STATUS: Optional[str] = Form("Pending for Approval"),
    ApplicationUsage: Optional[str] = Form(None),
    HEADER_ID: Optional[str] = Form(None),
    VehiclePurchaseDoc: Optional[UploadedFile] = File(None),
    insurances: str = Form(...),
    permits: str = Form(...),
    gps: str = Form(...),
    registration: str = Form(None),
    fuel: str = Form(None),
    roadtoll: str = Form(...),
    driver: str = Form(...),
    allocation: str = Form(...),
    is_approver: bool = Form(False),
    InsurancePolicAattachment: Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    InsurancePolicAattachmentNames: Optional[List[str]] = Form(None),
):
    try:
        with transaction.atomic():
            current_user = request.user if request.user.is_authenticated else None
            
            if FLEET_CONTROL_NO:
                old_fleet_master = XXGTD_VEHICLE_INFO.objects.get(FLEET_CONTROL_NO=FLEET_CONTROL_NO)
                created = False
            elif HEADER_ID:
                old_fleet_master = XXGTD_VEHICLE_INFO.objects.filter(HEADER_ID=HEADER_ID).first()
                if old_fleet_master:
                    created = False
                else:
                    old_fleet_master = None
                    created = True
            else:
                old_fleet_master = None
                created = True

            if created:
                fleet_master = XXGTD_VEHICLE_INFO()
                fleet_master.CREATED_BY = current_user.username if current_user else "System"
           
            else:
                fleet_master = old_fleet_master
                fleet_master.LAST_UPDATED_BY = current_user.username if current_user else "System"    

            tracked_fields = [
                'COMPANY_NAME', 'VIN_NO', 'MANUFACTURER', 'MODEL', 'VEHICLE_TYPE',
                'COLOR', 'FLEET_CATEGORY', 'FLEET_SUB_CATEGORY', 'ENGINE_NO',
                'MODEL_YEAR', 'COUNTRY_OF_ORIGIN', 'SEATING_CAPACITY', 'TONNAGE',
                'GROSS_WEIGHT_KG', 'EMPTY_WEIGHT_KG', 'PURCHASE_VALUE_AED',
                'COMMENTS', 'STATUS', 'ApplicationUsage'
            ]

            
            fleet_master_data = {
                "COMPANY_NAME": COMPANY_NAME,
                "VIN_NO": VIN_NO,
                "MANUFACTURER": MANUFACTURER,
                "MODEL": MODEL,
                "VEHICLE_TYPE": VEHICLE_TYPE,
                "COLOR": COLOR,
                "FLEET_CATEGORY": FLEET_CATEGORY,
                "FLEET_SUB_CATEGORY": FLEET_SUB_CATEGORY,
                "ENGINE_NO": ENGINE_NO,
                "MODEL_YEAR": MODEL_YEAR,
                "COUNTRY_OF_ORIGIN": COUNTRY_OF_ORIGIN,
                "SEATING_CAPACITY": SEATING_CAPACITY,
                "TONNAGE": TONNAGE,
                "GROSS_WEIGHT_KG": GROSS_WEIGHT_KG,
                "EMPTY_WEIGHT_KG": EMPTY_WEIGHT_KG,
                "PURCHASE_VALUE_AED": PURCHASE_VALUE_AED,
                "COMMENTS": COMMENTS,
                "STATUS": STATUS or "Pending for Approval",
                "HEADER_ID": HEADER_ID,
                "ApplicationUsage": ApplicationUsage
            }
            if created or (not created and fleet_master.FLEET_CREATION_DATE is None):
                fleet_master_data["FLEET_CREATION_DATE"] = FLEET_CREATION_DATE


            all_tracked_changes = []
            if not created:
                all_tracked_changes.extend(track_changes(old_fleet_master, fleet_master_data, tracked_fields, 'XXGTD_VEHICLE_INFO', current_user, HEADER_ID))

            for key, value in fleet_master_data.items():
                if value is not None:
                    setattr(fleet_master, key, value)
            
            fleet_master.save()
            
            
            # fleet_master_changes = []
            # for field in tracked_fields:
            #     new_value = getattr(fleet_master, field)
            #     fleet_master_changes.append({
            #         'COLUMN_NAME': field,
            #         'ACTUAL_COLUMN_NAME': field,
            #         'COLUMN_VALUE1': '',
            #         'COLUMN_VALUE2': str(new_value) if new_value is not None else '',
            #         'CREATED_BY': current_user,
            #         'TABLE_NAME': 'FleetMaster',
            #         'LINE_ID': str(fleet_master.id),
            #         'HEADER_ID': fleet_master.HEADER_ID
            #     })

            # all_tracked_changes.extend(fleet_master_changes)

            header_id_num = fleet_master.HEADER_ID
            fleet_control_number = fleet_master.FLEET_CONTROL_NO
            
            XXGTD_VEHICLE_AUDIT.objects.create(
                FLEET_MASTER=fleet_master,
                COMPANY_NAME=COMPANY_NAME,
                FLEET_CONTROL_NO=fleet_master.FLEET_CONTROL_NO,
                FLEET_CREATION_DATE=FLEET_CREATION_DATE,
                VIN_NO=VIN_NO,
                MANUFACTURER=MANUFACTURER,
                MODEL=MODEL,
                VEHICLE_TYPE=VEHICLE_TYPE,
                COLOR=COLOR,
                FLEET_CATEGORY=FLEET_CATEGORY,
                FLEET_SUB_CATEGORY=FLEET_SUB_CATEGORY,
                ENGINE_NO=ENGINE_NO,
                MODEL_YEAR=MODEL_YEAR,
                COUNTRY_OF_ORIGIN=COUNTRY_OF_ORIGIN,
                SEATING_CAPACITY=SEATING_CAPACITY,
                TONNAGE=TONNAGE,
                GROSS_WEIGHT_KG=GROSS_WEIGHT_KG,
                EMPTY_WEIGHT_KG=EMPTY_WEIGHT_KG,
                PURCHASE_VALUE_AED=PURCHASE_VALUE_AED,
                COMMENTS=COMMENTS,
                STATUS=STATUS,
                ApplicationUsage=ApplicationUsage,
                HEADER_ID=HEADER_ID,
                VehiclePurchaseDoc=VehiclePurchaseDoc,
                CREATED_BY=current_user.username if current_user else "System",
                LAST_UPDATED_BY=current_user.username if current_user else "System",
                ACTION_CODE='C' if created else 'U',
                ACTION='Created' if created else 'Updated',
            )

            Attachment.objects.filter(fleet_master=fleet_master, HEADER_ID=HEADER_ID).update(FleetNumber=fleet_control_number)

            if is_approver:
                fleet_master.STATUS = STATUS
            elif all(insurance.FLEET_PROCESS == 'Pending for Approval' for insurance in fleet_master.insurances.all()) and \
                all(permit.FLEET_PROCESS == 'Pending for Approval' for permit in fleet_master.permits.all()):
                fleet_master.STATUS = 'Pending for Approval'
            fleet_master.save()

            def handle_file_upload(existing_files, new_files, file_path_prefix):
                existing_files = json.loads(existing_files) if existing_files else []
                existing_base_names = set(re.sub(r'_[^_]+(?=\.[^.]+$)', '', os.path.basename(file)) for file in existing_files)
                new_file_paths = []

                for file in new_files:
                    base_name = re.sub(r'_[^_]+(?=\.[^.]+$)', '', file.name)
                    if base_name not in existing_base_names:
                        file_path = default_storage.save(f'{file_path_prefix}/{file.name}', ContentFile(file.read()))
                        new_file_paths.append(file_path)
                        existing_base_names.add(base_name)

                all_files = existing_files + new_file_paths
                return json.dumps(all_files)

            if 'VehiclePurchaseDoc' in request.FILES:
                files = request.FILES.getlist('VehiclePurchaseDoc')
                fleet_master.VehiclePurchaseDoc = handle_file_upload(
                    fleet_master.VehiclePurchaseDoc,
                    files,
                    'media/documents/vehicle_purchase'
                )
                for file_path in json.loads(fleet_master.VehiclePurchaseDoc):
                    Attachment.objects.get_or_create(
                        file=file_path,
                        attachment_type='Vehicle Info',
                        fleet_master=fleet_master,
                        FleetNumber=fleet_master.FLEET_CONTROL_NO
                    )
                fleet_master.save()

            insurance_tracked_fields = [
                'INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                'PLTS_INS_START_DATE', 'PLTS_INS_EXPIRY_DATE', 'CUR_STAT_MOT_INS'
            ]

            insurance_data = json.loads(insurances)

            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    old_insurance = XXGTD_INSURANCE_INFO.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], fleet_master=fleet_master)
                    insurance = old_insurance
                    if insurance.FLEET_PROCESS != 'Approved':
                        insurance.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(old_insurance, insurance_item, insurance_tracked_fields, 'Insurance', current_user, fleet_master.HEADER_ID))
                else:
                    insurance = XXGTD_INSURANCE_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    insurance.CREATED_BY = current_user.username if current_user else "System"
                    insurance.LAST_UPDATED_BY = current_user.username if current_user else "System"
       
                    for field in insurance_tracked_fields:
                        new_value = insurance_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Insurance',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in insurance_tracked_fields:
                    setattr(insurance, field, insurance_item.get(field))

                insurance.FLEET_CONTROL_NO = fleet_control_number
                insurance.HEADER_ID = header_id_num
                insurance.Process = "GTD"
                fleet_master.STATUS = "Pending for Approval"
                
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='InsuranceInfo'
                ).values_list('file', flat=True))

                file_key = f'InsurancePolicAattachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        insurance.InsurancePolicAattachment,
                        files,
                        'media/documents/insurance'
                    )
                    insurance.InsurancePolicAattachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='InsuranceInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )
                
                insurance.save()
                XXGTD_INSUR_AUDIT.objects.create(
                    INS_LINE_ID=insurance,
                    HEADER_ID=fleet_master.HEADER_ID,
                    INSURANCE_COMPANY=insurance.INSURANCE_COMPANY,
                    POLICY_NO=insurance.POLICY_NO,
                    POLICY_DATE=insurance.POLICY_DATE,
                    POLICY_EXPIRY_DATE=insurance.POLICY_EXPIRY_DATE,
                    PLTS_INS_EXPIRY_DATE=insurance.PLTS_INS_EXPIRY_DATE,
                    CUR_STAT_MOT_INS=insurance.CUR_STAT_MOT_INS,
                    PLTS_INS_START_DATE=insurance.PLTS_INS_START_DATE,
                    FLEET_PROCESS=fleet_master.STATUS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="GTD"
                    )

            
   
            registration_tracked_fields = [
                'EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO',
                'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1',
                'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG'
            ]

            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    old_registration = XXGTD_REGISTRATION_INFO.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], fleet_master=fleet_master)
                    reg = old_registration
                    if reg.FLEET_PROCESS != 'Approved':
                        reg.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(old_registration, reg_item, registration_tracked_fields, 'Registration', current_user, fleet_master.HEADER_ID))
                else:
                    reg = XXGTD_REGISTRATION_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    reg.CREATED_BY = current_user.username if current_user else "System"
                    reg.LAST_UPDATED_BY = current_user.username if current_user else "System"
                                        
                    for field in registration_tracked_fields:
                        new_value = reg_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Registration',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in registration_tracked_fields:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.FLEET_CONTROL_NO = fleet_control_number
                reg.HEADER_ID = header_id_num
                reg.Process = "GTD"
                fleet_master.STATUS = "Pending for Approval"
                
                if fleet_master.STATUS == 'Defleet' and reg.FLEET_PROCESS == 'Approved':
                    reg.FLEET_PROCESS = 'Defleet'
                
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='RegistrationInfo'
                ).values_list('file', flat=True))

                file_key = f'RegCardAttachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        reg.RegCardAttachment,
                        files,
                        'media/documents/registration'
                    )
                    reg.RegCardAttachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='RegistrationInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                reg.save()
                
                XXGTD_REGIS_AUDIT.objects.create(
                    REG_LINE_ID=reg,
                    HEADER_ID=fleet_master.HEADER_ID,
                    EMIRATES_TRF_FILE_NO=reg.EMIRATES_TRF_FILE_NO,
                    REGISTERED_EMIRATES=reg.REGISTERED_EMIRATES,
                    FEDERAL_TRF_FILE_NO=reg.FEDERAL_TRF_FILE_NO,
                    REG_COMPANY_NAME=reg.REG_COMPANY_NAME,
                    TRADE_LICENSE_NO=reg.TRADE_LICENSE_NO,
                    REGISTRATION_NO1=reg.REGISTRATION_NO1,
                    REGISTRATION_NO=reg.REGISTRATION_NO,
                    REGISTRATION_DATE=reg.REGISTRATION_DATE,
                    REG_EXPIRY_DATE=reg.REG_EXPIRY_DATE,
                    CUR_STAT_REG=reg.CUR_STAT_REG,
                    FLEET_PROCESS=reg.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="GTD"
                )

            
           
            roadtoll_tracked_fields = [
                'EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 
                'ACTIVATION_DATE', 'ACTIVATION_END_DATE', 'CURRENT_STATUS'
            ]
            
            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = XXGTD_ROAD_TOLL_INFO.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], fleet_master=fleet_master)
                    if road.FLEET_PROCESS != 'Approved':
                        road.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(road, roadtoll_item, roadtoll_tracked_fields, 'Roadtoll', current_user, fleet_master.HEADER_ID))
                else:
                    road = XXGTD_ROAD_TOLL_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    road.CREATED_BY = current_user.username if current_user else "System"
                    road.LAST_UPDATED_BY = current_user.username if current_user else "System"
                    
                    for field in roadtoll_tracked_fields:
                        new_value = roadtoll_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Roadtoll',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in roadtoll_tracked_fields:
                    value = roadtoll_item.get(field, '')
                    setattr(road, field, value if value != '' else None)

                road.FLEET_CONTROL_NO = fleet_control_number
                road.HEADER_ID = header_id_num
                road.Process = "GTD"
                fleet_master.STATUS = "Pending for Approval"
                
                
                
                        
                        
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='RoadtollInfo'
                ).values_list('file', flat=True))

                file_key = f'RoadtollAttachments_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        road.RoadtollAttachments,
                        files,
                        'media/documents/roadtoll'
                    )
                    road.RoadtollAttachments = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='RoadtollInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                road.save()
                XXGTD_ROAD_TOLL_AUDIT.objects.create(
                    RT_LINE_ID=road,
                    HEADER_ID=fleet_master.HEADER_ID,
                    EMIRATES=road.EMIRATES,
                    TOLL_TYPE=road.TOLL_TYPE,
                    ACCOUNT_NO=road.ACCOUNT_NO,
                    TAG_NO=road.TAG_NO,
                    ACTIVATION_DATE=road.ACTIVATION_DATE,
                    ACTIVATION_END_DATE=road.ACTIVATION_END_DATE,
                    CURRENT_STATUS=road.CURRENT_STATUS,
                    FLEET_PROCESS=road.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="GTD"
                    )

           
            allocation_tracked_fields = [
                'COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 
                'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE','ALLOCATION_END_DATE'
            ]
            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = XXGTD_ALLOCATION_INFO.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], fleet_master=fleet_master)
                    if allocations.FLEET_PROCESS != 'Approved':
                        allocations.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(allocations, allocation_item, allocation_tracked_fields, 'Allocation', current_user, fleet_master.HEADER_ID))
                else:
                    allocations = XXGTD_ALLOCATION_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    allocations.CREATED_BY = current_user.username if current_user else "System"
                    allocations.LAST_UPDATED_BY = current_user.username if current_user else "System"
                    
                    for field in allocation_tracked_fields:
                        new_value = allocation_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Allocation',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in allocation_tracked_fields:
                    value = allocation_item.get(field, '')
                    setattr(allocations, field, value if value != '' else None)

                allocations.FLEET_CONTROL_NO = fleet_control_number
                allocations.HEADER_ID = header_id_num
                allocations.Process = "GTD"
                fleet_master.STATUS = "Pending for Approval"
                            
               
                
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='AllocationInfo'
                ).values_list('file', flat=True))

                file_key = f'attachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        allocations.attachment,
                        files,
                        'media/documents/allocation'
                    )
                    allocations.attachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='AllocationInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                allocations.save()
                XXGTD_ALLOCATION_AUDIT.objects.create(
                    ALLOC_LINE_ID=allocations,
                    HEADER_ID=fleet_master.HEADER_ID,
                    COMPANY_NAME=allocations.COMPANY_NAME,
                    DIVISION=allocations.DIVISION,
                    OPERATING_LOCATION=allocations.OPERATING_LOCATION,
                    OPERATING_EMIRATES=allocations.OPERATING_EMIRATES,
                    APPICATION_USAGE=allocations.APPICATION_USAGE,
                    ALLOCATION_DATE=allocations.ALLOCATION_DATE,
                    ALLOCATION_END_DATE=allocations.ALLOCATION_END_DATE,
                    FLEET_PROCESS=allocations.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="GTD"
                )


            permits_tracked_fields = ['PERMIT_TYPE', 'EMIRATES', 'ISSUING_AUTHORITY', 'PERMIT_NO', 'PERMIT_DATE',
                          'PERMIT_EXPIRY_DATE', 'CUR_STAT_PERMIT', 'PermitColor']

            permits_data = json.loads(permits)
            for index, permit_item in enumerate(permits_data):
                if permit_item['PERMIT_LINE_ID'] != 'new':
                    permit = XXGTD_PARKING_PERMIT.objects.get(PERMIT_LINE_ID=permit_item['PERMIT_LINE_ID'], fleet_master=fleet_master)
                    if permit.FLEET_PROCESS != 'Approved':
                        permit.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(permit, permit_item, permits_tracked_fields, 'Permits', current_user, fleet_master.HEADER_ID))
                else:
                    permit = XXGTD_PARKING_PERMIT(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    permit.CREATED_BY = current_user.username if current_user else "System"
                    permit.LAST_UPDATED_BY = current_user.username if current_user else "System"
                    
                    for field in permits_tracked_fields:
                        new_value = permit_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Permits',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in permits_tracked_fields:
                    value = permit_item.get(field, '')
                    setattr(permit, field, value if value != '' else None)

                permit.FLEET_CONTROL_NO = fleet_control_number
                fleet_master.STATUS = "Pending for Approval"
                permit.HEADER_ID=header_id_num
                
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='PermitInfo'
                ).values_list('file', flat=True))


                file_key = f'PermitAattachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        permit.PermitAattachment,
                        files,
                        'media/documents/permit'
                    )
                    permit.PermitAattachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='PermitInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                permit.save()
                XXGTD_PARK_PERMIT_AUDIT.objects.create(
                    PERMIT_LINE_ID=permit,
                    HEADER_ID=fleet_master.HEADER_ID,
                    PERMIT_TYPE=permit.PERMIT_TYPE,
                    EMIRATES=permit.EMIRATES,
                    ISSUING_AUTHORITY=permit.ISSUING_AUTHORITY,
                    PERMIT_NO=permit.PERMIT_NO,
                    PERMIT_DATE=permit.PERMIT_DATE,
                    PERMIT_EXPIRY_DATE=permit.PERMIT_EXPIRY_DATE,
                    CUR_STAT_PERMIT=permit.CUR_STAT_PERMIT,
                    PermitColor=permit.PermitColor,
                    FLEET_PROCESS=permit.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                   
                )

          
            gps_tracked_fields = ['GPS_DEVICE_NO', 'GPS_INSTALLATION_DATE', 'GPS_SERVICE_PROVIDER']

            gps_data = json.loads(gps)
            for index, gps_item in enumerate(gps_data):
                if gps_item['GT_LINE_ID'] != 'new':
                    gp = XXGTD_GPS_TRACKING_INFO.objects.get(GT_LINE_ID=gps_item['GT_LINE_ID'], fleet_master=fleet_master)
                    if gp.FLEET_PROCESS != 'Approved':
                        gp.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(gp, gps_item, gps_tracked_fields, 'GPS', current_user, fleet_master.HEADER_ID))
                else:
                    gp = XXGTD_GPS_TRACKING_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    gp.CREATED_BY = current_user.username if current_user else "System"
                    gp.LAST_UPDATED_BY = current_user.username if current_user else "System"

                    for field in gps_tracked_fields:
                        new_value = gps_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'GPS',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in gps_tracked_fields:
                    value = gps_item.get(field, '')
                    setattr(gp, field, value if value != '' else None)


                gp.FLEET_CONTROL_NO = fleet_control_number
                fleet_master.STATUS = "Pending for Approval"
                gp.HEADER_ID=header_id_num
                
                
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='GPSInfo'
                ).values_list('file', flat=True))

                file_key = f'GpsAattachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        gp.GpsAattachment,
                        files,
                        'media/documents/gps'
                    )
                    gp.GpsAattachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='GPSInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )
                            
                            
               

                gp.save()
                XXGTD_GPS_TRACKING_AUDIT.objects.create(
                    GT_LINE_ID=gp,
                    HEADER_ID=fleet_master.HEADER_ID,
                    GPS_DEVICE_NO=gp.GPS_DEVICE_NO,
                    GPS_INSTALLATION_DATE=gp.GPS_INSTALLATION_DATE,
                    GPS_SERVICE_PROVIDER=gp.GPS_SERVICE_PROVIDER,
                    FLEET_PROCESS=gp.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
           
                )

            
           
            fuel_tracked_fields = ['FUEL_TYPE', 'MONTHLY_FUEL_LIMIT', 'FUEL_SERVICE_TYPE', 'FUEL_SERVICE_PROVIDER', 
                       'FUEL_DOCUMENT_NO', 'FUEL_DOCUMENT_DATE', 'FUEL_DOC_EXPIRY_DATE', 'CUR_STAT_FUEL_DOC']

            fuel_data = json.loads(fuel)
            for index, fuel_item in enumerate(fuel_data):
                if fuel_item['FUEL_LINE_ID'] != 'new':
                    ful = XXGTD_FUEL_INFO.objects.get(FUEL_LINE_ID=fuel_item['FUEL_LINE_ID'], fleet_master=fleet_master)
                    if ful.FLEET_PROCESS != 'Approved':
                        ful.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(ful, fuel_item, fuel_tracked_fields, 'Fuel', current_user, fleet_master.HEADER_ID))
                else:
                    ful = XXGTD_FUEL_INFO(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    ful.CREATED_BY = current_user.username if current_user else "System"
                    ful.LAST_UPDATED_BY = current_user.username if current_user else "System"

                    
                    for field in fuel_tracked_fields:
                        new_value = fuel_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Fuel',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in fuel_tracked_fields:
                    value = fuel_item.get(field, '')
                    setattr(ful, field, value if value != '' else None)


                ful.FLEET_CONTROL_NO = fleet_control_number
                ful.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                    
                         
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='FuelInfo'
                ).values_list('file', flat=True))

                file_key = f'FuelDocumentAttachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        ful.FuelDocumentAttachment,
                        files,
                        'media/documents/fuel'
                    )
                    ful.FuelDocumentAttachment = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                    attachment_type='FuelInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                ful.save()
                XXGTD_FUEL_AUDIT.objects.create(
                    FUEL_LINE_ID=ful,
                    HEADER_ID=fleet_master.HEADER_ID,
                    FUEL_TYPE=ful.FUEL_TYPE,
                    MONTHLY_FUEL_LIMIT=ful.MONTHLY_FUEL_LIMIT,
                    FUEL_SERVICE_TYPE=ful.FUEL_SERVICE_TYPE,
                    FUEL_SERVICE_PROVIDER=ful.FUEL_SERVICE_PROVIDER,
                    FUEL_DOCUMENT_NO=ful.FUEL_DOCUMENT_NO,
                    FUEL_DOCUMENT_DATE=ful.FUEL_DOCUMENT_DATE,
                    CUR_STAT_FUEL_DOC=ful.CUR_STAT_FUEL_DOC,
                    FUEL_DOC_EXPIRY_DATE=ful.FUEL_DOC_EXPIRY_DATE,
                    FLEET_PROCESS=ful.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                   
                )

           
            # Handle Driver
            driver_tracked_fields = ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE', 
                         'TRAFFIC_CODE_NO', 'DRIVING_LICENSE_NO', 'LICENSE_TYPE', 'PLACE_OF_ISSUE', 
                         'LICENSE_EXPIRY_DATE', 'GPS_TAG_NO', 'GPS_TAG_ASSIGN_DATE']

            driver_data = json.loads(driver)
            for index, driver_item in enumerate(driver_data):
                if driver_item['ASGN_LINE_ID'] != 'new':
                    drive = XXGTD_DRIVER_ASSIGNMENT.objects.get(ASGN_LINE_ID=driver_item['ASGN_LINE_ID'], fleet_master=fleet_master)
                    if drive.FLEET_PROCESS != 'Approved':
                        drive.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(drive, driver_item, driver_tracked_fields, 'Driver', current_user, fleet_master.HEADER_ID))
                else:
                    drive = XXGTD_DRIVER_ASSIGNMENT(fleet_master=fleet_master, FLEET_PROCESS='Pending for Approval')
                    drive.CREATED_BY = current_user.username if current_user else "System"
                    drive.LAST_UPDATED_BY = current_user.username if current_user else "System"
                    
                    for field in driver_tracked_fields:
                        new_value = driver_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Driver',
                                'LINE_ID': 'new',
                                'HEADER_ID': fleet_master.HEADER_ID
                            })

                for field in driver_tracked_fields:
                    value = driver_item.get(field, '')
                    setattr(drive, field, value if value != '' else None)


                drive.FLEET_CONTROL_NO = fleet_control_number
                drive.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                
                
                        
                        
                existing_attachments = set(Attachment.objects.filter(
                    fleet_master=fleet_master,
                    attachment_type='DriverInfo'
                ).values_list('file', flat=True))

                file_key = f'DriverAttachments_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    new_attachments = handle_file_upload(
                        drive.DriverAttachments,
                        files,
                        'media/documents/driver'
                    )
                    drive.DriverAttachments = new_attachments
                    
                    for file_path in json.loads(new_attachments):
                        if file_path not in existing_attachments:
                            Attachment.objects.create(
                                file=file_path,
                                attachment_type='DriverInfo',
                                fleet_master=fleet_master,
                                FleetNumber=fleet_master.FLEET_CONTROL_NO,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                drive.save()
                XXGTD_DRIVER_ASSIG_AUDIT.objects.create(
                    ASGN_LINE_ID=drive,
                    HEADER_ID=fleet_master.HEADER_ID,
                    EMPLOYEE_NO=drive.EMPLOYEE_NO,
                    EMPLOYEE_NAME=drive.EMPLOYEE_NAME,
                    DESIGNATION=drive.DESIGNATION,
                    CONTACT_NUMBER=drive.CONTACT_NUMBER,
                    ASSIGNMENT_DATE=drive.ASSIGNMENT_DATE,
                    TRAFFIC_CODE_NO=drive.TRAFFIC_CODE_NO,
                    DRIVING_LICENSE_NO=drive.DRIVING_LICENSE_NO,
                    LICENSE_TYPE=drive.LICENSE_TYPE,
                    PLACE_OF_ISSUE=drive.PLACE_OF_ISSUE,
                    LICENSE_EXPIRY_DATE=drive.LICENSE_EXPIRY_DATE,
                    GPS_TAG_NO=drive.GPS_TAG_NO,
                    GPS_TAG_ASSIGN_DATE=drive.GPS_TAG_ASSIGN_DATE,
                    FLEET_PROCESS=drive.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                  
                )
            
            
            
            if STATUS == 'Approved':
                # Clear existing records for this HEADER_ID
                REVERT_APPROVES.objects.filter(HEADER_ID=fleet_master.HEADER_ID).delete()

                # Add FleetMaster record to REVERT_APPROVES
                revert_data = {
                    'HEADER_ID': fleet_master.HEADER_ID,
                    'FM_LINE_ID': fleet_master.HEADER_ID,
                    'STATUS': 'Approved',
                }
                for field in XXGTD_VEHICLE_INFO._meta.fields:
                    if hasattr(REVERT_APPROVES, field.name) and field.name != 'STATUS':
                        revert_data[field.name] = getattr(fleet_master, field.name)

                REVERT_APPROVES.objects.create(**revert_data)

                # Handle child records
                for model, prefix in [
                    (XXGTD_INSURANCE_INFO, 'INS'),
                    (XXGTD_REGISTRATION_INFO, 'REG'),
                    (XXGTD_PARKING_PERMIT, 'PERMIT'),
                    (XXGTD_GPS_TRACKING_INFO, 'GT'),
                    (XXGTD_FUEL_INFO, 'FUEL'),
                    (XXGTD_ROAD_TOLL_INFO, 'RT'),
                    (XXGTD_DRIVER_ASSIGNMENT, 'ASGN'),
                    (XXGTD_ALLOCATION_INFO, 'ALLOC')
                ]:
                    instances = model.objects.filter(HEADER_ID=fleet_master.HEADER_ID)
                    for instance in instances:
                        child_revert_data = {
                            'HEADER_ID': fleet_master.HEADER_ID,
                            'FM_LINE_ID': fleet_master.HEADER_ID,
                            f'{prefix}_LINE_ID': getattr(instance, f'{prefix}_LINE_ID'),
                            'STATUS': 'Approved',
                        }
                        for field in model._meta.fields:
                            if hasattr(REVERT_APPROVES, field.name):
                                value = getattr(instance, field.name)
                                if value is not None:  # Only set non-null values
                                    child_revert_data[field.name] = value
                            else:
                                print(f"Warning: Field {field.name} from {model.__name__} not found in REVERT_APPROVES")

                        REVERT_APPROVES.objects.create(**child_revert_data)

                # Double-check to ensure all records for this HEADER_ID have STATUS 'Approved'
                REVERT_APPROVES.objects.filter(HEADER_ID=fleet_master.HEADER_ID).update(STATUS='Approved')

         

          
            if all_tracked_changes:
                move_to_history_and_cleanup(fleet_master.HEADER_ID, all_tracked_changes)
                
                
            for insurance_item in insurance_data:
                if insurance_item['INS_LINE_ID'] == 'new':
                    new_insurance = XXGTD_INSURANCE_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('INS_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Insurance',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_insurance.INS_LINE_ID))
                        
            for reg_item in registration_data:
                if reg_item['REG_LINE_ID'] == 'new':
                    new_registration = XXGTD_REGISTRATION_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('REG_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Registration',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_registration.REG_LINE_ID))
                       
            for roadtoll_item in roadtoll_data:
                if roadtoll_item['RT_LINE_ID'] == 'new':
                    new_roadtoll = XXGTD_ROAD_TOLL_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('RT_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Roadtoll',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_roadtoll.RT_LINE_ID))
           
            for allocation_item in allocation_data:
                if allocation_item['ALLOC_LINE_ID'] == 'new':
                    new_allocation = XXGTD_ALLOCATION_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('ALLOC_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Allocation',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_allocation.ALLOC_LINE_ID))
            
            for permit_item in permits_data:
                if permit_item['PERMIT_LINE_ID'] == 'new':
                    new_permit = XXGTD_PARKING_PERMIT.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('PERMIT_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Permits',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_permit.PERMIT_LINE_ID))
            
            for gps_item in gps_data:
                if gps_item['GT_LINE_ID'] == 'new':
                    new_gps = XXGTD_GPS_TRACKING_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('GT_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='GPS',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_gps.GT_LINE_ID))
            
            for fuel_item in fuel_data:
                if fuel_item['FUEL_LINE_ID'] == 'new':
                    new_fuel = XXGTD_FUEL_INFO.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('FUEL_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Fuel',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_fuel.FUEL_LINE_ID))
                    
            for driver_item in driver_data:
                if driver_item['ASGN_LINE_ID'] == 'new':
                    new_driver = XXGTD_DRIVER_ASSIGNMENT.objects.filter(
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    ).latest('ASGN_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Driver',
                        LINE_ID='new',
                        HEADER_ID=fleet_master.HEADER_ID
                    ).update(LINE_ID=str(new_driver.ASGN_LINE_ID))



                    
                    
                    
            ApprovalRequest.objects.update_or_create(
                request_number=fleet_master.FLEET_CONTROL_NO,
                defaults={
                    'company_name': fleet_master.COMPANY_NAME,
                    'request_type': 'FLEET MASTER',
                    'status': fleet_master.STATUS,
                    'comments': fleet_master.COMMENTS,
                    'fleet_master': fleet_master
                }
            )

            try:
                action = "created" if created else "updated"
                
                current_user = request.user if request.user.is_authenticated else None
                if is_approver:
                    fleet_master.STATUS = STATUS
                else:
                    fleet_master.STATUS = STATUS or "Pending for Approval"


                current_user = request.user if request.user.is_authenticated else None

            
                insurances = fleet_master.insurances.all()
                registrations = fleet_master.registration.all()
                permits = fleet_master.permits.all()
                gps_entries = fleet_master.gps.all()
                fuels = fleet_master.fuel.all()
                roadtolls = fleet_master.roadtoll.all()
                drivers = fleet_master.driver.all()
                allocations = fleet_master.allocation.all()

                max_records = max(
                    insurances.count(), 
                    registrations.count(),
                    permits.count(),
                    gps_entries.count(),
                    fuels.count(),
                    roadtolls.count(),
                    drivers.count(),
                    allocations.count()
                )
                
                
                for i in range(max_records):
                    insurance = insurances[i] if i < insurances.count() else None
                    registration = registrations[i] if i < registrations.count() else None
                    permit = permits[i] if i < permits.count() else None
                    gps = gps_entries[i] if i < gps_entries.count() else None
                    fuel = fuels[i] if i < fuels.count() else None
                    roadtoll = roadtolls[i] if i < roadtolls.count() else None
                    driver = drivers[i] if i < drivers.count() else None
                    allocation = allocations[i] if i < allocations.count() else None
                    print(f"Fleet master status before audit entry: {fleet_master.STATUS}")

                    audit_entry = XXALY_GTD_AUDIT_T.objects.create(
                        HEADER_ID=fleet_master.HEADER_ID,
                        FLEET_CONTROL_NO=fleet_master.FLEET_CONTROL_NO,
                        FLEET_CREATION_DATE=fleet_master.FLEET_CREATION_DATE,
                        VIN_NO=fleet_master.VIN_NO,
                        MANUFACTURER=fleet_master.MANUFACTURER,
                        MODEL=fleet_master.MODEL,
                        VEHICLE_TYPE=fleet_master.VEHICLE_TYPE,
                        COLOR=fleet_master.COLOR,
                        FLEET_CATEGORY=fleet_master.FLEET_CATEGORY,
                        FLEET_SUB_CATEGORY=fleet_master.FLEET_SUB_CATEGORY,
                        ENGINE_NO=fleet_master.ENGINE_NO,
                        MODEL_YEAR=fleet_master.MODEL_YEAR,
                        COUNTRY_OF_ORIGIN=fleet_master.COUNTRY_OF_ORIGIN,
                        SEATING_CAPACITY=fleet_master.SEATING_CAPACITY,
                        TONNAGE=fleet_master.TONNAGE,
                        GROSS_WEIGHT_KG=fleet_master.GROSS_WEIGHT_KG,
                        EMPTY_WEIGHT_KG=fleet_master.EMPTY_WEIGHT_KG,
                        PURCHASE_VALUE_AED=fleet_master.PURCHASE_VALUE_AED,
                        FLEET_STATUS=fleet_master.STATUS,
                        VEH_COMPANY=fleet_master.COMPANY_NAME,
                        COMMENTS=fleet_master.COMMENTS,
                        ACTION_CODE='C' if created else 'U',
                        ACTION='Created' if created else 'Updated',
                        CREATION_DATE=timezone.now(),
                        CREATED_BY=current_user.username if current_user else "System",
                        LAST_UPDATE_DATE=timezone.now(),
                        LAST_UPDATED_BY=current_user.username if current_user else "System",
                    )

                    if insurance:
                        audit_entry.INSURANCE_COMPANY = insurance.INSURANCE_COMPANY
                        audit_entry.POLICY_NO = insurance.POLICY_NO
                        audit_entry.POLICY_DATE = insurance.POLICY_DATE
                        audit_entry.POLICY_EXPIRY_DATE = insurance.POLICY_EXPIRY_DATE
                        audit_entry.PLTS_INS_START_DATE = insurance.PLTS_INS_START_DATE
                        audit_entry.POLICY_INSUR_EXPIRY_DATE = insurance.PLTS_INS_EXPIRY_DATE
                        audit_entry.INSUR_CURRENT_STATUS = insurance.CUR_STAT_MOT_INS
                        audit_entry.INS_LINE_ID = insurance

                    if registration:
                        audit_entry.REGISTRATION_NO = registration.REGISTRATION_NO
                        
                        audit_entry.REGISTRATION_NO1 = registration.REGISTRATION_NO1
                        audit_entry.REGISTRATION_DATE = registration.REGISTRATION_DATE
                        audit_entry.REGISTERED_EMIRATES = registration.REGISTERED_EMIRATES
                        audit_entry.EMIRATES_TRF_FILE_NO = registration.EMIRATES_TRF_FILE_NO
                        audit_entry.FEDERAL_TRF_FILE_NO = registration.FEDERAL_TRF_FILE_NO
                        audit_entry.REG_EXPIRY_DATE = registration.REG_EXPIRY_DATE
                        audit_entry.REG_COMPANY_NAME = registration.REG_COMPANY_NAME
                        audit_entry.REGISTRATION_STATUS = registration.CUR_STAT_REG
                        audit_entry.TRADE_LICENSE_NO = registration.TRADE_LICENSE_NO
                        audit_entry.REG_LINE_ID = registration
                    
                    if roadtoll:
                        audit_entry.TOLL_EMIRATES = roadtoll.EMIRATES
                        audit_entry.TOLL_TYPE = roadtoll.TOLL_TYPE
                        audit_entry.ACCOUNT_NO = roadtoll.ACCOUNT_NO
                        audit_entry.TAG_NO = roadtoll.TAG_NO
                        audit_entry.ACTIVATION_DATE = roadtoll.ACTIVATION_DATE
                        audit_entry.TOLL_STATUS = roadtoll.CURRENT_STATUS
                        audit_entry.ACTIVATION_END_DATE=roadtoll.ACTIVATION_END_DATE
                        
                        audit_entry.RT_LINE_ID = roadtoll    
                    
                    
                    if allocation:
                        audit_entry.COMPANY_NAME = allocation.COMPANY_NAME
                        audit_entry.DIVISION = allocation.DIVISION
                        audit_entry.OPERATING_LOCATION = allocation.OPERATING_LOCATION
                        audit_entry.OPERATING_EMIRATES = allocation.OPERATING_EMIRATES
                        audit_entry.APPICATION_USAGE = allocation.APPICATION_USAGE
                        audit_entry.ALLOCATION_DATE = allocation.ALLOCATION_DATE
                        
                        
                        audit_entry.ALLOCATION_END_DATE = allocation.ALLOCATION_END_DATE
                        audit_entry.ALLOC_LINE_ID = allocation
                    
                    if permit:
                            audit_entry.PERMIT_TYPE = permit.PERMIT_TYPE
                            audit_entry.PARKING_EMIRATES = permit.EMIRATES
                            audit_entry.PARKING_AUTHORITY = permit.ISSUING_AUTHORITY
                            audit_entry.PERMIT_NO = permit.PERMIT_NO
                            audit_entry.PERMIT_DATE = permit.PERMIT_DATE
                            audit_entry.PERMIT_EXPIRY_DATE = permit.PERMIT_EXPIRY_DATE
                            audit_entry.PARKING_STATUS = permit.CUR_STAT_PERMIT
                            
                            audit_entry.PERMIT_LINE_ID = permit

                    if gps:
                        audit_entry.GPS_DEVICE_NO = gps.GPS_DEVICE_NO
                        audit_entry.GPS_INSTALLATION_DATE = gps.GPS_INSTALLATION_DATE
                        audit_entry.GPS_SERVICE_PROVIDER = gps.GPS_SERVICE_PROVIDER
                        audit_entry.GT_LINE_ID = gps


                    
                    if fuel:
                        audit_entry.FUEL_TYPE = fuel.FUEL_TYPE
                        audit_entry.MONTHLY_FUEL_LIMIT = fuel.MONTHLY_FUEL_LIMIT
                        audit_entry.FUEL_SERVICE_TYPE = fuel.FUEL_SERVICE_TYPE
                        audit_entry.FUEL_SERVICE_PROVIDER = fuel.FUEL_SERVICE_PROVIDER
                        audit_entry.FUEL_DOCUMENT_NO = fuel.FUEL_DOCUMENT_NO
                        audit_entry.FUEL_DOCUMENT_DATE = fuel.FUEL_DOCUMENT_DATE
                        audit_entry.FUEL_DOC_EXPIRY_DATE = fuel.FUEL_DOC_EXPIRY_DATE
                        audit_entry.FUEL_DOC_STATUS = fuel.CUR_STAT_FUEL_DOC
                        audit_entry.FUEL_LINE_ID = fuel

                

                    if driver:
                        audit_entry.EMPLOYEE_NO = driver.EMPLOYEE_NO
                        audit_entry.EMPLOYEE_NAME = driver.EMPLOYEE_NAME
                        audit_entry.DESIGNATION = driver.DESIGNATION
                        audit_entry.CONTACT_NUMBER = driver.CONTACT_NUMBER
                        audit_entry.ASSIGNMENT_DATE = driver.ASSIGNMENT_DATE
                        audit_entry.TRAFFIC_CODE_NO = driver.TRAFFIC_CODE_NO
                        audit_entry.DRIVING_LICENSE_NO = driver.DRIVING_LICENSE_NO
                        audit_entry.LICENSE_TYPE = driver.LICENSE_TYPE
                        audit_entry.PLACE_OF_ISSUE = driver.PLACE_OF_ISSUE
                        audit_entry.LICENSE_EXPIRY_DATE = driver.LICENSE_EXPIRY_DATE
                        audit_entry.GPS_TAG_NO = driver.GPS_TAG_NO
                        audit_entry.GPS_TAG_ASSIGN_DATE = driver.GPS_TAG_ASSIGN_DATE
                        audit_entry.ASGN_LINE_ID = driver

                

                    audit_entry.save()
                
                
                
                 # Modify the status handling logic to ensure consistency
                display_status = STATUS or "Pending for Approval"
                if STATUS == "Draft":
                    display_status = "Pending for Approval"

                # Update the XXALY_GTD_ACTION_HISTORY creation with the correct status
                XXALY_GTD_ACTION_HISTORY.objects.create(
                    APPLICATION_ID=str(fleet_master.id),
                    APPL_NUMBER=fleet_master.FLEET_CONTROL_NO,
                    REQUEST_TYPE="FLEET_MASTER",
                    REQUEST_NUMBER=fleet_master.FLEET_CONTROL_NO,
                    PROCESS_STATUS=display_status,  # Use the corrected status
                    DOC_STATUS=display_status,      # Use the corrected status
                    RESPONSE_DATE=timezone.now(),
                    RESPONDED_BY=current_user.username if current_user else "System",
                    RESPONDER_ROLE=current_user.roles if current_user else "System",
                    RESPONSE_COMMENTS=fleet_master.COMMENTS,
                    ACTION_PERFORMED=f"Fleet Master {action}",
                    CREATED_BY=current_user.username if current_user else "System",
                    CREATION_DATE=timezone.now().date(),
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATE_DATE=timezone.now().date(),
                    NEXT_RESP="APPROVER" if current_user and current_user.roles == "REQUESTOR" else "REQUESTOR"
                )

                # Update fleet_master status
                if is_approver:
                    fleet_master.STATUS = STATUS
                else:
                    fleet_master.STATUS = display_status

                fleet_master.save()
                
            except Exception as e:
                # Handle the exception
                print(f"An error occurred: {str(e)}")
                        
            print(f"Finished processing FleetMaster with HEADER_ID: {header_id_num}")


            return {
                "message": "Fleet Master and related records created/updated successfully",
                "fleet_master": FleetMasterSchema.from_orm(fleet_master)
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}




class FleetMasterSchema(Schema):
    COMPANY_NAME: Optional[str] = None
    FLEET_CONTROL_NO: Optional[str] = None
    FLEET_CREATION_DATE: Optional[date] = None
    VIN_NO: Optional[str] = None
    MANUFACTURER: Optional[str] = None
    MODEL: Optional[str] = None
    VEHICLE_TYPE: Optional[str] = None
    COLOR: Optional[str] = None
    FLEET_CATEGORY: Optional[str] = None
    FLEET_SUB_CATEGORY: Optional[str] = None
    ENGINE_NO: Optional[str] = None
    MODEL_YEAR: Optional[str] = None
    COUNTRY_OF_ORIGIN: Optional[str] = None
    SEATING_CAPACITY: Optional[Union[str,int]] = None
    TONNAGE: Optional[float] = None
    GROSS_WEIGHT_KG: Optional[float] = None
    EMPTY_WEIGHT_KG: Optional[float] = None
    PURCHASE_VALUE_AED: Optional[float] = None
    COMMENTS: Optional[str] = None
    STATUS: Optional[str] = None
    ApplicationUsage: Optional[str] = None
    VehiclePurchaseDoc: Optional[str] = None
    HEADER_ID: Optional[str] = None
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class FleetMasterResponse(Schema):
    message: str
    fleet_master: FleetMasterSchema

@api.post("/fleet-master/save", response=FleetMasterResponse)
def create_or_update_fleet_master(
    request,
    COMPANY_NAME: Optional[str] = Form(None),
    HEADER_ID: Optional[str] = Form(None),
    FLEET_CREATION_DATE: Optional[date] = Form(None),
    VIN_NO: Optional[str] = Form(None),
    MANUFACTURER: Optional[str] = Form(None),
    MODEL: Optional[str] = Form(None),
    VEHICLE_TYPE: Optional[str] = Form(None),
    COLOR: Optional[str] = Form(None),
    FLEET_CATEGORY: Optional[str] = Form(None),
    FLEET_SUB_CATEGORY: Optional[str] = Form(None),
    ENGINE_NO: Optional[str] = Form(None),
    MODEL_YEAR: Optional[str] = Form(None),
    COUNTRY_OF_ORIGIN: Optional[str] = Form(None),
    SEATING_CAPACITY: Optional[Union[int,str]] = Form(None),
    TONNAGE: Optional[str] = Form(None),
    GROSS_WEIGHT_KG: Optional[str] = Form(None),
    EMPTY_WEIGHT_KG: Optional[str] = Form(None),
    PURCHASE_VALUE_AED: Optional[str] = Form(None),
    COMMENTS: Optional[str] = Form(None),
    ApplicationUsage: Optional[str] = Form(None),
    VehiclePurchaseDoc: Optional[UploadedFile] = File(None),
    insurances: Optional[str] = Form(None),
    permits: Optional[str] = Form(None),
    gps: Optional[str] = Form(None),
    registration: Optional[str] = Form(None),
    fuel: Optional[str] = Form(None),
    roadtoll: Optional[str] = Form(None),
    driver: Optional[str] = Form(None),
    allocation: Optional[str] = Form(None),
    
    InsurancePolicAattachment: Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    InsurancePolicAattachmentNames: Optional[List[str]] = Form(None),
):
    try:
        with transaction.atomic():
            
            if HEADER_ID:
                fleet_master = XXGTD_VEHICLE_INFO.objects.get(HEADER_ID=HEADER_ID)
                created = False
            else:
                fleet_master = XXGTD_VEHICLE_INFO()
                created = True
                
            current_user = request.user if request.user.is_authenticated else None
            username = current_user.username if current_user else "System"


            fleet_master_data = {
                key: value for key, value in {
                    "COMPANY_NAME": COMPANY_NAME,
                    "FLEET_CREATION_DATE": FLEET_CREATION_DATE,
                    "VIN_NO": VIN_NO,
                    "MANUFACTURER": MANUFACTURER,
                    "MODEL": MODEL,
                    "VEHICLE_TYPE": VEHICLE_TYPE,
                    "COLOR": COLOR,
                    "FLEET_CATEGORY": FLEET_CATEGORY,
                    "FLEET_SUB_CATEGORY": FLEET_SUB_CATEGORY,
                    "ENGINE_NO": ENGINE_NO,
                    "MODEL_YEAR": MODEL_YEAR,
                    "COUNTRY_OF_ORIGIN": COUNTRY_OF_ORIGIN,
                    "SEATING_CAPACITY": int(SEATING_CAPACITY) if SEATING_CAPACITY else None,
                    "TONNAGE": float(TONNAGE) if TONNAGE else None,
                    "GROSS_WEIGHT_KG": float(GROSS_WEIGHT_KG) if GROSS_WEIGHT_KG else None,
                    "EMPTY_WEIGHT_KG": float(EMPTY_WEIGHT_KG) if EMPTY_WEIGHT_KG else None,
                    "PURCHASE_VALUE_AED": float(PURCHASE_VALUE_AED) if PURCHASE_VALUE_AED else None,
                    "COMMENTS": COMMENTS,
                    "STATUS": "Draft",
                    "CREATED_BY": username if created else None,
                    "LAST_UPDATED_BY": username,
                    "ApplicationUsage": ApplicationUsage,
                }.items() if value is not None
            }
            
            
            
            
            
            if not fleet_master_data:
                return {"message": "At least one field is required to save the fleet master."}

            for key, value in fleet_master_data.items():
                setattr(fleet_master, key, value)
            fleet_master.save(generate_fleet_control_number=False)

            HEADER_ID = fleet_master.HEADER_ID



        
            def handle_file_upload(existing_files, new_files, file_path_prefix):
                existing_files = json.loads(existing_files) if existing_files else []
                existing_base_names = set(re.sub(r'[^]+(?=\.[^.]+$)', '', os.path.basename(file)) for file in existing_files)
                new_file_paths = []

                for file in new_files:
                    base_name = re.sub(r'[^]+(?=\.[^.]+$)', '', file.name)
                    if base_name not in existing_base_names:
                        file_path = default_storage.save(f'{file_path_prefix}/{file.name}', ContentFile(file.read()))
                        new_file_paths.append(file_path)
                        existing_base_names.add(base_name)

                all_files = existing_files + new_file_paths
                return json.dumps(all_files)

                if 'VehiclePurchaseDoc' in request.FILES:
                  files = request.FILES.getlist('VehiclePurchaseDoc')
                fleet_master.VehiclePurchaseDoc = handle_file_upload(
                    fleet_master.VehiclePurchaseDoc,
                    files,
                    'media/documents/vehicle_purchase'
                )
                for file_path in json.loads(fleet_master.VehiclePurchaseDoc):
                    Attachment.objects.get_or_create(
                        file=file_path,
                        attachment_type='Vehicle Info',
                        fleet_master=fleet_master,
                        HEADER_ID=fleet_master.HEADER_ID
                    )
                fleet_master.save(generate_fleet_control_number=False)

            if insurances:
                insurance_data = json.loads(insurances)
                for index, insurance_item in enumerate(insurance_data):
                    if insurance_item['INS_LINE_ID'] != 'new':
                        try:
                            insurance = XXGTD_INSURANCE_INFO.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], fleet_master=fleet_master)
                        except XXGTD_INSURANCE_INFO.DoesNotExist:
                            insurance = XXGTD_INSURANCE_INFO(fleet_master=fleet_master)
                    else:
                        insurance = XXGTD_INSURANCE_INFO(fleet_master=fleet_master)

                    for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                                  'PLTS_INS_EXPIRY_DATE', 'PLTS_INS_START_DATE', 'CUR_STAT_MOT_INS']:
                        setattr(insurance, field, insurance_item.get(field))
                   
                    insurance.HEADER_ID = HEADER_ID
                    insurance.Process = "GTD"

                    file_key = f'InsurancePolicAattachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        insurance.InsurancePolicAattachment = handle_file_upload(
                            insurance.InsurancePolicAattachment,
                            files,
                            'media/documents/insurance'
                        )
                        for file_path in json.loads(insurance.InsurancePolicAattachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='InsuranceInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )
                    
                    insurance.save()

            if permits:
                permits_data = json.loads(permits)
                for index, permit_item in enumerate(permits_data):
                    if permit_item['PERMIT_LINE_ID'] != 'new':
                        permit = XXGTD_PARKING_PERMIT.objects.get(PERMIT_LINE_ID=permit_item['PERMIT_LINE_ID'], fleet_master=fleet_master)
                    else:
                        permit = XXGTD_PARKING_PERMIT(fleet_master=fleet_master)

                    for field in ['PERMIT_TYPE', 'EMIRATES', 'ISSUING_AUTHORITY', 'PERMIT_NO', 'PERMIT_DATE',
                                'PERMIT_EXPIRY_DATE', 'CUR_STAT_PERMIT', 'PermitColor']:
                        setattr(permit, field, permit_item.get(field))

                    permit.HEADER_ID = HEADER_ID
                    permit.Process = "GTD"
                   
                    file_key = f'PermitAattachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        permit.PermitAattachment = handle_file_upload(
                            permit.PermitAattachment,
                            files,
                            'media/documents/permit'
                        )
                        for file_path in json.loads(permit.PermitAattachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='PermitInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    permit.save()

            if gps:
                gps_data = json.loads(gps)
                for index, gps_item in enumerate(gps_data):
                    if gps_item['GT_LINE_ID'] != 'new':
                        gp = XXGTD_GPS_TRACKING_INFO.objects.get(GT_LINE_ID=gps_item['GT_LINE_ID'], fleet_master=fleet_master)
                    else:
                        gp = XXGTD_GPS_TRACKING_INFO(fleet_master=fleet_master)

                    for field in ['GPS_DEVICE_NO', 'GPS_INSTALLATION_DATE', 'GPS_SERVICE_PROVIDER']:
                        setattr(gp, field, gps_item.get(field))

                    gp.HEADER_ID = HEADER_ID
                    gp.Process = "GTD"

                    file_key = f'GpsAattachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        gp.GpsAattachment = handle_file_upload(
                            gp.GpsAattachment,
                            files,
                            'media/documents/gps'
                        )
                        for file_path in json.loads(gp.GpsAattachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='GPSInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    gp.save()

            if registration:
                registration_data = json.loads(registration)
                for index, reg_item in enumerate(registration_data):
                    if reg_item['REG_LINE_ID'] != 'new':
                        reg = XXGTD_REGISTRATION_INFO.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], fleet_master=fleet_master)
                    else:
                        reg = XXGTD_REGISTRATION_INFO(fleet_master=fleet_master)

                    for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                        value = reg_item.get(field, '')
                        setattr(reg, field, value if value != '' else None)

                    reg.HEADER_ID = HEADER_ID
                    reg.Process = "GTD"

                    file_key = f'RegCardAttachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        reg.RegCardAttachment = handle_file_upload(
                            reg.RegCardAttachment,
                            files,
                            'media/documents/registration'
                        )
                        for file_path in json.loads(reg.RegCardAttachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='RegistrationInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    reg.save()

            if fuel:
                fuel_data = json.loads(fuel)
                for index, fuel_item in enumerate(fuel_data):
                    if fuel_item['FUEL_LINE_ID'] != 'new':
                        ful = XXGTD_FUEL_INFO.objects.get(FUEL_LINE_ID=fuel_item['FUEL_LINE_ID'], fleet_master=fleet_master)
                    else:
                        ful = XXGTD_FUEL_INFO(fleet_master=fleet_master)

                    for field in ['FUEL_TYPE', 'MONTHLY_FUEL_LIMIT', 'FUEL_SERVICE_TYPE', 'FUEL_SERVICE_PROVIDER', 'FUEL_DOCUMENT_NO', 'FUEL_DOCUMENT_DATE', 'FUEL_DOC_EXPIRY_DATE', 'CUR_STAT_FUEL_DOC']:
                        value = fuel_item.get(field, '')
                        setattr(ful, field, value if value != '' else None)

                    ful.HEADER_ID = HEADER_ID
                    ful.Process = "GTD"

                    file_key = f'FuelDocumentAttachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        ful.FuelDocumentAttachment = handle_file_upload(
                            ful.FuelDocumentAttachment,
                            files,
                            'media/documents/fuel'
                        )
                        for file_path in json.loads(ful.FuelDocumentAttachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='FuelInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    ful.save()

            if roadtoll:
                roadtoll_data = json.loads(roadtoll)
                for index, roadtoll_item in enumerate(roadtoll_data):
                    if roadtoll_item['RT_LINE_ID'] != 'new':
                        road = XXGTD_ROAD_TOLL_INFO.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], fleet_master=fleet_master)
                    else:
                        road = XXGTD_ROAD_TOLL_INFO(fleet_master=fleet_master)

                    for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE', 'ACTIVATION_END_DATE', 'CURRENT_STATUS']:
                        setattr(road, field, roadtoll_item.get(field))

                    road.HEADER_ID = HEADER_ID
                    road.Process = "GTD"
                   
                    file_key = f'RoadtollAttachments_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        road.RoadtollAttachments = handle_file_upload(
                            road.RoadtollAttachments,
                            files,
                            'media/documents/roadtoll'
                        )
                        for file_path in json.loads(road.RoadtollAttachments):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='RoadtollInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    road.save()

            if driver:
                driver_data = json.loads(driver)
                for index, driver_item in enumerate(driver_data):
                    if driver_item['ASGN_LINE_ID'] != 'new':
                        drive = XXGTD_DRIVER_ASSIGNMENT.objects.get(ASGN_LINE_ID=driver_item['ASGN_LINE_ID'], fleet_master=fleet_master)
                    else:
                        drive = XXGTD_DRIVER_ASSIGNMENT(fleet_master=fleet_master)
                    for field in ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE',
                                  'TRAFFIC_CODE_NO', 'DRIVING_LICENSE_NO', 'LICENSE_TYPE', 'PLACE_OF_ISSUE',
                                  'LICENSE_EXPIRY_DATE', 'GPS_TAG_NO', 'GPS_TAG_ASSIGN_DATE']:
                        setattr(drive, field, driver_item.get(field))

                    drive.HEADER_ID = HEADER_ID
                    drive.Process = "GTD"

                    file_key = f'DriverAttachments_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        drive.DriverAttachments = handle_file_upload(
                            drive.DriverAttachments,
                            files,
                            'media/documents/driver'
                        )
                        for file_path in json.loads(drive.DriverAttachments):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='DriverInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    drive.save()

            if allocation:
                allocation_data = json.loads(allocation)
                for index, allocation_item in enumerate(allocation_data):
                    if allocation_item['ALLOC_LINE_ID'] != 'new':
                        allocations = XXGTD_ALLOCATION_INFO.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], fleet_master=fleet_master)
                    else:
                        allocations = XXGTD_ALLOCATION_INFO(fleet_master=fleet_master)

                    for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE', 'ALLOCATION_END_DATE']:
                        setattr(allocations, field, allocation_item.get(field))

                    allocations.HEADER_ID = HEADER_ID
                    allocations.Process = "GTD"

                    file_key = f'attachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        allocations.attachment = handle_file_upload(
                            allocations.attachment,
                            files,
                            'media/documents/allocation'
                        )
                        for file_path in json.loads(allocations.attachment):
                            Attachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='AllocationInfo',
                                fleet_master=fleet_master,
                                HEADER_ID=fleet_master.HEADER_ID
                            )

                    allocations.save()

            ApprovalRequest.objects.update_or_create(
                request_number=fleet_master.HEADER_ID,
                defaults={
                    'company_name': fleet_master.COMPANY_NAME,
                    'request_type': 'FLEET MASTER',
                    'status': fleet_master.STATUS,
                    'comments': fleet_master.COMMENTS,
                    'fleet_master': fleet_master
                }
            )

            action = "created" if created else "updated"
            return {
                "message": f"Fleet Master {action} successfully",
                "fleet_master": FleetMasterSchema.from_orm(fleet_master)
                            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}




class InsuranceSchema(Schema):
    INS_LINE_ID: int 
    INSURANCE_COMPANY: Optional[str] = None
    POLICY_NO: Optional[str] = None
    POLICY_DATE:  Optional[date] = None
    PLTS_INS_START_DATE:  Optional[date] = None
    POLICY_EXPIRY_DATE:  Optional[date] = None
    PLTS_INS_EXPIRY_DATE:  Optional[date] = None
    CUR_STAT_MOT_INS: Optional[str] = None
    InsurancePolicAattachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None

class PermitsSchema(Schema):
    PERMIT_LINE_ID: int 
    PERMIT_TYPE: Optional[str] = None
    EMIRATES: Optional[str] = None
    ISSUING_AUTHORITY: Optional[str] = None
    PERMIT_NO: Optional[str] = None
    PERMIT_DATE:  Optional[date] = None
    PERMIT_EXPIRY_DATE:  Optional[date] = None
    CUR_STAT_PERMIT: Optional[str] = None
    PermitColor: Optional[str] = None
    PermitAattachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None

class GpsSchema(Schema):
    GT_LINE_ID: int 
    GPS_DEVICE_NO: Optional[str] = None
    GPS_INSTALLATION_DATE:  Optional[date] = None
    GPS_SERVICE_PROVIDER: Optional[str] = None
    GpsAattachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None

class RegistrationSchema(Schema):
    REG_LINE_ID: int 
    EMIRATES_TRF_FILE_NO: Optional[str] = None
    REGISTERED_EMIRATES: Optional[str] = None
    FEDERAL_TRF_FILE_NO: Optional[str] = None
    REG_COMPANY_NAME: Optional[str] = None
    TRADE_LICENSE_NO: Optional[str] = None
    REGISTRATION_NO1: Optional[str] = None
    REGISTRATION_NO: Optional[str] = None
    REGISTRATION_DATE:  Optional[date] = None
    REG_EXPIRY_DATE:  Optional[date] = None
    CUR_STAT_REG: Optional[str] = None
    RegCardAttachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None


class FuelSchema(Schema):
    FUEL_LINE_ID: int 
    FUEL_TYPE: Optional[str] = None
    MONTHLY_FUEL_LIMIT: Optional[str] = None
    FUEL_SERVICE_TYPE: Optional[str] = None
    FUEL_SERVICE_PROVIDER: Optional[str] = None
    FUEL_DOCUMENT_NO: Optional[str] = None
    FUEL_DOCUMENT_DATE: Optional[date] = None
    FUEL_DOC_EXPIRY_DATE:  Optional[date] = None
    CUR_STAT_FUEL_DOC: Optional[str] = None
    FuelDocumentAttachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None


class RoadtollSchema(Schema):
    RT_LINE_ID: int 
    EMIRATES: Optional[str] = None
    TOLL_TYPE: Optional[str] = None
    ACCOUNT_NO: Optional[str] = None
    TAG_NO: Optional[str] = None
    ACTIVATION_DATE: Optional[date] = None
    ACTIVATION_END_DATE: Optional[date] = None
    CURRENT_STATUS: Optional[str] = None
    RoadtollAttachments: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None

    
class DriverSchema(Schema):
    ASGN_LINE_ID: int 
    EMPLOYEE_NAME: Optional[str] = None
    DESIGNATION: Optional[str] = None
    CONTACT_NUMBER: Optional[str] = None
    ASSIGNMENT_DATE: Optional[date] = None
    TRAFFIC_CODE_NO: Optional[str] = None
    DRIVING_LICENSE_NO: Optional[str] = None
    LICENSE_TYPE: Optional[str] = None
    PLACE_OF_ISSUE: Optional[str] = None
    LICENSE_EXPIRY_DATE: Optional[date] = None
    GPS_TAG_NO: Optional[str] = None
    GPS_TAG_ASSIGN_DATE: Optional[date] = None
    DriverAttachments: Optional[str] = None
    EMPLOYEE_NO:Optional[str]=None
    FLEET_PROCESS:Optional[str]=None

    
    
class AllocationSchema(Schema):
    ALLOC_LINE_ID: int 
    COMPANY_NAME: Optional[str] = None
    DIVISION: Optional[str] = None
    OPERATING_LOCATION: Optional[str] = None
    OPERATING_EMIRATES: Optional[str] = None
    APPICATION_USAGE: Optional[str] = None
    ALLOCATION_DATE: Optional[date] = None
    ALLOCATION_END_DATE:Optional[date]=None
    attachment: Optional[str] = None
    FLEET_PROCESS:Optional[str]=None



class FleetMasterDetailSchema(FleetMasterSchema):
    insurances: List[InsuranceSchema]
    permits: List[PermitsSchema]
    gps: List[GpsSchema]
    registration: List[RegistrationSchema]
    fuel: List[FuelSchema]
    roadtoll:List[RoadtollSchema]
    driver:List[DriverSchema]
    allocation:List[AllocationSchema]



@api.get("/fleet-master/{identifier}", response=FleetMasterDetailSchema)
def get_fleet_master(request, identifier: str):
    try:
        # Try to fetch by FLEET_CONTROL_NO first
        fleet_master = XXGTD_VEHICLE_INFO.objects.prefetch_related(
            'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(FLEET_CONTROL_NO=identifier)
    except XXGTD_VEHICLE_INFO.DoesNotExist:
        try:
            # If not found, try to fetch by header_id
            fleet_master = XXGTD_VEHICLE_INFO.objects.prefetch_related(
                'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
            ).get(HEADER_ID=identifier)
        except XXGTD_VEHICLE_INFO.DoesNotExist:
            return JsonResponse({"error": f"FleetMaster with identifier {identifier} does not exist"}, status=404)

    return FleetMasterDetailSchema.from_orm(fleet_master)


@api.get("/fleet-master-by-header/{HEADER_ID}", response=FleetMasterDetailSchema)
def get_fleet_master_by_header(request, HEADER_ID: str):
    try:
        fleet_master = XXGTD_VEHICLE_INFO.objects.prefetch_related(
            'insurances', 'registration', 'permits', 'gps',
            'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(HEADER_ID=HEADER_ID)
        return FleetMasterDetailSchema.from_orm(fleet_master)
    except XXGTD_VEHICLE_INFO.DoesNotExist:
        return JsonResponse({"error": f"FleetMaster with header_id {HEADER_ID} does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)




class FleetInfoSchema(Schema):
    HEADER_ID: Optional[str] = None
    FLEET_CONTROL_NO: Optional[str]=None
    VIN_NO: Optional[str]=None
    MANUFACTURER: Optional[str]=None
    MODEL: Optional[str]=None
    ENGINE_NO: Optional[str]=None
    STATUS:Optional[str]=None
    REGISTRATION_NO: Optional[str] = None

from django.db.models import F, OuterRef, Subquery

@api.get("/fleet-info", response=List[FleetInfoSchema])
def get_fleet_info(request):
    reg_subquery = XXGTD_REGISTRATION_INFO.objects.filter(fleet_master=OuterRef('pk')).values('REGISTRATION_NO')[:1]
    
    fleet_info = XXGTD_VEHICLE_INFO.objects.annotate(
        REGISTRATION_NO=Subquery(reg_subquery)
    ).values(
        'HEADER_ID',
        'FLEET_CONTROL_NO',
        'VIN_NO',
        'MANUFACTURER',
        'MODEL',
        'ENGINE_NO',
        'STATUS',
        'REGISTRATION_NO'
       
    )
    
    return list(fleet_info)



@api.get("/fleet-control-numbers", response=List[str])
def get_fleet_control_numbers(request):
    fleet_control_numbers = XXGTD_VEHICLE_INFO.objects.values_list('FLEET_CONTROL_NO', flat=True)
    return list(fleet_control_numbers)




class AttachmentSchema(Schema):
    id: int
    file: Union[str,Any]
    attachment_type: str
    FleetNumber: str
    upload_date:date
    uploaded_by: Optional[str] = None

@api.get("/attachments/{fleet_number}", response=List[AttachmentSchema])
def get_attachments(request, fleet_number: str):
    attachments = Attachment.objects.filter(FleetNumber=fleet_number)
    return [
        AttachmentSchema(
            id=attachment.id,
            file=str(attachment.file),
            attachment_type=attachment.attachment_type,
            FleetNumber=attachment.FleetNumber,
            upload_date=attachment.upload_date.date(),
            uploaded_by=attachment.uploaded_by
        )
        for attachment in attachments
    ]


class AttachmentSchema(Schema):
    id: int
    file:  Union[str,Any]
    attachment_type: str
    FleetNumber: str
    upload_date:date
    uploaded_by: Optional[str] = None

@api.get("/attachments", response=List[AttachmentSchema])
def get_attachments(request):
    attachments = Attachment.objects.all()
    return [AttachmentSchema.from_orm(attachment) for attachment in attachments]




@api.get("/unique-fleet-numbers", response=List[str])
def get_unique_fleet_numbers(request):
    unique_fleet_numbers = Attachment.objects.values_list('FLEET_CONTROL_NO', flat=True).distinct()
    return list(filter(None, unique_fleet_numbers))


    

## LOOKUP MASTER MEANING
@api.get("/meanings/")
def get_meanings(request):
    meanings = XXALY_GTD_LOOKUP_MASTER.objects.values_list('MEANING', flat=True).distinct()
    return list(meanings)

## LOOKUP DETAILS BY MEANING
@api.get("/lookup-details/")
def get_lookup_details(request, meaning: str):
    # Fetch the record where MEANING matches the selected value
    lookup = get_object_or_404(XXALY_GTD_LOOKUP_MASTER, MEANING=meaning)
    return {
        "lookup_name": lookup.LOOKUP_NAME,
        "meaning": lookup.MEANING,
    }

from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import ValidationError as PydanticValidationError


from pydantic import BaseModel, Field
from typing import Optional
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

class XXALY_GTD_LOOKUP_DETAILIn(BaseModel):
    LOOKUP_CODE: str
    LOOKUP_VALUE: str
    MEANING: str
    LOOKUP_SHORT_CODE: Optional[str] = None
    START_DATE: date
    END_DATE: Optional[date] = None
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    ATTRIBUTE_CATEGORY: Optional[str] = None
    ATTRIBUTE1: Optional[str] = None
    ATTRIBUTE2: Optional[str] = None
    ATTRIBUTE3: Optional[str] = None
    ATTRIBUTE4: Optional[str] = None
    ATTRIBUTE5: Optional[str] = None
    ATTRIBUTE6: Optional[str] = None
    ATTRIBUTE7: Optional[str] = None
    ATTRIBUTE8: Optional[str] = None
    ATTRIBUTE9: Optional[str] = None
    ATTRIBUTE10: Optional[str] = None
    ATTRIBUTE11: Optional[str] = None
    ATTRIBUTE12: Optional[str] = None
    ATTRIBUTE13: Optional[str] = None
    ATTRIBUTE14: Optional[str] = None
    ATTRIBUTE15: Optional[str] = None
    ACTIVE: Optional[str] = None
    LOOKUP_NAME: str



class XXALY_GTD_LOOKUP_DETAILSchema(Schema):
    LOOKUP_CODE: str
    LOOKUP_VALUE: str
    ACTIVE: str
    START_DATE: str
    END_DATE: Optional[date] = None
    CREATION_DATE: Optional[date] = None
    LAST_UPDATE_DATE: Optional[date] = None
    LOOKUP_SHORT_CODE:Optional[str] =None
    MEANING: str
    LOOKUP_NAME: str
    CREATED_BY:Optional[str] =None
    LAST_UPDATED_BY: Optional[str] = None

    
class ErrorResponse(Schema):
    detail: str

@api.post("/xxaly-gtd-lookup-detail/")
@csrf_exempt
def create_xxaly_gtd_lookup_detail(request, payload: List[XXALY_GTD_LOOKUP_DETAILSchema]):
    try:
        print("Received POST request to /xxaly-gtd-lookup-detail/")
        print(f"Payload received: {payload}")

        created_items = []
        current_date = timezone.now().date()
        
        # Get the username of the logged-in user
        username = request.user.username if request.user.is_authenticated else "System"

        for item in payload:
            print(f"Processing item: {item}")
            item_dict = item.dict(exclude_unset=True)
            
            # Clean up data
            if 'START_DATE' in item_dict:
                item_dict['START_DATE'] = item_dict['START_DATE'].strip()
            if 'MEANING' in item_dict:
                item_dict['MEANING'] = item_dict['MEANING'].strip()

            item_dict['CREATION_DATE'] = current_date
            item_dict['LAST_UPDATE_DATE'] = current_date
            
            # Set CREATED_BY only if it's not already set
            if 'CREATED_BY' not in item_dict or not item_dict['CREATED_BY']:
                item_dict['CREATED_BY'] = username
            
            # Always update LAST_UPDATED_BY
            item_dict['LAST_UPDATED_BY'] = username

            # Validate required fields
            required_fields = ['LOOKUP_CODE', 'LOOKUP_VALUE', 'ACTIVE', 'START_DATE', 'MEANING', 'LOOKUP_NAME']
            for field in required_fields:
                if not item_dict.get(field):
                    raise ValidationError(f"{field} is required")

            lookup_detail = XXALY_GTD_LOOKUP_DETAIL.objects.create(**item_dict)
            print(f"Created lookup_detail with id: {lookup_detail.id}")

            created_items.append({
                "id": lookup_detail.id,
                "LOOKUP_CODE": lookup_detail.LOOKUP_CODE,
                "LOOKUP_VALUE": lookup_detail.LOOKUP_VALUE,
                "MEANING": lookup_detail.MEANING,
                "LOOKUP_SHORT_CODE": lookup_detail.LOOKUP_SHORT_CODE,
                "START_DATE": lookup_detail.START_DATE,
                "END_DATE": lookup_detail.END_DATE,
                "ACTIVE": lookup_detail.ACTIVE,
                "CREATION_DATE": lookup_detail.CREATION_DATE,
                "LAST_UPDATE_DATE": lookup_detail.LAST_UPDATE_DATE,
                "LOOKUP_NAME": lookup_detail.LOOKUP_NAME,
                "CREATED_BY": lookup_detail.CREATED_BY,
                "LAST_UPDATED_BY": lookup_detail.LAST_UPDATED_BY,
            })
            

        response = {"message": f"{len(created_items)} XXALY_GTD_LOOKUP_DETAIL items created successfully", "items": created_items}
        return JsonResponse(response, status=201)
    
    except ValidationError as e:
        error_details = [{"field": error['loc'][0], "error": error['msg']} for error in e.errors()]
        return JsonResponse({"detail": error_details}, status=422)
    
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=500)




    

## DATA FETCHING RELATED TO LOOKUP NAME
@api.get("/related-data/", response=list)
def fetch_related_data(request, lookup_name: str = None, lookup_value: str = None):
    if not lookup_name and not lookup_value:
        return JsonResponse({'error': 'Either lookup name or lookup value is required'}, status=400)
   
    try:
        query = XXALY_GTD_LOOKUP_DETAIL.objects
        if lookup_name:
            query = query.filter(LOOKUP_NAME__iexact=lookup_name.strip())
        if lookup_value:
            query = query.filter(LOOKUP_VALUE__iexact=lookup_value.strip())

        related_data = query.values(
            'LOOKUP_CODE',
            'LOOKUP_VALUE',
            'MEANING',
            'LOOKUP_SHORT_CODE',
            'START_DATE',
            'END_DATE',
            'ACTIVE'
        )
       
        data_list = list(related_data)
        
        if not data_list:
            return JsonResponse({'error': 'No related data found for the given lookup name or value'}, status=404)
       
        return data_list
    
    except Exception as e:
        print(f"Error fetching related data: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
    


## POST DATA IN LOOKUP MASTER
class LookupMasterCreate(Schema):
    LOOKUP_NAME: str
    MEANING: str
    ACTIVE: Optional[str] = None
    START_DATE: Optional[str] = None
    END_DATE: Optional[str] = None
    CREATION_DATE: Optional[str] = None
    CREATED_BY: Optional[str] = None
    LAST_UPDATE_DATE: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    DISPLAY_TO_ADMIN: Optional[str] = "Y"
    DISPLAY_TO_USER: Optional[str] = "Y"

class ResponseSchema(Schema):
    message: str

@api.post("/lookup-master/", response=ResponseSchema)
def create_lookup_master(request, data: LookupMasterCreate):
    # Check if LOOKUP_NAME already exists
    if XXALY_GTD_LOOKUP_MASTER.objects.filter(LOOKUP_NAME=data.LOOKUP_NAME).exists():
        return ResponseSchema(message="LOOKUP_NAME already exists")

    # Get the current date
    current_date = timezone.now().date()
    current_user = request.user.username if request.user.is_authenticated else "System"

    # Set date fields to current date if not provided
    start_date = data.START_DATE if data.START_DATE else current_date
    creation_date = data.CREATION_DATE if data.CREATION_DATE else current_date
    last_update_date = data.LAST_UPDATE_DATE if data.LAST_UPDATE_DATE else current_date

    # Create a new instance of the model with default dates if not provided
    lookup_master = XXALY_GTD_LOOKUP_MASTER(
        MEANING=data.MEANING,
        LOOKUP_NAME=data.LOOKUP_NAME,
        ACTIVE=data.ACTIVE,
        START_DATE=start_date,
        END_DATE=data.END_DATE,
        CREATION_DATE=creation_date,
        CREATED_BY=current_user,
        LAST_UPDATE_DATE=last_update_date,
        LAST_UPDATED_BY=current_user,
        DISPLAY_TO_ADMIN=data.DISPLAY_TO_ADMIN or "Y",
        DISPLAY_TO_USER=data.DISPLAY_TO_USER or "Y"
    )
    # Save the instance to the database
    lookup_master.save()
    
    return ResponseSchema(message="Lookup Master entry created successfully")
    


## FLEET MASTER DROPDOWNS
@api.get("/dropdown-options/")
def get_meaning_options(request, lookup_name: str):
    """
    Fetch MEANING values related to a given LOOKUP_NAME from XXALY_GTD_LOOKUP_DETAIL table.
    """
    meanings = XXALY_GTD_LOOKUP_DETAIL.objects.filter(LOOKUP_NAME=lookup_name).values_list('MEANING', flat=True)
    return {"meanings": list(meanings)}    
    
    
@api.delete("/delete-file/{model_name}/{instance_id}/{file_index}")
def delete_file(request, model_name: str, instance_id: int, file_index: int):
    try:
        model_map = {
            'fleetmaster': XXGTD_VEHICLE_INFO,
            'insurance': XXGTD_INSURANCE_INFO,
            'permits': XXGTD_PARKING_PERMIT,
            'gps': XXGTD_GPS_TRACKING_INFO,
            'registration': XXGTD_REGISTRATION_INFO,
            'fuel': XXGTD_FUEL_INFO,
            'roadtoll': XXGTD_ROAD_TOLL_INFO,
            'driver': XXGTD_DRIVER_ASSIGNMENT,
            'allocation': XXGTD_ALLOCATION_INFO,
        }

        Model = model_map.get(model_name.lower())
        if not Model:
            return {"message": "Invalid model name"}

        instance = Model.objects.get(id=instance_id)

        attachment_field = {
            'fleetmaster': 'VehiclePurchaseDoc',
            'insurance': 'InsurancePolicAattachment',
            'permits': 'PermitAattachment',
            'gps': 'GpsAattachment',
            'registration': 'RegCardAttachment',
            'fuel': 'FuelDocumentAttachment',
            'roadtoll': 'RoadtollAttachments',
            'driver': 'DriverAttachments',
            'allocation': 'attachment',
        }.get(model_name.lower())

        attachments = json.loads(getattr(instance, attachment_field))

        if file_index < 0 or file_index >= len(attachments):
            return {"message": "Invalid file index"}

        file_path = attachments[file_index]

        # Delete from specific model's attachment list
        del attachments[file_index]
        setattr(instance, attachment_field, json.dumps(attachments))
        instance.save()

        # Delete from Attachment model
        Attachment.objects.filter(
            FLEET_CONTROL_NO=instance.FLEET_CONTROL_NO,
            file__icontains=file_path.split('/')[-1]
        ).delete()

        # Delete file from storage
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        return {"message": "File deleted successfully from both model and all attachments"}

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}
    
    
    
    ## POST DATA IN LOOKUP MASTER
class LookupMasterCreate(Schema):
    LOOKUP_NAME: str
    MEANING: str
    ACTIVE: Optional[str] = None
    START_DATE: Optional[str] = None
    END_DATE: Optional[str] = None
    CREATION_DATE: Optional[str] = None
    CREATED_BY: Optional[str] = None
    LAST_UPDATE_DATE: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    DISPLAY_TO_ADMIN: Optional[str] = "Y"
    DISPLAY_TO_USER: Optional[str] = "Y"



class ResponseSchema(Schema):
    message: str

@api.post("/lookup-master/", response=ResponseSchema)
def create_lookup_master(request, data: LookupMasterCreate):
    # Check if LOOKUP_NAME already exists
    if XXALY_GTD_LOOKUP_MASTER.objects.filter(LOOKUP_NAME=data.LOOKUP_NAME).exists():
        return ResponseSchema(message="LOOKUP_NAME already exists")

    # Get the current date
    current_date = timezone.now().date()

    # Set date fields to current date if not provided
    start_date = data.START_DATE if data.START_DATE else current_date
    creation_date = data.CREATION_DATE if data.CREATION_DATE else current_date
    last_update_date = data.LAST_UPDATE_DATE if data.LAST_UPDATE_DATE else current_date

    # Create a new instance of the model with default dates if not provided
    lookup_master = XXALY_GTD_LOOKUP_MASTER(
        MEANING=data.MEANING,
        LOOKUP_NAME=data.LOOKUP_NAME,
        ACTIVE=data.ACTIVE,
        START_DATE=start_date,
        END_DATE=data.END_DATE,
        CREATION_DATE=creation_date,
        CREATED_BY=data.CREATED_BY,
        LAST_UPDATE_DATE=last_update_date,
        LAST_UPDATED_BY=data.LAST_UPDATED_BY,
        DISPLAY_TO_ADMIN=data.DISPLAY_TO_ADMIN or "Y",
        DISPLAY_TO_USER=data.DISPLAY_TO_USER or "Y"
    )
    # Save the instance to the database
    lookup_master.save()
    
    return ResponseSchema(message="Lookup Master entry created successfully")





class TrafficFileSchema(Schema):
    TRAFFIC_FILE_ID: Optional[int] = None
    TRAFFIC_FILE_NO: str
    COMPANY_NAME: str
    TRADE_LICENSE_NO: str
    EMIRATES: str
    FEDERAL_TRAFFIC_FILE_NO: str
    SALIK_ACCOUNT_NO: Union[str,int]
    STATUS: str
    NO_OF_VEHICLES: Optional[int] = None

class TrafficFileResponse(Schema):
    message: str
    traffic_file: Optional[TrafficFileSchema] = None

@api.post("/traffic-file-master", response=TrafficFileResponse)
def create_or_update_traffic_file_master(
    request,
    TRAFFIC_FILE_ID: str = Form(...),
    TRAFFIC_FILE_NO: str = Form(...),
    COMPANY_NAME: str = Form(...),
    TRADE_LICENSE_NO: str = Form(...),
    EMIRATES: str = Form(...),
    FEDERAL_TRAFFIC_FILE_NO: str = Form(...),
    SALIK_ACCOUNT_NO: str = Form(...),
    STATUS: str = Form(...),
    COMMENTS: str = Form(None),
    ACTION_CODE: str = Form(None),
    ACTION: str = Form(None),
    RECORD_STATUS: str = Form(None),
):
    try:
        with transaction.atomic():
            if TRAFFIC_FILE_ID != 'new':
                try:
                    traffic_file = XXGTD_TRAFFIC_FILE_MASTER.objects.get(TRAFFIC_FILE_ID=TRAFFIC_FILE_ID)
                    created = False
                except XXGTD_TRAFFIC_FILE_MASTER.DoesNotExist:
                    return {"message": f"Error: Traffic File with id {TRAFFIC_FILE_ID} does not exist"}
            else:
                traffic_file = XXGTD_TRAFFIC_FILE_MASTER()
                created = True

            # Update TrafficFileMaster fields
            traffic_file_fields = [
                "TRAFFIC_FILE_NO", "COMPANY_NAME", "TRADE_LICENSE_NO", "EMIRATES",
                "FEDERAL_TRAFFIC_FILE_NO", "SALIK_ACCOUNT_NO", "STATUS", "COMMENTS",
                "ACTION_CODE", "ACTION", "RECORD_STATUS", "ATTRIBUTE1", "ATTRIBUTE2",
                "ATTRIBUTE3", "ATTRIBUTE4", "ATTRIBUTE5", "ATTRIBUTE6", "ATTRIBUTE7",
                "ATTRIBUTE8", "ATTRIBUTE9", "ATTRIBUTE10"
            ]
            
            for field in traffic_file_fields:
                value = locals().get(field)
                if value is not None:
                    setattr(traffic_file, field, value)

            if created:
                traffic_file.CREATION_DATE = timezone.now()
                traffic_file.CREATED_BY = request.user.username if request.user.is_authenticated else 'Anonymous'

            traffic_file.LAST_UPDATE_DATE = timezone.now()
            traffic_file.LAST_UPDATED_BY = request.user.username if request.user.is_authenticated else 'Anonymous'

            traffic_file.save()

            # Determine the action based on the user's role
            current_user = request.user if request.user.is_authenticated else None
            is_approver = current_user.roles == "APPROVER" if current_user and hasattr(current_user, 'roles') else False
           
            if is_approver:
                approval_action = "Request Approved"
                approval_status = "Active"
            else:
                approval_action = "Submitted for Approval"
                approval_status = "New"

            # Create or update ApprovalRequest
            ApprovalRequest.objects.update_or_create(
                request_number=traffic_file.TRAFFIC_FILE_NO,
                defaults={
                    'application_number': traffic_file.TRAFFIC_FILE_NO,
                    'company_name': traffic_file.COMPANY_NAME,
                    'request_type': 'TRAFFIC FILE MASTER',
                    'status': approval_status,
                    'comments': traffic_file.COMMENTS,
                    'traffic_file_master': traffic_file,
                    'responded_by': current_user.username if current_user else "System",
                    'response_role': current_user.roles if current_user and hasattr(current_user, 'roles') else "System",
                    'action': approval_action
                }
            )

            # Create XXALY_GTD_ACTION_HISTORY entry
            XXALY_GTD_ACTION_HISTORY.objects.create(
                APPLICATION_ID=str(traffic_file.TRAFFIC_FILE_ID),
                APPL_NUMBER=traffic_file.TRAFFIC_FILE_NO,
                REQUEST_TYPE="TRAFFIC_FILE_MASTER",
                REQUEST_NUMBER=traffic_file.TRAFFIC_FILE_NO,
                PROCESS_STATUS=approval_status,
                DOC_STATUS=approval_status,
                RESPONSE_DATE=timezone.now().date(),
                RESPONDED_BY=current_user.username if current_user else "System",
                RESPONDER_ROLE=current_user.roles if current_user else "System",
                RESPONSE_COMMENTS=traffic_file.COMMENTS,
                ACTION_PERFORMED=f"Traffic File Master {'created' if created else 'updated'}",
                CREATED_BY=current_user.username if current_user else "System",
                CREATION_DATE=timezone.now().date(),
                LAST_UPDATED_BY=current_user.username if current_user else "System",
                LAST_UPDATE_DATE=timezone.now().date(),
                NEXT_RESP="APPROVER" if current_user and current_user.roles == "REQUESTOR" else "REQUESTOR"
            )

            # Count approved vehicles
            approved_vehicle_count = XXGTD_REGISTRATION_INFO.objects.filter(
                EMIRATES_TRF_FILE_NO=traffic_file.TRAFFIC_FILE_NO,
                FLEET_PROCESS='Approved'
            ).count()

            action = "created" if created else "updated"
            return {
                "message": f"Traffic File Master {action} successfully",
                "traffic_file": TrafficFileSchema(
                    TRAFFIC_FILE_ID=traffic_file.TRAFFIC_FILE_ID,
                    TRAFFIC_FILE_NO=traffic_file.TRAFFIC_FILE_NO,
                    COMPANY_NAME=traffic_file.COMPANY_NAME,
                    TRADE_LICENSE_NO=traffic_file.TRADE_LICENSE_NO,
                    EMIRATES=traffic_file.EMIRATES,
                    FEDERAL_TRAFFIC_FILE_NO=traffic_file.FEDERAL_TRAFFIC_FILE_NO,
                    SALIK_ACCOUNT_NO=traffic_file.SALIK_ACCOUNT_NO,
                    STATUS=traffic_file.STATUS,
                    NO_OF_VEHICLES=approved_vehicle_count
                ).dict()
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}
    


from django.db.models import F, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from typing import List, Optional

class TrafficFileSchema(Schema):
    TRAFFIC_FILE_ID: Optional[int] = None
    TRAFFIC_FILE_NO: Optional[str] = None
    COMPANY_NAME: Optional[str] = None
    TRADE_LICENSE_NO: Optional[str] = None
    EMIRATES: Optional[str] = None
    FEDERAL_TRAFFIC_FILE_NO: Optional[str] = None
    SALIK_ACCOUNT_NO: Optional[str] = None
    STATUS: Optional[str] = None
    NO_OF_VEHICLES: Optional[Union[str,int]] = None

@api.get("/traffic-files", response=List[TrafficFileSchema])
def get_traffic_files(request):
    # Subquery to count approved registrations for each traffic file
    approved_vehicle_count_subquery = XXGTD_REGISTRATION_INFO.objects.filter(
        EMIRATES_TRF_FILE_NO=OuterRef('TRAFFIC_FILE_NO'),
        FLEET_PROCESS='Approved'  # Only count approved registrations
    ).values('EMIRATES_TRF_FILE_NO').annotate(
        count=Count('*')
    ).values('count')

    # Annotate TrafficFileMaster with the count of approved vehicles
    traffic_files = XXGTD_TRAFFIC_FILE_MASTER.objects.annotate(
        approved_vehicle_count=Coalesce(Subquery(approved_vehicle_count_subquery), 0)
    )
   
    return [
        {
            "TRAFFIC_FILE_ID": str(tf.TRAFFIC_FILE_ID),
            "TRAFFIC_FILE_NO": tf.TRAFFIC_FILE_NO,
            "COMPANY_NAME": tf.COMPANY_NAME,
            "TRADE_LICENSE_NO": tf.TRADE_LICENSE_NO,
            "EMIRATES": tf.EMIRATES,
            "FEDERAL_TRAFFIC_FILE_NO": tf.FEDERAL_TRAFFIC_FILE_NO,
            "SALIK_ACCOUNT_NO": tf.SALIK_ACCOUNT_NO,
            "STATUS": tf.STATUS,
            "NO_OF_VEHICLES": tf.approved_vehicle_count
        }
        for tf in traffic_files
    ]



from django.db.models.functions import Greatest
def update_registration_status(registration_id, new_status):
    with transaction.atomic():
        registration = XXGTD_REGISTRATION_INFO.objects.select_for_update().get(REG_LINE_ID=registration_id)
        old_process = registration.FLEET_PROCESS
        registration.FLEET_PROCESS = new_status
        
        fleet_master = XXGTD_VEHICLE_INFO.objects.select_for_update().get(HEADER_ID=registration.HEADER_ID)

        traffic_file = XXGTD_TRAFFIC_FILE_MASTER.objects.select_for_update().get(
            TRAFFIC_FILE_NO=registration.EMIRATES_TRF_FILE_NO
        )

        # Handle status changes
        if new_status == 'Approved' and old_process != 'Approved':
            traffic_file.NO_OF_VEHICLES = F('NO_OF_VEHICLES') + 1
        elif old_process == 'Approved' and new_status != 'Approved':
            traffic_file.NO_OF_VEHICLES = F('NO_OF_VEHICLES') - 1

        traffic_file.NO_OF_VEHICLES = Greatest(F('NO_OF_VEHICLES'), 0)
        traffic_file.save()

        registration.save()

    return {"message": f"Registration status updated to {new_status} and vehicle count adjusted successfully"}



from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=XXGTD_VEHICLE_INFO)
def update_registrations_on_dfleet(sender, instance, **kwargs):
    if instance.STATUS == 'Defleet':
        registrations = XXGTD_REGISTRATION_INFO.objects.filter(HEADER_ID=instance.HEADER_ID, FLEET_PROCESS='Approved')
        for registration in registrations:
            update_registration_status(registration.REG_LINE_ID, 'Defleet')

from typing import List, Optional

class TrafficFileResponseSchema(Schema):
    TRAFFIC_FILE_ID: Optional[int] = None
    TRAFFIC_FILE_NO: Optional[str] = None
    COMPANY_NAME: Optional[str] = None
    TRADE_LICENSE_NO: Optional[str] = None
    EMIRATES: Optional[str] = None
    FEDERAL_TRAFFIC_FILE_NO: Optional[str] = None
    SALIK_ACCOUNT_NO: Optional[str] = None
    STATUS: Optional[str] = None
    NO_OF_VEHICLES: Optional[Union[str,int]] = None
    

@api.get("/traffic-files/{TRAFFIC_FILE_NO}", response=TrafficFileResponseSchema)
def get_specific_traffic_file(request, TRAFFIC_FILE_NO: str):
    try:
        # Subquery to count approved registrations
        approved_count_subquery = XXGTD_REGISTRATION_INFO.objects.filter(
            EMIRATES_TRF_FILE_NO=OuterRef('TRAFFIC_FILE_NO'),
            FLEET_PROCESS='Approved'
        ).values('EMIRATES_TRF_FILE_NO').annotate(
            count=Count('*')
        ).values('count')

        traffic_file = XXGTD_TRAFFIC_FILE_MASTER.objects.annotate(
            approved_vehicle_count=Subquery(approved_count_subquery)
        ).get(TRAFFIC_FILE_NO=TRAFFIC_FILE_NO)

        return TrafficFileResponseSchema(
            TRAFFIC_FILE_ID=traffic_file.TRAFFIC_FILE_ID,
            TRAFFIC_FILE_NO=traffic_file.TRAFFIC_FILE_NO,
            COMPANY_NAME=traffic_file.COMPANY_NAME,
            TRADE_LICENSE_NO=traffic_file.TRADE_LICENSE_NO,
            EMIRATES=traffic_file.EMIRATES,
            FEDERAL_TRAFFIC_FILE_NO=traffic_file.FEDERAL_TRAFFIC_FILE_NO,
            SALIK_ACCOUNT_NO=traffic_file.SALIK_ACCOUNT_NO,
            STATUS=traffic_file.STATUS,
            NO_OF_VEHICLES=traffic_file.approved_vehicle_count or 0
        )
    except XXGTD_TRAFFIC_FILE_MASTER.DoesNotExist:
        raise Http404("Traffic file not found")



from django.db.models import Q
from ninja import Schema
from typing import List, Optional
from datetime import date

class TrafficFileActionHistorySchema(Schema):
    APPLICATION_ID: Optional[str]
    APPL_NUMBER: Optional[str]
    REQUEST_TYPE: Optional[str]
    REQUEST_NUMBER: Optional[str]
    PROCESS_STATUS: Optional[str]
    DOC_STATUS: Optional[str]
    RESPONSE_DATE: Optional[date]
    RESPONDED_BY: Optional[str]
    RESPONDER_ROLE: Optional[str]
    RESPONSE_COMMENTS: Optional[str]
    ACTION_PERFORMED: Optional[str]
    CREATED_BY: Optional[str]
    CREATION_DATE: Optional[date]
    LAST_UPDATED_BY: Optional[str]
    LAST_UPDATE_DATE: Optional[date]
    NEXT_RESP: Optional[str]

class TrafficFileActionHistoryResponse(Schema):
    count: int
    results: List[TrafficFileActionHistorySchema]

@api.get("/traffic-file-action-history", response=TrafficFileActionHistoryResponse)
def get_traffic_file_action_history(request):
    try:
        queryset = XXALY_GTD_ACTION_HISTORY.objects.filter(
            REQUEST_TYPE="TRAFFIC_FILE_MASTER"
        ).order_by('-CREATION_DATE')

        action_history = list(queryset.values())

        # Convert date objects to strings
        for item in action_history:
            for field in ['RESPONSE_DATE', 'CREATION_DATE', 'LAST_UPDATE_DATE']:
                if isinstance(item.get(field), date):
                    item[field] = item[field].isoformat()

        return {
            "count": len(action_history),
            "results": action_history
        }

    except Exception as e:
        logger.error(f"Error retrieving Traffic File Master action history: {str(e)}")
        return {"count": 0, "results": [], "error": "An unexpected error occurred"}


class TrafficFileInfoSchema(Schema):
    TRAFFIC_FILE_NO: Optional[str] = None
    COMPANY_NAME: Optional[str] = None  # Added this line
    TRADE_LICENSE_NO: Optional[str] = None
    EMIRATES: Optional[str] = None
    FEDERAL_TRAFFIC_FILE_NO: Optional[str] = None
    STATUS: Optional[str] = None

@api.get("/traffic-file-info", response=List[TrafficFileInfoSchema])
def get_traffic_file_info(request):
    traffic_file_info = XXGTD_TRAFFIC_FILE_MASTER.objects.filter(
        Q(STATUS='active') | Q(STATUS='Active')
    ).values(
        'TRAFFIC_FILE_NO',
        'COMPANY_NAME',  # Added this line
        'TRADE_LICENSE_NO',
        'EMIRATES',
        'FEDERAL_TRAFFIC_FILE_NO',
        'STATUS'
    )
    
    return list(traffic_file_info)
















# Commercial Master


    
class CommercialMasterSchema(Schema):
    COMPANY_NAME: str
    COMM_CONTROL_NO: Optional[str] = None
    COMM_PLATE_DATE: Optional[date] = None
    COMM_PLATE_NO: str
    COMM_PLATE_CATEGORY: str
    CP_ISSUED_AUTHORITY: str
    CP_VEHICLE_TYPE: str
    CP_COLOR: str
    COMMENTS: Optional[str] = None
    HEADER_ID:Optional[str] = None
    STATUS: Optional[str] = "Pending for Approval"
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None
    LAST_UPDATE_DATE: Optional[str]=None
    

class CommercialMasterResponse(Schema):
    message: str
    commercial_master: Optional[CommercialMasterSchema] = None




@api.post("/commercial-master", response=CommercialMasterResponse)
def create_or_update_commercial_master(
    request,
    COMPANY_NAME: Optional[str] = Form(None),
    COMM_CONTROL_NO: Optional[str] = Form(None),
    COMM_PLATE_NO: Optional[str] = Form(None),
    COMM_PLATE_DATE: Optional[date] = Form(None),
    COMM_PLATE_CATEGORY:Optional[str] = Form(None),
    CP_ISSUED_AUTHORITY: Optional[str] = Form(None),
    CP_VEHICLE_TYPE: Optional[str] = Form(None),
    CP_COLOR: Optional[str] = Form(None),
    COMMENTS:Optional[str] = Form(None),
    STATUS: Optional[str] = Form("Pending for Approval"), 
    HEADER_ID:Optional[str]=Form(None),
    
    insurances: str = Form(...),
    registration: str = Form(None),
    roadtoll: str = Form(...),
    allocation: str = Form(...),
    is_approver: bool = Form(False),
    InsurancePolicAattachment: Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    
    RegCardAttachment:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    RoadtollAttachments:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    AllocationAttachment:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
):
    try:
        with transaction.atomic():
            if COMM_CONTROL_NO:
                old_commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.get(COMM_CONTROL_NO=COMM_CONTROL_NO)
                created = False
            elif HEADER_ID:
                old_commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.filter(HEADER_ID=HEADER_ID).first()
                if old_commercial_master:
                    created = False
                else:
                    old_commercial_master = None
                    created = True
            else:
                old_commercial_master = None
                created = True

            if created:
                commercial_master = XXGTD_COMMERCIAL_PLATE_INFO()
            else:
                commercial_master = old_commercial_master

            tracked_fields = [
                'COMPANY_NAME', 'COMM_PLATE_NO', 'COMM_PLATE_DATE', 'COMM_PLATE_CATEGORY',
                'CP_ISSUED_AUTHORITY', 'CP_VEHICLE_TYPE', 'CP_COLOR', 'COMMENTS', 'STATUS'
            ]

            current_user = request.user if request.user.is_authenticated else None
            username = current_user.username if current_user else "System"

             # Set CREATED_BY only for new records, always update LAST_UPDATED_BY
            if created:
                commercial_master.CREATED_BY = username
            commercial_master.LAST_UPDATED_BY = username
            commercial_master.save()



            commercial_master_data = {
                    "COMPANY_NAME": COMPANY_NAME,
                    "COMM_PLATE_NO": COMM_PLATE_NO,
                    "COMM_PLATE_CATEGORY": COMM_PLATE_CATEGORY,
                    "CP_ISSUED_AUTHORITY": CP_ISSUED_AUTHORITY,
                    "CP_VEHICLE_TYPE": CP_VEHICLE_TYPE,
                    "CP_COLOR": CP_COLOR,
                    "COMMENTS": COMMENTS,
                    "STATUS": STATUS or "Pending For Approval",
                    "HEADER_ID":HEADER_ID,
                    "LAST_UPDATE_DATE":timezone.now().date(),
                    
            }
           
            all_tracked_changes = []
            if not created:
                all_tracked_changes.extend(track_changes(old_commercial_master, commercial_master_data, tracked_fields, 'XXGTD_COMMERCIAL_PLATE_INFO', current_user, HEADER_ID))

            for key, value in commercial_master_data.items():
                
                setattr(commercial_master, key, value)
                
            commercial_master.COMM_PLATE_DATE = COMM_PLATE_DATE

          
            commercial_master.save()
            
            # commercial_master_changes = []
            # for field in tracked_fields:
            #     new_value = getattr(commercial_master, field)
            #     commercial_master_changes.append({
            #         'COLUMN_NAME': field,
            #         'ACTUAL_COLUMN_NAME': field,
            #         'COLUMN_VALUE1': '',
            #         'COLUMN_VALUE2': str(new_value) if new_value is not None else '',
            #         'CREATED_BY': current_user,
            #         'TABLE_NAME': 'CommercialMaster',
            #         'LINE_ID': str(commercial_master.id),
            #         'HEADER_ID': commercial_master.HEADER_ID
            #     })

            # all_tracked_changes.extend(commercial_master_changes)


            header_id_num=commercial_master.HEADER_ID
            commercial_control_number = commercial_master.COMM_CONTROL_NO
            
            XXGTD_CPI_AUDIT.objects.create(
                
                COMPANY_NAME=COMPANY_NAME,
                COMM_CONTROL_NO=commercial_master.COMM_CONTROL_NO,
                COMM_PLATE_NO=COMM_PLATE_NO,
                COMM_PLATE_DATE=COMM_PLATE_DATE,
                COMM_PLATE_CATEGORY=COMM_PLATE_CATEGORY,
                CP_ISSUED_AUTHORITY=CP_ISSUED_AUTHORITY,
                CP_VEHICLE_TYPE=CP_VEHICLE_TYPE,
                CP_COLOR=CP_COLOR,
                RECORD_STATUS=commercial_master.RECORD_STATUS,
                
                COMMENTS=COMMENTS,
                STATUS=STATUS,
               
                HEADER_ID=HEADER_ID,
                
                CREATED_BY=current_user.username if current_user else "System",
                LAST_UPDATED_BY=current_user.username if current_user else "System",
                ACTION_CODE='C' if created else 'U',
                ACTION='Created' if created else 'Updated',
            )
            
            
            if is_approver:
                commercial_master.STATUS = STATUS
            elif all(insurance.FLEET_PROCESS == 'Pending for Approval' for insurance in commercial_master.insurances.all()) and \
                all(reg.FLEET_PROCESS == 'Pending for Approval' for reg in commercial_master.registration.all()):
                commercial_master.STATUS = 'Pending for Approval'
            commercial_master.save()

            def handle_file_upload(existing_files, new_files, file_path_prefix):
                existing_files = json.loads(existing_files) if existing_files else []
                existing_base_names = set(re.sub(r'_[^_]+(?=\.[^.]+$)', '', os.path.basename(file)) for file in existing_files)
                new_file_paths = []

                for file in new_files:
                    base_name = re.sub(r'_[^_]+(?=\.[^.]+$)', '', file.name)
                    if base_name not in existing_base_names:
                        file_path = default_storage.save(f'{file_path_prefix}/{file.name}', ContentFile(file.read()))
                        new_file_paths.append(file_path)
                        existing_base_names.add(base_name)

                all_files = existing_files + new_file_paths
                return json.dumps(all_files)
                
            insurance_tracked_fields = [
                'INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                'PLTS_INS_START_DATE', 'PLTS_INS_EXPIRY_DATE', 'CUR_STAT_MOT_INS'
            ]

            insurance_data = json.loads(insurances)

            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    old_insurance = XXGTD_INSURANCE_INFO.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], commercial_master=commercial_master)
                    insurance = old_insurance
                    if insurance.FLEET_PROCESS != 'Approved':
                        insurance.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(old_insurance, insurance_item, insurance_tracked_fields, 'Insurance', current_user, commercial_master.HEADER_ID))
                else:
                    insurance = XXGTD_INSURANCE_INFO(commercial_master=commercial_master, FLEET_PROCESS='Pending for Approval')
                    
                    for field in insurance_tracked_fields:
                        new_value = insurance_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Insurance',
                                'LINE_ID': 'new',
                                'HEADER_ID': commercial_master.HEADER_ID
                            })

                for field in insurance_tracked_fields:
                    setattr(insurance, field, insurance_item.get(field))
                    
                    insurance.COMM_CONTROL_NO = commercial_control_number
                    insurance.HEADER_ID = header_id_num
                    insurance.Process = 'Commercial' 
                    commercial_master.STATUS = "Pending for Approval"


                    file_key = f'InsurancePolicAattachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        insurance.InsurancePolicAattachment = handle_file_upload(
                            insurance.InsurancePolicAattachment,
                            files,
                            'media/documents/insurance'
                        )
                        for file_path in json.loads(insurance.InsurancePolicAattachment):
                            CommercialAttachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='InsuranceInfo',
                                commercial_master=commercial_master,
                                HEADER_ID=commercial_master.HEADER_ID,
                                CommercialNumber=commercial_control_number
                            )

                    insurance.save()
                    XXGTD_INSUR_AUDIT.objects.create(
                        INS_LINE_ID=insurance,
                        HEADER_ID=commercial_master.HEADER_ID,
                        INSURANCE_COMPANY=insurance.INSURANCE_COMPANY,
                        POLICY_NO=insurance.POLICY_NO,
                        POLICY_DATE=insurance.POLICY_DATE,
                        POLICY_EXPIRY_DATE=insurance.POLICY_EXPIRY_DATE,
                        PLTS_INS_EXPIRY_DATE=insurance.PLTS_INS_EXPIRY_DATE,
                        CUR_STAT_MOT_INS=insurance.CUR_STAT_MOT_INS,
                        PLTS_INS_START_DATE=insurance.PLTS_INS_START_DATE,
                        FLEET_PROCESS=commercial_master.STATUS,
                        CREATED_BY=current_user.username if current_user else "System",
                        LAST_UPDATED_BY=current_user.username if current_user else "System",
                        PROCESS="Commercial"
                        )


            registration_tracked_fields = [
                'EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO',
                'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1',
                'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG'
            ]

            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    old_registration = XXGTD_REGISTRATION_INFO.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], commercial_master=commercial_master)
                    reg = old_registration
                    if reg.FLEET_PROCESS != 'Approved':
                        reg.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(old_registration, reg_item, registration_tracked_fields, 'Registration', current_user, commercial_master.HEADER_ID))
                else:
                    reg = XXGTD_REGISTRATION_INFO(commercial_master=commercial_master, FLEET_PROCESS='Pending for Approval')
                    
                    for field in registration_tracked_fields:
                        new_value = reg_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Registration',
                                'LINE_ID': 'new',
                                'HEADER_ID': commercial_master.HEADER_ID
                            })

                for field in registration_tracked_fields:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)
            

                reg.COMM_CONTROL_NO = commercial_control_number
                reg.HEADER_ID = header_id_num
                reg.Process = 'Commercial' 
                commercial_master.STATUS = "Pending for Approval"
                
                
                
                
                
                file_key = f'RegCardAttachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    reg.RegCardAttachment = handle_file_upload(
                        reg.RegCardAttachment,
                        files,
                        'media/documents/registration'
                    )
                    for file_path in json.loads(reg.RegCardAttachment):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='RegistrationInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID,
                            CommercialNumber=commercial_control_number
                        )
                
                reg.save()
                XXGTD_REGIS_AUDIT.objects.create(
                    REG_LINE_ID=reg,
                    HEADER_ID=commercial_master.HEADER_ID,
                    EMIRATES_TRF_FILE_NO=reg.EMIRATES_TRF_FILE_NO,
                    REGISTERED_EMIRATES=reg.REGISTERED_EMIRATES,
                    FEDERAL_TRF_FILE_NO=reg.FEDERAL_TRF_FILE_NO,
                    REG_COMPANY_NAME=reg.REG_COMPANY_NAME,
                    TRADE_LICENSE_NO=reg.TRADE_LICENSE_NO,
                    REGISTRATION_NO1=reg.REGISTRATION_NO1,
                    REGISTRATION_NO=reg.REGISTRATION_NO,
                    REGISTRATION_DATE=reg.REGISTRATION_DATE,
                    REG_EXPIRY_DATE=reg.REG_EXPIRY_DATE,
                    CUR_STAT_REG=reg.CUR_STAT_REG,
                    FLEET_PROCESS=reg.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="Commercial"
                )
                
              

            
             # Handle Roadtoll
            
            
            roadtoll_tracked_fields = [
                'EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 
                'ACTIVATION_DATE', 'ACTIVATION_END_DATE', 'CURRENT_STATUS'
            ]
            
            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = XXGTD_ROAD_TOLL_INFO.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], commercial_master=commercial_master)
                    if road.FLEET_PROCESS != 'Approved':
                        road.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(road, roadtoll_item, roadtoll_tracked_fields, 'Roadtoll', current_user, commercial_master.HEADER_ID))
                else:
                    road = XXGTD_ROAD_TOLL_INFO(commercial_master=commercial_master, FLEET_PROCESS='Pending for Approval')
                    
                    for field in roadtoll_tracked_fields:
                        new_value = roadtoll_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Roadtoll',
                                'LINE_ID': 'new',
                                'HEADER_ID': commercial_master.HEADER_ID
                            })

                for field in roadtoll_tracked_fields:
                    value = roadtoll_item.get(field, '')
                    setattr(road, field, value if value != '' else None)

                road.COMM_CONTROL_NO = commercial_control_number
                road.HEADER_ID = header_id_num
                road.Process = 'Commercial' 
                commercial_master.STATUS = "Pending for Approval"
                
                
                
                        
                        
                
                file_key = f'RoadtollAttachments_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    road.RoadtollAttachments = handle_file_upload(
                        road.RoadtollAttachments,
                        files,
                        'media/documents/registration'
                    )
                    for file_path in json.loads(road.RoadtollAttachments):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='RoadtollInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )


                road.save()
                XXGTD_ROAD_TOLL_AUDIT.objects.create(
                    RT_LINE_ID=road,
                    HEADER_ID=commercial_master.HEADER_ID,
                    EMIRATES=road.EMIRATES,
                    TOLL_TYPE=road.TOLL_TYPE,
                    ACCOUNT_NO=road.ACCOUNT_NO,
                    TAG_NO=road.TAG_NO,
                    ACTIVATION_DATE=road.ACTIVATION_DATE,
                    ACTIVATION_END_DATE=road.ACTIVATION_END_DATE,
                    CURRENT_STATUS=road.CURRENT_STATUS,
                    FLEET_PROCESS=road.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="Commercial"
                    )

            # Handle Allocation
            allocation_tracked_fields = [
                'COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 
                'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE','ALLOCATION_END_DATE'
            ]
            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = XXGTD_ALLOCATION_INFO.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], commercial_master=commercial_master)
                    if allocations.FLEET_PROCESS != 'Approved':
                        allocations.FLEET_PROCESS = STATUS if is_approver else 'Pending for Approval'
                    
                    all_tracked_changes.extend(track_changes(allocations, allocation_item, allocation_tracked_fields, 'Allocation', current_user, commercial_master.HEADER_ID))
                else:
                    allocations = XXGTD_ALLOCATION_INFO(commercial_master=commercial_master, FLEET_PROCESS='Pending for Approval')
                    
                    for field in allocation_tracked_fields:
                        new_value = allocation_item.get(field)
                        if new_value is not None:
                            all_tracked_changes.append({
                                'COLUMN_NAME': field,
                                'ACTUAL_COLUMN_NAME': field,
                                'COLUMN_VALUE1': '',
                                'COLUMN_VALUE2': str(new_value),
                                'CREATED_BY': current_user,
                                'TABLE_NAME': 'Allocation',
                                'LINE_ID': 'new',
                                'HEADER_ID': commercial_master.HEADER_ID
                            })

                for field in allocation_tracked_fields:
                    value = allocation_item.get(field, '')
                    setattr(allocations, field, value if value != '' else None)

                allocations.COMM_CONTROL_NO = commercial_control_number
                allocations.HEADER_ID = header_id_num
                allocations.Process = 'Commercial' 
                commercial_master.STATUS = "Pending for Approval"
                
               
                
                file_key = f'attachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    allocations.attachment = handle_file_upload(
                        allocations.attachment,
                        files,
                        'media/documents/allocation'
                    )
                    for file_path in json.loads(allocations.attachment):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='AllocationInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID,
                            CommercialNumber=commercial_control_number
                        )

                allocations.save()
                XXGTD_ALLOCATION_AUDIT.objects.create(
                    ALLOC_LINE_ID=allocations,
                    HEADER_ID=commercial_master.HEADER_ID,
                    COMPANY_NAME=allocations.COMPANY_NAME,
                    DIVISION=allocations.DIVISION,
                    OPERATING_LOCATION=allocations.OPERATING_LOCATION,
                    OPERATING_EMIRATES=allocations.OPERATING_EMIRATES,
                    APPICATION_USAGE=allocations.APPICATION_USAGE,
                    ALLOCATION_DATE=allocations.ALLOCATION_DATE,
                    ALLOCATION_END_DATE=allocations.ALLOCATION_END_DATE,
                    FLEET_PROCESS=allocations.FLEET_PROCESS,
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                    PROCESS="Commercial"
                )

             
          
            
            
            if all_tracked_changes:
                move_to_history_and_cleanup(commercial_master.HEADER_ID, all_tracked_changes)
                
            # Update LINE_ID for new records
            
        
            for insurance_item in insurance_data:
                if insurance_item['INS_LINE_ID'] == 'new':
                    new_insurance = XXGTD_INSURANCE_INFO.objects.filter(
                        commercial_master=commercial_master,
                        HEADER_ID=commercial_master.HEADER_ID
                    ).latest('INS_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Insurance',
                        LINE_ID='new',
                        HEADER_ID=commercial_master.HEADER_ID
                    ).update(LINE_ID=str(new_insurance.INS_LINE_ID))

                if insurance_item['INS_LINE_ID'] == 'new':
                    insurance.CREATED_BY = username
                insurance.LAST_UPDATED_BY = username
                insurance.save()

            for reg_item in registration_data:
                if reg_item['REG_LINE_ID'] == 'new':
                    new_registration = XXGTD_REGISTRATION_INFO.objects.filter(
                        commercial_master=commercial_master,
                        HEADER_ID=commercial_master.HEADER_ID
                    ).latest('REG_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Registration',
                        LINE_ID='new',
                        HEADER_ID=commercial_master.HEADER_ID
                    ).update(LINE_ID=str(new_registration.REG_LINE_ID))

                if reg_item['REG_LINE_ID'] == 'new':
                    reg.CREATED_BY = username
                reg.LAST_UPDATED_BY = username
                reg.save()
                   
            for roadtoll_item in roadtoll_data:
                if roadtoll_item['RT_LINE_ID'] == 'new':
                    new_roadtoll = XXGTD_ROAD_TOLL_INFO.objects.filter(
                        commercial_master=commercial_master,
                        HEADER_ID=commercial_master.HEADER_ID
                    ).latest('RT_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Roadtoll',
                        LINE_ID='new',
                        HEADER_ID=commercial_master.HEADER_ID
                    ).update(LINE_ID=str(new_roadtoll.RT_LINE_ID))

                if roadtoll_item['RT_LINE_ID'] == 'new':
                    road.CREATED_BY = username
                road.LAST_UPDATED_BY = username
                road.save()
           
            for allocation_item in allocation_data:
                if allocation_item['ALLOC_LINE_ID'] == 'new':
                    new_allocation = XXGTD_ALLOCATION_INFO.objects.filter(
                        commercial_master=commercial_master,
                        HEADER_ID=commercial_master.HEADER_ID
                    ).latest('ALLOC_LINE_ID')
                    XXALY_GTD_DATA_COMPARE_T.objects.filter(
                        TABLE_NAME='Allocation',
                        LINE_ID='new',
                        HEADER_ID=commercial_master.HEADER_ID
                    ).update(LINE_ID=str(new_allocation.ALLOC_LINE_ID))

                if allocation_item['ALLOC_LINE_ID'] == 'new':
                    allocations.CREATED_BY = username
                allocations.LAST_UPDATED_BY = username
                allocations.save()
   


            ApprovalRequest.objects.update_or_create(
                request_number=commercial_master.COMM_CONTROL_NO,
                defaults={
                    'company_name': commercial_master.COMPANY_NAME,
                    'request_type': 'COMMERCIAL MASTER',
                    'status': commercial_master.STATUS,
                    'comments': commercial_master.COMMENTS,
                    'commercial_master': commercial_master,
                }
            )
            CommercialAttachment.objects.filter(commercial_master=commercial_master).update(CommercialNumber=commercial_control_number)

            action = "created" if created else "updated"

            current_user = request.user if request.user.is_authenticated else None
            if is_approver:
                commercial_master.STATUS = STATUS
            else:
                commercial_master.STATUS = STATUS or "Pending for Approval"

            insurances = commercial_master.insurances.all()
            registrations = commercial_master.registration.all()
            roadtolls = commercial_master.roadtoll.all()
            allocations = commercial_master.allocation.all()
            
            max_records = max(
                insurances.count(),
                registrations.count(),
                roadtolls.count(),
                allocations.count()
            )
            
            
             
            for i in range(max_records):
                insurance = insurances[i] if i < insurances.count() else None
                registration = registrations[i] if i < registrations.count() else None
                roadtoll = roadtolls[i] if i < roadtolls.count() else None
                allocation = allocations[i] if i < allocations.count() else None

                audit_entry = XXGTD_COMM_DETAIL_AUDIT.objects.create(
                    
                    
                    
                    
                    HEADER_ID=commercial_master.HEADER_ID,
                    COMM_PLATE_NO=commercial_master.COMM_PLATE_NO,
                    COMM_PLATE_DATE=commercial_master.COMM_PLATE_DATE,
                    COMM_PLATE_CATEGORY=commercial_master.COMM_PLATE_CATEGORY,
                    CP_ISSUED_AUTHORITY=commercial_master.CP_ISSUED_AUTHORITY,
                    CP_VEHICLE_TYPE=commercial_master.CP_VEHICLE_TYPE,
                    CP_COLOR=commercial_master.CP_COLOR,
                    STATUS=commercial_master.STATUS,
                   
                    
                    COMM_CONTROL_NO=commercial_master.COMM_CONTROL_NO,
                    
                    COMPANY_NAME=commercial_master.COMPANY_NAME,
                    COMMENTS=commercial_master.COMMENTS,
                    ACTION_CODE='C' if created else 'U',
                    ACTION='Created' if created else 'Updated',
                    CREATION_DATE=timezone.now(),
                    CREATED_BY=current_user.username if current_user else "System",
                    LAST_UPDATE_DATE=timezone.now(),
                    LAST_UPDATED_BY=current_user.username if current_user else "System",
                )

                if insurance:
                    audit_entry.INSURANCE_COMPANY = insurance.INSURANCE_COMPANY
                    audit_entry.POLICY_NO = insurance.POLICY_NO
                    audit_entry.POLICY_DATE = insurance.POLICY_DATE
                    audit_entry.POLICY_EXPIRY_DATE = insurance.POLICY_EXPIRY_DATE
                    audit_entry.PLTS_INS_START_DATE = insurance.PLTS_INS_START_DATE
                    audit_entry.POLICY_INSUR_EXPIRY_DATE = insurance.PLTS_INS_EXPIRY_DATE
                    audit_entry.INSUR_CURRENT_STATUS = insurance.CUR_STAT_MOT_INS
                    audit_entry.INS_LINE_ID = insurance

                if registration:
                    audit_entry.REGISTRATION_NO = registration.REGISTRATION_NO
                    
                    audit_entry.REGISTRATION_NO1 = registration.REGISTRATION_NO1
                    audit_entry.REGISTRATION_DATE = registration.REGISTRATION_DATE
                    audit_entry.REGISTERED_EMIRATES = registration.REGISTERED_EMIRATES
                    audit_entry.EMIRATES_TRF_FILE_NO = registration.EMIRATES_TRF_FILE_NO
                    audit_entry.FEDERAL_TRF_FILE_NO = registration.FEDERAL_TRF_FILE_NO
                    audit_entry.REG_EXPIRY_DATE = registration.REG_EXPIRY_DATE
                    audit_entry.REG_COMPANY_NAME = registration.REG_COMPANY_NAME
                    audit_entry.REGISTRATION_STATUS = registration.CUR_STAT_REG
                    audit_entry.TRADE_LICENSE_NO = registration.TRADE_LICENSE_NO
                    audit_entry.REG_LINE_ID = registration
                
                if roadtoll:
                    audit_entry.TOLL_EMIRATES = roadtoll.EMIRATES
                    audit_entry.TOLL_TYPE = roadtoll.TOLL_TYPE
                    audit_entry.ACCOUNT_NO = roadtoll.ACCOUNT_NO
                    audit_entry.TAG_NO = roadtoll.TAG_NO
                    audit_entry.ACTIVATION_DATE = roadtoll.ACTIVATION_DATE
                    audit_entry.ACTIVATION_END_DATE=roadtoll.ACTIVATION_END_DATE
                    audit_entry.TOLL_STATUS = roadtoll.CURRENT_STATUS
                    audit_entry.RT_LINE_ID = roadtoll    
                
                
                if allocation:
                    audit_entry.COMPANY_NAME = allocation.COMPANY_NAME
                    audit_entry.DIVISION = allocation.DIVISION
                    audit_entry.OPERATING_LOCATION = allocation.OPERATING_LOCATION
                    audit_entry.OPERATING_EMIRATES = allocation.OPERATING_EMIRATES
                    audit_entry.APPICATION_USAGE = allocation.APPICATION_USAGE
                    audit_entry.ALLOCATION_DATE = allocation.ALLOCATION_DATE
                    
                    
                    audit_entry.ALLOCATION_END_DATE = allocation.ALLOCATION_END_DATE
                    audit_entry.ALLOC_LINE_ID = allocation
                

                audit_entry.save()
                    
                    

            # Modify the status handling logic to ensure consistency
            display_status = STATUS or "Pending for Approval"
            if STATUS == "Draft":
                display_status = "Pending for Approval"

            # Update the XXALY_GTD_ACTION_HISTORY creation with the correct status
            XXALY_GTD_ACTION_HISTORY.objects.create(
                APPLICATION_ID=str(commercial_master.id),
                APPL_NUMBER=commercial_master.COMM_CONTROL_NO,
                REQUEST_TYPE="COMMERCIAL_MASTER",
                REQUEST_NUMBER=commercial_master.COMM_CONTROL_NO,
                PROCESS_STATUS=display_status,  # Use the corrected status
                DOC_STATUS=display_status,      # Use the corrected status
                RESPONSE_DATE=timezone.now(),
                RESPONDED_BY=current_user.username if current_user else "System",
                RESPONDER_ROLE=current_user.roles if current_user else "System",
                RESPONSE_COMMENTS=commercial_master.COMMENTS,
                ACTION_PERFORMED=f"Commercial Master {action}",
                CREATED_BY=current_user.username if current_user else "System",
                CREATION_DATE=timezone.now().date(),
                LAST_UPDATED_BY=current_user.username if current_user else "System",
                LAST_UPDATE_DATE=timezone.now().date(),
                NEXT_RESP="APPROVER" if current_user and current_user.roles == "REQUESTOR" else "REQUESTOR"
            )

            # Update commercial_master status
            if is_approver:
                commercial_master.STATUS = STATUS
            else:
                commercial_master.STATUS = display_status

            commercial_master.save()

            if STATUS == 'Approved':
                # Clear existing approved records for this HEADER_ID
                REVERT_COMMERCIAL_APPROVES.objects.filter(HEADER_ID=commercial_master.HEADER_ID).delete()

                # Store CommercialMaster data
                revert_data = {
                    'HEADER_ID': commercial_master.HEADER_ID,
                    'CM_LINE_ID': commercial_master.HEADER_ID,
                    'COMPANY_NAME': commercial_master.COMPANY_NAME,
                    'COMM_CONTROL_NO': commercial_master.COMM_CONTROL_NO,
                    'COMM_PLATE_NO': commercial_master.COMM_PLATE_NO,
                    'COMM_PLATE_DATE': commercial_master.COMM_PLATE_DATE,
                    'COMM_PLATE_CATEGORY': commercial_master.COMM_PLATE_CATEGORY,
                    'CP_ISSUED_AUTHORITY': commercial_master.CP_ISSUED_AUTHORITY,
                    'CP_VEHICLE_TYPE': commercial_master.CP_VEHICLE_TYPE,
                    'CP_COLOR': commercial_master.CP_COLOR,
                    'STATUS': commercial_master.STATUS,
                }
                REVERT_COMMERCIAL_APPROVES.objects.create(**revert_data)

                # Store Insurance data
                for insurance in commercial_master.insurances.all():
                    revert_data = {
                        'HEADER_ID': commercial_master.HEADER_ID,
                        'INS_LINE_ID': insurance.INS_LINE_ID,
                        'INSURANCE_COMPANY': insurance.INSURANCE_COMPANY,
                        'POLICY_NO': insurance.POLICY_NO,
                        'POLICY_DATE': insurance.POLICY_DATE,
                        'POLICY_EXPIRY_DATE': insurance.POLICY_EXPIRY_DATE,
                        'PLTS_INS_START_DATE': insurance.PLTS_INS_START_DATE,
                        'PLTS_INS_EXPIRY_DATE': insurance.PLTS_INS_EXPIRY_DATE,
                        'CUR_STAT_MOT_INS': insurance.CUR_STAT_MOT_INS,
                    }
                    REVERT_COMMERCIAL_APPROVES.objects.create(**revert_data)

                # Store Registration data
                for registration in commercial_master.registration.all():
                    revert_data = {
                        'HEADER_ID': commercial_master.HEADER_ID,
                        'REG_LINE_ID': registration.REG_LINE_ID,
                        'EMIRATES_TRF_FILE_NO': registration.EMIRATES_TRF_FILE_NO,
                        'REGISTERED_EMIRATES': registration.REGISTERED_EMIRATES,
                        'FEDERAL_TRF_FILE_NO': registration.FEDERAL_TRF_FILE_NO,
                        'REG_COMPANY_NAME': registration.REG_COMPANY_NAME,
                        'TRADE_LICENSE_NO': registration.TRADE_LICENSE_NO,
                        'REGISTRATION_NO1': registration.REGISTRATION_NO1,
                        'REGISTRATION_NO': registration.REGISTRATION_NO,
                        'REGISTRATION_DATE': registration.REGISTRATION_DATE,
                        'REG_EXPIRY_DATE': registration.REG_EXPIRY_DATE,
                        'CUR_STAT_REG': registration.CUR_STAT_REG,
                    }
                    REVERT_COMMERCIAL_APPROVES.objects.create(**revert_data)

                # Store Roadtoll data
                for roadtoll in commercial_master.roadtoll.all():
                    revert_data = {
                        'HEADER_ID': commercial_master.HEADER_ID,
                        'RT_LINE_ID': roadtoll.RT_LINE_ID,
                        'EMIRATES': roadtoll.EMIRATES,
                        'TOLL_TYPE': roadtoll.TOLL_TYPE,
                        'ACCOUNT_NO': roadtoll.ACCOUNT_NO,
                        'TAG_NO': roadtoll.TAG_NO,
                        'ACTIVATION_DATE': roadtoll.ACTIVATION_DATE,
                        'ACTIVATION_END_DATE': roadtoll.ACTIVATION_END_DATE,
                        'CURRENT_STATUS': roadtoll.CURRENT_STATUS,
                    }
                    REVERT_COMMERCIAL_APPROVES.objects.create(**revert_data)

                # Store Allocation data
                for allocation in commercial_master.allocation.all():
                    revert_data = {
                        'HEADER_ID': commercial_master.HEADER_ID,
                        'ALLOC_LINE_ID': allocation.ALLOC_LINE_ID,
                        'COMPANY_NAME': allocation.COMPANY_NAME,
                        'DIVISION': allocation.DIVISION,
                        'OPERATING_LOCATION': allocation.OPERATING_LOCATION,
                        'OPERATING_EMIRATES': allocation.OPERATING_EMIRATES,
                        'APPICATION_USAGE': allocation.APPICATION_USAGE,
                        'ALLOCATION_DATE': allocation.ALLOCATION_DATE,
                        'ALLOCATION_END_DATE': allocation.ALLOCATION_END_DATE,
                    }
                    REVERT_COMMERCIAL_APPROVES.objects.create(**revert_data)



            return {
                "message": "Commercial Master and related records created/updated successfully",
                "commercial_master": CommercialMasterSchema.from_orm(commercial_master)
                
            }

    except Exception as e:
        return {"message": f"Error occurred:{str(e)}"}



@api.get("/revert-commercial-data/{header_id}")
def revert_commercial_data(request, header_id: str):
    try:
        with transaction.atomic():
            approved_records = REVERT_COMMERCIAL_APPROVES.objects.filter(HEADER_ID=header_id)

            if not approved_records.exists():
                return JsonResponse({"message": "No approved data found for this HEADER_ID"}, status=400)

            commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.get(HEADER_ID=header_id)
            main_record = approved_records.filter(CM_LINE_ID=header_id).first()

            if main_record:
                update_fields = [field.name for field in XXGTD_COMMERCIAL_PLATE_INFO._meta.fields 
                                 if field.name not in ['COMM_CONTROL_NO', 'id'] and hasattr(main_record, field.name)]
                for field in update_fields:
                    setattr(commercial_master, field, getattr(main_record, field))
                commercial_master.save(update_fields=update_fields)

            for model, prefix in [
                (XXGTD_INSURANCE_INFO, 'INS'),
                (XXGTD_REGISTRATION_INFO, 'REG'),
                (XXGTD_ROAD_TOLL_INFO, 'RT'),
                (XXGTD_ALLOCATION_INFO, 'ALLOC')
            ]:
                child_records = approved_records.filter(**{f'{prefix}_LINE_ID__isnull': False})
                for approved_record in child_records:
                    line_id = getattr(approved_record, f'{prefix}_LINE_ID')
                    update_data = {field.name: getattr(approved_record, field.name)
                                   for field in model._meta.fields
                                   if hasattr(approved_record, field.name) and field.name not in ['commercial_master', 'id']}
                    model.objects.update_or_create(
                        commercial_master=commercial_master,
                        **{f'{prefix}_LINE_ID': line_id},
                        defaults=update_data
                    )

            return JsonResponse({"message": "Data reverted successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)





class CommercialMasterSchema(Schema):
    COMPANY_NAME: Optional[str] = None
    COMM_CONTROL_NO: Optional[str] = None
    COMM_PLATE_DATE: Optional[date] = None
    COMM_PLATE_NO: Optional[str] = None
    COMM_PLATE_CATEGORY: Optional[str] = None
    CP_ISSUED_AUTHORITY: Optional[str] = None
    CP_VEHICLE_TYPE: Optional[str] = None
    CP_COLOR: Optional[str] = None
    COMMENTS: Optional[str] = None
    HEADER_ID: Optional[str] = None
    STATUS: Optional[str] = "Pending for Approval"
    CREATED_BY: Optional[str] = None
    LAST_UPDATED_BY: Optional[str] = None

class CommercialMasterResponse(Schema):
    message: str
    commercial_master: Optional[CommercialMasterSchema] = None
@api.post("/commercial-master/save", response=CommercialMasterResponse)
def create_or_update_commercial_master(
    request,
    COMPANY_NAME:Optional[str] = Form(None),
    HEADER_ID: Optional[str] = Form(None),
    COMM_PLATE_NO: Optional[str] = Form(None),
    COMM_PLATE_DATE: Optional[date] = Form(None),
    COMM_PLATE_CATEGORY: Optional[str] =  Form(None),
    CP_ISSUED_AUTHORITY: Optional[str] =  Form(None),
    CP_VEHICLE_TYPE: Optional[str] = Form(None),
    CP_COLOR: Optional[str] =  Form(None),
    COMMENTS: Optional[str] = Form(None),
    
    insurances: Optional[str] = Form(None),
    registration: Optional[str] = Form(None),
    roadtoll: Optional[str] = Form(None),
    allocation: Optional[str] = Form(None),
    InsurancePolicAattachment: Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    
    RegCardAttachment:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    RoadtollAttachments:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    AllocationAttachment:  Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),


):
    try:
        with transaction.atomic():
            if HEADER_ID:
                commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.get(HEADER_ID=HEADER_ID)
                created = False
            else:
                commercial_master = XXGTD_COMMERCIAL_PLATE_INFO()
                created = True


            current_user = request.user if request.user.is_authenticated else None
            username = current_user.username if current_user else "System"
            if created:
                commercial_master.CREATED_BY = username
            commercial_master.LAST_UPDATED_BY = username

            commercial_master_data = {
                key: value for key, value in {
                    "COMPANY_NAME": COMPANY_NAME,
                    "COMM_PLATE_NO": COMM_PLATE_NO,
                    "COMM_PLATE_DATE": COMM_PLATE_DATE,
                    "COMM_PLATE_CATEGORY": COMM_PLATE_CATEGORY,
                    "CP_ISSUED_AUTHORITY": CP_ISSUED_AUTHORITY,
                    "CP_VEHICLE_TYPE": CP_VEHICLE_TYPE,
                    "CP_COLOR": CP_COLOR,
                    "COMMENTS": COMMENTS,
                    "STATUS": "Draft",
                    "HEADER_ID": HEADER_ID,
                    "CREATED_BY": username if created else None,
                    "LAST_UPDATED_BY": username,
                }.items() if value is not None
            }
            
            
            

            if not any(commercial_master_data.values()):
                return {"message": "At least one field is required to save the commercial master."}
            for key, value in commercial_master_data.items():
                setattr(commercial_master, key, value)
            commercial_master.save(generate_commercial_control_number=False)
                        
            HEADER_ID = commercial_master.HEADER_ID

            def handle_file_upload(existing_files, new_files, file_path_prefix):
                existing_files = json.loads(existing_files) if existing_files else []
                existing_base_names = set(re.sub(r'_[^_]+(?=\.[^.]+$)', '', os.path.basename(file)) for file in existing_files)
                new_file_paths = []

                for file in new_files:
                    base_name = re.sub(r'_[^_]+(?=\.[^.]+$)', '', file.name)
                    if base_name not in existing_base_names:
                        file_path = default_storage.save(f'{file_path_prefix}/{file.name}', ContentFile(file.read()))
                        new_file_paths.append(file_path)
                        existing_base_names.add(base_name)

                all_files = existing_files + new_file_paths
                return json.dumps(all_files)
            
            

            if insurances:
                insurance_data = json.loads(insurances)
                for index, insurance_item in enumerate(insurance_data):
                    if insurance_item['INS_LINE_ID'] != 'new':
                        insurance = XXGTD_INSURANCE_INFO.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], commercial_master=commercial_master)
                    else:
                        insurance = XXGTD_INSURANCE_INFO(commercial_master=commercial_master)

                    for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                                  'PLTS_INS_START_DATE', 'PLTS_INS_EXPIRY_DATE', 'CUR_STAT_MOT_INS']:
                        setattr(insurance, field, insurance_item.get(field))
                    
                    insurance.HEADER_ID = commercial_master.HEADER_ID
                    insurance.Process="Commercial"

                    file_key = f'InsurancePolicAattachment_{index}'
                    if file_key in request.FILES:
                        files = request.FILES.getlist(file_key)
                        insurance.InsurancePolicAattachment = handle_file_upload(
                            insurance.InsurancePolicAattachment,
                            files,
                            'media/documents/insurance'
                        )
                        for file_path in json.loads(insurance.InsurancePolicAattachment):
                            CommercialAttachment.objects.get_or_create(
                                file=file_path,
                                attachment_type='InsuranceInfo',
                                commercial_master=commercial_master,
                                HEADER_ID=commercial_master.HEADER_ID
                            )

                    insurance.save()




            registration_data = json.loads(registration)if registration else []
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    reg = XXGTD_REGISTRATION_INFO.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], commercial_master=commercial_master)
                else:
                    reg = XXGTD_REGISTRATION_INFO(commercial_master=commercial_master)

                for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.HEADER_ID = HEADER_ID
                reg.Process="Commercial"

                


                file_key = f'RegCardAttachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    reg.RegCardAttachment = handle_file_upload(
                        reg.RegCardAttachment,
                        files,
                        'media/documents/registration'
                    )
                    for file_path in json.loads(reg.RegCardAttachment):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='RegistrationInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                reg.save()

            roadtoll_data = json.loads(roadtoll) if roadtoll else []
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = XXGTD_ROAD_TOLL_INFO.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], commercial_master=commercial_master)
                else:
                    road = XXGTD_ROAD_TOLL_INFO(commercial_master=commercial_master)

                for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE','ACTIVATION_END_DATE', 'CURRENT_STATUS']:
                    setattr(road, field, roadtoll_item.get(field))

                road.HEADER_ID = HEADER_ID
                road.Process="Commercial"
                file_key = f'RoadtollAttachments_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    road.RoadtollAttachments = handle_file_upload(
                        road.RoadtollAttachments,
                        files,
                        'media/documents/registration'
                    )
                    for file_path in json.loads(road.RoadtollAttachments):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='RoadtollInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                

                road.save()


            allocation_data = json.loads(allocation) if allocation else []
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = XXGTD_ALLOCATION_INFO.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], commercial_master=commercial_master)
                else:
                    allocations = XXGTD_ALLOCATION_INFO(commercial_master=commercial_master)

                for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE','ALLOCATION_END_DATE']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.HEADER_ID = HEADER_ID

                allocations.Process="Commercial"

                file_key = f'attachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    allocations.attachment = handle_file_upload(
                        allocations.attachment,
                        files,
                        'media/documents/allocation'
                    )
                    for file_path in json.loads(allocations.attachment):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='AllocationInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )


                file_key = f'attachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    allocations.attachment = handle_file_upload(
                        allocations.attachment,
                        files,
                        'media/documents/allocation'
                    )
                    for file_path in json.loads(allocations.attachment):
                        CommercialAttachment.objects.get_or_create(
                            file=file_path,
                            attachment_type='AllocationInfo',
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                allocations.save()

          

            action = "created" if created else "updated"
            return {
                "message": f"Commercial Master {'created' if created else 'updated'} successfully",
                "commercial_master": CommercialMasterSchema.from_orm(commercial_master)
            }
                            

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}




class CommercialMasterDetailSchema(CommercialMasterSchema):
    insurances: List[InsuranceSchema]
    registration: List[RegistrationSchema]
    roadtoll:List[RoadtollSchema]
    allocation:List[AllocationSchema]

@api.get("/commercial-master/{identifier}", response=CommercialMasterDetailSchema)
def get_commercial_master(request, identifier: str):
    try:
        # Try to fetch by COMMERCIAL_CONTROL_NO first
        commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.prefetch_related(
            'insurances','registration','roadtoll','allocation'
        ).get(COMM_CONTROL_NO=identifier)
    except XXGTD_COMMERCIAL_PLATE_INFO.DoesNotExist:
        try:
            # If not found, try to fetch by header_id
            commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.prefetch_related(
                'insurances','registration', 'roadtoll','allocation'
            ).get(HEADER_ID=identifier)
        except XXGTD_COMMERCIAL_PLATE_INFO.DoesNotExist:
            return JsonResponse({"error": f"CommercialMaster with identifier {identifier} does not exist"}, status=404)

    return CommercialMasterDetailSchema.from_orm(commercial_master)


@api.get("/commercial-master-by-header/{HEADER_ID}", response=CommercialMasterDetailSchema)
def get_commercial_master_by_header(request, HEADER_ID: str):
    try:
        commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.prefetch_related(
            'insurances', 'registration',
            'roadtoll', 'allocation'
        ).get(HEADER_ID=HEADER_ID)
        return CommercialMasterDetailSchema.from_orm(commercial_master)
    except XXGTD_COMMERCIAL_PLATE_INFO.DoesNotExist:
        return JsonResponse({"error": f"CommercialMaster with header_id {HEADER_ID} does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    


class CommercialInfoSchema(Schema):
    HEADER_ID: Optional[str] = None
    COMM_CONTROL_NO: Optional[str] = None
    COMM_PLATE_DATE: Optional[date] = None
    COMM_PLATE_NO: Optional[str] = None
    COMM_PLATE_CATEGORY: Optional[str] = None
    CP_ISSUED_AUTHORITY: Optional[str] = None
    CP_VEHICLE_TYPE: Optional[str] = None
    CP_COLOR: Optional[str] = None
    STATUS: Optional[str] = None
    

@api.get("/commercial-info", response=List[CommercialInfoSchema])
def get_commercial_info(request):
    
    commercial_info = XXGTD_COMMERCIAL_PLATE_INFO.objects.annotate(
        
    ).values(
        'HEADER_ID',
        'COMM_CONTROL_NO',
        'COMM_PLATE_DATE',
        'COMM_PLATE_NO',
        'COMM_PLATE_CATEGORY',
        'CP_ISSUED_AUTHORITY',
        'CP_VEHICLE_TYPE',
        'CP_COLOR',
        'STATUS',
       
   )
    
    return list(commercial_info)


@api.get("/commercial-control-numbers", response=List[str])
def get_commercial_control_numbers(request):
    commercial_control_number = XXGTD_COMMERCIAL_PLATE_INFO.objects.values_list('CommercialControlNumber', flat=True)
    return list(commercial_control_number)


# class AttachmentSchema(Schema):
#     id: int
#     file: Union[str,Any]
#     attachment_type: str
#     CommercialNumber:str
#     upload_date:date
#     uploaded_by: Optional[str] = None

# @api.get("/commercial-attachments/{commercial_number}", response=List[AttachmentSchema])
# def get_attachments(request, commercial_number: str):
#     attachments = AttachmentSchema.objects.filter(CommercialNumber=commercial_number)
#     return [
       
#         AttachmentSchema(
#             id=attachment.id,
#             file=str(attachment.file),
#             attachment_type=attachment.attachment_type,
#             FleetNumber=attachment.FleetNumber,
#             upload_date=attachment.upload_date.date(),
#             uploaded_by=attachment.uploaded_by
#         )
#         for attachment in attachments
#     ]


# class AttachmentSchema(Schema):
#     id: int
#     file: Union[str,Any]
#     attachment_type: str
#     CommercialNumber:str
#     upload_date:date
#     uploaded_by: Optional[str] = None



# @api.get("/commercial-attachments", response=List[AttachmentSchema])
# def get_attachments(request):
#     attachments = AttachmentSchema.objects.all()
#     return [AttachmentSchema.from_orm(attachment) for attachment in attachments]


class ComAttachmentSchema(Schema):
    id: int
    file: Union[str, Any]
    attachment_type: str
    CommercialNumber: Optional[str] = None
    upload_date: date
    uploaded_by: Optional[str] = None


@api.get("/commercial-attachments/{commercial_number}", response=List[ComAttachmentSchema])
def get_attachments(request, commercial_number: str):
    attachments = CommercialAttachment.objects.filter(CommercialNumber=commercial_number)
    return [
        ComAttachmentSchema(
            id=attachment.id,
            file=str(attachment.file),
            attachment_type=attachment.attachment_type,
            CommercialNumber=attachment.CommercialNumber or None,
            upload_date=attachment.upload_date.date(),
            uploaded_by=attachment.uploaded_by
        )
        for attachment in attachments
    ]

@api.get("/commercial-attachments", response=List[ComAttachmentSchema])
def get_attachments(request):
    attachments = CommercialAttachment.objects.all()
    return [
        ComAttachmentSchema(
            id=attachment.id,
            file=str(attachment.file),
            attachment_type=attachment.attachment_type,
            CommercialNumber=attachment.CommercialNumber or None,
            upload_date=attachment.upload_date.date(),
            uploaded_by=attachment.uploaded_by
        )
        for attachment in attachments
    ]


@api.get("/unique-commercial-numbers", response=List[str])
def get_unique_commercial_numbers(request):
    unique_commercial_numbers = CommercialAttachment.objects.values_list('COMM_CONTROL_NO', flat=True).distinct()
    return list(filter(None, unique_commercial_numbers))



@api.get("/commercial-master/{commercial_control_number}", response=CommercialMasterDetailSchema)
def get_commercial_master_detail(request, commercial_control_number: str):
    commercial_master = XXGTD_COMMERCIAL_PLATE_INFO.objects.prefetch_related('insurances','registration','roadtoll','allocation').get(CommercialControlNumber=commercial_control_number)
    return CommercialMasterDetailSchema.from_orm(commercial_master)







from django.db.models import Q

@api.get("/approval-requests", response=List[Dict])
def get_approval_requests(request):
    fleet_requests = XXGTD_VEHICLE_INFO.objects.filter(
        Q(FLEET_CONTROL_NO__startswith='AY-') | Q(FLEET_CONTROL_NO__startswith='ALY')
    ).exclude(
        FLEET_CONTROL_NO=''
    ).order_by('FLEET_CONTROL_NO').values(
        'FLEET_CONTROL_NO', 'COMPANY_NAME', 'STATUS', 'FLEET_CREATION_DATE', 'COMMENTS'
    )

    commercial_requests = XXGTD_COMMERCIAL_PLATE_INFO.objects.filter(
    Q(COMM_CONTROL_NO__startswith='AY-') | Q(COMM_CONTROL_NO__startswith='ALY')
    ).exclude(
        COMM_CONTROL_NO=''
    ).order_by('COMM_CONTROL_NO').values(
        'COMM_CONTROL_NO', 'COMPANY_NAME', 'STATUS', 'COMM_PLATE_DATE', 'COMMENTS'
    )
    traffic_requests = XXGTD_TRAFFIC_FILE_MASTER.objects.exclude(
        TRAFFIC_FILE_NO=''
    ).order_by('TRAFFIC_FILE_NO').values(
        'TRAFFIC_FILE_NO', 'COMPANY_NAME', 'STATUS', 'CREATION_DATE', 'LAST_UPDATE_DATE', 'COMMENTS'
    )


    combined_requests = []

    for fr in fleet_requests:
        combined_requests.append({
            'request_number': fr['FLEET_CONTROL_NO'],
            'company_name': fr['COMPANY_NAME'],
            'request_type': 'Fleet Master',
            'request_details': 'Modified',
            'status': fr['STATUS'],
            'creation_date': fr['FLEET_CREATION_DATE'],
            'last_update_date': fr['FLEET_CREATION_DATE'],
            'comments': fr['COMMENTS']
        })

    for cr in commercial_requests:
        combined_requests.append({
            'request_number': cr['COMM_CONTROL_NO'],
            'company_name': cr['COMPANY_NAME'],
            'request_type': 'Commercial Master',
            'request_details': 'Modified',
            'status': cr['STATUS'],
            'creation_date': cr['COMM_PLATE_DATE'],
            'last_update_date': cr['COMM_PLATE_DATE'],
            'comments': cr['COMMENTS']
        })

    for tr in traffic_requests:
        combined_requests.append({
            'request_number': tr['TRAFFIC_FILE_NO'],
            'company_name': tr['COMPANY_NAME'],
            'request_type': 'Traffic File Master',
            'request_details': 'Modified',
            'status': tr['STATUS'],
            'creation_date': tr['CREATION_DATE'],
            'last_update_date': tr['LAST_UPDATE_DATE'],
            'comments': tr['COMMENTS']
        })

    return combined_requests






import logging

logger = logging.getLogger(__name__)

class ActionHistorySchema(Schema):
    APPLICATION_ID: Optional[str]
    APPL_NUMBER: Optional[str]
    REQUEST_TYPE: Optional[str]
    REQUEST_NUMBER: Optional[str]
    PROCESS_STATUS: Optional[str]
    DOC_STATUS: Optional[str]
    RESPONSE_DATE: Optional[date]
    RESPONDED_BY: Optional[str]
    RESPONDER_ROLE: Optional[str]
    RESPONSE_COMMENTS: Optional[str]
    ACTION_PERFORMED: Optional[str]
    ERROR_MISTAKE_FLAG: Optional[str]
    NEED_INFO_FLAG: Optional[str]
    NEXT_RESP: Optional[str]
    ATTRIBUTE_CATEGORY: Optional[str]
    ATTRIBUTE1: Optional[str]
    ATTRIBUTE2: Optional[str]
    ATTRIBUTE3: Optional[str]
    ATTRIBUTE4: Optional[str]
    ATTRIBUTE5: Optional[str]
    CREATED_BY: Optional[str]
    CREATION_DATE: Optional[date]
    LAST_UPDATED_BY: Optional[str]
    LAST_UPDATE_DATE: Optional[date]

class ActionHistoryResponse(Schema):
    count: int
    results: List[ActionHistorySchema]

@api.get("/action-history/{fleet_control_number}", response=ActionHistoryResponse)
def get_action_history(request, fleet_control_number: str):
    try:
        queryset = XXALY_GTD_ACTION_HISTORY.objects.filter(
            Q(APPL_NUMBER=fleet_control_number) | Q(REQUEST_NUMBER=fleet_control_number)
        ).order_by('-CREATION_DATE')

        action_history = list(queryset.values())

        # Convert date objects to strings
        for item in action_history:
            for field in ['RESPONSE_DATE', 'CREATION_DATE', 'LAST_UPDATE_DATE']:
                if isinstance(item.get(field), date):
                    item[field] = item[field].isoformat()

        if not action_history:
            logger.info(f"No action history found for fleet control number: {fleet_control_number}")
            return {"count": 0, "results": []}

        return {
            "count": len(action_history),
            "results": action_history
        }

    except ValidationError as e:
        logger.error(f"Validation error for fleet control number {fleet_control_number}: {str(e)}")
        return {"count": 0, "results": [], "error": "Invalid input data"}
    except Exception as e:
        logger.error(f"Error retrieving action history for fleet control number {fleet_control_number}: {str(e)}")
        return {"count": 0, "results": [], "error": "An unexpected error occurred"}
    


from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from typing import Optional
import json



# @api.post("/send-email")
# def send_email(
#     request,
#     recipient: str = Form(...),
#     cc: str = Form(None),
#     bcc: str = Form(None),
#     subject: str = Form(...),
#     data: str = Form(...),
#     custom_message: str = Form(None),
#     attachment: Optional[UploadedFile] = File(None)
# ):
#     try:
#         # Parse cc and bcc
#         cc_list = [email.strip() for email in cc.split(',')] if cc else []
#         bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

#         # Parse data
#         data_dict = json.loads(data)

#         # Add custom_message to data_dict if provided
#         if custom_message:
#             data_dict['custom_message'] = custom_message

#         # Render the HTML template
#         html_message = render_to_string('ALY_GTD/email_template.html', {'data': data_dict})

#         text_message = strip_tags(html_message)

#         # Create the email message
#         email = EmailMultiAlternatives(
#             subject,
#             text_message,
#             settings.EMAIL_HOST_USER,
#             [recipient],
#             cc=cc_list,
#             bcc=bcc_list
#         )
       
#         # Attach the HTML version
#         email.attach_alternative(html_message, "text/html")

#         if attachment:
#             email.attach(
#                 attachment.name,
#                 attachment.read(),
#                 attachment.content_type
#             )
       
#         email.send(fail_silently=False)
#         return {"status": "success", "message": "Email sent successfully"}
#     except json.JSONDecodeError:
#         return {"status": "error", "message": "Invalid JSON in data field"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}


        



@api.get("/action-history/{control_number}", response=ActionHistoryResponse)
def get_action_history(request, control_number: str):
    try:
        queryset = XXALY_GTD_ACTION_HISTORY.objects.filter(
            Q(APPL_NUMBER=control_number) | 
            Q(REQUEST_NUMBER=control_number) |
            Q(ATTRIBUTE1=control_number) |  # Assuming ATTRIBUTE1 stores the commercial control number
            Q(ATTRIBUTE2=control_number)    # Assuming ATTRIBUTE2 stores the fleet control number
        ).order_by('-CREATION_DATE')

        action_history = list(queryset.values())

        # Convert date objects to strings
        for item in action_history:
            for field in ['RESPONSE_DATE', 'CREATION_DATE', 'LAST_UPDATE_DATE']:
                if isinstance(item.get(field), date):
                    item[field] = item[field].isoformat()

        if not action_history:
            logger.info(f"No action history found for control number: {control_number}")
            return {"count": 0, "results": []}

        return {
            "count": len(action_history),
            "results": action_history
        }

    except ValidationError as e:
        logger.error(f"Validation error for control number {control_number}: {str(e)}")
        return {"count": 0, "results": [], "error": "Invalid input data"}
    except Exception as e:
        logger.error(f"Error retrieving action history for control number {control_number}: {str(e)}")
        return {"count": 0, "results": [], "error": "An unexpected error occurred"}
    
    
    
# class InsuranceInfoSchema(BaseModel):
#     INSURANCE_COMPANY: Optional[str] = None
#     POLICY_NO: Optional[str] = None
#     POLICY_DATE: Optional[date] = None
#     POLICY_EXPIRY_DATE: Optional[date] = None

# @api.get("/insurance-info", response=List[InsuranceInfoSchema])
# def get_insurance_info(request):
#     insurance_info = Insurance.objects.values(
#         'INSURANCE_COMPANY',
#         'POLICY_NO',
#         'POLICY_DATE',
#         'POLICY_EXPIRY_DATE'
#     ).distinct()

#     # Convert date objects to strings
#     for info in insurance_info:
#         if info['POLICY_DATE']:
#             info['POLICY_DATE'] = info['POLICY_DATE'].isoformat()
#         if info['POLICY_EXPIRY_DATE']:
#             info['POLICY_EXPIRY_DATE'] = info['POLICY_EXPIRY_DATE'].isoformat()

#     return list(insurance_info)



# from ninja import Path

# class CompanyDetailsSchema(BaseModel):
#     INSURANCE_COMPANY: str
#     POLICY_NO: str
#     POLICY_DATE: Optional[date]
#     POLICY_EXPIRY_DATE: Optional[date]
#     # Add any other relevant fields you want to include

# @api.get("/company-details/{company_name}", response=List[CompanyDetailsSchema])
# def get_company_details(request, company_name: str = Path(...)):
#     company_details = Insurance.objects.filter(INSURANCE_COMPANY=company_name).values(
#         'INSURANCE_COMPANY',
#         'POLICY_NO',
#         'POLICY_DATE',
#         'POLICY_EXPIRY_DATE'
#         # Add any other fields you want to include
#     ).distinct()

#     # Convert date objects to strings
#     for detail in company_details:
#         if detail['POLICY_DATE']:
#             detail['POLICY_DATE'] = detail['POLICY_DATE'].isoformat()
#         if detail['POLICY_EXPIRY_DATE']:
#             detail['POLICY_EXPIRY_DATE'] = detail['POLICY_EXPIRY_DATE'].isoformat()

#     return list(company_details)
class InsuranceInfoSchema(Schema):
    INSURANCE_COMPANY: str = None
    POLICY_NO: str = None
    POLICY_DATE: date = None
    POLICY_EXPIRY_DATE: date = None
@api.get("/insurance-info", response=List[InsuranceInfoSchema])
def get_insurance_info(request):
    insurance_info = XXGTD_INSURANCE_INFO.objects.values(
        'INSURANCE_COMPANY',
        'POLICY_NO',
        'POLICY_DATE',
        'POLICY_EXPIRY_DATE'
    ).order_by('INSURANCE_COMPANY').distinct('INSURANCE_COMPANY')

    # Convert date objects to strings
    for info in insurance_info:
        if info['POLICY_DATE']:
            info['POLICY_DATE'] = info['POLICY_DATE'].isoformat()
        if info['POLICY_EXPIRY_DATE']:
            info['POLICY_EXPIRY_DATE'] = info['POLICY_EXPIRY_DATE'].isoformat()

    return list(insurance_info)





class CompareDataSchema(Schema):
    column_name: str
    column_value1: str
    column_value2: str

@api.get("/compare-data/{header_id}", response=List[CompareDataSchema])
def get_compare_data(request, header_id: str):
    compare_data = XXALY_GTD_DATA_COMPARE_T.objects.filter(HEADER_ID=header_id)
    
    result = []
    for data in compare_data:
        result.append({
            "column_name": data.COLUMN_NAME,
            "column_value1": data.COLUMN_VALUE1,
            "column_value2": data.COLUMN_VALUE2
        })
    
    return result


# @api.post("/send-email")
# def send_email(
#     request,
#     recipient: str = Form(...),
#     cc: str = Form(None),
#     bcc: str = Form(None),
#     subject: str = Form(...),
#     data: str = Form(...),
#     custom_message: str = Form(None),
#     comparison_data: str = Form(None),
#     is_new_submission: bool = Form(False),
#     attachment: Optional[UploadedFile] = File(None)
# ):
#     try:
#         cc_list = [email.strip() for email in cc.split(',')] if cc else []
#         bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

#         data_dict = json.loads(data)
#         if custom_message:
#             data_dict['custom_message'] = custom_message

#         context = {
#             'data': data_dict,
#             'is_new_submission': is_new_submission,
#             'comparison_data': json.loads(comparison_data) if comparison_data else None
#         }

#         html_message = render_to_string('ALY_GTD/email_template.html', context)
#         text_message = strip_tags(html_message)

#         email = EmailMultiAlternatives(
#             subject,
#             text_message,
#             settings.EMAIL_HOST_USER,
#             [recipient],
#             cc=cc_list,
#             bcc=bcc_list
#         )
        
#         email.attach_alternative(html_message, "text/html")

#         if attachment:
#             email.attach(
#                 attachment.name,
#                 attachment.read(),
#                 attachment.content_type
#             )
        
#         email.send(fail_silently=False)
#         return {"status": "success", "message": "Email sent successfully"}
#     except json.JSONDecodeError:
#         return {"status": "error", "message": "Invalid JSON in data field"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

def parse_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 'yes', 'on')


import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ninja import Form, File
from ninja.files import UploadedFile
from typing import Optional

@api.post("/send-email")
def send_email(
    request,
    recipient: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(...),
    data: str = Form(...),
    custom_message: str = Form(None),
    comparison_data: str = Form(None),
    is_new_submission: bool = Form(False),
    
    is_approver_action: bool = Form(default=False, description="Is this an approver action?", alias="is_approver_action"),
    action: str = Form(None),
    attachment: Optional[UploadedFile] = File(None)
):
    try:
        
        print(f"Sending email to: {recipient}")
        print(f"CC: {cc}")
        print(f"BCC: {bcc}")
        print(f"Subject: {subject}")
        print(f"Data: {data}")
        print(f"Is approver action: {is_approver_action}")
        print(f"Action: {action}")
        print(f"Is new submission: {is_new_submission}")

        cc_list = [email.strip() for email in cc.split(',')] if cc else []
        bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

        data_dict = json.loads(data)
        current_status = data_dict.get('STATUS') or data_dict.get('fleet_master', {}).get('STATUS', 'N/A')
        data_dict['STATUS'] = current_status
        data_dict['CREATION_DATE'] = data_dict.get('FLEET_CREATION_DATE', data_dict.get('CREATION_DATE', 'N/A'))
        data_dict['LAST_UPDATE_DATE'] = datetime.now().strftime('%Y-%m-%d')
        data_dict['LAST_UPDATED_BY'] = request.user.username  # Assuming you have access to the current user

        
        print(f"Creation Date being sent to template: {data_dict.get('CREATION_DATE', 'Not found')}")
        print(f"LAST_UPDATE_DATE being sent to template: {data_dict.get('LAST_UPDATE_DATE', 'Not found')}")
        print(f"LAST_UPDATED_BY being sent to template: {data_dict.get('LAST_UPDATED_BY', 'Not found')}")
        print(f"Current Status: {current_status}")
        print(f"Updated Subject: {subject}")
 
        
        if custom_message:
            data_dict['custom_message'] = custom_message

        fleet_control_no = data_dict.get('FLEET_CONTROL_NO', '')
        fleet_master_url = f"http://127.0.0.1:8000/ALY_GTD/fleet_master/?fleet_number={fleet_control_no}&from_approver=true"
        data_dict['fleet_master_url'] = fleet_master_url

 
        
        context = {
            'data': {
                **data_dict,
                'registration': data_dict.get('registration', []),
                'allocation': data_dict.get('allocation', []),
                'STATUS': current_status  # Ensure the status is explicitly included
            },
            'is_new_submission': is_new_submission,
            'comparison_data': json.loads(comparison_data) if comparison_data else None,
            'is_approver_action': is_approver_action,
            'action': action,
            'current_status': current_status  # Add this line
        }
        
        
        print(f"Rendering template with context: {context}")
        print(f"Context Status: {context['data']['STATUS']}")

        if is_approver_action or not is_approver_action:
            html_message = render_to_string('ALY_GTD/email_template.html', context)
            text_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject,
                text_message,
                settings.EMAIL_HOST_USER,
                [recipient],
                cc=cc_list,
                bcc=bcc_list
            )
       
            email.attach_alternative(html_message, "text/html")

            if attachment:
                email.attach(
                    attachment.name,
                    attachment.read(),
                    attachment.content_type
                )
            print("Sending email...")
            email.send(fail_silently=False)
            print("Email sent successfully")
            return {"status": "success", "message": "Email sent successfully"}
        else:
            print("Skipping email for unknown scenario")
            return {"status": "skipped", "message": "Email skipped for unknown scenario"}
    
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON in data field"}
    except Exception as e:
        return {"status": "error", "message": str(e)}




# def parse_bool(value: str) -> bool:
#     return value.lower() in ('true', '1', 'yes', 'on')

# @api.post("/send-commercial-email")
# def send_commercial_email(
#     request,
#     recipient: str = Form(...),
#     cc: str = Form(None),
#     bcc: str = Form(None),
#     subject: str = Form(...),
#     data: str = Form(...),
#     custom_message: str = Form(None),
#     comparison_data: str = Form(None),
#     is_new_submission: bool = Form(False),
#     is_approver_action: bool = Form(default=False, description="Is this an approver action?", alias="is_approver_action"),
#     action: str = Form(None),
#     attachment: Optional[UploadedFile] = File(None)
# ):
#     try:
#         print(f"Sending email to: {recipient}")
#         print(f"CC: {cc}")
#         print(f"BCC: {bcc}")
#         print(f"Subject: {subject}")
#         print(f"Data: {data}")
#         print(f"Is approver action: {is_approver_action}")
#         print(f"Action: {action}")
#         print(f"Is new submission: {is_new_submission}")

#         cc_list = [email.strip() for email in cc.split(',')] if cc else []
#         bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

#         data_dict = json.loads(data)
#         current_status = data_dict.get('STATUS') or data_dict.get('commercial_master', {}).get('STATUS', 'N/A')
#         data_dict['STATUS'] = current_status
#         data_dict['CREATION_DATE'] = data_dict.get('COMM_PLATE_DATE', data_dict.get('CREATION_DATE', 'N/A'))
        
#          # Ensure LAST_UPDATE_DATE is set
#         #data_dict['LAST_UPDATE_DATE'] = data_dict.get('COMM_PLATE_DATE', data_dict.get('LAST_UPDATE_DATE', 'N/A'))
        
#         data_dict['LAST_UPDATE_DATE'] = datetime.now().strftime('%Y-%m-%d')
#         data_dict['LAST_UPDATED_BY'] = request.user.username  # Assuming you have access to the current user

        
#         print(f"Creation Date being sent to template: {data_dict.get('CREATION_DATE', 'Not found')}")
#         print(f"LAST_UPDATE_DATE being sent to template: {data_dict.get('LAST_UPDATE_DATE', 'Not found')}")
#         print(f"LAST_UPDATED_BY being sent to template: {data_dict.get('LAST_UPDATED_BY', 'Not found')}")
#         print(f"Current Status: {current_status}")
#         print(f"Updated Subject: {subject}")

#         if custom_message:
#             data_dict['custom_message'] = custom_message

#         commercial_control_num = data_dict.get('COMM_CONTROL_NO', '')
#         commercial_master_url = f"http://127.0.0.1:8000/ALY_GTD/commercial_master/?commercial_master={commercial_control_num}&from_approver=true"
#         data_dict['commercial_master_url'] = commercial_master_url

#         context = {
#             'data': data_dict,
#             'is_new_submission': is_new_submission,
#             'comparison_data': json.loads(comparison_data) if comparison_data else None,
#             'is_approver_action': is_approver_action,
#             'action': action,
#             'current_status': current_status
#         }

#         print(f"Rendering template with context: {context}")
#         print(f"Context Status: {context['data']['STATUS']}")

#         if is_approver_action or not is_approver_action:
#             html_message = render_to_string('ALY_GTD/commercial_email.html', context)
#             text_message = strip_tags(html_message)

#             email = EmailMultiAlternatives(
#                 subject,
#                 text_message,
#                 settings.EMAIL_HOST_USER,
#                 [recipient],
#                 cc=cc_list,
#                 bcc=bcc_list
#             )

#             email.attach_alternative(html_message, "text/html")

#             if attachment:
#                 email.attach(
#                     attachment.name,
#                     attachment.read(),
#                     attachment.content_type
#                 )

#             print("Sending email...")
#             email.send(fail_silently=False)
#             print("Email sent successfully")
#             return {"status": "success", "message": "Email sent successfully"}
#         else:
#             print("Skipping email for unknown scenario")
#             return {"status": "skipped", "message": "Email skipped for unknown scenario"}

#     except json.JSONDecodeError:
#         return {"status": "error", "message": "Invalid JSON in data field"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}


def parse_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 'yes', 'on')

@api.post("/send-commercial-email")
def send_commercial_email(
    request,
    recipient: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(...),
    data: str = Form(...),
    custom_message: str = Form(None),
    comparison_data: str = Form(None),
    is_new_submission: bool = Form(False),
    is_approver_action: bool = Form(default=False, description="Is this an approver action?", alias="is_approver_action"),
    action: str = Form(None),
    attachment: Optional[UploadedFile] = File(None)
):
    try:
        print(f"Sending email to: {recipient}")
        print(f"CC: {cc}")
        print(f"BCC: {bcc}")
        print(f"Subject: {subject}")
        print(f"Data: {data}")
        print(f"Is approver action: {is_approver_action}")
        print(f"Action: {action}")
        print(f"Is new submission: {is_new_submission}")

        cc_list = [email.strip() for email in cc.split(',')] if cc else []
        bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

        data_dict = json.loads(data)
        current_status = data_dict.get('STATUS') or data_dict.get('commercial_master', {}).get('STATUS', 'N/A')
        data_dict['STATUS'] = current_status
        data_dict['CREATION_DATE'] = data_dict.get('COMM_PLATE_DATE', data_dict.get('CREATION_DATE', 'N/A'))
        
         # Ensure LAST_UPDATE_DATE is set
        data_dict['LAST_UPDATE_DATE'] = data_dict.get('COMM_PLATE_DATE', data_dict.get('LAST_UPDATE_DATE', 'N/A'))
        
        data_dict['LAST_UPDATED_BY'] = data_dict.get('LAST_UPDATED_BY', 'N/A')

        
        print(f"Creation Date being sent to template: {data_dict.get('CREATION_DATE', 'Not found')}")
        print(f"Last Update Date being sent to template: {data_dict.get('LAST_UPDATE_DATE', 'Not found')}")
        print(f"Last Updated By being sent to template: {data_dict.get('LAST_UPDATED_BY', 'Not found')}")
        print(f"Current Status: {current_status}")
        print(f"Updated Subject: {subject}")

        if custom_message:
            data_dict['custom_message'] = custom_message

        commercial_control_num = data_dict.get('COMM_CONTROL_NO', '')
        commercial_master_url = f"http://127.0.0.1:8000/ALY_GTD/commercial_master/?commercial_master={commercial_control_num}&from_approver=true"
        data_dict['commercial_master_url'] = commercial_master_url

        context = {
            'data': data_dict,
            'is_new_submission': is_new_submission,
            'comparison_data': json.loads(comparison_data) if comparison_data else None,
            'is_approver_action': is_approver_action,
            'action': action,
            'current_status': current_status
        }

        print(f"Rendering template with context: {context}")
        print(f"Context Status: {context['data']['STATUS']}")

        if is_approver_action or not is_approver_action:
            html_message = render_to_string('ALY_GTD/commercial_email.html', context)
            text_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject,
                text_message,
                settings.EMAIL_HOST_USER,
                [recipient],
                cc=cc_list,
                bcc=bcc_list
            )

            email.attach_alternative(html_message, "text/html")

            if attachment:
                email.attach(
                    attachment.name,
                    attachment.read(),
                    attachment.content_type
                )

            print("Sending email...")
            email.send(fail_silently=False)
            print("Email sent successfully")
            return {"status": "success", "message": "Email sent successfully"}
        else:
            print("Skipping email for unknown scenario")
            return {"status": "skipped", "message": "Email skipped for unknown scenario"}

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON in data field"}
    except Exception as e:
        return {"status": "error", "message": str(e)}




from django.core.cache import cache
from ALY_GTD.models import XXGTD_TRAFFIC_FILE_MASTER

@api.post("/send-traffic-email")
def send_traffic_email(
    request,
    recipient: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(...),
    data: str = Form(...),
    custom_message: str = Form(None),
    comparison_data: str = Form(None),
    is_new_submission: bool = Form(False),
    attachment: Optional[UploadedFile] = File(None)
):
    try:
        cache_key = f"traffic_email_{recipient}_{subject}"
       
        if cache.get(cache_key):
            return {"status": "success", "message": "Email already sent"}
       
        cache.set(cache_key, True, timeout=60)
       
        print(f"Sending email to: {recipient}")
        print(f"CC: {cc}")
        print(f"BCC: {bcc}")
        print(f"Subject: {subject}")
        print(f"Data: {data}")

        cc_list = [email.strip() for email in cc.split(',')] if cc else []
        bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

        data_dict = json.loads(data)
        if custom_message:
            data_dict['custom_message'] = custom_message

        traffic_file_no = data_dict.get('TRAFFIC_FILE_NO', '')
        traffic_file = XXGTD_TRAFFIC_FILE_MASTER.objects.filter(TRAFFIC_FILE_NO=traffic_file_no).first()

        if traffic_file:
            data_dict['CREATED_BY'] = traffic_file.CREATED_BY
            data_dict['CREATION_DATE'] = traffic_file.CREATION_DATE.strftime('%Y-%m-%d %H:%M:%S') if traffic_file.CREATION_DATE else 'N/A'

        traffic_file_url = f"http://127.0.0.1:8000/ALY_GTD/traffic_master/?traffic_file_no={traffic_file_no}&from_approver=true"
        data_dict['traffic_file_url'] = traffic_file_url

        context = {
            'data': data_dict,
            'is_new_submission': is_new_submission,
            'comparison_data': json.loads(comparison_data) if comparison_data else None
        }

        print(f"Rendering template with context: {context}")

        html_message = render_to_string('ALY_GTD/traffic_file_email.html', context)
        text_message = strip_tags(html_message)

        print("Email content generated successfully")

        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.EMAIL_HOST_USER,
            [recipient],
            cc=cc_list,
            bcc=bcc_list
        )
       
        email.attach_alternative(html_message, "text/html")

        if attachment:
            email.attach(
                attachment.name,
                attachment.read(),
                attachment.content_type
            )
       
        print("Sending email...")
        email.send(fail_silently=False)
        print("Email sent successfully")

        return {"status": "success", "message": "Traffic email sent successfully"}
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {"status": "error", "message": str(e)}





@api.get("/revert-data/{header_id}")
def revert_data(request, header_id: str):
    try:
        with transaction.atomic():
            approved_records = REVERT_APPROVES.objects.filter(HEADER_ID=header_id)

            if not approved_records.exists():
                return JsonResponse({"message": "No approved data found for this HEADER_ID"}, status=400)

            # Revert FleetMaster
            fleet_master = XXGTD_VEHICLE_INFO.objects.get(HEADER_ID=header_id)
            main_record = approved_records.filter(FM_LINE_ID=header_id).first()
            if main_record:
                for field in XXGTD_VEHICLE_INFO._meta.fields:
                    if hasattr(main_record, field.name):
                        setattr(fleet_master, field.name, getattr(main_record, field.name))
                fleet_master.save()

            # Revert related models
            for model, prefix in [
                (XXGTD_INSURANCE_INFO, 'INS'),
                (XXGTD_REGISTRATION_INFO, 'REG'),
                (XXGTD_PARKING_PERMIT, 'PERMIT'),
                (XXGTD_GPS_TRACKING_INFO, 'GT'),
                (XXGTD_FUEL_INFO, 'FUEL'),
                (XXGTD_ROAD_TOLL_INFO, 'RT'),
                (XXGTD_DRIVER_ASSIGNMENT, 'ASGN'),
                (XXGTD_ALLOCATION_INFO, 'ALLOC')
            ]:
                child_records = approved_records.filter(**{f'{prefix}_LINE_ID__isnull': False})
                for approved_record in child_records:
                    line_id = getattr(approved_record, f'{prefix}_LINE_ID')
                    try:
                        instance = model.objects.get(fleet_master=fleet_master, **{f'{prefix}_LINE_ID': line_id})
                        for field in model._meta.fields:
                            if hasattr(approved_record, field.name) and field.name != 'fleet_master':
                                setattr(instance, field.name, getattr(approved_record, field.name))
                        instance.save()
                    except model.DoesNotExist:
                        # If the record doesn't exist, we don't create a new one
                        pass

            return JsonResponse({"message": "Data reverted successfully and REVERT_APPROVES cleared"}, status=200)

    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)
