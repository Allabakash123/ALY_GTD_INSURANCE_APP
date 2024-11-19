function freezeForm() {
  const form = document.getElementById('vehicleForm');
  if (!form) {
    console.error("Form with id 'vehicleForm' not found");
    return;
  }

  // Disable all form elements
    const elements = form.elements;
    for (let i = 0; i < elements.length; i++) {
      elements[i].disabled = true;
    }
    const alwaysEnabledButtons = [
    document.querySelector('button[onclick="navigateToAllActionHistory()"]'),
    document.querySelector('button[onclick="navigateToAllAttachments()"]')
  ];

  alwaysEnabledButtons.forEach(button => {
    if (button) {
      button.disabled = false;
      button.style.pointerEvents = 'auto';
      button.style.opacity = '1';
    }
  });
  // Disable all buttons within the form
  const buttons = form.querySelectorAll('button:not([onclick="navigateToAllActionHistory()"]):not([onclick="navigateToAllAttachments()"])');
  buttons.forEach(button => button.disabled = true);
  // Disable specific navbar buttons
  const navbarButtons = ['editButton', 'addRow', 'removeRow', 'submitForm'];
  navbarButtons.forEach(buttonId => {
    const button = document.getElementById(buttonId);
    if (button) {
      button.disabled = true;
      button.style.pointerEvents = 'none';
      button.style.opacity = '0.5';
    }
  });

  // Hide the edit button if it exists
  const editButton = document.getElementById('editButton');
  if (editButton) {
    editButton.style.display = 'none';
  }

  // Add a visual indicator that the form is frozen
  form.classList.add('form-frozen');

  
}


function validateAllTables() {
  const requiredFields = {
    'insuranceTable': ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'PLTS_INS_START_DATE', 'POLICY_EXPIRY_DATE', 'PLTS_INS_EXPIRY_DATE', 'CURRENT STATUS_LOOKUP_NAME'],
    'registrationTable': ['EMIRATES_TRF_FILE_NO', 'REGISTRATION_NO1', 'REGISTRATION_NO', 'REGISTRATION_DATE', 'REG_EXPIRY_DATE', 'CURRENT STATUS_LOOKUP_NAME'],
    'driverTable': ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE','ASSIGNMENT_END_DATE'],
    'allocationTable': ['COMPANY NAME_LOOKUP_NAME', 'DIVISIONS_LOOKUP_NAME', 'OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME', 'AE_EMIRATES_LOOKUP_NAME', 'ALLOCATION_DATE']
  };

  let errorMessages = [];



  const insuranceTable = document.getElementById('insuranceTable');
  if (insuranceTable) {
    const insuranceRows = insuranceTable.querySelectorAll('tbody tr');
    let hasValidInsuranceRow = false;
    let hasPartialInsuranceData = false;

    insuranceRows.forEach(row => {
      const insuranceCompany = row.querySelector('input[name="INSURANCE_COMPANY"]')?.value;
      if (insuranceCompany?.trim()) {
        // If any insurance data is entered, all required fields must be filled
        const allFieldsFilled = requiredFields['insuranceTable'].every(field => {
          const input = row.querySelector(`[name="${field}"]`);
          return input && input.value.trim();
        });
        
        if (allFieldsFilled) {
          hasValidInsuranceRow = true;
        } else {
          hasPartialInsuranceData = true;
        }
      }
    });

    if (hasPartialInsuranceData || (!hasValidInsuranceRow && insuranceRows.length > 0)) {
      errorMessages.push('Please fill in all required fields in the Insurance section.');
    }
  }
  const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');

  for (const [tableId, fields] of Object.entries(requiredFields)) {
    const table = document.getElementById(tableId);
    if (table) {
      const rows = table.querySelectorAll('tbody tr');
      let tableIsValid = false;
      let tableHasPartialData = false;

      rows.forEach(row => {
        let rowIsValid = true;
        let rowHasData = false;
        fields.forEach(fieldName => {
          const input = row.querySelector(`[name="${fieldName}"]`);
          if (input && !input.value.trim()) {
            if (tableId ===  `${activeTab}Table`) {
              input.style.border = '2px solid red';
            }
            rowIsValid = false;
          } else if (input && input.value.trim()) {
            rowHasData = true;
            input.style.border = '';
          }
        });

        if (rowIsValid) {
          tableIsValid = true;
        }
        if (rowHasData && !rowIsValid) {
          tableHasPartialData = true;
        }
      });

      if (!tableIsValid || (tableId === 'insuranceTable' && tableHasPartialData)) {
        errorMessages.push(`${tableId.replace('Table', '')} is required. Please fill in all required fields.`);
      }
    }
  }

  return errorMessages;
}


function validateVehicleForm() {
const mandatoryFields = [
  'COMPANY NAME_LOOKUP_NAME',
  'VIN_NO',
  'MANUFACTURER_LOOKUP_NAME',
  'MODEL_LOOKUP_NAME',
  'VEHICLE TYPE_LOOKUP_NAME',
  'COLOR_LOOKUP_NAME',
  'FLEET CATEGORY_LOOKUP_NAME',
  'FLEET SUB CATEGORY_LOOKUP_NAME',
  'VEHICLE USAGE_LOOKUP_NAME',
  'ENGINE_NO',
  'MODEL YEAR_LOOKUP_NAME',
  'COUNTRY OR ORIGIN_LOOKUP_NAME',
  'SEATING CAPACITY_LOOKUP_NAME',
  'TONNAGE_LOOKUP_NAME',
  'GROSS_WEIGHT_KG',
  'EMPTY_WEIGHT_KG',
  'PURCHASE_VALUE_AED'
];

let isValid = true;

mandatoryFields.forEach(fieldName => {
  const input = document.querySelector(`[name="${fieldName}"]`);
  if (input && !input.value.trim()) {
    input.style.border = '2px solid red';
    isValid = false;
  } else if (input) {
    input.style.border = '';
  }
});

return isValid;
}


//post api for vrhicle and insurance
let isNewForm = false;
const form = document.getElementById('vehicleForm');
const submitButton = document.getElementById('submitForm');
submitButton.addEventListener('click', async function (event) {
  // Inside the submit button event listener, before the fetch call

  if (isPopulatedData && !isEditMode) {
    alert("Please enable editing first.");
    return;
  }
  const isVehicleFormValid = validateVehicleForm();
  const allTablesErrorMessages = validateAllTables();

  const fleetControlNumber = document.querySelector('input[name="FLEET_CONTROL_NO"]').value;
  const isNewSubmission = !fleetControlNumber;

  let errorMessages = [];

    if (!isVehicleFormValid) {
      errorMessages.push("Please fill in all required fields in the vehicle form.");
    }

    if (isNewSubmission) {
      errorMessages = errorMessages.concat(allTablesErrorMessages);
    }

    if (errorMessages.length > 0) {
      alert(errorMessages.join('\n'));
      return;
    }

    const formData = new FormData(form);
    const commentsField = document.querySelector('textarea[name="COMMENTS"]');
    if (commentsField) {
        formData.append('COMMENTS', commentsField.value);
    }
    const statusInput = document.querySelector('input[name="STATUS"]');
    const action = window.isRequestingCancellation ? 'Request For Cancellation' : '';


    const currentDate = new Date().toISOString().split('T')[0];
    formData.set('FLEET_CREATION_DATE', currentDate);



    const fieldMappings = {
      'COMPANY NAME_LOOKUP_NAME': 'COMPANY_NAME',
      'MANUFACTURER_LOOKUP_NAME': 'MANUFACTURER',
      'MODEL_LOOKUP_NAME':'MODEL',
      'VEHICLE TYPE_LOOKUP_NAME': 'VEHICLE_TYPE',
      'COLOR_LOOKUP_NAME': 'COLOR',
      'FLEET CATEGORY_LOOKUP_NAME': 'FLEET_CATEGORY',
      'FLEET SUB CATEGORY_LOOKUP_NAME': 'FLEET_SUB_CATEGORY',
      'VEHICLE USAGE_LOOKUP_NAME':'ApplicationUsage',
      'MODEL YEAR_LOOKUP_NAME': 'MODEL_YEAR',
      'COUNTRY OR ORIGIN_LOOKUP_NAME': 'COUNTRY_OF_ORIGIN',
      'SEATING CAPACITY_LOOKUP_NAME': 'SEATING_CAPACITY',
      'TONNAGE_LOOKUP_NAME': {
          apiName: 'TONNAGE',
          handler: (value) => parseFloat(value.split(' ')[0])
      }

  };

  for (let [lookupName, mapping] of Object.entries(fieldMappings)) {
      const select = form.querySelector(`select[name="${lookupName}"]`);
      if (select && select.value) {
          if (typeof mapping === 'object' && mapping.handler) {
              formData.append(mapping.apiName, mapping.handler(select.value));
          } else {
              formData.append(typeof mapping === 'string' ? mapping : mapping.apiName, select.value);
          }
      }
  }



  const fleetStatus = document.querySelector('input[name="STATUS"]').value;

  console.log("Current FleetStatus:", fleetStatus);

    const insuranceData = [];
    const permitData = [];
    const gpsData = [];
    const registrationData = [];
    const fuelData = [];
    const roadtollData = [];
    const driverData = [];
    const allocationData = [];
    const fromApprover = new URLSearchParams(window.location.search).get('from_approver') === 'true';


    const insuranceRows = document.querySelectorAll('#insuranceTable tbody tr');
    insuranceRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="insurance_id"]');
      const insuranceCompany = row.querySelector('input[name="INSURANCE_COMPANY"]')?.value || '';

    // Skip empty rows
    if (!insuranceCompany.trim()) {
          return; // Skip this iteration if the Insurance Company is empty
        }

        const insuranceRecord = {
          INS_LINE_ID: idInput ? idInput.value : 'new',
          INSURANCE_COMPANY: insuranceCompany,
          POLICY_NO: row.querySelector('input[name="POLICY_NO"]')?.value ,
          POLICY_DATE: row.querySelector('input[name="POLICY_DATE"]')?.value,
          POLICY_EXPIRY_DATE: row.querySelector('input[name="POLICY_EXPIRY_DATE"]')?.value ,
          PLTS_INS_START_DATE: row.querySelector('input[name="PLTS_INS_START_DATE"]')?.value,
          PLTS_INS_EXPIRY_DATE: row.querySelector('input[name="PLTS_INS_EXPIRY_DATE"]')?.value ,
          CUR_STAT_MOT_INS: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]')?.value,
          FLEET_PROCESS: fleetStatus
          };


          const filteredinsuranceRecord= Object.fromEntries(
            Object.entries(insuranceRecord).filter(([key, value]) => value !== '' && value !== null)
        );

        insuranceData.push(filteredinsuranceRecord);
        console.log(`Insurance Record ${index}:`, insuranceRecord);


        const fileInput = row.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
              for (let i = 0; i < fileInput.files.length; i++) {
                formData.append(`InsurancePolicAattachment_${index}`, fileInput.files[i]);
              }
            }
    });

    formData.append('insurances', JSON.stringify(insuranceData));
    formData.append('is_approver', fromApprover ? 'true' : 'false');


    const permitRows = document.querySelectorAll('#permitsTable tbody tr');
    permitRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="permit_id"]');
        const permitRecord = {
            PERMIT_LINE_ID: idInput ? idInput.value : 'new',
            PERMIT_TYPE: row.querySelector('select[name="PERMIT_LOOKUP_NAME"]').value,
            EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
            ISSUING_AUTHORITY: row.querySelector('select[name="ISSUING AUTHORITY_LOOKUP_NAME"]').value,
            PERMIT_NO: row.querySelector('input[name="PERMIT_NO"]').value,
            PERMIT_DATE: row.querySelector('input[name="PERMIT_DATE"]')?.value || null,
            PERMIT_EXPIRY_DATE: row.querySelector('input[name="PERMIT_EXPIRY_DATE"]')?.value || null,
            CUR_STAT_PERMIT: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value,
            PermitColor: row.querySelector('input[name="PermitColor"]') ? row.querySelector('input[name="PermitColor"]').value : null,
            FLEET_PROCESS: fleetStatus

        };

        const filteredpermitRecord= Object.fromEntries(
              Object.entries(permitRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          permitData.push(filteredpermitRecord);

        const fileInput = row.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append(`PermitAattachment_${index}`, fileInput.files[i]);
            }
        }
    });

    formData.append('permits', JSON.stringify(permitData));
    formData.append('is_approver', fromApprover ? 'true' : 'false');



      const gpsRows = document.querySelectorAll('#gpsTable tbody tr');
      gpsRows.forEach((row, index) => {
          const idInput = row.querySelector('input[name="gps_id"]');
          const gpsRecord = {
              GT_LINE_ID: idInput ? idInput.value : 'new',
              GPS_DEVICE_NO: row.querySelector('input[name="GPS_DEVICE_NO"]').value,
              GPS_INSTALLATION_DATE: row.querySelector('input[name="GPS_INSTALLATION_DATE"]')?.value || null,
              GPS_SERVICE_PROVIDER: row.querySelector('input[name="GPS_SERVICE_PROVIDER"]').value,
              FLEET_PROCESS: fleetStatus
          };
          const filteredgpsRecord= Object.fromEntries(
              Object.entries(gpsRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          gpsData.push(filteredgpsRecord);

          const fileInput = row.querySelector('input[type="file"]');
          if (fileInput && fileInput.files.length > 0) {
              for (let i = 0; i < fileInput.files.length; i++) {
                  formData.append(`GpsAattachment_${index}`, fileInput.files[i]);
              }
          }
      });
      formData.append('gps', JSON.stringify(gpsData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');

      const registrationRows = document.querySelectorAll('#registrationTable tbody tr');
      registrationRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="registration_id"]');
        const emiratesTrafficFileNumber = row.querySelector('input[name="EMIRATES_TRF_FILE_NO"]')?.value || '';
        
        // Skip empty rows
        if (!emiratesTrafficFileNumber.trim()) {
          return; // Skip this iteration if the EmiratesTrafficFileNumber is empty
        }
        const registrationRecord = {
          REG_LINE_ID: idInput ? idInput.value : 'new',
          EMIRATES_TRF_FILE_NO:emiratesTrafficFileNumber,
          REGISTERED_EMIRATES: row.querySelector('input[name="REGISTERED_EMIRATES"]')?.value || '',
          FEDERAL_TRF_FILE_NO: row.querySelector('input[name="FEDERAL_TRF_FILE_NO"]')?.value || '',
          REG_COMPANY_NAME: row.querySelector('input[name="REG_COMPANY_NAME"]')?.value || '',
          TRADE_LICENSE_NO: row.querySelector('input[name="TRADE_LICENSE_NO"]')?.value || '',
          REGISTRATION_NO1: row.querySelector('input[name="REGISTRATION_NO1"]')?.value || '',
          REGISTRATION_NO: row.querySelector('input[name="REGISTRATION_NO"]')?.value || '',
          REGISTRATION_DATE: row.querySelector('input[name="REGISTRATION_DATE"]')?.value || null,
          REG_EXPIRY_DATE: row.querySelector('input[name="REG_EXPIRY_DATE"]')?.value || null,
          CUR_STAT_REG: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]')?.value || '',
          FLEET_PROCESS:fleetStatus
        };
        const filteredregistrationRecord= Object.fromEntries(
              Object.entries(registrationRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          registrationData.push(filteredregistrationRecord);

        const fileInput = row.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
          for (let i = 0; i < fileInput.files.length; i++) {
            formData.append(`RegCardAttachment_${index}`, fileInput.files[i]);
          }
        }
      });
      formData.append('registration', JSON.stringify(registrationData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');


      const fuelRows = document.querySelectorAll('#fuelTable tbody tr');
      fuelRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="fuel_id"]');
        const fuelRecord = {
          FUEL_LINE_ID: idInput ? idInput.value : 'new',
          FUEL_TYPE: row.querySelector('select[name="FUEL TYPE_LOOKUP_NAME"]')?.value || '',
          MONTHLY_FUEL_LIMIT: row.querySelector('input[name="MONTHLY_FUEL_LIMIT"]').value,
          FUEL_SERVICE_TYPE: row.querySelector('select[name="FUEL SERVICE TYPE_LOOKUP_NAME"]').value,
          FUEL_SERVICE_PROVIDER: row.querySelector('select[name="FUEL SERVICE PROVIDER_LOOKUP_NAME"]').value,
          FUEL_DOCUMENT_NO: row.querySelector('input[name="FUEL_DOCUMENT_NO"]').value,
          FUEL_DOCUMENT_DATE: row.querySelector('input[name="FUEL_DOCUMENT_DATE"]')?.value || null,
          FUEL_DOC_EXPIRY_DATE: row.querySelector('input[name="FUEL_DOC_EXPIRY_DATE"]')?.value || null,
          CUR_STAT_FUEL_DOC: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value,
          FLEET_PROCESS: fleetStatus
        };
        const filteredfuelRecord= Object.fromEntries(
              Object.entries(fuelRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          fuelData.push(filteredfuelRecord);

        const fileInput = row.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
          for (let i = 0; i < fileInput.files.length; i++) {
            formData.append(`FuelDocumentAttachment_${index}`, fileInput.files[i]);
          }
        }
      });
      formData.append('fuel', JSON.stringify(fuelData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');

      const roadtollRows = document.querySelectorAll('#roadtollTable tbody tr');
      roadtollRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="roadtoll_id"]');
        const roadtollRecord = {
          RT_LINE_ID: idInput ? idInput.value : 'new',
          EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
          TOLL_TYPE: row.querySelector('select[name="TOLL TYPE_LOOKUP_NAME"]').value,
          ACCOUNT_NO: row.querySelector('input[name="ACCOUNT_NO"]').value,
          TAG_NO: row.querySelector('input[name="TAG_NO"]').value,
          ACTIVATION_DATE: row.querySelector('input[name="ACTIVATION_DATE"]')?.value || null,
          
          ACTIVATION_END_DATE: row.querySelector('input[name="ACTIVATION_END_DATE"]')?.value || null,

          CURRENT_STATUS: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value,
          FLEET_PROCESS: fleetStatus
        };
        const filteredroadtollRecord= Object.fromEntries(
              Object.entries(roadtollRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          roadtollData.push(filteredroadtollRecord);

        const fileInput = row.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
          for (let i = 0; i < fileInput.files.length; i++) {
            formData.append(`RoadtollAttachments_${index}`, fileInput.files[i]);
          }
        }
      });
      formData.append('roadtoll', JSON.stringify(roadtollData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');


      
      const driverRows = document.querySelectorAll('#driverTable tbody tr');
      driverRows.forEach((row, index) => {
          const idInput = row.querySelector('input[name="driver_id"]');
          const employeeNo = row.querySelector('input[name="EMPLOYEE_NO"]')?.value || '';
    
          // Skip empty rows
          if (!employeeNo.trim()) {
            return; // Skip this iteration if the EmiratesTrafficFileNumber is empty
          }  
          const driverRecord = {
              ASGN_LINE_ID: idInput ? idInput.value : 'new',
              EMPLOYEE_NO: parseInt(employeeNo.replace(/\D/g, ''), 10),
              EMPLOYEE_NAME: row.querySelector('input[name="EMPLOYEE_NAME"]').value,
              DESIGNATION: row.querySelector('input[name="DESIGNATION"]').value,
              CONTACT_NUMBER: row.querySelector('input[name="CONTACT_NUMBER"]').value,
              ASSIGNMENT_DATE: row.querySelector('input[name="ASSIGNMENT_DATE"]')?.value || null,
              
              ASSIGNMENT_END_DATE: row.querySelector('input[name="ASSIGNMENT_END_DATE"]')?.value || null,
              TRAFFIC_CODE_NO: row.querySelector('input[name="TRAFFIC_CODE_NO"]').value,
              DRIVING_LICENSE_NO: row.querySelector('input[name="DRIVING_LICENSE_NO"]').value,
              LICENSE_TYPE: row.querySelector('input[name="LICENSE_TYPE"]').value,
              PLACE_OF_ISSUE: row.querySelector('input[name="PLACE_OF_ISSUE"]').value,
              LICENSE_EXPIRY_DATE: row.querySelector('input[name="LICENSE_EXPIRY_DATE"]')?.value || null,
              GPS_TAG_NO: row.querySelector('input[name="GPS_TAG_NO"]').value,
              GPS_TAG_ASSIGN_DATE: row.querySelector('input[name="GPS_TAG_ASSIGN_DATE"]').value,
              FLEET_PROCESS: fleetStatus
          };

          // Filter out empty fields
          const filteredDriverRecord = Object.fromEntries(
              Object.entries(driverRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          driverData.push(filteredDriverRecord);

          const fileInput = row.querySelector('input[type="file"]');
          if (fileInput && fileInput.files.length > 0) {
              for (let i = 0; i < fileInput.files.length; i++) {
                  formData.append(`DriverAttachments_${index}`, fileInput.files[i]);
              }
          }
      });
      formData.append('driver', JSON.stringify(driverData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');



      const allocationRows = document.querySelectorAll('#allocationTable tbody tr');
      allocationRows.forEach((row, index) => {
        const idInput = row.querySelector('input[name="allocation_id"]');
        const allocationRecord = {
          ALLOC_LINE_ID: idInput ? idInput.value : 'new',
          COMPANY_NAME: row.querySelector('select[name="COMPANY NAME_LOOKUP_NAME"]').value,
          DIVISION: row.querySelector('select[name="DIVISIONS_LOOKUP_NAME"]').value,
          OPERATING_LOCATION: row.querySelector('select[name="OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME"]').value,
          OPERATING_EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
          ALLOCATION_DATE: row.querySelector('input[name="ALLOCATION_DATE"]')?.value || null,
          
          ALLOCATION_END_DATE: row.querySelector('input[name="ALLOCATION_END_DATE"]')?.value || null,
          FLEET_PROCESS: fleetStatus
        };
        const filteredallocationRecord= Object.fromEntries(
              Object.entries(allocationRecord).filter(([key, value]) => value !== '' && value !== null)
          );

          allocationData.push(filteredallocationRecord);

        const fileInput = row.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
          for (let i = 0; i < fileInput.files.length; i++) {
            formData.append(`attachment_${index}`, fileInput.files[i]);
          }
        }
      });
      formData.append('allocation', JSON.stringify(allocationData));
      formData.append('is_approver', fromApprover ? 'true' : 'false');






    formData.append('insurances', JSON.stringify(insuranceData));
    formData.append('permits', JSON.stringify(permitData));
    formData.append('allocation', JSON.stringify(allocationData));
    formData.append('driver', JSON.stringify(driverData));
    formData.append('roadtoll', JSON.stringify(roadtollData));
    formData.append('fuel', JSON.stringify(fuelData));
    formData.append('registration', JSON.stringify(registrationData));
    formData.append('gps', JSON.stringify(gpsData));

    if (action) {
          formData.append('ACTION', action);
      }


    try {
        const response = await fetch('http://127.0.0.1:8000/api/fleet-master', {
            method: 'POST',
            body: formData,
          
            
        });
        const data = await response.json();
        console.log(data);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }


      
        console.log('Success:', data);

        alert(`Fleet master and insurance and registration and gps and permits information submitted successfully!\nFleet Control Number: ${data.fleet_master.FLEET_CONTROL_NO}`);
      
       

       console.log('Data structure:', JSON.stringify(data, null, 2));

       if (data.fleet_master) {
         const fleetControlNumber = data.fleet_master;
         
         // Log COMM_CONTROL_NO for debugging
         console.log('FLEET_CONTROL_NO:', data.fleet_master.FLEET_CONTROL_NO);
         
         if (action === 'Request For Cancellation') {
             try {
                 await sendCancellationEmail(data.fleet_master.FLEET_CONTROL_NO);
                 console.log('Cancellation email sent successfully.');
             } catch (error) {
                 console.error('Error sending cancellation email:', error);
             }
         } else {
             try {
              await sendEmailAutomatically(data.fleet_master.FLEET_CONTROL_NO, data.fleet_master,isNewSubmission);
                 console.log('Submission email sent successfully.');
             } catch (error) {
                 console.error('Error sending submission email:', error);
             }
         }
         window.isRequestingCancellation = false;
     } else {
         console.error('Unexpected API response:', data);
         alert('Unexpected API response. Please check the console for details.');
     }
     console.log('Before clearing comments:', document.querySelector('textarea[name="COMMENTS"]').value);
     const commentsField = document.querySelector('textarea[name="COMMENTS"]');
     if (commentsField) {
         commentsField.value = '';
         console.log('After clearing comments:', commentsField.value);
     }
        clearForm();
        form.reset();
        clearInsuranceTable();
        cleargpsTable();
        clearPermitTable();
        clearFuelTable();
        clearRegistrationTable();
        clearRoadtollTable();
        clearDriverTable();
        clearAllocationTable();

        document.querySelectorAll('#insuranceTable tbody tr input, #insuranceTable tbody tr select').forEach(input => {
            input.value = '';
        });
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.value = '';
        });

    } catch (error) {
        console.error('Detailed error:', error);
        //alert(`An error occurred while submitting the information: ${error.message}`);
    }
});




const saveButton = document.getElementById('saveform');
saveButton.addEventListener('click', async function (event) {
  if (isPopulatedData && !isEditMode) {
    alert("Please enable editing first.");
    return;
  }

  
  const form = document.getElementById('vehicleForm');
  const formData = new FormData(form);

  const fieldMappings = {
    'COMPANY NAME_LOOKUP_NAME': 'COMPANY_NAME',
    'MANUFACTURER_LOOKUP_NAME': 'MANUFACTURER',
    'MODEL_LOOKUP_NAME':'MODEL',
    'VEHICLE TYPE_LOOKUP_NAME': 'VEHICLE_TYPE',
    'COLOR_LOOKUP_NAME': 'COLOR',
    'FLEET CATEGORY_LOOKUP_NAME': 'FLEET_CATEGORY',
    'FLEET SUB CATEGORY_LOOKUP_NAME': 'FLEET_SUB_CATEGORY',
    'VEHICLE USAGE_LOOKUP_NAME':'ApplicationUsage',
    'MODEL YEAR_LOOKUP_NAME': 'MODEL_YEAR',
    'COUNTRY OR ORIGIN_LOOKUP_NAME': 'COUNTRY_OF_ORIGIN',
    'SEATING CAPACITY_LOOKUP_NAME': 'SEATING_CAPACITY',
    'TONNAGE_LOOKUP_NAME': {
      apiName: 'TONNAGE',
      handler: (value) => parseFloat(value.split(' ')[0])
    }
  };

  for (let [lookupName, mapping] of Object.entries(fieldMappings)) {
    const select = form.querySelector(`select[name="${lookupName}"]`);
    if (select && select.value) {
      if (typeof mapping === 'object' && mapping.handler) {
        formData.append(mapping.apiName, mapping.handler(select.value));
      } else {
        formData.append(typeof mapping === 'string' ? mapping : mapping.apiName, select.value);
      }
    }
  }

  const numericFields = ['GROSS_WEIGHT_KG', 'EMPTY_WEIGHT_KG', 'PURCHASE_VALUE_AED', 'TONNAGE'];
  numericFields.forEach(field => {
    const input = form.querySelector(`input[name="${field}"]`);
    if (input && input.value.trim() !== '') {
      const numValue = parseFloat(input.value);
      if (!isNaN(numValue)) {
        formData.append(field, numValue);
      }
    }
  });

  const insuranceData = [];
  const permitData = [];
  const gpsData = [];
  const registrationData = [];
  const fuelData = [];
  const roadtollData = [];
  const driverData = [];
  const allocationData = [];

  const insuranceRows = document.querySelectorAll('#insuranceTable tbody tr');
  insuranceRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="insurance_id"]');
    const insuranceCompany = row.querySelector('input[name="INSURANCE_COMPANY"]')?.value || '';

    // Skip empty rows
    if (!insuranceCompany.trim()) {
      return; // Skip this iteration if the Insurance Company is empty
    }

    const insuranceRecord = {
      INS_LINE_ID: idInput ? idInput.value : 'new',
      INSURANCE_COMPANY: insuranceCompany,
      POLICY_NO: row.querySelector('input[name="POLICY_NO"]')?.value || '',
      POLICY_DATE: row.querySelector('input[name="POLICY_DATE"]').value || null,
      POLICY_EXPIRY_DATE: row.querySelector('input[name="POLICY_EXPIRY_DATE"]').value || null,
      PLTS_INS_START_DATE: row.querySelector('input[name="PLTS_INS_START_DATE"]').value || null,
      PLTS_INS_EXPIRY_DATE: row.querySelector('input[name="PLTS_INS_EXPIRY_DATE"]').value || null,
      CUR_STAT_MOT_INS: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]')?.value || ''
    };

    insuranceData.push(insuranceRecord);

    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`InsurancePolicAattachment_${index}`, fileInput.files[i]);
      }
    }
  });

  formData.append('insurances', JSON.stringify(insuranceData));

  const permitRows = document.querySelectorAll('#permitsTable tbody tr');
  permitRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="permit_id"]');
    const permitRecord = {
      PERMIT_LINE_ID: idInput ? idInput.value : 'new',
      PERMIT_TYPE: row.querySelector('select[name="PERMIT_LOOKUP_NAME"]').value,
      EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
      ISSUING_AUTHORITY: row.querySelector('select[name="ISSUING AUTHORITY_LOOKUP_NAME"]').value,
      PERMIT_NO: row.querySelector('input[name="PERMIT_NO"]').value,
      PERMIT_DATE: row.querySelector('input[name="PERMIT_DATE"]').value || null,
      PERMIT_EXPIRY_DATE: row.querySelector('input[name="PERMIT_EXPIRY_DATE"]').value || null,
      CUR_STAT_PERMIT: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value,
      PermitColor: row.querySelector('input[name="PermitColor"]') ? row.querySelector('input[name="PermitColor"]').value : null
    };
    permitData.push(permitRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`PermitAattachment_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('permits', JSON.stringify(permitData));

  const gpsRows = document.querySelectorAll('#gpsTable tbody tr');
  gpsRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="gps_id"]');
    const gpsRecord = {
      GT_LINE_ID: idInput ? idInput.value : 'new',
      GPS_DEVICE_NO: row.querySelector('input[name="GPS_DEVICE_NO"]').value,
      GPS_INSTALLATION_DATE: row.querySelector('input[name="GPS_INSTALLATION_DATE"]').value || null,
      GPS_SERVICE_PROVIDER: row.querySelector('input[name="GPS_SERVICE_PROVIDER"]').value
    };
    gpsData.push(gpsRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`GpsAattachment_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('gps', JSON.stringify(gpsData));

  const registrationRows = document.querySelectorAll('#registrationTable tbody tr');
  registrationRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="registration_id"]');
    const emiratesTrafficFileNumber = row.querySelector('input[name="EMIRATES_TRF_FILE_NO"]')?.value || '';
    
    // Skip empty rows
    if (!emiratesTrafficFileNumber.trim()) {
      return; // Skip this iteration if the EmiratesTrafficFileNumber is empty
    }                          
    const registrationRecord = {
      REG_LINE_ID: idInput ? idInput.value : 'new',
      EMIRATES_TRF_FILE_NO: emiratesTrafficFileNumber,
      REGISTERED_EMIRATES: row.querySelector('input[name="REGISTERED_EMIRATES"]')?.value || '',
      FEDERAL_TRF_FILE_NO: row.querySelector('input[name="FEDERAL_TRF_FILE_NO"]')?.value || '',
      REG_COMPANY_NAME: row.querySelector('input[name="REG_COMPANY_NAME"]')?.value || '',
      TRADE_LICENSE_NO: row.querySelector('input[name="TRADE_LICENSE_NO"]')?.value || '',
      REGISTRATION_NO1: row.querySelector('input[name="REGISTRATION_NO1"]')?.value || '',
      REGISTRATION_NO: row.querySelector('input[name="REGISTRATION_NO"]')?.value || '',
      REGISTRATION_DATE: row.querySelector('input[name="REGISTRATION_DATE"]').value || null,
      REG_EXPIRY_DATE: row.querySelector('input[name="REG_EXPIRY_DATE"]').value || null,
      CUR_STAT_REG: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]')?.value || ''
    };
    registrationData.push(registrationRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`RegCardAttachment_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('registration', JSON.stringify(registrationData));

  const fuelRows = document.querySelectorAll('#fuelTable tbody tr');
  fuelRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="fuel_id"]');
    const fuelRecord = {
      FUEL_LINE_ID: idInput ? idInput.value : 'new',
      FUEL_TYPE: row.querySelector('select[name="FUEL TYPE_LOOKUP_NAME"]').value || '',
      MONTHLY_FUEL_LIMIT: row.querySelector('input[name="MONTHLY_FUEL_LIMIT"]').value || '',
      FUEL_SERVICE_TYPE: row.querySelector('select[name="FUEL SERVICE TYPE_LOOKUP_NAME"]').value || '',
      FUEL_SERVICE_PROVIDER: row.querySelector('select[name="FUEL SERVICE PROVIDER_LOOKUP_NAME"]').value || '',
      FUEL_DOCUMENT_NO: row.querySelector('input[name="FUEL_DOCUMENT_NO"]').value || '',
      FUEL_DOCUMENT_DATE: row.querySelector('input[name="FUEL_DOCUMENT_DATE"]').value || null,
      FUEL_DOC_EXPIRY_DATE: row.querySelector('input[name="FUEL_DOC_EXPIRY_DATE"]').value || null,
      CUR_STAT_FUEL_DOC: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value || ''
    };
    fuelData.push(fuelRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`FuelDocumentAttachment_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('fuel', JSON.stringify(fuelData));

  const roadtollRows = document.querySelectorAll('#roadtollTable tbody tr');
  roadtollRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="roadtoll_id"]');
    const roadtollRecord = {
      RT_LINE_ID: idInput ? idInput.value : 'new',
      EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
      TOLL_TYPE: row.querySelector('select[name="TOLL TYPE_LOOKUP_NAME"]').value,
      ACCOUNT_NO: row.querySelector('input[name="ACCOUNT_NO"]').value,
      TAG_NO: row.querySelector('input[name="TAG_NO"]').value,
      ACTIVATION_DATE: row.querySelector('input[name="ACTIVATION_DATE"]')?.value || null,
      
      ACTIVATION_END_DATE: row.querySelector('input[name="ACTIVATION_END_DATE"]')?.value || null,
      CURRENT_STATUS: row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]').value
    };
    roadtollData.push(roadtollRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`RoadtollAttachments_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('roadtoll', JSON.stringify(roadtollData));

  const driverRows = document.querySelectorAll('#driverTable tbody tr');
  driverRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="driver_id"]');
    const employeeNo = row.querySelector('input[name="EMPLOYEE_NO"]')?.value || '';
    
    // Skip empty rows
    if (!employeeNo.trim()) {
      return; // Skip this iteration if the EmiratesTrafficFileNumber is empty
    }   
    const driverRecord = {
      ASGN_LINE_ID: idInput ? idInput.value : 'new',
      EMPLOYEE_NO: employeeNo,
      EMPLOYEE_NAME: row.querySelector('input[name="EMPLOYEE_NAME"]').value,
      DESIGNATION: row.querySelector('input[name="DESIGNATION"]').value,
      CONTACT_NUMBER: row.querySelector('input[name="CONTACT_NUMBER"]').value,
      ASSIGNMENT_DATE: row.querySelector('input[name="ASSIGNMENT_DATE"]').value || null,
      
      ASSIGNMENT_END_DATE: row.querySelector('input[name="ASSIGNMENT_END_DATE"]').value || null,
      TRAFFIC_CODE_NO: row.querySelector('input[name="TRAFFIC_CODE_NO"]').value,
      DRIVING_LICENSE_NO: row.querySelector('input[name="DRIVING_LICENSE_NO"]').value,
      LICENSE_TYPE: row.querySelector('input[name="LICENSE_TYPE"]').value,
      PLACE_OF_ISSUE: row.querySelector('input[name="PLACE_OF_ISSUE"]').value,
      LICENSE_EXPIRY_DATE: row.querySelector('input[name="LICENSE_EXPIRY_DATE"]').value || null,
      GPS_TAG_NO: row.querySelector('input[name="GPS_TAG_NO"]').value,
      GPS_TAG_ASSIGN_DATE: row.querySelector('input[name="GPS_TAG_ASSIGN_DATE"]').value || null
    };
    driverData.push(driverRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0;      i < fileInput.files.length; i++) {
        formData.append(`DriverAttachments_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('driver', JSON.stringify(driverData));

  const allocationRows = document.querySelectorAll('#allocationTable tbody tr');
  allocationRows.forEach((row, index) => {
    const idInput = row.querySelector('input[name="allocation_id"]');
    const allocationRecord = {
      ALLOC_LINE_ID: idInput ? idInput.value : 'new',
      COMPANY_NAME: row.querySelector('select[name="COMPANY NAME_LOOKUP_NAME"]').value,
      DIVISION: row.querySelector('select[name="DIVISIONS_LOOKUP_NAME"]').value,
      OPERATING_LOCATION: row.querySelector('select[name="OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME"]').value,
      OPERATING_EMIRATES: row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]').value,
      ALLOCATION_DATE: row.querySelector('input[name="ALLOCATION_DATE"]').value || null,
      
      ALLOCATION_END_DATE: row.querySelector('input[name="ALLOCATION_END_DATE"]').value || null,
    };
    allocationData.push(allocationRecord);
    const fileInput = row.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
      for (let i = 0; i < fileInput.files.length; i++) {
        formData.append(`attachment_${index}`, fileInput.files[i]);
      }
    }
  });
  formData.append('allocation', JSON.stringify(allocationData));

  try {
    const response = await fetch('http://127.0.0.1:8000/api/fleet-master/save', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const data = await response.json();
    console.log('Success:', data);

    alert(`Fleet master information saved successfully!\nHeader Id: ${data.fleet_master.HEADER_ID}`);
    clearForm();
  } catch (error) {
    console.error('Detailed error:', error);
    alert(`An error occurred while saving the information: ${error.message}`);
  }
});

function areAllTablesFilled() {
  const tables = ['insuranceTable', 'registrationTable', 'gpsTable', 'permitsTable', 'fuelTable', 'roadtollTable', 'driverTable', 'allocationTable'];
  return tables.every(tableId => {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tbody tr');
    return Array.from(rows).some(row => {
      const inputs = row.querySelectorAll('input:not([type="hidden"]), select');
      return Array.from(inputs).some(input => input.value.trim() !== '');
    });
  });
}

function clearForm() {
  document.querySelectorAll('#vehicleForm input, #vehicleForm select, #vehicleForm textarea').forEach(input => {
      if (input.type !== 'file') {
          input.value = '';
      } else {
          // Clear file inputs
          input.value = '';
          // Clear any associated file name display
          const fileLabel = input.nextElementSibling;
          if (fileLabel && fileLabel.tagName === 'SPAN') {
              fileLabel.textContent = '';
          }
      }
    });

    const vehiclePurchaseDocInput = document.querySelector('input[name="VehiclePurchaseDoc"]');
  
    if (vehiclePurchaseDocInput) {
    vehiclePurchaseDocInput.addEventListener('change', function() {
      handleFileSelection(this);
    });
    }

    clearInsuranceTable();
    clearPermitTable();
    cleargpsTable();
    clearFuelTable();

    clearRegistrationTable();
    clearRoadtollTable();
    clearDriverTable();
    clearAllocationTable();


    enableEditingControls();
    hideEditButton();
    isPopulatedData = false;
    enableAllFields();
    const editButton = document.getElementById('editButton');
    if (editButton) {
      editButton.style.display = 'none';
    }

    isEditMode = false;
    const fleetControlNumberField = document.querySelector('[name="FLEET_CONTROL_NO"]');
    fleetControlNumberField.disabled = true;
    fleetControlNumberField.value = '';



}

function clearInsuranceTable() {
  const insuranceTable = document.querySelector('#insuranceTable tbody');
  insuranceTable.innerHTML = '';
  //addInsuranceRow();
}

function clearRegistrationTable() {
  const registrationTable = document.querySelector('#registrationTable tbody');
  registrationTable.innerHTML = '';
  //addregistrationRow();
}

function clearPermitTable() {
  const permitTable = document.querySelector('#permitsTable tbody');
  permitTable.innerHTML = '';
  
}

function clearFuelTable() {
  const fuelTable = document.querySelector('#fuelTable tbody');
  fuelTable.innerHTML = '';
  //addFuelRow();
}

function clearRoadtollTable() {
  const roadtollTable = document.querySelector('#roadtollTable tbody');
  roadtollTable.innerHTML = '';
  //addRoadtollRow();
}

function clearDriverTable() {
  const driverTable = document.querySelector('#driverTable tbody');
  driverTable.innerHTML = '';
  //addDriverRow();
}

function clearAllocationTable() {
  const allocationTable = document.querySelector('#allocationTable tbody');
  allocationTable.innerHTML = '';
  //addAllocationRow();
}

function cleargpsTable() {
  const gpsTable = document.querySelector('#gpsTable tbody');
  gpsTable.innerHTML = '';
  //addgpsRow();
}