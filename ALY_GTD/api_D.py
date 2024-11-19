

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
from datetime import date
from django.utils import timezone
from pydantic import BaseModel
from requests import Response
from .models import XXALY_GTD_ACTION_HISTORY, XXALY_GTD_LOOKUP_DETAIL, XXALY_GTD_LOOKUP_MASTER, Allocation, ApprovalRequest, Attachment, CommercialAllocation, CommercialAttachment, CommercialInsurance, CommercialMaster, CommercialRegistration, CommercialRoadtoll, Driver, FleetMaster, Fuel, Insurance, Permits, Gps, Registration, Roadtoll, SharedControlNumber, TrafficFileMaster
from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ninja import NinjaAPI, Form, File
from ninja.files import UploadedFile
from typing import List, Optional
from django.db.models import F


class InsuranceSchema(Schema):
    InsuranceCompany: str
    PolicyNumber: str
    PolicyStartDate: date
    VehicleInsuranceStartDate: date
    PolicyExpiryDate: date
    VehicleInsuranceExpiryDate: date
    CurrentStatusMotorInsurance: str
    InsurancePolicAattachment: str
class PermitsSchema(Schema):
    Permit_Type: str
    Permit_Emirates: str
    PermitIssuing: str
    PemtiNum: str
    PemtitDate: date
    PermitExpiryDate: date
    CurrentStatusPermit: str
    PermitAattachment: str
class GpsSchema(Schema):
    GpsDeviceNo: str
    GpsInstallationDate: date
    GpsServiceProvider: str
    GpsAattachment: str

class RegistrationSchema(Schema):
    EmiratesTrafficFileNumber: str
    RegisteredEmirates: str
    FederalTrafficFileNumber: str
    RegisteredCompanyName: str
    TradeLicenseNumber: str
    Reg_No1: str
    Reg_No2: str
    Reg_Date: date
    Reg_Exp_Date: date
    CurrentStatusRegistration: str
    RegCardAttachment: str


class FuelSchema(Schema):
    FuelType: str
    MonthlyFuelLimit_AED: str
    FuelServiceType: str
    FuelServiceProvider: str
    FuelDocumentNumber: str
    FuelDocumentDate: date
    FuelDocumentExpiryDate: date
    CurrentStatusFuelDocument: str
    FuelDocumentAttachment: str

class FleetMasterSchema(Schema):
    FleetCompanyName: Optional[str] = None
    FleetControlNumber: Optional[str] = None
    FleetCreationDate: Optional[date] = None
    VinNumber: Optional[str] = None
    Manufacturer: Optional[str] = None
    Model: Optional[str] = None
    VehicleType: Optional[str] = None
    Color: Optional[str] = None
    FleetCategory: Optional[str] = None
    FleetSubCategory: Optional[str] = None
    EngineNumber: Optional[str] = None
    ModelYear: Optional[str] = None
    CountryofOrigin: Optional[str] = None
    SeatingCapacity: Optional[str] = None
    Tonnage: Optional[float] = None
    GrossWeight_Kg: Optional[float] = None
    EmptyWeight_Kg: Optional[float] = None
    PurchaseValue_AED: Optional[float] = None
    Comments: Optional[str] = None
    FleetStatus: Optional[str] = "Pending for Approval"
    ApplicationUsage: Optional[str] = None
    VehiclePurchaseDoc: Optional[str] = None
    header_id:Optional[str]=None
    
    

class RoadtollSchema(Schema):
    Emirates: str
    TollType: str
    AccountNo: str
    TagNo: str
    ActivationDate: date
    CurrentStatus: str
    RoadtollAttachments: str
    
class DriverSchema(Schema):
    EmployeeName: str
    Designation: str
    ContactNo: str
    DriverAssignmentDate: date
    TrafficCodeNo: str
    DriverLicenseNo: str
    LicenseType: str
    PlaceOfIssue: str
    LicenseExpiryDate: date
    GPSDriverTagNo: str
    GPSDriverTagAssignmentDate: date
    DriverAttachments: str
    
class AllocationSchema(Schema):
    company_name_allocation: str
    division: str
    operating_location: str
    operating_emirates: str
    application_usage: str
    allocation_date: date
    attachment: Optional[str] = None


class FleetMasterResponse(Schema):
    message: str
    fleet_master: Optional[FleetMasterSchema] = None


api = NinjaAPI()

def update_fleet_master_status(fleet_master):
    fleet_master.FleetStatus = FleetMaster.DEFAULT_STATUS
    fleet_master.save()


@api.post("/fleet-master", response=FleetMasterResponse)
def create_or_update_fleet_master(
    request,
    FleetCompanyName: Optional[str] = Form(None),
    FleetControlNumber: Optional[str] = Form(None),
    FleetCreationDate: Optional[date] = Form(None),
    VinNumber: Optional[str] = Form(None),
    Manufacturer: Optional[str] = Form(None),
    Model: Optional[str] = Form(None),
    VehicleType:Optional[str] = Form(None),
    Color: Optional[str] = Form(None),
    FleetCategory:Optional[str] = Form(None),
    FleetSubCategory: Optional[str] = Form(None),
    EngineNumber: Optional[str] = Form(None),
    ModelYear: Optional[str] = Form(None),
    CountryofOrigin: Optional[str] = Form(None),
    SeatingCapacity: Optional[Union[str,int]] = Form(None),
    Tonnage: Optional[float] = Form(None),
    GrossWeight_Kg:Optional[float] = Form(None),
    EmptyWeight_Kg: Optional[float] = Form(None),
    PurchaseValue_AED: Optional[float] = Form(None),
    Comments: Optional[str] = Form(None),
    FleetStatus: Optional[str] = Form("Pending for Approval"),
    ApplicationUsage: Optional[str] = Form(None),
    header_id: Optional[str] = Form(None),

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
            if FleetControlNumber:
                fleet_master = FleetMaster.objects.get(FleetControlNumber=FleetControlNumber)
                created = False
            elif header_id:
                fleet_master = FleetMaster.objects.filter(header_id=header_id).first()
                if fleet_master:
                    created = False
                else:
                    fleet_master = FleetMaster(header_id=header_id)
                    created = True
            else:
                fleet_master = FleetMaster()
                created = True

            fleet_master_data = {
                "FleetCompanyName": FleetCompanyName,
                "FleetCreationDate": FleetCreationDate,
                "VinNumber": VinNumber,
                "Manufacturer": Manufacturer,
                "Model": Model,
                "VehicleType": VehicleType,
                "Color": Color,
                "FleetCategory": FleetCategory,
                "FleetSubCategory": FleetSubCategory,
                "EngineNumber": EngineNumber,
                "ModelYear": ModelYear,
                "CountryofOrigin": CountryofOrigin,
                "SeatingCapacity": SeatingCapacity,
                "Tonnage": Tonnage,
                "GrossWeight_Kg": GrossWeight_Kg,
                "EmptyWeight_Kg": EmptyWeight_Kg,
                "PurchaseValue_AED": PurchaseValue_AED,
                "Comments": Comments,
                "FleetStatus" : FleetStatus or "Pending for Approval",
                "header_id": header_id,
                "ApplicationUsage": ApplicationUsage
            }
            for key, value in fleet_master_data.items():
                setattr(fleet_master, key, value)
            
            fleet_master.save()

            header_id_num = fleet_master.header_id
            fleet_control_number = fleet_master.FleetControlNumber
            Attachment.objects.filter(fleet_master=fleet_master, header_id=header_id).update(FleetNumber=fleet_control_number)

            if is_approver:
                fleet_master.FleetStatus = FleetStatus
            elif all(insurance.Process == 'Pending for Approval' for insurance in fleet_master.insurances.all()) and \
                all(permit.Process == 'Pending for Approval' for permit in fleet_master.permits.all()):
                fleet_master.FleetStatus = 'Pending for Approval'
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
                        FleetNumber=fleet_master.FleetControlNumber
                    )
                fleet_master.save()

            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['id'] != 'new':
                    insurance = Insurance.objects.get(id=insurance_item['id'], fleet_master=fleet_master)
                    if insurance.Process != 'Approved':
                        insurance.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    insurance = Insurance(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['InsuranceCompany', 'PolicyNumber', 'PolicyStartDate', 'PolicyExpiryDate',
                              'VehicleInsuranceStartDate', 'VehicleInsuranceExpiryDate', 'CurrentStatusMotorInsurance']:
                    setattr(insurance, field, insurance_item.get(field))
                
                insurance.FleetControlNumber = fleet_control_number
                insurance.header_id = header_id_num
                fleet_master.FleetStatus = "Pending for Approval"

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
                if permit_item['id'] != 'new':
                    permit = Permits.objects.get(id=permit_item['id'], fleet_master=fleet_master)
                    if permit.Process != 'Approved':
                        permit.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    permit = Permits(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['Permit_Type', 'Permit_Emirates', 'PermitIssuing', 'PemtiNum', 'PemtitDate',
                            'PermitExpiryDate', 'CurrentStatusPermit', 'PermitColor']:
                    setattr(permit, field, permit_item.get(field))

                permit.FleetControlNumber = fleet_control_number
                fleet_master.FleetStatus = "Pending for Approval"
                
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
                if gps_item['id'] != 'new':
                    gp = Gps.objects.get(id=gps_item['id'], fleet_master=fleet_master)
                    if gp.Process != 'Approved':
                        gp.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    gp = Gps(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['GpsDeviceNo', 'GpsInstallationDate', 'GpsServiceProvider']:
                    setattr(gp, field, gps_item.get(field))

                gp.FleetControlNumber = fleet_control_number
                fleet_master.FleetStatus = "Pending for Approval"
                
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
                if reg_item['id'] != 'new':
                    reg = Registration.objects.get(id=reg_item['id'], fleet_master=fleet_master)
                    if reg.Process != 'Approved':
                        reg.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    reg = Registration(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['EmiratesTrafficFileNumber', 'RegisteredEmirates', 'FederalTrafficFileNumber', 'RegisteredCompanyName', 'TradeLicenseNumber', 'Reg_No1', 'Reg_No2', 'Reg_Date', 'Reg_Exp_Date', 'CurrentStatusRegistration']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.FleetControlNumber = fleet_control_number
                reg.header_id = header_id_num
                fleet_master.FleetStatus = "Pending for Approval"

                if is_approver and reg_item.get('Process') == 'Approved':
                    reg.Process = 'Approved'
                else:
                    reg.Process = 'Pending for Approval'
                
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

                if reg.Process == 'Approved':
                    approve_registration(reg.id)

            # Handle Fuel
            if fuel:
                fuel_data = json.loads(fuel)
                for index, fuel_item in enumerate(fuel_data):
                    if fuel_item['id'] != 'new':
                        ful = Fuel.objects.get(id=fuel_item['id'], fleet_master=fleet_master)
                        if ful.Process != 'Approved':
                            ful.Process = FleetStatus if is_approver else 'Pending for Approval'
                    else:
                        ful = Fuel(fleet_master=fleet_master, Process='Pending for Approval')

                    for field in ['FuelType', 'MonthlyFuelLimit_AED', 'FuelServiceType', 'FuelServiceProvider', 'FuelDocumentNumber', 'FuelDocumentDate', 'FuelDocumentExpiryDate', 'CurrentStatusFuelDocument']:
                        value = fuel_item.get(field, '')
                        setattr(ful, field, value if value != '' else None)

                    ful.FleetControlNumber = fleet_control_number
                    ful.header_id = header_id_num
                    fleet_master.FleetStatus = "Pending for Approval"
                    
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
                if roadtoll_item['id'] != 'new':
                    road = Roadtoll.objects.get(id=roadtoll_item['id'], fleet_master=fleet_master)
                    if road.Process != 'Approved':
                        road.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    road = Roadtoll(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['Emirates', 'TollType', 'AccountNo', 'TagNo', 'ActivationDate', 'CurrentStatus']:
                    setattr(road, field, roadtoll_item.get(field))

                road.FleetControlNumber = fleet_control_number
                road.header_id = header_id_num
                fleet_master.FleetStatus = "Pending for Approval"
                
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
                if driver_item['id'] != 'new':
                    drive = Driver.objects.get(id=driver_item['id'], fleet_master=fleet_master)
                    if drive.Process != 'Approved':
                        drive.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    drive = Driver(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['DriverEmployeeNo', 'EmployeeName', 'Designation', 'ContactNo', 'DriverAssignmentDate', 'TrafficCodeNo', 'DriverLicenseNo', 'LicenseType', 'PlaceOfIssue', 'LicenseExpiryDate', 'GPSDriverTagNo', 'GPSDriverTagAssignmentDate']:
                    setattr(drive, field, driver_item.get(field))

                drive.FleetControlNumber = fleet_control_number
                drive.header_id = header_id
                fleet_master.FleetStatus = "Pending for Approval"
                
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
                if allocation_item['id'] != 'new':
                    allocations = Allocation.objects.get(id=allocation_item['id'], fleet_master=fleet_master)
                    if allocations.Process != 'Approved':
                        allocations.Process = FleetStatus if is_approver else 'Pending for Approval'
                else:
                    allocations = Allocation(fleet_master=fleet_master, Process='Pending for Approval')

                for field in ['company_name_allocation', 'division', 'operating_location', 'operating_emirates', 'application_usage', 'allocation_date']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.FleetControlNumber = fleet_control_number
                allocations.header_id = header_id
                fleet_master.FleetStatus = "Pending for Approval"
                
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


            current_user = request.user if request.user.is_authenticated else None
            is_approver = current_user.roles == "APPROVER" if current_user and hasattr(current_user, 'roles') else False
            
            if is_approver:
                action = "Request Approved"
                status = "APPROVED"
            else:
                action = "Submitted for Approval"
                status = "Pending for Approval"

            # Create or update ApprovalRequest
            ApprovalRequest.objects.update_or_create(
                request_number=fleet_master.FleetControlNumber,
                defaults={
                    'application_number': fleet_master.FleetControlNumber,
                    'company_name': fleet_master.FleetCompanyName,
                    'request_type': 'FLEET MASTER',
                    'status': status,
                    'comments': fleet_master.Comments,
                    'fleet_master': fleet_master,
                    'responded_by': current_user.username if current_user else "System",  # Store username
                    'response_role': current_user.roles if current_user and hasattr(current_user, 'roles') else "System",
                    'action': action
                }
            )

            action = "created" if created else "updated"
            
            current_user = request.user if request.user.is_authenticated else None

            XXALY_GTD_ACTION_HISTORY.objects.create(
                APPLICATION_ID=str(fleet_master.id),
                APPL_NUMBER=fleet_master.FleetControlNumber,
                REQUEST_TYPE="FLEET_MASTER",
                REQUEST_NUMBER=fleet_master.FleetControlNumber,
                PROCESS_STATUS=fleet_master.FleetStatus,
                DOC_STATUS=fleet_master.FleetStatus,
                RESPONSE_DATE=timezone.now().date(),
                RESPONDED_BY=current_user.username if current_user else "System",
                RESPONDER_ROLE=current_user.roles if current_user else "System",
                RESPONSE_COMMENTS=fleet_master.Comments,
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
    FleetCompanyName: str = Form(...),
    header_id: Optional[str] = Form(None),
    FleetCreationDate: Optional[date] = Form(None),
    VinNumber: str = Form(...),
    Manufacturer: str = Form(...),
    Model: str = Form(...),
    VehicleType: str = Form(...),
    Color: str = Form(...),
    FleetCategory: str = Form(...),
    FleetSubCategory: str = Form(...),
    EngineNumber: str = Form(...),
    ModelYear: str = Form(...),
    CountryofOrigin: str = Form(...),
    SeatingCapacity: Union[int,str] = Form(...),
    Tonnage: float = Form(...),
    GrossWeight_Kg: float = Form(...),
    EmptyWeight_Kg: float = Form(...),
    PurchaseValue_AED: float = Form(...),
    Comments: str = Form(...),
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
            if header_id:
                fleet_master = FleetMaster.objects.get(header_id=header_id)
                created = False
            else:
                fleet_master = FleetMaster()
                created = True

            fleet_master_data = {
                "FleetCompanyName": FleetCompanyName,
                "FleetCreationDate": FleetCreationDate,
                "VinNumber": VinNumber,
                "Manufacturer": Manufacturer,
                "Model": Model,
                "VehicleType": VehicleType,
                "Color": Color,
                "FleetCategory": FleetCategory,
                "FleetSubCategory": FleetSubCategory,
                "EngineNumber": EngineNumber,
                "ModelYear": ModelYear,
                "CountryofOrigin": CountryofOrigin,
                "SeatingCapacity": SeatingCapacity,
                "Tonnage": Tonnage,
                "GrossWeight_Kg": GrossWeight_Kg,
                "EmptyWeight_Kg": EmptyWeight_Kg,
                "PurchaseValue_AED": PurchaseValue_AED,
                "Comments": Comments,
                "FleetStatus": "Draft",
                "ApplicationUsage": ApplicationUsage
            }
            for key, value in fleet_master_data.items():
                setattr(fleet_master, key, value)
            fleet_master.save(generate_fleet_control_number=False)

            header_id = fleet_master.header_id

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
                        header_id=fleet_master.header_id
                    )
                fleet_master.save(generate_fleet_control_number=False)

            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['id'] != 'new':
                    try:
                        insurance = Insurance.objects.get(id=insurance_item['id'], fleet_master=fleet_master)
                    except Insurance.DoesNotExist:
                        insurance = Insurance(fleet_master=fleet_master)
                else:
                    insurance = Insurance(fleet_master=fleet_master)

                for field in ['InsuranceCompany', 'PolicyNumber', 'PolicyStartDate', 'PolicyExpiryDate',
                              'VehicleInsuranceStartDate', 'VehicleInsuranceExpiryDate', 'CurrentStatusMotorInsurance']:
                    setattr(insurance, field, insurance_item.get(field))
               
                insurance.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                insurance.save()

            permits_data = json.loads(permits)
            for index, permit_item in enumerate(permits_data):
                if permit_item['id'] != 'new':
                    permit = Permits.objects.get(id=permit_item['id'], fleet_master=fleet_master)
                else:
                    permit = Permits(fleet_master=fleet_master)

                for field in ['Permit_Type', 'Permit_Emirates', 'PermitIssuing', 'PemtiNum', 'PemtitDate',
                            'PermitExpiryDate', 'CurrentStatusPermit', 'PermitColor']:
                    setattr(permit, field, permit_item.get(field))

                permit.header_id = header_id
               
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
                            header_id=fleet_master.header_id
                        )

                permit.save()

            gps_data = json.loads(gps)
            for index, gps_item in enumerate(gps_data):
                if gps_item['id'] != 'new':
                    gp = Gps.objects.get(id=gps_item['id'], fleet_master=fleet_master)
                else:
                    gp = Gps(fleet_master=fleet_master)

                for field in ['GpsDeviceNo', 'GpsInstallationDate', 'GpsServiceProvider']:
                    setattr(gp, field, gps_item.get(field))

                gp.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                gp.save()

            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['id'] != 'new':
                    reg = Registration.objects.get(id=reg_item['id'], fleet_master=fleet_master)
                else:
                    reg = Registration(fleet_master=fleet_master)

                for field in ['EmiratesTrafficFileNumber', 'RegisteredEmirates', 'FederalTrafficFileNumber', 'RegisteredCompanyName', 'TradeLicenseNumber', 'Reg_No1', 'Reg_No2', 'Reg_Date', 'Reg_Exp_Date', 'CurrentStatusRegistration']:
                    value = reg_item.get(field, '')
                    setattr(reg, field, value if value != '' else None)

                reg.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                reg.save()

            if fuel:
                fuel_data = json.loads(fuel)
                for index, fuel_item in enumerate(fuel_data):
                    if fuel_item['id'] != 'new':
                        ful = Fuel.objects.get(id=fuel_item['id'], fleet_master=fleet_master)
                    else:
                        ful = Fuel(fleet_master=fleet_master)

                    for field in ['FuelType', 'MonthlyFuelLimit_AED', 'FuelServiceType', 'FuelServiceProvider', 'FuelDocumentNumber', 'FuelDocumentDate', 'FuelDocumentExpiryDate', 'CurrentStatusFuelDocument']:
                        value = fuel_item.get(field, '')
                        setattr(ful, field, value if value != '' else None)

                    ful.header_id = header_id

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
                                header_id=fleet_master.header_id
                            )

                    ful.save()

            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['id'] != 'new':
                    road = Roadtoll.objects.get(id=roadtoll_item['id'], fleet_master=fleet_master)
                else:
                    road = Roadtoll(fleet_master=fleet_master)

                for field in ['Emirates', 'TollType', 'AccountNo', 'TagNo', 'ActivationDate', 'CurrentStatus']:
                    setattr(road, field, roadtoll_item.get(field))

                road.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                road.save()

            driver_data = json.loads(driver)
            for index, driver_item in enumerate(driver_data):
                if driver_item['id'] != 'new':
                    drive = Driver.objects.get(id=driver_item['id'], fleet_master=fleet_master)
                else:
                    drive = Driver(fleet_master=fleet_master)
                for field in ['DriverEmployeeNo', 'EmployeeName', 'Designation', 'ContactNo', 'DriverAssignmentDate', 'TrafficCodeNo', 'DriverLicenseNo', 'LicenseType', 'PlaceOfIssue', 'LicenseExpiryDate', 'GPSDriverTagNo', 'GPSDriverTagAssignmentDate']:
                    setattr(drive, field, driver_item.get(field))

                drive.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                drive.save()

            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['id'] != 'new':
                    allocations = Allocation.objects.get(id=allocation_item['id'], fleet_master=fleet_master)
                else:
                    allocations = Allocation(fleet_master=fleet_master)

                for field in ['company_name_allocation', 'division', 'operating_location', 'operating_emirates', 'application_usage', 'allocation_date']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.header_id = header_id

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
                            header_id=fleet_master.header_id
                        )

                allocations.save()

            ApprovalRequest.objects.update_or_create(
                request_number=fleet_master.header_id,
                defaults={
                    'company_name': fleet_master.FleetCompanyName,
                    'request_type': 'FLEET MASTER',
                    'status': fleet_master.FleetStatus,
                    'comments': fleet_master.Comments,
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
    id: int 
    InsuranceCompany: Optional[str] = None
    PolicyNumber: Optional[str] = None
    PolicyStartDate:  Optional[date] = None
    VehicleInsuranceStartDate:  Optional[date] = None
    PolicyExpiryDate:  Optional[date] = None
    VehicleInsuranceExpiryDate:  Optional[date] = None
    CurrentStatusMotorInsurance: Optional[str] = None
    InsurancePolicAattachment: Optional[str] = None
    Process:Optional[str]=None

class PermitsSchema(Schema):
    id: int 
    Permit_Type: Optional[str] = None
    Permit_Emirates: Optional[str] = None
    PermitIssuing: Optional[str] = None
    PemtiNum: Optional[str] = None
    PemtitDate:  Optional[date] = None
    PermitExpiryDate:  Optional[date] = None
    CurrentStatusPermit: Optional[str] = None
    PermitColor: Optional[str] = None
    PermitAattachment: Optional[str] = None
    Process:Optional[str]=None

class GpsSchema(Schema):
    id: int 
    GpsDeviceNo: Optional[str] = None
    GpsInstallationDate:  Optional[date] = None
    GpsServiceProvider: Optional[str] = None
    GpsAattachment: Optional[str] = None
    Process:Optional[str]=None

class RegistrationSchema(Schema):
    id: int 
    EmiratesTrafficFileNumber: Optional[str] = None
    RegisteredEmirates: Optional[str] = None
    FederalTrafficFileNumber: Optional[str] = None
    RegisteredCompanyName: Optional[str] = None
    TradeLicenseNumber: Optional[str] = None
    Reg_No1: Optional[str] = None
    Reg_No2: Optional[str] = None
    Reg_Date:  Optional[date] = None
    Reg_Exp_Date:  Optional[date] = None
    CurrentStatusRegistration: Optional[str] = None
    RegCardAttachment: Optional[str] = None
    Process:Optional[str]=None


class FuelSchema(Schema):
    id: int 
    FuelType: Optional[str] = None
    MonthlyFuelLimit_AED: Optional[str] = None
    FuelServiceType: Optional[str] = None
    FuelServiceProvider: Optional[str] = None
    FuelDocumentNumber: Optional[str] = None
    FuelDocumentDate: Optional[date] = None
    FuelDocumentExpiryDate:  Optional[date] = None
    CurrentStatusFuelDocument: Optional[str] = None
    FuelDocumentAttachment: Optional[str] = None
    Process:Optional[str]=None


class RoadtollSchema(Schema):
    id: int 
    Emirates: Optional[str] = None
    TollType: Optional[str] = None
    AccountNo: Optional[str] = None
    TagNo: Optional[str] = None
    ActivationDate: Optional[date] = None
    CurrentStatus: Optional[str] = None
    RoadtollAttachments: Optional[str] = None
    Process:Optional[str]=None

    
class DriverSchema(Schema):
    id: int 
    EmployeeName: Optional[str] = None
    Designation: Optional[str] = None
    ContactNo: Optional[str] = None
    DriverAssignmentDate: Optional[date] = None
    TrafficCodeNo: Optional[str] = None
    DriverLicenseNo: Optional[str] = None
    LicenseType: Optional[str] = None
    PlaceOfIssue: Optional[str] = None
    LicenseExpiryDate: Optional[date] = None
    GPSDriverTagNo: Optional[str] = None
    GPSDriverTagAssignmentDate: Optional[date] = None
    DriverAttachments: Optional[str] = None
    DriverEmployeeNo:Optional[str]=None
    Process:Optional[str]=None

    
    
class AllocationSchema(Schema):
    id: int 
    company_name_allocation: Optional[str] = None
    division: Optional[str] = None
    operating_location: Optional[str] = None
    operating_emirates: Optional[str] = None
    application_usage: Optional[str] = None
    allocation_date: Optional[date] = None
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
        # Try to fetch by FleetControlNumber first
        fleet_master = FleetMaster.objects.prefetch_related(
            'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(FleetControlNumber=identifier)
    except FleetMaster.DoesNotExist:
        try:
            # If not found, try to fetch by header_id
            fleet_master = FleetMaster.objects.prefetch_related(
                'insurances', 'gps', 'permits', 'registration', 'fuel', 'roadtoll', 'driver', 'allocation'
            ).get(header_id=identifier)
        except FleetMaster.DoesNotExist:
            return JsonResponse({"error": f"FleetMaster with identifier {identifier} does not exist"}, status=404)

    return FleetMasterDetailSchema.from_orm(fleet_master)



@api.get("/fleet-master-by-header/{header_id}", response=FleetMasterDetailSchema)
def get_fleet_master_by_header(request, header_id: str):
    try:
        fleet_master = FleetMaster.objects.prefetch_related(
            'insurances', 'registration', 'permits', 'gps',
            'fuel', 'roadtoll', 'driver', 'allocation'
        ).get(header_id=header_id)
        return FleetMasterDetailSchema.from_orm(fleet_master)
    except FleetMaster.DoesNotExist:
        return JsonResponse({"error": f"FleetMaster with header_id {header_id} does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)




class FleetInfoSchema(Schema):
    header_id: Optional[str] = None
    FleetControlNumber: Optional[str]=None
    VinNumber: Optional[str]=None
    Manufacturer: Optional[str]=None
    Model: Optional[str]=None
    EngineNumber: Optional[str]=None
    FleetStatus:Optional[str]=None
    Reg_No2: Optional[str] = None

from django.db.models import F, OuterRef, Subquery

@api.get("/fleet-info", response=List[FleetInfoSchema])
def get_fleet_info(request):
    reg_subquery = Registration.objects.filter(fleet_master=OuterRef('pk')).values('Reg_No2')[:1]
    
    fleet_info = FleetMaster.objects.annotate(
        Reg_No2=Subquery(reg_subquery)
    ).values(
        'header_id',
        'FleetControlNumber',
        'VinNumber',
        'Manufacturer',
        'Model',
        'EngineNumber',
        'FleetStatus',
        'Reg_No2'
       
    )
    
    return list(fleet_info)






@api.get("/fleet-control-numbers", response=List[str])
def get_fleet_control_numbers(request):
    fleet_control_numbers = FleetMaster.objects.values_list('FleetControlNumber', flat=True)
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
    unique_fleet_numbers = Attachment.objects.values_list('FleetControlNumber', flat=True).distinct()
    return list(filter(None, unique_fleet_numbers))


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
            FleetControlNumber=instance.FleetControlNumber,
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
    approved_vehicle_count_subquery = Registration.objects.filter(
        EmiratesTrafficFileNumber=OuterRef('TRAFFIC_FILE_NO'),
        Process='Approved'  # Only count approved registrations
    ).values('EmiratesTrafficFileNumber').annotate(
        count=Count('*')
    ).values('count')

    # Annotate TrafficFileMaster with the count of approved vehicles
    traffic_files = TrafficFileMaster.objects.annotate(
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

def approve_registration(registration_id):
    with transaction.atomic():
        registration = Registration.objects.select_for_update().get(id=registration_id)
        if registration.Process != 'Approved':
            registration.Process = 'Approved'
            registration.save()

            # Update the NO_OF_VEHICLES in TrafficFileMaster
            traffic_file = TrafficFileMaster.objects.select_for_update().get(
                TRAFFIC_FILE_NO=registration.EmiratesTrafficFileNumber
            )
            traffic_file.NO_OF_VEHICLES = Registration.objects.filter(
                EmiratesTrafficFileNumber=traffic_file.TRAFFIC_FILE_NO,
                Process='Approved'
            ).count()
            traffic_file.save()

    return {"message": "Registration approved and vehicle count updated successfully"}

@api.post("/approve-registration/{registration_id}")
def approve_registration_endpoint(request, registration_id: int):
    return approve_registration(registration_id)

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
        approved_count_subquery = Registration.objects.filter(
            EmiratesTrafficFileNumber=OuterRef('TRAFFIC_FILE_NO'),
            Process='Approved'
        ).values('EmiratesTrafficFileNumber').annotate(
            count=Count('*')
        ).values('count')

        traffic_file = TrafficFileMaster.objects.annotate(
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
    except TrafficFileMaster.DoesNotExist:
        raise Http404("Traffic file not found")
    
# @api.get("/traffic-files/{TRAFFIC_FILE_NO}", response=List[TrafficFileResponseSchema])
# def get_specific_traffic_file(request, TRAFFIC_FILE_NO: str):
#     traffic_files = TrafficFileMaster.objects.filter(TRAFFIC_FILE_NO=TRAFFIC_FILE_NO)
#     if not traffic_files:
#         return Response({"error": "Traffic file not found"}, status=404)
#     return list(traffic_files)







# class TrafficFileSchema(Schema):
#     TRAFFIC_FILE_NO: str
#     COMPANY_NAME: str
#     TRADE_LICENSE_NO: str
#     EMIRATES: str
#     FEDERAL_TRAFFIC_FILE_NO: str
#     SALIK_ACCOUNT_NO: Union[str,int]
#     STATUS: str
    


# class TrafficFileResponse(Schema):
#     message: str
#     traffic_file: Optional[TrafficFileSchema] = None

# @api.post("/traffic-file-master", response=TrafficFileResponse)
# def create_or_update_traffic_file_master(
#     request,
#     TRAFFIC_FILE_ID: str = Form(...),
#     TRAFFIC_FILE_NO: str = Form(...),
#     COMPANY_NAME: str = Form(...),
#     TRADE_LICENSE_NO: str = Form(...),
#     EMIRATES: str = Form(...),
#     FEDERAL_TRAFFIC_FILE_NO: str = Form(...),
#     SALIK_ACCOUNT_NO: str = Form(...),
#     STATUS: str = Form(...),
#     COMMENTS: str = Form(None),
#     ACTION_CODE: str = Form(None),
#     ACTION: str = Form(None),
#     RECORD_STATUS: str = Form(None),
#     ATTRIBUTE1: Optional[str] = Form(None),
#     ATTRIBUTE2: Optional[str] = Form(None),
#     ATTRIBUTE3: Optional[str] = Form(None),
#     ATTRIBUTE4: Optional[str] = Form(None),
#     ATTRIBUTE5: Optional[str] = Form(None),
#     ATTRIBUTE6: Optional[str] = Form(None),
#     ATTRIBUTE7: Optional[str] = Form(None),
#     ATTRIBUTE8: Optional[str] = Form(None),
#     ATTRIBUTE9: Optional[str] = Form(None),
#     ATTRIBUTE10: Optional[str] = Form(None),
    
# ):
#     try:
#         with transaction.atomic():
#             if TRAFFIC_FILE_ID != 'new':
#                 try:
#                     traffic_file = TrafficFileMaster.objects.get(TRAFFIC_FILE_ID=TRAFFIC_FILE_ID)
#                     created = False
#                 except TrafficFileMaster.DoesNotExist:
#                     return {"message": f"Error: Traffic File with id {TRAFFIC_FILE_ID} does not exist"}
#             else:
#                 traffic_file = TrafficFileMaster()
#                 created = True

#             # Update TrafficFileMaster fields
#             traffic_file_fields = [
#                 "TRAFFIC_FILE_NO", "COMPANY_NAME", "TRADE_LICENSE_NO", "EMIRATES",
#                 "FEDERAL_TRAFFIC_FILE_NO", "SALIK_ACCOUNT_NO", "STATUS", "COMMENTS",
#                 "ACTION_CODE", "ACTION", "RECORD_STATUS", "ATTRIBUTE1", "ATTRIBUTE2",
#                 "ATTRIBUTE3", "ATTRIBUTE4", "ATTRIBUTE5","ATTRIBUTE6","ATTRIBUTE7",
#                 "ATTRIBUTE8","ATTRIBUTE9","ATTRIBUTE10"

#             ]
           
#             for field in traffic_file_fields:
#                 value = locals().get(field)
#                 if value is not None:
#                     setattr(traffic_file, field, value)

#             if created:
#                 traffic_file.CREATION_DATE = timezone.now()
#                 traffic_file.CREATED_BY = request.user.username if request.user.is_authenticated else 'Anonymous'

#             traffic_file.LAST_UPDATE_DATE = timezone.now()
#             traffic_file.LAST_UPDATED_BY = request.user.username if request.user.is_authenticated else 'Anonymous'

#             traffic_file.save()

#             # Determine the action based on the user's role
#             current_user = request.user if request.user.is_authenticated else None
#             is_approver = current_user.roles == "APPROVER" if current_user and hasattr(current_user, 'roles') else False
           
#             if is_approver:
#                 approval_action = "Request Approved"
#                 approval_status = "Active"
#             else:
#                 approval_action = "Submitted for Approval"
#                 approval_status = "New"

#             # Create or update ApprovalRequest
#             ApprovalRequest.objects.update_or_create(
#                 request_number=traffic_file.TRAFFIC_FILE_NO,
#                 defaults={
#                     'application_number': traffic_file.TRAFFIC_FILE_NO,
#                     'company_name': traffic_file.COMPANY_NAME,
#                     'request_type': 'TRAFFIC FILE MASTER',
#                     'status': approval_status,
#                     'comments': traffic_file.COMMENTS,
#                     'traffic_file_master': traffic_file,
#                     'responded_by': current_user.username if current_user else "System",
#                     'response_role': current_user.roles if current_user and hasattr(current_user, 'roles') else "System",
#                     'action': approval_action
#                 }
#             )

#             # Create XXALY_GTD_ACTION_HISTORY entry
#             XXALY_GTD_ACTION_HISTORY.objects.create(
#                 APPLICATION_ID=str(traffic_file.TRAFFIC_FILE_ID),
#                 APPL_NUMBER=traffic_file.TRAFFIC_FILE_NO,
#                 REQUEST_TYPE="TRAFFIC_FILE_MASTER",
#                 REQUEST_NUMBER=traffic_file.TRAFFIC_FILE_NO,
#                 PROCESS_STATUS=approval_status,
#                 DOC_STATUS=approval_status,
#                 RESPONSE_DATE=timezone.now().date(),
#                 RESPONDED_BY=current_user.username if current_user else "System",
#                 RESPONDER_ROLE=current_user.roles if current_user else "System",
#                 RESPONSE_COMMENTS=traffic_file.COMMENTS,
#                 ACTION_PERFORMED=f"Traffic File Master {'created' if created else 'updated'}",
#                 CREATED_BY=current_user.username if current_user else "System",
#                 CREATION_DATE=timezone.now().date(),
#                 LAST_UPDATED_BY=current_user.username if current_user else "System",
#                 LAST_UPDATE_DATE=timezone.now().date(),
#                 NEXT_RESP="APPROVER" if current_user and current_user.roles == "REQUESTOR" else "REQUESTOR"
#             )

#             action = "created" if created else "updated"
#             return {
#                 "message": f"Traffic File Master {action} successfully",
#                 "traffic_file": TrafficFileSchema(
#                     TRAFFIC_FILE_ID=traffic_file.TRAFFIC_FILE_ID,
#                     TRAFFIC_FILE_NO=traffic_file.TRAFFIC_FILE_NO,
#                     COMPANY_NAME=traffic_file.COMPANY_NAME,
#                     TRADE_LICENSE_NO=traffic_file.TRADE_LICENSE_NO,
#                     EMIRATES=traffic_file.EMIRATES,
#                     FEDERAL_TRAFFIC_FILE_NO=traffic_file.FEDERAL_TRAFFIC_FILE_NO,
#                     SALIK_ACCOUNT_NO=traffic_file.SALIK_ACCOUNT_NO,
#                     STATUS=traffic_file.STATUS,
#                 ).dict()
#             }

#     except Exception as e:
#         return {"message": f"Error occurred: {str(e)}"}




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
    ATTRIBUTE1: Optional[str] = Form(None),
    ATTRIBUTE2: Optional[str] = Form(None),
    ATTRIBUTE3: Optional[str] = Form(None),
    ATTRIBUTE4: Optional[str] = Form(None),
    ATTRIBUTE5: Optional[str] = Form(None),
    ATTRIBUTE6: Optional[str] = Form(None),
    ATTRIBUTE7: Optional[str] = Form(None),
    ATTRIBUTE8: Optional[str] = Form(None),
    ATTRIBUTE9: Optional[str] = Form(None),
    ATTRIBUTE10: Optional[str] = Form(None),
):
    try:
        with transaction.atomic():
            if TRAFFIC_FILE_ID != 'new':
                try:
                    traffic_file = TrafficFileMaster.objects.get(TRAFFIC_FILE_ID=TRAFFIC_FILE_ID)
                    created = False
                except TrafficFileMaster.DoesNotExist:
                    return {"message": f"Error: Traffic File with id {TRAFFIC_FILE_ID} does not exist"}
            else:
                traffic_file = TrafficFileMaster()
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
            approved_vehicle_count = Registration.objects.filter(
                EmiratesTrafficFileNumber=traffic_file.TRAFFIC_FILE_NO,
                Process='Approved'
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





class CommercialInsuranceSchema(Schema):
    InsuranceCompany : str
    PolicyNumber : str
    PolicyStartDate : str
    VehicleInsuranceStartDate : str
    PolicyExpiryDate : date
    VehicleInsuranceExpiryDate : date
    CurrentStatusMotorInsurance : str
    InsurancePolicAattachment:str
    

class CommercialRegistrationSchema(Schema):
    EmiratesTrafficFileNumber: str
    RegisteredEmirates: str
    FederalTrafficFileNumber: str
    RegisteredCompanyName: str
    TradeLicenseNumber: str
    Reg_No1: str
    Reg_No2: str
    Reg_Date: date
    Reg_Exp_Date: date
    CurrentStatusRegistration: str
    RegCardAttachment: str
    
    
class CommercialRoadtollSchema(Schema):
    Emirates: str
    TollType: str
    AccountNo: str
    TagNo: str
    ActivationDate: date
    CurrentStatus: str
    RoadtollAttachments: str
    


class CommercialAllocationSchema(Schema):
    company_name_allocation: str
    division: str
    operating_location: str
    operating_emirates: str
    application_usage: str
    allocation_date: date
    attachment: Optional[str] = None
    
    
    
class CommercialMasterSchema(Schema):
    CompanyName: str
    CommercialControlNumber: Optional[str] = None
    Date: Optional[date] = None
    PlateNo: str
    Category: str
    IssuedAuthority: str
    VehicleType: str
    Color: str
    Comments: Optional[str] = None
    Status: Optional[str] = "Pending for Approval"



class CommercialMasterResponse(Schema):
    message: str
    commercial_master: Optional[CommercialMasterSchema] = None

@api.post("/commercial-master", response=CommercialMasterResponse)
def create_or_update_commercial_master(
    request,
    CompanyName: str = Form(...),
    CommercialControlNumber: Optional[str] = Form(None),
    Date: Optional[date] = Form(None),
    PlateNo: str = Form(...),
    Category: str = Form(...),
    IssuedAuthority: str = Form(...),
    VehicleType: str = Form(...),
    Color: str = Form(...),
    Comments: str = Form(...),
    Status: Optional[str] = Form("Pending for Approval"),
    
    insurances: str = Form(...),
    registration: str = Form(None),
    roadtoll: str = Form(...),
    allocation: str = Form(...),
):
    try:
        with transaction.atomic():
            if CommercialControlNumber:
                commercial_master = CommercialMaster.objects.get(CommercialControlNumber=CommercialControlNumber)
                created = False
            else:
                commercial_master = CommercialMaster()
                created = True

            commercial_master_data = {
                "CompanyName": CompanyName,
                "Date": Date,
                "PlateNo": PlateNo,
                "Category": Category,
                "IssuedAuthority": IssuedAuthority,
                "VehicleType": VehicleType,
                "Color": Color,
                "Comments": Comments,
                "Status": Status,
            }
            for key, value in commercial_master_data.items():
                setattr(commercial_master, key, value)
            commercial_master.save()
            commercial_control_number = commercial_master.CommercialControlNumber

            # Handle Insurance data
            insurance_data = json.loads(insurances)
            for index, insurance_item in enumerate(insurance_data):
                if insurance_item['id'] != 'new':
                    insurance = CommercialInsurance.objects.get(id=insurance_item['id'], commercial_master=commercial_master)
                else:
                    insurance = CommercialInsurance(commercial_master=commercial_master)

                for field in ['InsuranceCompany', 'PolicyNumber', 'PolicyStartDate', 'PolicyExpiryDate',
                              'VehicleInsuranceStartDate', 'VehicleInsuranceExpiryDate', 'CurrentStatusMotorInsurance']:
                    setattr(insurance, field, insurance_item.get(field))
                
                insurance.CommercialControlNumber = commercial_control_number

                file_key = f'InsurancePolicAattachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    existing_files = json.loads(insurance.InsurancePolicAattachment) if insurance.InsurancePolicAattachment else []
                    new_files = []
                    for file in files:
                        file_path = default_storage.save(f'media/documents/commercial_insurance/{file.name}', ContentFile(file.read()))
                        new_files.append(file_path)
                        
                        CommercialAttachment.objects.create(
                            file=file_path,
                            attachment_type='InsuranceInfo',
                            commercial_master=commercial_master,
                            CommercialControlNumber=commercial_master.CommercialControlNumber
                        )

                    all_files = existing_files + new_files
                    insurance.InsurancePolicAattachment = json.dumps(all_files)

                insurance.save()

            # Handle Registration  
            # Handle Registration data
            registration_data = json.loads(registration)
            for index, reg_item in enumerate(registration_data):
                if reg_item['id'] != 'new':
                    reg = CommercialRegistration.objects.get(id=reg_item['id'], commercial_master=commercial_master)
                else:
                    reg = CommercialRegistration(commercial_master=commercial_master)

                for field in ['EmiratesTrafficFileNumber', 'RegisteredEmirates', 'FederalTrafficFileNumber', 'RegisteredCompanyName', 'TradeLicenseNumber', 'Reg_No1', 'Reg_No2', 'Reg_Date', 'Reg_Exp_Date', 'CurrentStatusRegistration']:
                    setattr(reg, field, reg_item.get(field))

                reg.CommercialControlNumber = commercial_control_number

                file_key = f'RegCardAttachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    existing_files = json.loads(reg.RegCardAttachment) if reg.RegCardAttachment else []
                    new_files = []
                    for file in files:
                        file_path = default_storage.save(f'media/documents/commercial_registration/{file.name}', ContentFile(file.read()))
                        new_files.append(file_path)
                        
                        CommercialAttachment.objects.create(
                            file=file_path,
                            attachment_type='RegistrationInfo',
                            commercial_master=commercial_master,
                            CommercialControlNumber=commercial_master.CommercialControlNumber
                        )

                    all_files = existing_files + new_files
                    reg.RegCardAttachment = json.dumps(all_files)

                reg.save()

            # Handle Roadtoll data
            roadtoll_data = json.loads(roadtoll)
            for index, roadtoll_item in enumerate(roadtoll_data):
                if roadtoll_item['id'] != 'new':
                    road = CommercialRoadtoll.objects.get(id=roadtoll_item['id'], commercial_master=commercial_master)
                else:
                    road = CommercialRoadtoll(commercial_master=commercial_master)

                for field in ['Emirates', 'TollType', 'AccountNo', 'TagNo', 'ActivationDate', 'CurrentStatus']:
                    setattr(road, field, roadtoll_item.get(field))

                road.CommercialControlNumber = commercial_control_number

                file_key = f'RoadtollAttachments_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    existing_files = json.loads(road.RoadtollAttachments) if road.RoadtollAttachments else []
                    new_files = []
                    for file in files:
                        file_path = default_storage.save(f'media/documents/commercial_roadtoll/{file.name}', ContentFile(file.read()))
                        new_files.append(file_path)
                        
                        CommercialAttachment.objects.create(
                            file=file_path,
                            attachment_type='RoadtollInfo',
                            commercial_master=commercial_master,
                            CommercialControlNumber=commercial_master.CommercialControlNumber
                        )

                    all_files = existing_files + new_files
                    road.RoadtollAttachments = json.dumps(all_files)

                road.save()

            # Handle Allocation data
            allocation_data = json.loads(allocation)
            for index, allocation_item in enumerate(allocation_data):
                if allocation_item['id'] != 'new':
                    allocations = CommercialAllocation.objects.get(id=allocation_item['id'], commercial_master=commercial_master)
                else:
                    allocations = CommercialAllocation(commercial_master=commercial_master)

                for field in ['company_name_allocation', 'division', 'operating_location', 'operating_emirates', 'application_usage', 'allocation_date']:
                    setattr(allocations, field, allocation_item.get(field))

                allocations.CommercialControlNumber = commercial_control_number

                file_key = f'attachment_{index}'
                if file_key in request.FILES:
                    files = request.FILES.getlist(file_key)
                    existing_files = json.loads(allocations.attachment) if allocations.attachment else []
                    new_files = []
                    for file in files:
                        file_path = default_storage.save(f'media/documents/commercial_allocation/{file.name}', ContentFile(file.read()))
                        new_files.append(file_path)
                        
                        CommercialAttachment.objects.create(
                            file=file_path,
                            attachment_type='AllocationInfo',
                            commercial_master=commercial_master,
                            CommercialControlNumber=commercial_master.CommercialControlNumber
                        )

                    all_files = existing_files + new_files
                    allocations.attachment = json.dumps(all_files)

                allocations.save()

            ApprovalRequest.objects.update_or_create(
                request_number=commercial_master.CommercialControlNumber,
                defaults={
                    'company_name': commercial_master.CompanyName,
                    'request_type': 'COMMERCIAL MASTER',
                    'status': commercial_master.Status,
                    'comments': commercial_master.Comments,
                    'commercial_master': commercial_master
                }
            )

            action = "created" if created else "updated"
            return {
                "message": f"Commercial Master and related records {action} successfully",
                "commercial_master": CommercialMasterSchema.from_orm(commercial_master)
            }

    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

class CommercialInsuranceSchema(Schema):
    id: int 
    InsuranceCompany: Optional[str] = None
    PolicyNumber: Optional[str] = None
    PolicyStartDate:  Optional[date] = None
    VehicleInsuranceStartDate:  Optional[date] = None
    PolicyExpiryDate:  Optional[date] = None
    VehicleInsuranceExpiryDate:  Optional[date] = None
    CurrentStatusMotorInsurance: Optional[str] = None
    InsurancePolicAattachment: Optional[str] = None




class CommercialRegistrationSchema(Schema):
    id: int 
    EmiratesTrafficFileNumber: Optional[str] = None
    RegisteredEmirates: Optional[str] = None
    FederalTrafficFileNumber: Optional[str] = None
    RegisteredCompanyName: Optional[str] = None
    TradeLicenseNumber: Optional[str] = None
    Reg_No1: Optional[str] = None
    Reg_No2: Optional[str] = None
    Reg_Date:  Optional[date] = None
    Reg_Exp_Date:  Optional[date] = None
    CurrentStatusRegistration: Optional[str] = None
    RegCardAttachment: Optional[str] = None


    
class CommercialRoadtollSchema(Schema):
    id: int 
    Emirates: Optional[str] = None
    TollType: Optional[str] = None
    AccountNo: Optional[str] = None
    TagNo: Optional[str] = None
    ActivationDate: Optional[date] = None
    CurrentStatus: Optional[str] = None
    RoadtollAttachments: Optional[str] = None
    

    
    
class CommercialAllocationSchema(Schema):
    id: int 
    company_name_allocation: Optional[str] = None
    division: Optional[str] = None
    operating_location: Optional[str] = None
    operating_emirates: Optional[str] = None
    application_usage: Optional[str] = None
    allocation_date: Optional[date] = None
    attachment: Optional[str] = None


class CommercialMasterDetailSchema(CommercialMasterSchema):
    insurances: List[CommercialInsuranceSchema]
    registration: List[CommercialRegistrationSchema]
    roadtoll:List[CommercialRoadtollSchema]
    allocation:List[CommercialAllocationSchema]



@api.get("/commercial-master/{commercial_control_number}", response=CommercialMasterDetailSchema)
def get_fleet_master_detail(request, commercial_control_number: str):
    commercial_master = CommercialMaster.objects.prefetch_related('insurances','registration','roadtoll','allocation').get(CommercialControlNumber=commercial_control_number)
    return CommercialMasterDetailSchema.from_orm(commercial_master)




@api.get("/commercial_control_numbers", response=List[str])
def get_fleet_control_numbers(request):
    commercial_control_number = CommercialMaster.objects.values_list('CommercialControlNumber', flat=True)
    return list(commercial_control_number)



class CommercialAttachmentSchema(Schema):
    id: int
    file: str
    attachment_type: str
    CommercialControlNumber: str  # Changed from FleetControlNumber
    upload_date: date
    uploaded_by: Optional[str] = None

@api.get("/commercial-attachments/{commercial_control_number}", response=List[CommercialAttachmentSchema])
def get_attachments(request, commercial_control_number: str):
    attachments = CommercialAttachment.objects.filter(CommercialControlNumber=commercial_control_number)
    return [
        CommercialAttachmentSchema(
            id=attachment.id,
            file=attachment.file,
            attachment_type=attachment.attachment_type,
            CommercialControlNumber=attachment.CommercialControlNumber,
            upload_date=attachment.upload_date.date(),
            uploaded_by=attachment.uploaded_by
        )
        for attachment in attachments
    ]

class CommercialAttachmentSchema(Schema):
    id: int
    file: str
    attachment_type: str
    CommercialControlNumber: str
    upload_date:date
    uploaded_by: Optional[str] = None

@api.get("/commercial-attachments", response=List[CommercialAttachmentSchema])
def get_attachments(request):
    attachments = CommercialAttachment.objects.all()
    return [
        CommercialAttachmentSchema(
            id=attachment.id,
            file=attachment.file,
            attachment_type=attachment.attachment_type,
            CommercialControlNumber=attachment.CommercialControlNumber,
            upload_date=attachment.upload_date.date(),  # Convert datetime to date
            uploaded_by=attachment.uploaded_by
        )
        for attachment in attachments
    ]
    
    
@api.get("/unique-commercial-numbers", response=List[str])
def get_unique_fleet_numbers(request):
    unique_fleet_numbers = CommercialAttachment.objects.values_list('CommercialControlNumber', flat=True).distinct()
    return list(filter(None, unique_fleet_numbers))



from typing import List, Dict

@api.get("/approval-requests", response=List[Dict])
def get_approval_requests(request):
    fleet_requests = FleetMaster.objects.filter(
        FleetControlNumber__startswith='ALY'
    ).exclude(
        FleetControlNumber=''
    ).order_by('FleetControlNumber').values(
        'FleetControlNumber', 'FleetCompanyName', 'FleetStatus', 'FleetCreationDate', 'Comments'
    )

    commercial_requests = CommercialMaster.objects.filter(
        CommercialControlNumber__startswith='ALY'
    ).exclude(
        CommercialControlNumber=''
    ).order_by('CommercialControlNumber').values(
        'CommercialControlNumber', 'CompanyName', 'Status', 'Date', 'Comments'
    )

    traffic_requests = TrafficFileMaster.objects.exclude(
        TRAFFIC_FILE_NO=''
    ).order_by('TRAFFIC_FILE_NO').values(
        'TRAFFIC_FILE_NO', 'COMPANY_NAME', 'STATUS', 'CREATION_DATE', 'LAST_UPDATE_DATE', 'COMMENTS'
    )

    combined_requests = []

    for fr in fleet_requests:
        combined_requests.append({
            'request_number': fr['FleetControlNumber'],
            'company_name': fr['FleetCompanyName'],
            'request_type': 'Fleet Master',
            'request_details': 'Modified',
            'status': fr['FleetStatus'],
            'creation_date': fr['FleetCreationDate'],
            'last_update_date': fr['FleetCreationDate'],
            'comments': fr['Comments']
        })

    for cr in commercial_requests:
        combined_requests.append({
            'request_number': cr['CommercialControlNumber'],
            'company_name': cr['CompanyName'],
            'request_type': 'Commercial Master',
            'request_details': 'Modified',
            'status': cr['Status'],
            'creation_date': cr['Date'],
            'last_update_date': cr['Date'],
            'comments': cr['Comments']
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




# @api.get("/approval-requests", response=List[Dict])
# def get_approval_requests(request):
#     fleet_requests = FleetMaster.objects.filter(
#         FleetControlNumber__startswith='ALY'
#     ).exclude(
#         FleetControlNumber=''
#     ).order_by('FleetControlNumber').values(
#         'FleetControlNumber', 'FleetCompanyName', 'FleetStatus', 'FleetCreationDate', 'Comments'
#     )

#     commercial_requests = CommercialMaster.objects.filter(
#         CommercialControlNumber__startswith='ALY'
#     ).exclude(
#         CommercialControlNumber=''
#     ).order_by('CommercialControlNumber').values(
#         'CommercialControlNumber', 'CompanyName', 'Status', 'Date', 'Comments'
#     )

#     traffic_requests = TrafficFileMaster.objects.exclude(
#         traffic_file_no=''
#     ).order_by('traffic_file_no').values(
#         'traffic_file_no', 'company_name', 'status', 'creation_date', 'last_update_date', 'comments'
#     )

#     combined_requests = []

#     for fr in fleet_requests:
#         combined_requests.append({
#             'request_number': fr['FleetControlNumber'],
#             'company_name': fr['FleetCompanyName'],
#             'request_type': 'Fleet Master',
#             'request_details': 'Modified',
#             'status': fr['FleetStatus'],
#             'creation_date': fr['FleetCreationDate'],
#             'last_update_date': fr['FleetCreationDate'],
#             'comments': fr['Comments']
#         })

#     for cr in commercial_requests:
#         combined_requests.append({
#             'request_number': cr['CommercialControlNumber'],
#             'company_name': cr['CompanyName'],
#             'request_type': 'Commercial Master',
#             'request_details': 'Modified',
#             'status': cr['Status'],
#             'creation_date': cr['Date'],
#             'last_update_date': cr['Date'],
#             'comments': cr['Comments']
#         })

#     for tr in traffic_requests:
#         combined_requests.append({
#             'request_number': tr['traffic_file_no'],
#             'company_name': tr['company_name'],
#             'request_type': 'Traffic File Master',
#             'request_details': 'Modified',
#             'status': tr['status'],
#             'creation_date': tr['creation_date'],
#             'last_update_date': tr['last_update_date'],
#             'comments': tr['comments']
#         })

#     return combined_requests


@api.get("/all-approval-requests", response=List[Dict])
def get_approval_requests(request):
    approval_requests = ApprovalRequest.objects.all().order_by('-creation_date')

    combined_requests = []

    for ar in approval_requests:
        combined_requests.append({
            'request_number': ar.request_number,
            'application_number': ar.application_number,
            'company_name': ar.company_name,
            'request_type': ar.request_type,
            'request_details': ar.request_details,
            'status': ar.status,
            'creation_date': ar.creation_date,
            'last_update_date': ar.last_update_date,
            'comments': ar.comments,
            'responded_by': ar.responded_by.username if ar.responded_by else None,
            'response_role': ar.response_role,
            'action': ar.action
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
    TRAFFIC_FILE_NO: Optional[str] = None
    COMPANY_NAME: Optional[str] = None  # Added this line
    TRADE_LICENSE_NO: Optional[str] = None
    EMIRATES: Optional[str] = None
    FEDERAL_TRAFFIC_FILE_NO: Optional[str] = None
    STATUS: Optional[str] = None

@api.get("/traffic-file-info", response=List[TrafficFileInfoSchema])
def get_traffic_file_info(request):
    traffic_file_info = TrafficFileMaster.objects.filter(
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

