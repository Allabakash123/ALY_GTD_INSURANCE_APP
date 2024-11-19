

import json
import os
import re
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Form, File, NinjaAPI, Schema
from ninja.files import UploadedFile
from typing import Any, Dict, List, Optional, Union
from datetime import date
from .models import XXALY_GTD_ACTION_HISTORY, XXALY_GTD_AUDIT_T, XXALY_GTD_LOOKUP_DETAIL, XXALY_GTD_LOOKUP_MASTER, Allocation, ApprovalRequest, Attachment, CommercialAllocation, CommercialAttachment, CommercialInsurance, CommercialMaster, CommercialRegistration, CommercialRoadtoll, Driver, FleetMaster, Fuel, Insurance, Permits, Gps, Registration, Roadtoll, SharedControlNumber, TrafficFileMaster
from django.db.models import Q

    
    
    
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

class PermitsSchema(Schema):
    PERMIT_TYPE: str
    EMIRATES: str
    ISSUING_AUTHORITY: str
    PERMIT_NO: str
    PERMIT_DATE: date
    PERMIT_EXPIRY_DATE: date
    CUR_STAT_PERMIT: str
    PermitAattachment: str

class GpsSchema(Schema):
    GPS_DEVICE_NO: str
    GPS_INSTALLATION_DATE: date
    GPS_SERVICE_PROVIDER: str
    GpsAattachment: str

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
    SEATING_CAPACITY: Optional[str] = None
    TONNAGE: Optional[float] = None
    GROSS_WEIGHT_KG: Optional[float] = None
    EMPTY_WEIGHT_KG: Optional[float] = None
    PURCHASE_VALUE_AED: Optional[float] = None
    COMMENTS: Optional[str] = None
    STATUS: Optional[str] = "Pending for Approval"
    ApplicationUsage: Optional[str] = None
    VehiclePurchaseDoc: Optional[str] = None
    HEADER_ID:Optional[str]=None
    
    

class RoadtollSchema(Schema):
    EMIRATES: str
    TOLL_TYPE: str
    ACCOUNT_NO: str
    TAG_NO: str
    ACTIVATION_DATE: date
    CURRENT_STATUS: str
    RoadtollAttachments: str
    
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
    
class AllocationSchema(Schema):
    COMPANY_NAME: str
    DIVISION: str
    OPERATING_LOCATION: str
    OPERATING_EMIRATES: str
    APPICATION_USAGE: str
    ALLOCATION_DATE: date
    attachment: Optional[str] = None


class FleetMasterResponse(Schema):
    message: str
    fleet_master: Optional[FleetMasterSchema] = None


api = NinjaAPI()

def update_fleet_master_status(fleet_master):
    fleet_master.STATUS = FleetMaster.DEFAULT_STATUS
    fleet_master.save()




@api.post("/fleet-master", response=FleetMasterResponse)


def create_or_update_fleet_master(
    request,
    COMPANY_NAME: Optional[str] = Form(None),
    FLEET_CONTROL_NO: Optional[str] = Form(None),
    FLEET_CREATION_DATE: Optional[date] = Form(None),
    VIN_NO: Optional[str] = Form(None),
    MANUFACTURER: Optional[str] = Form(None),
    MODEL: Optional[str] = Form(None),
    VEHICLE_TYPE:Optional[str] = Form(None),
    COLOR: Optional[str] = Form(None),
    FLEET_CATEGORY:Optional[str] = Form(None),
    FLEET_SUB_CATEGORY: Optional[str] = Form(None),
    ENGINE_NO: Optional[str] = Form(None),
    MODEL_YEAR: Optional[str] = Form(None),
    COUNTRY_OF_ORIGIN: Optional[str] = Form(None),
    SEATING_CAPACITY: Optional[Union[str,int]] = Form(None),
    TONNAGE: Optional[float] = Form(None),
    GROSS_WEIGHT_KG:Optional[float] = Form(None),
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
            current_fleet_status = None
            if FLEET_CONTROL_NO:
                fleet_master = FleetMaster.objects.get(FLEET_CONTROL_NO=FLEET_CONTROL_NO)
                created = False
            elif HEADER_ID:
                fleet_master = FleetMaster.objects.filter(HEADER_ID=HEADER_ID).first()
                if fleet_master:
                    created = False
                else:
                    fleet_master = FleetMaster(HEADER_ID=HEADER_ID)
                    created = True
            else:
                fleet_master = FleetMaster()
                created = True

            fleet_master_data = {
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
                "SEATING_CAPACITY": SEATING_CAPACITY,
                "TONNAGE": TONNAGE,
                "GROSS_WEIGHT_KG": GROSS_WEIGHT_KG,
                "EMPTY_WEIGHT_KG": EMPTY_WEIGHT_KG,
                "PURCHASE_VALUE_AED": PURCHASE_VALUE_AED,
                "COMMENTS": COMMENTS,
                "STATUS" : STATUS or "Pending for Approval",
                "HEADER_ID": HEADER_ID,
                "ApplicationUsage": ApplicationUsage
            }
            for key, value in fleet_master_data.items():
                setattr(fleet_master, key, value)
            
            fleet_master.save()
           

            header_id_num = fleet_master.HEADER_ID
            fleet_control_number = fleet_master.FLEET_CONTROL_NO
            Attachment.objects.filter(fleet_master=fleet_master, HEADER_ID=HEADER_ID).update(FleetNumber=fleet_control_number)

            if is_approver:
                fleet_master.STATUS = STATUS
            elif all(insurance.Process == 'Pending for Approval' for insurance in fleet_master.insurances.all()) and \
                all(permit.Process == 'Pending for Approval' for permit in fleet_master.permits.all()):
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

            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    insurance = Insurance.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], fleet_master=fleet_master)
                    if insurance.Process != 'Approved':
                        insurance.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    insurance = Insurance(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                              'PLTS_INS_START_DATE', 'PLTS_INS_EXPIRY_DATE', 'CUR_STAT_MOT_INS']:
                    setattr(insurance, field, insurance_item.get(field))
                
                insurance.FLEET_CONTROL_NO = fleet_control_number
                insurance.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"

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
                            fleet_master=fleet_master
                        )

                insurance.save()

            # Handle Permits data
            permits_data = json.loads(permits)
            for index, permit_item in enumerate(permits_data):
                if permit_item['PERMIT_LINE_ID'] != 'new':
                    permit = Permits.objects.get(PERMIT_LINE_ID=permit_item['PERMIT_LINE_ID'], fleet_master=fleet_master)
                    if permit.Process != 'Approved':
                        permit.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    permit = Permits(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['PERMIT_TYPE', 'EMIRATES', 'ISSUING_AUTHORITY', 'PERMIT_NO', 'PERMIT_DATE',
                            'PERMIT_EXPIRY_DATE', 'CUR_STAT_PERMIT', 'PermitColor']:
                    setattr(permit, field, permit_item.get(field))

                permit.FLEET_CONTROL_NO = fleet_control_number
                fleet_master.STATUS = "Pending for Approval"
                permit.HEADER_ID=header_id_num
                
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
                            fleet_master=fleet_master
                        )

                permit.save()

            # Handle GPS data
            gps_data = json.loads(gps)
            for index, gps_item in enumerate(gps_data):
                if gps_item['GT_LINE_ID'] != 'new':
                    gp = Gps.objects.get(GT_LINE_ID=gps_item['GT_LINE_ID'], fleet_master=fleet_master)
                    if gp.Process != 'Approved':
                        gp.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    gp = Gps(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['GPS_DEVICE_NO', 'GPS_INSTALLATION_DATE', 'GPS_SERVICE_PROVIDER']:
                    setattr(gp, field, gps_item.get(field))

                gp.FLEET_CONTROL_NO = fleet_control_number
                fleet_master.STATUS = "Pending for Approval"
                gp.HEADER_ID=header_id_num
                
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
                        )

                gp.save()

            # Handle Registration  
            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    reg = Registration.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], fleet_master=fleet_master)
                    if reg.Process != 'Approved':
                        reg.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    reg = Registration(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.FLEET_CONTROL_NO = fleet_control_number
                reg.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                
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
                            fleet_master=fleet_master
                        )

                reg.save()

            # Handle Fuel
            if fuel:
                fuel_data = json.loads(fuel)
                for index, fuel_item in enumerate(fuel_data):
                    if fuel_item['FUEL_LINE_ID'] != 'new':
                        ful = Fuel.objects.get(FUEL_LINE_ID=fuel_item['FUEL_LINE_ID'], fleet_master=fleet_master)
                        if ful.Process != 'Approved':
                            ful.Process = STATUS if is_approver else 'Pending for Approval'
                    else:
                        ful = Fuel(fleet_master=fleet_master, Process='Pending for Approval')

                    for field in ['FUEL_TYPE', 'MONTHLY_FUEL_LIMIT', 'FUEL_SERVICE_TYPE', 'FUEL_SERVICE_PROVIDER', 'FUEL_DOCUMENT_NO', 'FuelDocumentDate', 'FUEL_DOC_EXPIRY_DATE', 'CUR_STAT_FUEL_DOC']:
                        value = fuel_item.get(field, '')
                        setattr(ful, field, value if value != '' else None)

                    ful.FLEET_CONTROL_NO = fleet_control_number
                    ful.HEADER_ID = header_id_num
                    fleet_master.STATUS = "Pending for Approval"
                    
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
                            )

                    ful.save()

            # Handle Roadtoll
            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = Roadtoll.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], fleet_master=fleet_master)
                    if road.Process != 'Approved':
                        road.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    road = Roadtoll(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE', 'CURRENT_STATUS']:
                    setattr(road, field, roadtoll_item.get(field))

                road.FLEET_CONTROL_NO = fleet_control_number
                road.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                
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
                        )

                road.save()

            # Handle Driver
            driver_data = json.loads(driver)
            for index, driver_item in enumerate(driver_data):
                if driver_item['ASGN_LINE_ID'] != 'new':
                    drive = Driver.objects.get(ASGN_LINE_ID=driver_item['ASGN_LINE_ID'], fleet_master=fleet_master)
                    if drive.Process != 'Approved':
                        drive.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    drive = Driver(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE', 'TRAFFIC_CODE_NO', 'DRIVING_LICENSE_NO', 'LICENSE_TYPE', 'PLACE_OF_ISSUE', 'LICENSE_EXPIRY_DATE', 'GPS_TAG_NO', 'GPS_TAG_ASSIGN_DATE']:
                    setattr(drive, field, driver_item.get(field))

                drive.FLEET_CONTROL_NO = fleet_control_number
                drive.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                
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
                        )

                drive.save()

            # Handle Allocation
            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = Allocation.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], fleet_master=fleet_master)
                    if allocations.Process != 'Approved':
                        allocations.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    allocations = Allocation(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.FLEET_CONTROL_NO = fleet_control_number
                allocations.HEADER_ID = header_id_num
                fleet_master.STATUS = "Pending for Approval"
                
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
                        )

                allocations.save()


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

            action = "created" if created else "updated"
            
            current_user = request.user if request.user.is_authenticated else None
            if is_approver:
                fleet_master.STATUS = STATUS
            else:
                fleet_master.STATUS = STATUS or "Pending for Approval"

            
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
                COMPANY_NAME=fleet_master.COMPANY_NAME,
                COMMENTS=fleet_master.COMMENTS,
                ACTION_CODE='C' if created else 'U',
                ACTION='Created' if created else 'Updated',
                CREATION_DATE=timezone.now(),
                CREATED_BY=current_user.username if current_user else "System",
                LAST_UPDATE_DATE=timezone.now(),
                LAST_UPDATED_BY=current_user.username if current_user else "System",
            )

            # Add related data to the audit entry
            if fleet_master.insurances.exists():
                latest_insurance = fleet_master.insurances.latest('INS_LINE_ID')
                audit_entry.INSURANCE_COMPANY = latest_insurance.INSURANCE_COMPANY
                audit_entry.POLICY_NO = latest_insurance.POLICY_NO
                audit_entry.POLICY_DATE = latest_insurance.POLICY_DATE
                audit_entry.POLICY_EXPIRY_DATE = latest_insurance.POLICY_EXPIRY_DATE
                audit_entry.POLICY_INSUR_EXPIRY_DATE = latest_insurance.PLTS_INS_EXPIRY_DATE
                audit_entry.INSUR_CURRENT_STATUS = latest_insurance.CUR_STAT_MOT_INS
                audit_entry.INS_LINE_ID = latest_insurance  # Assign the Insurance instance, not the id

            if fleet_master.registration.exists():
                latest_registration = fleet_master.registration.latest('REG_LINE_ID')
                audit_entry.REGISTRATION_NO = latest_registration.REGISTRATION_NO
                audit_entry.REGISTRATION_DATE = latest_registration.REGISTRATION_DATE
                audit_entry.REGISTERED_EMIRATES = latest_registration.REGISTERED_EMIRATES
                audit_entry.EMIRATES_TRF_FILE_NO = latest_registration.EMIRATES_TRF_FILE_NO
                audit_entry.FEDERAL_TRF_FILE_NO = latest_registration.FEDERAL_TRF_FILE_NO
                audit_entry.REG_EXPIRY_DATE = latest_registration.REG_EXPIRY_DATE
                audit_entry.REG_COMPANY_NAME = latest_registration.REG_COMPANY_NAME
                audit_entry.REGISTRATION_STATUS = latest_registration.CUR_STAT_REG
                audit_entry.TRADE_LICENSE_NO = latest_registration.TRADE_LICENSE_NO
                audit_entry.REG_LINE_ID = latest_registration  # Assign the Registration instance, not the id

          
            audit_entry.save()
            
            
            XXALY_GTD_ACTION_HISTORY.objects.create(
                APPLICATION_ID=str(fleet_master.id),
                APPL_NUMBER=fleet_master.FLEET_CONTROL_NO,
                REQUEST_TYPE="FLEET_MASTER",
                REQUEST_NUMBER=fleet_master.FLEET_CONTROL_NO,
                PROCESS_STATUS=fleet_master.STATUS,
                DOC_STATUS=fleet_master.STATUS,
                RESPONSE_DATE=timezone.now().date(),
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

            return {
                "message": "Fleet Master and related records created/updated successfully",
                "fleet_master": FleetMasterSchema.from_orm(fleet_master)
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}



@api.post("/fleet-master/save", response=FleetMasterResponse)
def create_or_update_fleet_master(
    request,
    COMPANY_NAME: str = Form(...),
    HEADER_ID: Optional[str] = Form(None),
    FLEET_CREATION_DATE: Optional[date] = Form(None),
    VIN_NO: str = Form(...),
    MANUFACTURER: str = Form(...),
    MODEL: str = Form(...),
    VEHICLE_TYPE: str = Form(...),
    COLOR: str = Form(...),
    FLEET_CATEGORY: str = Form(...),
    FLEET_SUB_CATEGORY: str = Form(...),
    ENGINE_NO: str = Form(...),
    MODEL_YEAR: str = Form(...),
    COUNTRY_OF_ORIGIN: str = Form(...),
    SEATING_CAPACITY: Union[int,str] = Form(...),
    TONNAGE: float = Form(...),
    GROSS_WEIGHT_KG: float = Form(...),
    EMPTY_WEIGHT_KG: float = Form(...),
    PURCHASE_VALUE_AED: float = Form(...),
    COMMENTS: str = Form(...),
    ApplicationUsage: str = Form(...),
   
    VehiclePurchaseDoc: Optional[UploadedFile] = File(None),
    insurances: str = Form(...),
    permits: str = Form(...),
    gps: str = Form(...),
    registration: str = Form(None),
    fuel: str = Form(None),
    roadtoll: str = Form(...),
    driver: str = Form(...),
    allocation: str = Form(...),
   
    InsurancePolicAattachment: Optional[Union[UploadedFile, List[UploadedFile]]] = File(None),
    InsurancePolicAattachmentNames: Optional[List[str]] = Form(None),
):
    try:
        with transaction.atomic():
            if HEADER_ID:
                fleet_master = FleetMaster.objects.get(HEADER_ID=HEADER_ID)
                created = False
            else:
                fleet_master = FleetMaster()
                created = True

            fleet_master_data = {
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
                "SEATING_CAPACITY": SEATING_CAPACITY,
                "TONNAGE": TONNAGE,
                "GROSS_WEIGHT_KG": GROSS_WEIGHT_KG,
                "EMPTY_WEIGHT_KG": EMPTY_WEIGHT_KG,
                "PURCHASE_VALUE_AED": PURCHASE_VALUE_AED,
                "COMMENTS": COMMENTS,
                "STATUS": "Draft",
                "ApplicationUsage": ApplicationUsage
            }
            for key, value in fleet_master_data.items():
                setattr(fleet_master, key, value)
            fleet_master.save(generate_fleet_control_number=False)

            HEADER_ID = fleet_master.HEADER_ID

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
                        HEADER_ID=fleet_master.HEADER_ID
                    )
                fleet_master.save(generate_fleet_control_number=False)

            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    try:
                        insurance = Insurance.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], fleet_master=fleet_master)
                    except Insurance.DoesNotExist:
                        insurance = Insurance(fleet_master=fleet_master)
                else:
                    insurance = Insurance(fleet_master=fleet_master)

                for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                              'PLTS_INS_EXPIRY_DATE', 'PLTS_INS_START_DATE', 'CUR_STAT_MOT_INS']:
                    setattr(insurance, field, insurance_item.get(field))
               
                insurance.HEADER_ID = HEADER_ID

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

            permits_data = json.loads(permits)
            for index, permit_item in enumerate(permits_data):
                if permit_item['PERMIT_LINE_ID'] != 'new':
                    permit = Permits.objects.get(PERMIT_LINE_ID=permit_item['PERMIT_LINE_ID'], fleet_master=fleet_master)
                else:
                    permit = Permits(fleet_master=fleet_master)

                for field in ['PERMIT_TYPE', 'EMIRATES', 'ISSUING_AUTHORITY', 'PERMIT_NO', 'PERMIT_DATE',
                            'PERMIT_EXPIRY_DATE', 'CUR_STAT_PERMIT', 'PermitColor']:
                    setattr(permit, field, permit_item.get(field))

                permit.HEADER_ID = HEADER_ID
               
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

            gps_data = json.loads(gps)
            for index, gps_item in enumerate(gps_data):
                if gps_item['GT_LINE_ID'] != 'new':
                    gp = Gps.objects.get(GT_LINE_ID=gps_item['GT_LINE_ID'], fleet_master=fleet_master)
                else:
                    gp = Gps(fleet_master=fleet_master)

                for field in ['GPS_DEVICE_NO', 'GPS_INSTALLATION_DATE', 'GPS_SERVICE_PROVIDER']:
                    setattr(gp, field, gps_item.get(field))

                gp.HEADER_ID = HEADER_ID

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

            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    reg = Registration.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], fleet_master=fleet_master)
                else:
                    reg = Registration(fleet_master=fleet_master)

                for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.HEADER_ID = HEADER_ID

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
                        ful = Fuel.objects.get(FUEL_LINE_ID=fuel_item['FUEL_LINE_ID'], fleet_master=fleet_master)
                    else:
                        ful = Fuel(fleet_master=fleet_master)

                    for field in ['FUEL_TYPE', 'MONTHLY_FUEL_LIMIT', 'FUEL_SERVICE_TYPE', 'FUEL_SERVICE_PROVIDER', 'FUEL_DOCUMENT_NO', 'FUEL_DOCUMENT_DATE', 'FUEL_DOC_EXPIRY_DATE', 'CUR_STAT_FUEL_DOC']:
                        value = fuel_item.get(field, '')
                        setattr(ful, field, value if value != '' else None)

                    ful.HEADER_ID = HEADER_ID

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

            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = Roadtoll.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], fleet_master=fleet_master)
                else:
                    road = Roadtoll(fleet_master=fleet_master)

                for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE', 'CURRENT_STATUS']:
                    setattr(road, field, roadtoll_item.get(field))

                road.HEADER_ID = HEADER_ID

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

            driver_data = json.loads(driver)
            for index, driver_item in enumerate(driver_data):
                if driver_item['ASGN_LINE_ID'] != 'new':
                    drive = Driver.objects.get(ASGN_LINE_ID=driver_item['ASGN_LINE_ID'], fleet_master=fleet_master)
                else:
                    drive = Driver(fleet_master=fleet_master)
                for field in ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE', 
                              'TRAFFIC_CODE_NO', 'DRIVING_LICENSE_NO', 'LICENSE_TYPE', 'PLACE_OF_ISSUE',
                              'LICENSE_EXPIRY_DATE', 'GPS_TAG_NO', 'GPS_TAG_ASSIGN_DATE']:
                    setattr(drive, field, driver_item.get(field))

                drive.HEADER_ID = HEADER_ID

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

            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = Allocation.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], fleet_master=fleet_master)
                else:
                    allocations = Allocation(fleet_master=fleet_master)

                for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.HEADER_ID = HEADER_ID

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
                "message": "Fleet Master and related records created/updated successfully",
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
    Process:Optional[str]=None

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
    Process:Optional[str]=None

class GpsSchema(Schema):
    GT_LINE_ID: int 
    GPS_DEVICE_NO: Optional[str] = None
    GPS_INSTALLATION_DATE:  Optional[date] = None
    GPS_SERVICE_PROVIDER: Optional[str] = None
    GpsAattachment: Optional[str] = None
    Process:Optional[str]=None

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
    Process:Optional[str]=None


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
    Process:Optional[str]=None


class RoadtollSchema(Schema):
    RT_LINE_ID: int 
    EMIRATES: Optional[str] = None
    TOLL_TYPE: Optional[str] = None
    ACCOUNT_NO: Optional[str] = None
    TAG_NO: Optional[str] = None
    ACTIVATION_DATE: Optional[date] = None
    CURRENT_STATUS: Optional[str] = None
    RoadtollAttachments: Optional[str] = None
    Process:Optional[str]=None

    
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
    Process:Optional[str]=None

    
    
class AllocationSchema(Schema):
    ALLOC_LINE_ID: int 
    COMPANY_NAME: Optional[str] = None
    DIVISION: Optional[str] = None
    OPERATING_LOCATION: Optional[str] = None
    OPERATING_EMIRATES: Optional[str] = None
    APPICATION_USAGE: Optional[str] = None
    ALLOCATION_DATE: Optional[date] = None
    attachment: Optional[str] = None
    Process:Optional[str]=None



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
        fleet_master = FleetMaster.objects.prefetch_related(
            'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(FLEET_CONTROL_NO=identifier)
    except FleetMaster.DoesNotExist:
        try:
            # If not found, try to fetch by header_id
            fleet_master = FleetMaster.objects.prefetch_related(
                'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
            ).get(HEADER_ID=identifier)
        except FleetMaster.DoesNotExist:
            return JsonResponse({"error": f"FleetMaster with identifier {identifier} does not exist"}, status=404)

    return FleetMasterDetailSchema.from_orm(fleet_master)


@api.get("/fleet-master-by-header/{HEADER_ID}", response=FleetMasterDetailSchema)
def get_fleet_master_by_header(request, HEADER_ID: str):
    try:
        fleet_master = FleetMaster.objects.prefetch_related(
            'insurances', 'registration', 'permits', 'gps',
            'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(HEADER_ID=HEADER_ID)
        return FleetMasterDetailSchema.from_orm(fleet_master)
    except FleetMaster.DoesNotExist:
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
    reg_subquery = Registration.objects.filter(fleet_master=OuterRef('pk')).values('REGISTRATION_NO')[:1]
    
    fleet_info = FleetMaster.objects.annotate(
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
    fleet_control_numbers = FleetMaster.objects.values_list('FLEET_CONTROL_NO', flat=True)
    return list(fleet_control_numbers)



class AttachmentSchema(Schema):
    id: int
    file: Union[str,Any]
    attachment_type: str
    FleetNumber: str
    CommercialNumber:str
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
    CommercialNUmber:str
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
        

        for item in payload:
            print(f"Processing item: {item}")
            item_dict = item.dict(exclude_unset=True)
            item_dict['CREATION_DATE'] = current_date
            item_dict['LAST_UPDATE_DATE'] = current_date
           
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
def fetch_related_data(request, lookup_name: str):
    lookup_name = lookup_name.strip()

    if not lookup_name:
        return JsonResponse({'error': 'Lookup name is required'}, status=400)
    
    try:
        # Fetch data from the XXALY_GTD_LOOKUP_DETAIL table based on LOOKUP_NAME
        related_data = XXALY_GTD_LOOKUP_DETAIL.objects.filter(LOOKUP_NAME__iexact=lookup_name).values(
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
            return JsonResponse({'error': 'No related data found for the given lookup name'}, status=404)
        
        return data_list
    
    except Exception as e:
        print(f"Error fetching related data: {str(e)}")  # Replace with proper logging if necessary
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
            'fleetmaster': FleetMaster,
            'insurance': Insurance,
            'permits': Permits,
            'gps': Gps,
            'registration': Registration,
            'fuel': Fuel,
            'roadtoll': Roadtoll,
            'driver': Driver,
            'allocation': Allocation,
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
    id: Optional[int] = None
    traffic_file_no: str = None
    company_name: str = None
    trade_license_no: str = None
    emirates: str = None
    federal_traffic_file_no: str = None
    salik_account_no: str = None
    status: str = None

@api.get("/traffic-files", response=List[TrafficFileSchema])
def get_traffic_files(request):
    traffic_files = TrafficFileMaster.objects.all()
    return [
        {
            "id": str(tf.id),
            "traffic_file_no": tf.traffic_file_no,
            "company_name": tf.company_name,
            "trade_license_no": tf.trade_license_no,
            "emirates": tf.emirates,
            "federal_traffic_file_no": tf.federal_traffic_file_no,
            "salik_account_no": tf.salik_account_no,
            "status": tf.status
        }
        for tf in traffic_files
    ]




class TrafficFileResponse(Schema):
    message: str
    traffic_file: Optional[TrafficFileSchema] = None
@api.post("/traffic-file-master", response=TrafficFileResponse)
def create_or_update_traffic_file_master(
    request,
    id: str = Form(...),
    traffic_file_no: str = Form(...),
    company_name: str = Form(...),
    trade_license_no: str = Form(...),
    emirates: str = Form(...),
    federal_traffic_file_no: str = Form(...),
    salik_account_no: str = Form(...),
    status: str = Form(...),
    comments: str = Form(None),
    action_code: str = Form(None),
    action: str = Form(None),
    record_status: str = Form(None),
    attribute1: Optional[str] = Form(None),
    attribute2: Optional[str] = Form(None),
    attribute3: Optional[str] = Form(None),
    attribute4: Optional[str] = Form(None),
    attribute5: Optional[str] = Form(None),
):
    try:
        with transaction.atomic():
            if id != 'new':
                traffic_file = TrafficFileMaster.objects.get(id=id)
                created = False
            else:
                traffic_file = TrafficFileMaster()
                created = True

            # Update TrafficFileMaster fields
            traffic_file_fields = [
                "traffic_file_no", "company_name", "trade_license_no", "emirates",
                "federal_traffic_file_no", "salik_account_no", "status", "comments",
                "action_code", "action", "record_status", "attribute1", "attribute2",
                "attribute3", "attribute4", "attribute5"
            ]
            
            for field in traffic_file_fields:
                value = locals().get(field)
                if value is not None:
                    setattr(traffic_file, field, value)

            traffic_file.save()

            action = "created" if created else "updated"
            return {
                "message": f"Traffic File Master {action} successfully",
                "traffic_file": TrafficFileSchema(
                    traffic_file_no=traffic_file.traffic_file_no,
                    company_name=traffic_file.company_name,
                    trade_license_no=traffic_file.trade_license_no,
                    emirates=traffic_file.emirates,
                    federal_traffic_file_no=traffic_file.federal_traffic_file_no,
                    salik_account_no=traffic_file.salik_account_no,
                    status=traffic_file.status,
                ).dict()
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}
    

class TrafficFileListSchema(Schema):
    traffic_file_no: str

@api.get("/trafficlist-files", response=List[TrafficFileListSchema])
def list_traffic_files(request):
    traffic_files = TrafficFileMaster.objects.values_list('traffic_file_no', flat=True)
    return [{"traffic_file_no": file_no} for file_no in traffic_files] 
    
class TrafficFilesSchema(Schema):
    traffic_file_no: str = None
    company_name: str = None
    trade_license_no: str = None
    emirates: str = None
    federal_traffic_file_no: str = None
    
    
@api.get("/traffic-file/{traffic_file_no}", response=TrafficFilesSchema)
def get_traffic_file(request, traffic_file_no: str):
    traffic_file = TrafficFileMaster.objects.filter(traffic_file_no=traffic_file_no).first()
    if traffic_file:
        return traffic_file
    return api.create_response(request, {"detail": "Traffic file not found"}, status=404)

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
    STATUS: Optional[str] = "Pending for Approval"



class CommercialMasterResponse(Schema):
    message: str
    commercial_master: Optional[CommercialMasterSchema] = None

@api.post("/commercial-master", response=CommercialMasterResponse)
def create_or_update_commercial_master(
    request,
    COMPANY_NAME: str = Form(...),
    COMM_CONTROL_NO: Optional[str] = Form(None),
    COMM_PLATE_NO: str = Form(...),
    COMM_PLATE_DATE: Optional[date] = Form(None),
    COMM_PLATE_CATEGORY: str = Form(...),
    CP_ISSUED_AUTHORITY: str = Form(...),
    CP_VEHICLE_TYPE: str = Form(...),
    CP_COLOR: str = Form(...),
    COMMENTS: str = Form(...),
    STATUS: Optional[str] = Form("Pending for Approval"),
    HEADER_ID:Optional[str]=Form(None),
    
    insurances: str = Form(...),
    registration: str = Form(None),
    roadtoll: str = Form(...),
    allocation: str = Form(...),
    is_approver:bool=Form(...),
):
    try:
        with transaction.atomic():
            if COMM_CONTROL_NO:
                commercial_master = CommercialMaster.objects.get(COMM_CONTROL_NO=COMM_CONTROL_NO)
                created = False
            elif HEADER_ID:
                commercial_master=CommercialMaster.objects.filter(HEADER_ID=HEADER_ID).first()
                if commercial_master:
                    created=False
                else:
                    commercial_master = CommercialMaster(HEADER_ID=HEADER_ID)
                    created = True
            else:
                commercial_master=CommercialMaster()
                created=True

            commercial_master_data = {
                "COMPANY_NAME": COMPANY_NAME,
                "COMM_PLATE_DATE": COMM_PLATE_DATE,
                "COMM_PLATE_NO": COMM_PLATE_NO,
                "COMM_PLATE_CATEGORY": COMM_PLATE_CATEGORY,
                "CP_ISSUED_AUTHORITY": CP_ISSUED_AUTHORITY,
                "CP_VEHICLE_TYPE": CP_VEHICLE_TYPE,
                "CP_COLOR": CP_COLOR,
                "COMMENTS": COMMENTS,
                "STATUS": STATUS or "Pending For Approval",
                "HEADER_ID":HEADER_ID,
                
                }
            for key, value in commercial_master_data.items():
                setattr(commercial_master, key, value)

            commercial_master.save()



            header_id_num=commercial_master.HEADER_ID
            commercial_control_number = commercial_master.COMM_CONTROL_NO
            Attachment.objects.filter(commercial_master=commercial_master,HEADER_ID=HEADER_ID).update(CommercialNumber=commercial_control_number)

            if is_approver:
                commercial_master.STATUS = STATUS
            elif all(insurance.Process == 'Pending for Approval' for insurance in commercial_master.insurances.all()) and \
                all(permit.Process == 'Pending for Approval' for permit in commercial_master.permits.all()):
                commercial_master.STATUS = 'Pending for Approval'
            commercial_master.save()

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
            

            # Handle Insurance data
            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    insurance = Insurance.objects.get(id=insurance_item['INS_LINE_ID'], commercial_master=commercial_master)
                    if insurance.Process !='Approved':
                        insurance.Process=STATUS if is_approver else 'Pending for approval'
                else:
                    insurance =Insurance(commercial_master=commercial_master ,Process='Pending for approval')

                for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                              'PLTS_INS_START_DATE', 'PLTS_INS_EXPIRY_DATE', 'CUR_STAT_MOT_INS']:
                    setattr(insurance, field, insurance_item.get(field))
                
                insurance.COMM_CONTROL_NO=commercial_control_number
                insurance.HEADER_ID= header_id_num
                commercial_master.STATUS="Pending for approval"

                existing_attachments = set(Attachment.objects.filter(
                    commercial_master=commercial_master,
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
                                commercial_master=commercial_master,
                                CommercialNumber=commercial_master.COMM_CONTROL_NO,
                                HEADER_ID=commercial_master.HEADER_ID
                            )

                insurance.save()

        registration_data = json.loads(registration)
        for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    reg = Registration.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], commercial_master=commercial_master)
                    if reg.Process!= 'Approved':
                        reg.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    reg = Registration(commercial_master=commercial_master, Process='Pending for Approval')

                for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.COMM_CONTROL_NO = commercial_master
                reg.HEADER_ID = header_id_num
                commercial_master.STATUS = "Pending for Approval"
                
                
                
                
                
                existing_attachments = set(Attachment.objects.filter(
                    commercial_master=commercial_master,
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
                                commercial_master=commercial_master,
                                CommercialNumber=commercial_master.COMM_CONTROL_NO,
                                HEADER_ID=commercial_master.HEADER_ID
                            )
                
                    reg.save()
            # Handle Roadtoll
        roadtoll_data = json.loads(roadtoll)
        for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = Roadtoll.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], commercial_master=commercial_master)
                    if road.Process!= 'Approved':
                        road.Process= STATUS if is_approver else 'Pending for Approval'
                else:
                    road = Roadtoll(commercial_master=commercial_master, Process='Pending for Approval')

                for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE','ACTIVATION_END_DATE' ,'CURRENT_STATUS']:
                    setattr(road, field, roadtoll_item.get(field))

                road.COMM_CONTROL_NO = commercial_master
                road.HEADER_ID = header_id_num
                commercial_master.STATUS = "Pending for Approval"
                
                
                
                        
                        
                existing_attachments = set(Attachment.objects.filter(
                    commercial_master=commercial_master,
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
                                commercial_master=commercial_master,
                                CommercialNumber=commercial_master.COMM_CONTROL_NO,
                                HEADER_ID=commercial_master.HEADER_ID
                            )

                        road.save()


           # Handle Allocation
        allocation_data = json.loads(allocation)
        for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = Allocation.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], commercial_master=commercial_master)
                    if allocations.Process != 'Approved':
                        allocations.Process = STATUS if is_approver else 'Pending for Approval'
                else:
                    allocations = Allocation(commercial_master=commercial_master, Process='Pending for Approval')

                for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.COMM_CONTROL_NO = commercial_master
                allocations.HEADER_ID = header_id_num
                commercial_master.STATUS = "Pending for Approval"
                
               
                
                existing_attachments = set(Attachment.objects.filter(
                    commercial_master=commercial_master,
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
                                commercial_master=commercial_master,
                                CommercialNumber=commercial_master.COMM_CONTROL_NO,
                                HEADER_ID=commercial_master.HEADER_ID
                            )

                allocations.save()


        ApprovalRequest.objects.update_or_create(
                request_number=commercial_master.COMM_CONTROL_NO,
                defaults={
                    'company_name': commercial_master.COMPANY_NAME,
                    'request_type': 'COMMERCIAL MASTER',
                    'status': commercial_master.STATUS,
                    'comments': commercial_master.COMMENTS,
                    'commercial_master': commercial_master
                }
            )

        action = "created" if created else "updated"

        current_user = request.user if request.user.is_authenticated else None
        if is_approver:
                commercial_master.STATUS = STATUS
        else:
                commercial_master.STATUS = STATUS or "Pending for Approval"



        XXALY_GTD_ACTION_HISTORY.objects.create(
                APPLICATION_ID=str(commercial_master.id),
                APPL_NUMBER=commercial_master.COMM_CONTROL_NO,
                REQUEST_TYPE="COMMERCIAL_MASTER",
                REQUEST_NUMBER=commercial_master.COMM_CONTROL_NO,
                PROCESS_STATUS=commercial_master.STATUS,
                DOC_STATUS=commercial_master.STATUS,
                RESPONSE_DATE=timezone.now(),
                RESPONDED_BY=current_user.username if current_user else "System",
                RESPONDER_ROLE=current_user.roles if current_user else "System",
                RESPONSE_COMMENTS=commercial_master.COMMENTS,
                ACTION_PERFORMED=f"Fleet Master {action}",
                CREATED_BY=current_user.username if current_user else "System",
                CREATION_DATE=timezone.now().date(),
                LAST_UPDATED_BY=current_user.username if current_user else "System",
                LAST_UPDATE_DATE=timezone.now().date(),
                NEXT_RESP="APPROVER" if current_user and current_user.roles == "REQUESTOR" else "REQUESTOR"
            )

        return {
                "message": "Commercial Master and related records created/updated successfully",
                "fleet_master": CommercialMasterSchema.from_orm(commercial_master)
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}
        
        

@api.post("/commercial-master/save", response=CommercialMasterResponse)
def create_or_update_commercial_master(
    request,
    COMPANY_NAME: str = Form(...),
    HEADER_ID: Optional[str] = Form(None),
    COMM_PLATE_NO: str = Form(...),
    COMM_PLATE_DATE: Optional[date] = Form(None),
    COMM_PLATE_CATEGORY: str = Form(...),
    CP_ISSUED_AUTHORITY: str = Form(...),
    CP_VEHICLE_TYPE: str = Form(...),
    CP_COLOR: str = Form(...),
    COMMENTS: str = Form(...),
    
    
    insurances: str = Form(...),
    registration: str = Form(None),
    roadtoll: str = Form(...),
    allocation: str = Form(...),
):
    try:
        with transaction.atomic():
            if HEADER_ID:
                commercial_master = CommercialMaster.objects.get(HEADER_ID=HEADER_ID)
                created = False
            else:
                commercial_master = CommercialMaster()
                created = True

            commercial_master_data = {
                "COMPANY_NAME": COMPANY_NAME,
                "COMM_PLATE_DATE": COMM_PLATE_DATE,
                "COMM_PLATE_NO": COMM_PLATE_NO,
                "COMM_PLATE_CATEGORY": COMM_PLATE_CATEGORY,
                "CP_ISSUED_AUTHORITY": CP_ISSUED_AUTHORITY,
                "CP_VEHICLE_TYPE": CP_VEHICLE_TYPE,
                "CP_COLOR": CP_COLOR,
                "COMMENTS": COMMENTS,
                "STATUS": "Draft",
            }
            for key, value in commercial_master_data.items():
                setattr(commercial_master, key, value)
            commercial_master.save(generate_commercial_control_number=False)
                        
            HEADER_ID = commercial_master.HEADER_ID

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
            
            
            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['INS_LINE_ID'] != 'new':
                    try:
                        insurance = Insurance.objects.get(INS_LINE_ID=insurance_item['INS_LINE_ID'], commercial_master=commercial_master)
                    except Insurance.DoesNotExist:
                        insurance = Insurance(commercial_master=commercial_master)
                    
                else:
                    insurance =Insurance(commercial_master=commercial_master)

                for field in ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE',
                              'PLTS_INS_EXPIRY_DATE', 'PLTS_INS_START_DATE', 'CUR_STAT_MOT_INS']:
                    setattr(insurance, field, insurance_item.get(field))
               
                insurance.HEADER_ID = HEADER_ID

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
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )


                insurance.save()

            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['REG_LINE_ID'] != 'new':
                    reg = Registration.objects.get(REG_LINE_ID=reg_item['REG_LINE_ID'], commercial_master=commercial_master)
                else:
                    reg = Registration(commercial_master=commercial_master)

                for field in ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CUR_STAT_REG']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.HEADER_ID = HEADER_ID

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
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                reg.save()

            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['RT_LINE_ID'] != 'new':
                    road = Roadtoll.objects.get(RT_LINE_ID=roadtoll_item['RT_LINE_ID'], commercial_master=commercial_master)
                else:
                    road = Roadtoll(commercial_master=commercial_master)

                for field in ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE', 'CURRENT_STATUS']:
                    setattr(road, field, roadtoll_item.get(field))

                road.HEADER_ID = HEADER_ID

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
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                road.save()


            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['ALLOC_LINE_ID'] != 'new':
                    allocations = Allocation.objects.get(ALLOC_LINE_ID=allocation_item['ALLOC_LINE_ID'], commercial_master=commercial_master)
                else:
                    allocations = Allocation(commercial_master=commercial_master)

                for field in ['COMPANY_NAME', 'DIVISION', 'OPERATING_LOCATION', 'OPERATING_EMIRATES', 'APPICATION_USAGE', 'ALLOCATION_DATE']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.HEADER_ID = HEADER_ID

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
                            commercial_master=commercial_master,
                            HEADER_ID=commercial_master.HEADER_ID
                        )

                allocations.save()

            ApprovalRequest.objects.update_or_create(
                request_number=commercial_master.HEADER_ID,
                defaults={
                    'company_name': commercial_master.COMPANY_NAME,
                    'request_type': 'COMMERCIAL MASTER',
                    'status': commercial_master.STATUS,
                    'comments': commercial_master.COMMENTS,
                    'commercial_master': commercial_master
                }
            )

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
        commercial_master = CommercialMaster.objects.prefetch_related(
            'insurances','registration','roadtoll','allocation'
        ).get(COMM_CONTROL_NO=identifier)
    except CommercialMaster.DoesNotExist:
        try:
            # If not found, try to fetch by header_id
            commercial_master = CommercialMaster.objects.prefetch_related(
                'insurances','registration', 'roadtoll','allocation'
            ).get(HEADER_ID=identifier)
        except CommercialMaster.DoesNotExist:
            return JsonResponse({"error": f"CommercialMaster with identifier {identifier} does not exist"}, status=404)

    return CommercialMasterDetailSchema.from_orm(commercial_master)


@api.get("/commercial-master-by-header/{HEADER_ID}", response=CommercialMasterDetailSchema)
def get_commercial_master_by_header(request, HEADER_ID: str):
    try:
        commercial_master = CommercialMaster.objects.prefetch_related(
            'insurances', 'registration',
            'roadtoll', 'allocation'
        ).get(HEADER_ID=HEADER_ID)
        return CommercialMasterDetailSchema.from_orm(commercial_master)
    except CommercialMaster.DoesNotExist:
        return JsonResponse({"error": f"CommercialMaster with header_id {HEADER_ID} does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    


class CommercialInfoSchema(Schema):
    HEADER_ID: Optional[str] = None
    COMM_CONTROL_NO: Optional[str] = None
    COMPANY_NAME: Optional[str] = None
    COMM_PLATE_NO: Optional[str] = None
    COMM_PLATE_CATEGORY: Optional[str] = None
    CP_ISSUED_AUTHORITY: Optional[str] = None
    CP_VEHICLE_TYPE: Optional[str] = None
    CP_COLOR: Optional[str] = None
    STATUS: Optional[str] = None
    REGISTRATION_NO:Optional[str]=None

@api.get("/commercial-info", response=List[CommercialInfoSchema])
def get_commercial_info(request):
    reg_subquery = CommercialRegistration.objects.filter(commercial_master=OuterRef('pk')).values('REGISTRATION_NO')[:1]
    
    commercial_info = CommercialMaster.objects.annotate(
        REGISTRATION_NO=Subquery(reg_subquery)
    ).values(
        'HEADER_ID',
        'COMM_CONTROL_NO',
        'COMPANY_NAME',
        'COMM_PLATE_NO',
        'COMM_PLATE_CATEGORY',
        'CP_ISSUED_AUTHORITY',
        'CP_VEHICLE_TYPE',
        'CP_COLOR',
        'STATUS',
        'REGISTRATION_NO'
   )
    
    return list(commercial_info)


@api.get("/commercial-control-numbers", response=List[str])
def get_commercial_control_numbers(request):
    commercial_control_number = CommercialMaster.objects.values_list('CommercialControlNumber', flat=True)
    return list(commercial_control_number)


class AttachmentSchema(Schema):
    id: int
    file: Union[str,Any]
    attachment_type: str
    CommercialNumber:str
    upload_date:date
    uploaded_by: Optional[str] = None

@api.get("/commercial-attachments/{commercial_number}", response=List[AttachmentSchema])
def get_attachments(request, commercial_number: str):
    attachments = AttachmentSchema.objects.filter(CommercialNumber=commercial_number)
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
    file: Union[str,Any]
    attachment_type: str
    CommercialNumber:str
    upload_date:date
    uploaded_by: Optional[str] = None



@api.get("/commercial-attachments", response=List[AttachmentSchema])
def get_attachments(request):
    attachments = AttachmentSchema.objects.all()
    return [AttachmentSchema.from_orm(attachment) for attachment in attachments]



@api.get("/unique-commercial-numbers", response=List[str])
def get_unique_commercial_numbers(request):
    unique_commercial_numbers = CommercialAttachment.objects.values_list('COMM_CONTROL_NO', flat=True).distinct()
    return list(filter(None, unique_commercial_numbers))



@api.get("/commercial-master/{commercial_control_number}", response=CommercialMasterDetailSchema)
def get_commercial_master_detail(request, commercial_control_number: str):
    commercial_master = CommercialMaster.objects.prefetch_related('insurances','registration','roadtoll','allocation').get(CommercialControlNumber=commercial_control_number)
    return CommercialMasterDetailSchema.from_orm(commercial_master)


from django.db.models import Q

@api.get("/approval-requests", response=List[Dict])
def get_approval_requests(request):
    fleet_requests = FleetMaster.objects.filter(
        Q(FLEET_CONTROL_NO__startswith='AY-') | Q(FLEET_CONTROL_NO__startswith='ALY')
    ).exclude(
        FLEET_CONTROL_NO=''
    ).order_by('FLEET_CONTROL_NO').values(
        'FLEET_CONTROL_NO', 'COMPANY_NAME', 'STATUS', 'FLEET_CREATION_DATE', 'COMMENTS'
    )

    commercial_requests = CommercialMaster.objects.filter(
        Q(COMM_CONTROL_NO='AY-') | Q(COMM_CONTROL_NO='ALY')
    ).exclude(
        COMM_CONTROL_NO=''
    ).order_by('COMM_CONTROL_NO').values(
        'COMM_CONTROL_NO', 'COMPANY_NAME', 'STATUS', 'COMM_PLATE_DATE', 'COMMENTS'
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

    return combined_requests



@api.get("/approval-requests", response=List[Dict])
def get_approval_requests(request):
    approval_requests = ApprovalRequest.objects.all().values(
        'request_number', 'company_name', 'request_type', 'request_details',
        'status', 'creation_date', 'last_update_date', 'comments'
    )
    
    return [
        {
            'request_number': ar['request_number'],
            'company_name': ar['company_name'],
            'request_type': 'Fleet Master' if ar['request_type'] == 'FLEET' else 'Commercial Master',
            'request_details': ar['request_details'],
            'status': ar['status'],
            'creation_date': ar['creation_date'],
            'last_update_date': ar['last_update_date'],
            'comments': ar['comments']
        }
        for ar in approval_requests
    ]


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
    



@api.post("/send-email")
def send_email(
    request,
    recipient: str = Form(...),
    cc: str = Form(None),
    bcc: str = Form(None),
    subject: str = Form(...),
    data: str = Form(...),
    attachment: Optional[UploadedFile] = File(None)
):
    try:
        # Parse cc and bcc
        cc_list = [email.strip() for email in cc.split(',')] if cc else []
        bcc_list = [email.strip() for email in bcc.split(',')] if bcc else []

        # Parse data
        data_dict = json.loads(data)

        # Render the HTML template
        html_message = render_to_string('ALY_GTD/email_template.html', {'data': data_dict})

        text_message = strip_tags(html_message)

        # Create the email message
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.EMAIL_HOST_USER,
            [recipient],
            cc=cc_list,
            bcc=bcc_list
        )
        
        # Attach the HTML version
        email.attach_alternative(html_message, "text/html")

        if attachment:
            email.attach(
                attachment.name,
                attachment.read(),
                attachment.content_type
            )
       
        email.send(fail_silently=False)
        return {"status": "success", "message": "Email sent successfully"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON in data field"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
    
class TrafficFileInfoSchema(Schema):
    traffic_file_no: Optional[str] = None
    company_name: Optional[str] = None  # Added this line
    trade_license_no: Optional[str] = None
    emirates: Optional[str] = None
    federal_traffic_file_no: Optional[str] = None
    status: Optional[str] = None

@api.get("/traffic-file-info", response=List[TrafficFileInfoSchema])
def get_traffic_file_info(request):
    traffic_file_info = TrafficFileMaster.objects.filter(
        Q(status='active') | Q(status='Active')
    ).values(
        'traffic_file_no',
        'company_name',  # Added this line
        'trade_license_no',
        'emirates',
        'federal_traffic_file_no',
        'status'
    )
    
    return list(traffic_file_info)



# @api.get("/last-approved-fleet/{fleet_control_no}")
# def get_last_approved_fleet(request, fleet_control_no: str):
#     try:
#         last_approved = XXALY_GTD_AUDIT_T.objects.filter(
#             FLEET_CONTROL_NO=fleet_control_no,
#             FLEET_STATUS='Approved'
#         ).order_by('-CREATION_DATE').first()


#         if not last_approved:
#             return {"error": "No approved version found"}
#         # Fetch related data
#         insurances = Insurance.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         permits = Permits.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         gps_data = Gps.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         registrations = Registration.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         fuels = Fuel.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         roadtolls = Roadtoll.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         drivers = Driver.objects.filter(FLEET_CONTROL_NO=fleet_control_no)
#         allocations = Allocation.objects.filter(FLEET_CONTROL_NO=fleet_control_no)

#         return {
#             "fleet_master": {
#                 "COMPANY_NAME": last_approved.COMPANY_NAME,
#                 "VIN_NO": last_approved.VIN_NO,
#                 "MANUFACTURER": last_approved.MANUFACTURER,
#                 "MODEL": last_approved.MODEL,
#                 "VEHICLE_TYPE": last_approved.VEHICLE_TYPE,
#                 "COLOR": last_approved.COLOR,
#                 "FLEET_CATEGORY": last_approved.FLEET_CATEGORY,
#                 "FLEET_SUB_CATEGORY": last_approved.FLEET_SUB_CATEGORY,
#                 "ENGINE_NO": last_approved.ENGINE_NO,
#                 "MODEL_YEAR": last_approved.MODEL_YEAR,
#                 "COUNTRY_OF_ORIGIN": last_approved.COUNTRY_OF_ORIGIN,
#                 "SEATING_CAPACITY": last_approved.SEATING_CAPACITY,
#                 "TONNAGE": last_approved.TONNAGE,
#                 "GROSS_WEIGHT_KG": last_approved.GROSS_WEIGHT_KG,
#                 "EMPTY_WEIGHT_KG": last_approved.EMPTY_WEIGHT_KG,
#                 "PURCHASE_VALUE_AED": last_approved.PURCHASE_VALUE_AED,
#                 "COMMENTS": last_approved.COMMENTS,
#                 "STATUS": last_approved.FLEET_STATUS,
#             },
#             "insurances": [
#                 {
#                     "INS_LINE_ID": insurance.INS_LINE_ID,
#                     "INSURANCE_COMPANY": insurance.INSURANCE_COMPANY,
#                     "POLICY_NO": insurance.POLICY_NO,
#                     "POLICY_DATE": insurance.POLICY_DATE,
#                     "POLICY_EXPIRY_DATE": insurance.POLICY_EXPIRY_DATE,
#                     "PLTS_INS_START_DATE": insurance.PLTS_INS_START_DATE,
#                     "PLTS_INS_EXPIRY_DATE": insurance.PLTS_INS_EXPIRY_DATE,
#                     "CUR_STAT_MOT_INS": insurance.CUR_STAT_MOT_INS,
#                     "InsurancePolicAattachment": insurance.InsurancePolicAattachment,
#                 } for insurance in insurances
#             ],
#             "permits": [
#                 {
#                     "PERMIT_LINE_ID": permit.PERMIT_LINE_ID,
#                     "PERMIT_TYPE": permit.PERMIT_TYPE,
#                     "EMIRATES": permit.EMIRATES,
#                     "ISSUING_AUTHORITY": permit.ISSUING_AUTHORITY,
#                     "PERMIT_NO": permit.PERMIT_NO,
#                     "PERMIT_DATE": permit.PERMIT_DATE,
#                     "PERMIT_EXPIRY_DATE": permit.PERMIT_EXPIRY_DATE,
#                     "CUR_STAT_PERMIT": permit.CUR_STAT_PERMIT,
#                     "PermitColor": permit.PermitColor,
#                     "PermitAattachment": permit.PermitAattachment,
#                 } for permit in permits
#             ],
#             "gps": [
#                 {
#                     "GT_LINE_ID": gps.GT_LINE_ID,
#                     "GPS_DEVICE_NO": gps.GPS_DEVICE_NO,
#                     "GPS_INSTALLATION_DATE": gps.GPS_INSTALLATION_DATE,
#                     "GPS_SERVICE_PROVIDER": gps.GPS_SERVICE_PROVIDER,
#                     "GpsAattachment": gps.GpsAattachment,
#                 } for gps in gps_data
#             ],
#             "registrations": [
#                 {
#                     "REG_LINE_ID": reg.REG_LINE_ID,
#                     "EMIRATES_TRF_FILE_NO": reg.EMIRATES_TRF_FILE_NO,
#                     "REGISTERED_EMIRATES": reg.REGISTERED_EMIRATES,
#                     "FEDERAL_TRF_FILE_NO": reg.FEDERAL_TRF_FILE_NO,
#                     "REG_COMPANY_NAME": reg.REG_COMPANY_NAME,
#                     "TRADE_LICENSE_NO": reg.TRADE_LICENSE_NO,
#                     "REGISTRATION_NO1": reg.REGISTRATION_NO1,
#                     "REGISTRATION_NO": reg.REGISTRATION_NO,
#                     "REGISTRATION_DATE": reg.REGISTRATION_DATE,
#                     "REG_EXPIRY_DATE": reg.REG_EXPIRY_DATE,
#                     "CUR_STAT_REG": reg.CUR_STAT_REG,
#                     "RegCardAttachment": reg.RegCardAttachment,
#                 } for reg in registrations
#             ],
#             "fuels": [
#                 {
#                     "FUEL_LINE_ID": fuel.FUEL_LINE_ID,
#                     "FUEL_TYPE": fuel.FUEL_TYPE,
#                     "MONTHLY_FUEL_LIMIT": fuel.MONTHLY_FUEL_LIMIT,
#                     "FUEL_SERVICE_TYPE": fuel.FUEL_SERVICE_TYPE,
#                     "FUEL_SERVICE_PROVIDER": fuel.FUEL_SERVICE_PROVIDER,
#                     "FUEL_DOCUMENT_NO": fuel.FUEL_DOCUMENT_NO,
#                     "FUEL_DOCUMENT_DATE": fuel.FUEL_DOCUMENT_DATE,
#                     "FUEL_DOC_EXPIRY_DATE": fuel.FUEL_DOC_EXPIRY_DATE,
#                     "CUR_STAT_FUEL_DOC": fuel.CUR_STAT_FUEL_DOC,
#                     "FuelDocumentAttachment": fuel.FuelDocumentAttachment,
#                 } for fuel in fuels
#             ],
#             "roadtolls": [
#                 {
#                     "RT_LINE_ID": roadtoll.RT_LINE_ID,
#                     "EMIRATES": roadtoll.EMIRATES,
#                     "TOLL_TYPE": roadtoll.TOLL_TYPE,
#                     "ACCOUNT_NO": roadtoll.ACCOUNT_NO,
#                     "TAG_NO": roadtoll.TAG_NO,
#                     "ACTIVATION_DATE": roadtoll.ACTIVATION_DATE,
#                     "CURRENT_STATUS": roadtoll.CURRENT_STATUS,
#                     "RoadtollAttachments": roadtoll.RoadtollAttachments,
#                 } for roadtoll in roadtolls
#             ],
#             "drivers": [
#                 {
#                     "ASGN_LINE_ID": driver.ASGN_LINE_ID,
#                     "EMPLOYEE_NAME": driver.EMPLOYEE_NAME,
#                     "DESIGNATION": driver.DESIGNATION,
#                     "CONTACT_NUMBER": driver.CONTACT_NUMBER,
#                     "ASSIGNMENT_DATE": driver.ASSIGNMENT_DATE,
#                     "TRAFFIC_CODE_NO": driver.TRAFFIC_CODE_NO,
#                     "DRIVING_LICENSE_NO": driver.DRIVING_LICENSE_NO,
#                     "LICENSE_TYPE": driver.LICENSE_TYPE,
#                     "PLACE_OF_ISSUE": driver.PLACE_OF_ISSUE,
#                     "LICENSE_EXPIRY_DATE": driver.LICENSE_EXPIRY_DATE,
#                     "GPS_TAG_NO": driver.GPS_TAG_NO,
#                     "GPS_TAG_ASSIGN_DATE": driver.GPS_TAG_ASSIGN_DATE,
#                     "EMPLOYEE_NO": driver.EMPLOYEE_NO,
#                     "DriverAttachments": driver.DriverAttachments,
#                 } for driver in drivers
#             ],
#             "allocations": [
#                 {
#                     "ALLOC_LINE_ID": allocation.ALLOC_LINE_ID,
#                     "COMPANY_NAME": allocation.COMPANY_NAME,
#                     "DIVISION": allocation.DIVISION,
#                     "OPERATING_LOCATION": allocation.OPERATING_LOCATION,
#                     "OPERATING_EMIRATES": allocation.OPERATING_EMIRATES,
#                     "APPICATION_USAGE": allocation.APPICATION_USAGE,
#                     "ALLOCATION_DATE": allocation.ALLOCATION_DATE,
#                     "attachment": allocation.attachment,
#                 } for allocation in allocations
#             ],
#         }
#     except XXALY_GTD_AUDIT_T.DoesNotExist:
#         return {"error": "No approved version found"}


# @api.get("/last-approved-fleet/{fleet_control_no}")
# def get_last_approved_fleet(request, fleet_control_no: str):
#     try:
#         last_approved = XXALY_GTD_AUDIT_T.objects.filter(
#             FLEET_CONTROL_NO=fleet_control_no,
#             FLEET_STATUS='Approved'
#         ).order_by('-CREATION_DATE').first()

#         if not last_approved:
#             return {"error": "No approved version found"}

#         return {
#             "fleet_master": {
#                 "COMPANY_NAME": last_approved.COMPANY_NAME,
#                 "VIN_NO": last_approved.VIN_NO,
#                 "MANUFACTURER": last_approved.MANUFACTURER,
#                 "MODEL": last_approved.MODEL,
#                 "VEHICLE_TYPE": last_approved.VEHICLE_TYPE,
#                 "COLOR": last_approved.COLOR,
#                 "FLEET_CATEGORY": last_approved.FLEET_CATEGORY,
#                 "FLEET_SUB_CATEGORY": last_approved.FLEET_SUB_CATEGORY,
#                 "ENGINE_NO": last_approved.ENGINE_NO,
#                 "MODEL_YEAR": last_approved.MODEL_YEAR,
#                 "COUNTRY_OF_ORIGIN": last_approved.COUNTRY_OF_ORIGIN,
#                 "SEATING_CAPACITY": last_approved.SEATING_CAPACITY,
#                 "TONNAGE": last_approved.TONNAGE,
#                 "GROSS_WEIGHT_KG": last_approved.GROSS_WEIGHT_KG,
#                 "EMPTY_WEIGHT_KG": last_approved.EMPTY_WEIGHT_KG,
#                 "PURCHASE_VALUE_AED": last_approved.PURCHASE_VALUE_AED,
#                 "COMMENTS": last_approved.COMMENTS,
#                 "STATUS": last_approved.FLEET_STATUS,
#             },
#             "insurances": [
#                 {
#                     "INSURANCE_COMPANY": last_approved.INSURANCE_COMPANY,
#                     "POLICY_NO": last_approved.POLICY_NO,
#                     "POLICY_DATE": last_approved.POLICY_DATE,
#                     "POLICY_EXPIRY_DATE": last_approved.POLICY_EXPIRY_DATE,
#                     "POLICY_INSUR_EXPIRY_DATE": last_approved.POLICY_INSUR_EXPIRY_DATE,
#                     "INSUR_CURRENT_STATUS": last_approved.INSUR_CURRENT_STATUS,
#                 }
#             ],
#             "registration": [
#                 {
#                     "REGISTRATION_NO": last_approved.REGISTRATION_NO,
#                     "REGISTRATION_DATE": last_approved.REGISTRATION_DATE,
#                     "REGISTERED_EMIRATES": last_approved.REGISTERED_EMIRATES,
#                     "EMIRATES_TRF_FILE_NO": last_approved.EMIRATES_TRF_FILE_NO,
#                     "FEDERAL_TRF_FILE_NO": last_approved.FEDERAL_TRF_FILE_NO,
#                     "REG_EXPIRY_DATE": last_approved.REG_EXPIRY_DATE,
#                     "REG_COMPANY_NAME": last_approved.REG_COMPANY_NAME,
#                     "REGISTRATION_STATUS": last_approved.REGISTRATION_STATUS,
#                     "TRADE_LICENSE_NO": last_approved.TRADE_LICENSE_NO,
#                 }
#             ],
#         }
#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}


@api.get("/last-approved-fleet/{fleet_control_no}")
def get_last_approved_fleet(request, fleet_control_no: str):
    try:
        with transaction.atomic():
            last_approved = XXALY_GTD_AUDIT_T.objects.filter(
                FLEET_CONTROL_NO=fleet_control_no,
                FLEET_STATUS='Approved'
            ).order_by('-CREATION_DATE').first()

            if not last_approved:
                return {"error": "No approved version found"}

            # Update FleetMaster
            fleet_master = FleetMaster.objects.get(FLEET_CONTROL_NO=fleet_control_no)
            for field in FleetMaster._meta.fields:
                if hasattr(last_approved, field.name):
                    setattr(fleet_master, field.name, getattr(last_approved, field.name))
            fleet_master.save()

            # Update or create Insurance
            insurance, created = Insurance.objects.update_or_create(
                FLEET_CONTROL_NO=fleet_control_no,
                defaults={
                    'INSURANCE_COMPANY': last_approved.INSURANCE_COMPANY,
                    'POLICY_NO': last_approved.POLICY_NO,
                    'POLICY_DATE': last_approved.POLICY_DATE,
                    'POLICY_EXPIRY_DATE': last_approved.POLICY_EXPIRY_DATE,
                    'PLTS_INS_EXPIRY_DATE': last_approved.POLICY_INSUR_EXPIRY_DATE,
                    'CUR_STAT_MOT_INS': last_approved.INSUR_CURRENT_STATUS,
                }
            )

            # Update or create Registration
            registration, created = Registration.objects.update_or_create(
                FLEET_CONTROL_NO=fleet_control_no,
                defaults={
                    'REGISTRATION_NO': last_approved.REGISTRATION_NO,
                    'REGISTRATION_DATE': last_approved.REGISTRATION_DATE,
                    'REGISTERED_EMIRATES': last_approved.REGISTERED_EMIRATES,
                    'EMIRATES_TRF_FILE_NO': last_approved.EMIRATES_TRF_FILE_NO,
                    'FEDERAL_TRF_FILE_NO': last_approved.FEDERAL_TRF_FILE_NO,
                    'REG_EXPIRY_DATE': last_approved.REG_EXPIRY_DATE,
                    'REG_COMPANY_NAME': last_approved.REG_COMPANY_NAME,
                    'CUR_STAT_REG': last_approved.REGISTRATION_STATUS,
                    'TRADE_LICENSE_NO': last_approved.TRADE_LICENSE_NO,
                }
            )
            
            
            latest_record = XXALY_GTD_AUDIT_T.objects.filter(
                FLEET_CONTROL_NO=fleet_control_no
            ).order_by('-CREATION_DATE').first()

            # Create a new audit record with 'Rejected' status
            new_audit = XXALY_GTD_AUDIT_T.objects.create(
                FLEET_CONTROL_NO=fleet_control_no,
                FLEET_STATUS='Rejected',
                # Copy all other fields from latest_record to new_audit
                **{field.name: getattr(latest_record, field.name) for field in XXALY_GTD_AUDIT_T._meta.fields if field.name not in ['id', 'FLEET_STATUS', 'CREATION_DATE']}
            )
            new_audit.CREATION_DATE = timezone.now()
            new_audit.save()

            return {
                "message": "Data reverted successfully",
                "fleet_master": FleetMasterSchema.from_orm(fleet_master),
                "insurance": InsuranceSchema.from_orm(insurance),
                "registration": RegistrationSchema.from_orm(registration),
            }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
