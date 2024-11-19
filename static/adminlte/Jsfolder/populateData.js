async function populateFormFields(identifier, isApproverPage = false) {
  const urlParams = new URLSearchParams(window.location.search);
  const fromApprover = urlParams.get('from_approver') === 'true';
  
  
  console.log("URL from_approver parameter:", fromApprover);
  console.log("isApproverPage parameter:", isApproverPage);

    clearCachedData();
  
    try {
      const url =
        `http://127.0.0.1:8000/api/fleet-master/${identifier}`;
       

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          console.error(`Fleet master with ${isApproverPage ? 'fleet control number' : 'header ID'} ${identifier} not found`);
          // Handle the 404 error (e.g., show a message to the user)
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } else {
        const data = await response.json();
        console.log("Fetched fleet data:", data);
        
          updateSaveButtonVisibility(data.STATUS);
          
          // Handle read-only state for approver flow
          const isFromApprover = sessionStorage.getItem('fromApproverFlow') === 'true';
          const isReadOnly = sessionStorage.getItem('isReadOnly') === 'true';
          const isApprover = sessionStorage.getItem('isApprover') === 'true';
          const disableVehicleInfo = sessionStorage.getItem('disableVehicleInfo') === 'true';


          
          // Set background color for all disabled fields
          document.querySelectorAll('input:disabled, select:disabled, textarea:disabled').forEach(element => {
          // element.style.backgroundColor = '#ffff76';
            element.style.color = 'black'; // Ensure text remains visible
          });



          if (isFromApprover && isReadOnly) {
            // Disable all form fields except comments for approver
            const allInputs = document.querySelectorAll('input, select, textarea');
            allInputs.forEach(input => {
                // Enable comments field for approvers
                if (input.name === 'comments' || input.name === 'COMMENTS' || input.classList.contains('comments-field')) {
                    input.disabled = false;
                   // input.style.backgroundColor = '#ffff76';  // Set yellow background for comments field
                } else {
                    input.disabled = true;
                   // input.style.backgroundColor = '#e9ecef';
                }
            });

            
        
            // Specifically enable comments fields in all sections
            const commentFields = document.querySelectorAll('[name*="comment"], [name*="COMMENT"]');
            commentFields.forEach(field => {
                field.disabled = false;
                field.style.backgroundColor = '#ffffff';  // Set yellow background
            });
        
            // Enable the main comments textarea if it exists
            const mainComments = document.querySelector('#comments, #COMMENTS, .comments-field');
            if (mainComments) {
                mainComments.disabled = false;
               // mainComments.style.backgroundColor = '#ffff76';  // Set yellow background
            }
        
              // Add background color setting after vehicle info section handling
              if (disableVehicleInfo) {
                const vehicleInfoInputs = document.querySelectorAll('#vehicleInfoSection input, #vehicleInfoSection select');
                vehicleInfoInputs.forEach(input => {
                  if (!input.name.toLowerCase().includes('comment')) {
                    input.disabled = true;
                   // input.style.backgroundColor = '#ffff76';
                  }
                });
              }
            }



          
        if (isApproverPage) {

          const fleetControlNumberField = document.querySelector('[name="FLEET_CONTROL_NO"]');
          fleetControlNumberField.disabled = false;
          fleetControlNumberField.value = identifier;
        } else {
          const headerIdField = document.querySelector('#HEADER_ID');
          if (headerIdField) {
            headerIdField.value = data.HEADER_ID;
          }
        }


        setTimeout(() => {
          setDropdownValue(document.querySelector('[name="COMPANY NAME_LOOKUP_NAME"]'), data.COMPANY_NAME);
          setDropdownValue(document.querySelector('[name="MANUFACTURER_LOOKUP_NAME"]'), data.MANUFACTURER);
          setDropdownValue(document.querySelector('[name="MODEL_LOOKUP_NAME"]'), data.MODEL);
          setDropdownValue(document.querySelector('[name="VEHICLE TYPE_LOOKUP_NAME"]'), data.VEHICLE_TYPE);
          setDropdownValue(document.querySelector('[name="COLOR_LOOKUP_NAME"]'), data.COLOR);
          setDropdownValue(document.querySelector('[name="FLEET CATEGORY_LOOKUP_NAME"]'), data.FLEET_CATEGORY);
          setDropdownValue(document.querySelector('[name="FLEET SUB CATEGORY_LOOKUP_NAME"]'), data.FLEET_SUB_CATEGORY);
          setDropdownValue(document.querySelector('[name="VEHICLE USAGE_LOOKUP_NAME"]'), data.ApplicationUsage);
          setDropdownValue(document.querySelector('[name="MODEL YEAR_LOOKUP_NAME"]'), data.MODEL_YEAR);
          setDropdownValue(document.querySelector('[name="COUNTRY OR ORIGIN_LOOKUP_NAME"]'), data.COUNTRY_OF_ORIGIN);
          setDropdownValue(document.querySelector('[name="SEATING CAPACITY_LOOKUP_NAME"]'), data.SEATING_CAPACITY);
          setDropdownValue(document.querySelector('[name="TONNAGE_LOOKUP_NAME"]'), data.TONNAGE);

          // Add this line to set the Registered Company Name
          setDropdownValue(document.querySelector('[name="REG_COMPANY_NAME"]'), data.registration[0].REG_COMPANY_NAME);
          setDropdownValue(document.querySelector('[name=""]'), data.registration[0].REGISTERED_EMIRATES);
        }, 100);


        for (const [key, value] of Object.entries(data)) {
          if (key !== "insurances" && key !== "gps" && key !== "permits" && 
              key !== "registration" && key !== "fuel" && key !== "roadtoll" && 
              key !== "driver" && key !== "allocation" && key !== "COMMENTS") {
            const field = document.querySelector(`[name="${key}"]`);
            if (field && field.type !== "file") {
              field.value = value;
            }
          }
        }

        // Inside populateFormFields function, after the data is fetched
        console.log("Fetched comments value:", data.COMMENTS);

        // Before setting the comments value
        // Clear the comments field explicitly
        const commentsField = document.querySelector('textarea[name="COMMENTS"]');
        if (commentsField) {
            commentsField.value = '';
            console.log("Comments field cleared:", commentsField.value);
        }

      


        const vehiclePurchaseDocInput = document.querySelector('[name="VehiclePurchaseDoc"]');

        if (vehiclePurchaseDocInput && data.VehiclePurchaseDoc) {
            // Check if container already exists
            const existingContainer = vehiclePurchaseDocInput.closest('.file-input-wrapper');
            if (!existingContainer) {
                // Create container elements
                const fileListContainer = document.createElement("div");
                fileListContainer.className = "file-list-container";

                // Create and set up wrapper
                const wrapper = document.createElement('div');
                wrapper.className = 'file-input-wrapper';
                vehiclePurchaseDocInput.parentNode.insertBefore(wrapper, vehiclePurchaseDocInput);
                wrapper.appendChild(vehiclePurchaseDocInput);
                wrapper.appendChild(fileListContainer);

                // Create and append dropdown
                const fileDropdown = createFileDropdown();
                fileListContainer.appendChild(fileDropdown);
                if (fromApprover) {
                  fileInput.disabled = true;
                  fileInput.style.backgroundColor = '#e9ecef';
                  fileDropdown.style.pointerEvents = 'none';
                  fileDropdown.style.opacity = '0.7';
                  fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
              } else {
                  fileInput.disabled = false;
                  fileInput.style.backgroundColor = '';
                  fileDropdown.style.pointerEvents = 'auto';
                  fileDropdown.style.opacity = '1';
                  fileDropdown.querySelector('.file-list').style.backgroundColor = '';
              }
            }

            // Get instance ID and populate files
            const instanceId = data.HEADER_ID || document.querySelector('[name="HEADER_ID"]')?.value;
            vehiclePurchaseDocInput.dataset.instanceId = instanceId;

            const fileDropdown = vehiclePurchaseDocInput.closest('.file-input-wrapper')?.querySelector('.file-dropdown');
            if (fileDropdown && data.VehiclePurchaseDoc) {
                const fileNames = getAllFileNames(data.VehiclePurchaseDoc, 'VEHICLE', instanceId);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }
        }

    
        const insuranceTable = document.querySelector("#insuranceTable tbody");
        insuranceTable.innerHTML = "";
        const hasApprovedInsuranceRow = data.insurances.some(insurance => insurance.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.insurances)) {
          const sortedInsurances = data.insurances.sort((a, b) => {
            // First, prioritize 'Active' status
           if (a.CUR_STAT_MOT_INS === 'Active' && b.CUR_STAT_MOT_INS !== 'Active') return -1;
           if (b.CUR_STAT_MOT_INS === 'Active' && a.CUR_STAT_MOT_INS !== 'Active') return 1;
           
           // Then, consider 'Approved' status
           if (a.FLEET_PROCESS === 'Approved' && b.FLEET_PROCESS !== 'Approved') return -1;
           if (b.FLEET_PROCESS === 'Approved' && a.FLEET_PROCESS !== 'Approved') return 1;
           
           // If both have the same status, maintain their original order
           return 0;
           });
   
           sortedInsurances.forEach((insurance) => {
             const row = insuranceTable.insertRow();
             row.dataset.process = insurance.FLEET_PROCESS;

              let inputClass = '';
              if (insurance.FLEET_PROCESS === 'Approved') {
                inputClass = 'approved-input';
              } else if (insurance.FLEET_PROCESS === 'Pending for Approval') {
                inputClass = 'pending-input';
              } else if (insurance.FLEET_PROCESS === 'Return for Correction') {
                inputClass = 'rectification-input';
              }
              const isDisabled = isFromApprover || isApproverPage || insurance.FLEET_PROCESS === 'Approved';
              row.innerHTML = `
                <td><input type="text" class="form-control   ${inputClass}" name="INSURANCE_COMPANY" value="${insurance.INSURANCE_COMPANY}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><input type="text" class="form-control  ${inputClass}" name="POLICY_NO" value="${insurance.POLICY_NO}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><input type="date" class="form-control  ${inputClass}" name="POLICY_DATE" value="${insurance.POLICY_DATE}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><input type="date" class="form-control  ${inputClass}" name="POLICY_EXPIRY_DATE" value="${insurance.POLICY_EXPIRY_DATE}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><input type="date" class="form-control  ${inputClass}" name="PLTS_INS_START_DATE" value="${insurance.PLTS_INS_START_DATE}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><input type="date" class="form-control  ${inputClass}" name="PLTS_INS_EXPIRY_DATE" value="${insurance.PLTS_INS_EXPIRY_DATE}" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"/></td>
                <td><select class="form-control ${inputClass}" name="CURRENT STATUS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''} style="background-color: #ffff76; color: black"><option value=""></option></select></td>
                <td><input type="file" class="form-control ${inputClass}" name="InsurancePolicAattachment" ${isDisabled ? 'disabled' : ''}/></td>
                <input type="hidden" name="insurance_id" value="${insurance.INS_LINE_ID}" />
                <input type="hidden" name="FLEET_PROCESS" value="${insurance.FLEET_PROCESS}" />
              `;

              setupDropdownsForNewRow(row);
                  setupInsuranceFleetSearchFunctionality(row);

              setTimeout(() => {
                setDropdownValue(row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]'), insurance.CUR_STAT_MOT_INS);
              }, 0);
                
              
              const fileInput = row.querySelector('input[type="file"]');
              const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);
              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

              if (insurance.InsurancePolicAattachment) {
                const fileNames = getAllFileNames(insurance.InsurancePolicAattachment, 'insurance', insurance.INS_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
              }

              updateFileCount(fileInput, fileDropdown);
              addFileInputListeners();

              // setupInsuranceSearchFunctionality(row);
                });
        }

   



        const registrationTable = document.querySelector("#registrationTable tbody");
        registrationTable.innerHTML = "";
        const hasApprovedRegistrationRow = data.registration.some(registration => registration.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.registration)) {
          const sortedRegistraions = data.registration.sort((a, b) => {
            // First, prioritize 'Active' status
            if (a.CUR_STAT_PERMIT === 'Active' && b.CUR_STAT_REG !== 'Active') return -1;
            if (b.CUR_STAT_PERMIT === 'Active' && a.CUR_STAT_REG !== 'Active') return 1;
            
            // Then, consider 'Approved' status
            if (a.FLEET_PROCESS === 'Approved' && b.FLEET_PROCESS !== 'Approved') return -1;
            if (b.FLEET_PROCESS === 'Approved' && a.FLEET_PROCESS !== 'Approved') return 1;
            
            // If both have the same status, maintain their original order
            return 0;
          });
        
          sortedRegistraions.forEach((registration) => {
            const row = registrationTable.insertRow();
            row.dataset.process = registration.FLEET_PROCESS;
            
            let inputClass = '';
            if (registration.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (registration.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (registration.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }

            const isDisabled = isFromApprover || isApproverPage || registration.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="EMIRATES_TRF_FILE_NO" value="${registration.EMIRATES_TRF_FILE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="REGISTERED_EMIRATES" value="${registration.REGISTERED_EMIRATES || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="FEDERAL_TRF_FILE_NO" value="${registration.FEDERAL_TRF_FILE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control ${inputClass}" style="background-color: #ffff76; color: black" name="REG_COMPANY_NAME" value="${registration.REG_COMPANY_NAME || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control ${inputClass}" style="background-color: #ffff76; color: black" name="TRADE_LICENSE_NO" value="${registration.TRADE_LICENSE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black"  name="REGISTRATION_NO1" value="${registration.REGISTRATION_NO1 || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="REGISTRATION_NO" value="${registration.REGISTRATION_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="REGISTRATION_DATE" value="${registration.REGISTRATION_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="REG_EXPIRY_DATE" value="${registration.REG_EXPIRY_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><select class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="CURRENT STATUS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><input type="file" class="form-control ${inputClass}" name="RegCardAttachment" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="registration_id" value="${registration.REG_LINE_ID}" />
              <input type="hidden" name="FLEET_PROCESS" value="${registration.FLEET_PROCESS}" />
            `;

            setupRegistrationSearchFunctionality(row);
            setupDropdownsForNewRow(row);

            setTimeout(() => {
              setDropdownValue(row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]'), registration.CUR_STAT_REG);
            }, 0);

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
            fileListContainer.className = "file-list-container";

            const wrapper = document.createElement('div');
            wrapper.className = 'file-input-wrapper';
            fileInput.parentNode.insertBefore(wrapper, fileInput);
            wrapper.appendChild(fileInput);
            wrapper.appendChild(fileListContainer);

            const fileDropdown = createFileDropdown();
            fileListContainer.appendChild(fileDropdown);

            if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (registration.RegCardAttachment) {
              const fileNames = getAllFileNames(registration.RegCardAttachment, 'registration', registration.REG_LINE_ID);
              fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

            updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();

            // Set up traffic search functionality for this row
            setupTrafficSearchFunctionality(row);
          });
        }


        const fuelTable = document.querySelector("#fuelTable tbody");
        fuelTable.innerHTML = "";
        const hasApprovedFuelRow = data.fuel.some(fuel => fuel.FLEET_PROCESS === 'Approved');

        
        if (Array.isArray(data.fuel)) {
          const sortedFuel= data.fuel.sort((a, b) => {
            // First, prioritize 'Active' status
            if (a.CUR_STAT_PERMIT === 'Active' && b.CUR_STAT_FUEL_DOC !== 'Active') return -1;
            if (b.CUR_STAT_PERMIT === 'Active' && a.CUR_STAT_FUEL_DOC !== 'Active') return 1;
            
            // Then, consider 'Approved' status
            if (a.FLEET_PROCESS === 'Approved' && b.FLEET_PROCESS !== 'Approved') return -1;
            if (b.FLEET_PROCESS === 'Approved' && a.FLEET_PROCESS !== 'Approved') return 1;
            
            // If both have the same status, maintain their original order
            return 0;
          });
        
          sortedFuel.forEach((fuel) => {
            const row = fuelTable.insertRow();
            row.dataset.process = fuel.FLEET_PROCESS;
            
            
            
                let inputClass = '';

                if (fuel.FLEET_PROCESS === 'Approved') {
                  inputClass = 'approved-input';
                } else if (fuel.FLEET_PROCESS === 'Pending for Approval') {
                  inputClass = 'pending-input';
                } else if (fuel.FLEET_PROCESS === 'Return for Correction') {
                  inputClass = 'rectification-input';
                }

                
              const isDisabled = isFromApprover || isApproverPage || fuel.FLEET_PROCESS === 'Approved';

                row.innerHTML = `
                  <td><select class="form-control ${inputClass}" name="FUEL TYPE_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
                  <td><input type="text" class="${inputClass} form-control" name="MONTHLY_FUEL_LIMIT" value="${fuel.MONTHLY_FUEL_LIMIT || ""}" ${isDisabled ? 'disabled' : ''}/></td>
                  <td><select class=" ${inputClass} form-control" name="FUEL SERVICE TYPE_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
                  <td><select class=" ${inputClass} form-control" name="FUEL SERVICE PROVIDER_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
                  <td><input type="text" class=" ${inputClass} form-control" name="FUEL_DOCUMENT_NO" value="${fuel.FUEL_DOCUMENT_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
                  <td><input type="date" class="${inputClass} form-control" name="FUEL_DOCUMENT_DATE" value="${fuel.FUEL_DOCUMENT_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
                  <td><input type="date" class="${inputClass} form-control" name="FUEL_DOC_EXPIRY_DATE" value="${fuel.FUEL_DOC_EXPIRY_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
                  <td><select class="form-control ${inputClass}" name="CURRENT STATUS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
                  <td><input type="file" class="form-control ${inputClass}" name="FuelDocumentAttachment" multiple ${isDisabled ? 'disabled' : ''}/></td>
                  <input type="hidden" name="fuel_id" value="${fuel.FUEL_LINE_ID || ""}" />
                  <input type="hidden" name="FLEET_PROCESS" value="${fuel.FLEET_PROCESS}" />
                `;

                setupDropdownsForNewRow(row);

                setTimeout(() => {
                  setDropdownValue(row.querySelector('select[name="FUEL TYPE_LOOKUP_NAME"]'), fuel.FUEL_TYPE);
                  setDropdownValue(row.querySelector('select[name="FUEL SERVICE TYPE_LOOKUP_NAME"]'), fuel.FUEL_SERVICE_TYPE);
                  setDropdownValue(row.querySelector('select[name="FUEL SERVICE PROVIDER_LOOKUP_NAME"]'), fuel.FUEL_SERVICE_PROVIDER);
                  setDropdownValue(row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]'), fuel.CUR_STAT_FUEL_DOC);
                }, 0);

                const fileInput = row.querySelector('input[type="file"]');
                const fileListContainer = document.createElement("div");
                  fileListContainer.className = "file-list-container";

                  // Wrap the file input and dropdown in a container
                  const wrapper = document.createElement('div');
                  wrapper.className = 'file-input-wrapper';
                  fileInput.parentNode.insertBefore(wrapper, fileInput);
                  wrapper.appendChild(fileInput);
                  wrapper.appendChild(fileListContainer);

                  const fileDropdown = createFileDropdown();
                  fileListContainer.appendChild(fileDropdown);

                  if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

                if (fuel.FuelDocumentAttachment) {
                    const fileNames = getAllFileNames(fuel.FuelDocumentAttachment, 'fuel', fuel.FUEL_LINE_ID);
                    fileDropdown.querySelector('.file-list').innerHTML = fileNames;
                }

                  updateFileCount(fileInput, fileDropdown);
                addFileInputListeners();
              });
        }


        const roadtollTable = document.querySelector("#roadtollTable tbody");
        roadtollTable.innerHTML = "";
        const hasApprovedRoadtollRow = data.roadtoll.some(roadtoll => roadtoll.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.roadtoll)) {
         
          const sortedRoadtolls = data.roadtoll.sort((a, b) => {
            // First, prioritize 'Active' status
            if (a.CUR_STAT_PERMIT === 'Active' && b.CURRENT_STATUS !== 'Active') return -1;
            if (b.CUR_STAT_PERMIT === 'Active' && a.CURRENT_STATUS !== 'Active') return 1;
            
            // Then, consider 'Approved' status
            if (a.FLEET_PROCESS === 'Approved' && b.FLEET_PROCESS !== 'Approved') return -1;
            if (b.FLEET_PROCESS === 'Approved' && a.FLEET_PROCESS !== 'Approved') return 1;
            
            // If both have the same status, maintain their original order
            return 0;
          });
        
          sortedRoadtolls.forEach((roadtoll) => {
            const row = roadtollTable.insertRow();
            row.dataset.process = roadtoll.FLEET_PROCESS;
            let inputClass = '';

            if (roadtoll.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (roadtoll.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (roadtoll.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }
            const isDisabled = isFromApprover || isApproverPage || roadtoll.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><select class="form-control ${inputClass}" name="AE_EMIRATES_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control ${inputClass}" name="TOLL TYPE_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><input type="number" class="form-control ${inputClass}" name="ACCOUNT_NO" value="${roadtoll.ACCOUNT_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="number" class="form-control ${inputClass}" name="TAG_NO" value="${roadtoll.TAG_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="ACTIVATION_DATE" value="${roadtoll.ACTIVATION_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="ACTIVATION_END_DATE" value="${roadtoll.ACTIVATION_END_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              
              <td><select class="form-control ${inputClass}" name="CURRENT STATUS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><input type="file" class="form-control ${inputClass}" name="RoadtollAttachments" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="roadtoll_id" value="${roadtoll.RT_LINE_ID || ""}" />
              <input type="hidden" name="FLEET_PROCESS" value="${roadtoll.FLEET_PROCESS}" />
            `;

            setupDropdownsForNewRow(row);

            setTimeout(() => {
              setDropdownValue(row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]'), roadtoll.EMIRATES);
              setDropdownValue(row.querySelector('select[name="TOLL TYPE_LOOKUP_NAME"]'), roadtoll.TOLL_TYPE);
              setDropdownValue(row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]'), roadtoll.CURRENT_STATUS);
            }, 0);

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);

              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (roadtoll.RoadtollAttachments) {
                const fileNames = getAllFileNames(roadtoll.RoadtollAttachments, 'roadtoll', roadtoll.RT_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

              updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();
          });
        }

        const permitsTable = document.querySelector("#permitsTable tbody");
        permitsTable.innerHTML = "";
        const hasApprovedPermitRow = data.permits.some(permit => permit.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.permits)) {
          const sortedPermits = data.permits.sort((a, b) => {
            // First, prioritize 'Active' status
            if (a.CUR_STAT_PERMIT === 'Active' && b.CUR_STAT_PERMIT !== 'Active') return -1;
            if (b.CUR_STAT_PERMIT === 'Active' && a.CUR_STAT_PERMIT !== 'Active') return 1;
            
            // Then, consider 'Approved' status
            if (a.FLEET_PROCESS === 'Approved' && b.FLEET_PROCESS !== 'Approved') return -1;
            if (b.FLEET_PROCESS === 'Approved' && a.FLEET_PROCESS !== 'Approved') return 1;
            
            // If both have the same status, maintain their original order
            return 0;
          });
        
          sortedPermits.forEach((permit) => {
            const row = permitsTable.insertRow();
            row.dataset.process = permit.FLEET_PROCESS;
            let inputClass = '';
            // Set row color based on process
            if (permit.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (permit.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (permit.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }
           
            const isDisabled = isFromApprover || isApproverPage || permit.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><select class="form-control ${inputClass}" name="PERMIT_LOOKUP_NAME" onchange="togglePermitColour(this)" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control ${inputClass}" name="AE_EMIRATES_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control ${inputClass}" name="ISSUING AUTHORITY_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><input type="text" class="form-control ${inputClass}" name="PERMIT_NO" value="${permit.PERMIT_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="PERMIT_DATE" value="${permit.PERMIT_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="PERMIT_EXPIRY_DATE" value="${permit.PERMIT_EXPIRY_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><select class="form-control ${inputClass}" name="CURRENT STATUS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td class="permit-colour-cell ${inputClass}"></td>
              <td><input type="file" class="form-control ${inputClass}" name="PermitAattachment" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="permit_id" value="${permit.PERMIT_LINE_ID}" />
              <input type="hidden" name="FLEET_PROCESS" value="${permit.FLEET_PROCESS}" />
            `;

            setupDropdownsForNewRow(row);
            setTimeout(() => {
              setDropdownValue(row.querySelector('select[name="PERMIT_LOOKUP_NAME"]'), permit.PERMIT_TYPE);
              setDropdownValue(row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]'), permit.EMIRATES);
              setDropdownValue(row.querySelector('select[name="ISSUING AUTHORITY_LOOKUP_NAME"]'), permit.ISSUING_AUTHORITY);
              setDropdownValue(row.querySelector('select[name="CURRENT STATUS_LOOKUP_NAME"]'), permit.CUR_STAT_PERMIT);

              togglePermitColour(row.querySelector('select[name="PERMIT_LOOKUP_NAME"]'));

              const permitColorInput = row.querySelector('input[name="PermitColor"]');
              if (permitColorInput && permit.PermitColor) {
                permitColorInput.value = permit.PermitColor;
              }
            }, 0);

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);

              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (permit.PermitAattachment) {
                const fileNames = getAllFileNames(permit.PermitAattachment, 'permits', permit.PERMIT_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

              updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();
          });
        }


        
        const gpsTable = document.querySelector("#gpsTable tbody");
        gpsTable.innerHTML = "";
        const hasApprovedGpsRow = data.gps.some(gps => gps.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.gps)) {
          data.gps.forEach((gps) => {
            const row = gpsTable.insertRow();
            row.dataset.process = gps.FLEET_PROCESS;
            let inputClass = '';

            if (gps.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (gps.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (gps.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }

            const isDisabled = isFromApprover || isApproverPage || gps.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><input type="text" class="form-control ${inputClass}" name="GPS_DEVICE_NO" value="${gps.GPS_DEVICE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="GPS_INSTALLATION_DATE" value="${gps.GPS_INSTALLATION_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control ${inputClass}" name="GPS_SERVICE_PROVIDER" value="${gps.GPS_SERVICE_PROVIDER || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="file" class="form-control ${inputClass}" name="GpsAattachment" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="gps_id" value="${gps.GT_LINE_ID}" />
              <input type="hidden" name="FLEET_PROCESS" value="${gps.FLEET_PROCESS}" />
            `;

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);

              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (gps.GpsAattachment) {
                const fileNames = getAllFileNames(gps.GpsAattachment, 'gps', gps.GT_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

              updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();
          });
        }


        const allocationTable = document.querySelector("#allocationTable tbody");
        allocationTable.innerHTML = "";
        const hasApprovedAllocationRow = data.allocation.some(allocation => allocation.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.allocation)) {
          data.allocation.forEach((allocation) => {
            const row = allocationTable.insertRow();
            row.dataset.process = allocation.FLEET_PROCESS;
            let inputClass = '';

            if (allocation.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (allocation.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (allocation.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }

            const isDisabled = isFromApprover || isApproverPage || allocation.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><select class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="COMPANY NAME_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="DIVISIONS_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><select class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="AE_EMIRATES_LOOKUP_NAME" ${isDisabled ? 'disabled' : ''}><option value=""></option></select></td>
              <td><input type="date" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="ALLOCATION_DATE" value="${allocation.ALLOCATION_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="ALLOCATION_END_DATE" value="${allocation.ALLOCATION_END_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              
              <td><input type="file" class="form-control ${inputClass}" name="attachment" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="allocation_id" value="${allocation.ALLOC_LINE_ID|| ""}" />
              <input type="hidden" name="FLEET_PROCESS" value="${allocation.FLEET_PROCESS}" />
            `;


            setupDropdownsForNewRow(row);

            setTimeout(() => {
              setDropdownValue(row.querySelector('select[name="COMPANY NAME_LOOKUP_NAME"]'), allocation.COMPANY_NAME);
              setDropdownValue(row.querySelector('select[name="DIVISIONS_LOOKUP_NAME"]'), allocation.DIVISION);
              setDropdownValue(row.querySelector('select[name="OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME"]'), allocation.OPERATING_LOCATION);
              setDropdownValue(row.querySelector('select[name="AE_EMIRATES_LOOKUP_NAME"]'), allocation.OPERATING_EMIRATES);
            }, 0);

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);

              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (allocation.attachment) {
                const fileNames = getAllFileNames(allocation.attachment, 'allocation', allocation.ALLOC_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

              updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();
          });
        }



        const driverTable = document.querySelector("#driverTable tbody");
        driverTable.innerHTML = "";
        const hasApprovedDriverRow = data.driver.some(driver => driver.FLEET_PROCESS === 'Approved');

        if (Array.isArray(data.driver)) {
          data.driver.forEach((driver) => {
            const row = driverTable.insertRow();
            row.dataset.process = driver.FLEET_PROCESS;
            let inputClass = '';

            if (driver.FLEET_PROCESS === 'Approved') {
              inputClass = 'approved-input';
            } else if (driver.FLEET_PROCESS === 'Pending for Approval') {
              inputClass = 'pending-input';
            } else if (driver.FLEET_PROCESS === 'Return for Correction') {
              inputClass = 'rectification-input';
            }

            const isDisabled = isFromApprover || isApproverPage || driver.FLEET_PROCESS === 'Approved';

            row.innerHTML = `
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="EMPLOYEE_NO" value="${driver.EMPLOYEE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="EMPLOYEE_NAME" value="${driver.EMPLOYEE_NAME || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="DESIGNATION" value="${driver.DESIGNATION || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control  ${inputClass}" style="background-color: #ffff76; color: black" name="CONTACT_NUMBER" value="${driver.CONTACT_NUMBER || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" style="background-color: #ffff76; color: black" name="ASSIGNMENT_DATE" value="${driver.ASSIGNMENT_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              
              <td><input type="date" class="form-control ${inputClass}" style="background-color: #ffff76; color: black" name="ASSIGNMENT_END_DATE" value="${driver.ASSIGNMENT_END_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="number" class="form-control ${inputClass}" name="TRAFFIC_CODE_NO" value="${driver.TRAFFIC_CODE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="number" class="form-control ${inputClass}" name="DRIVING_LICENSE_NO" value="${driver.DRIVING_LICENSE_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control ${inputClass}" name="LICENSE_TYPE" value="${driver.LICENSE_TYPE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="text" class="form-control ${inputClass}" name="PLACE_OF_ISSUE" value="${driver.PLACE_OF_ISSUE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="LICENSE_EXPIRY_DATE" value="${driver.LICENSE_EXPIRY_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="number" class="form-control ${inputClass}" name="GPS_TAG_NO" value="${driver.GPS_TAG_NO || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="date" class="form-control ${inputClass}" name="GPS_TAG_ASSIGN_DATE" value="${driver.GPS_TAG_ASSIGN_DATE || ""}" ${isDisabled ? 'disabled' : ''}/></td>
              <td><input type="file" class="form-control ${inputClass}" name="DriverAttachments" multiple ${isDisabled ? 'disabled' : ''}/></td>
              <input type="hidden" name="driver_id" value="${driver.ASGN_LINE_ID}" />
              <input type="hidden" name="FLEET_PROCESS" value="${driver.FLEET_PROCESS}" />
            `;
            setupDriverSearchFunctionality(row);

            const fileInput = row.querySelector('input[type="file"]');
            const fileListContainer = document.createElement("div");
              fileListContainer.className = "file-list-container";

              // Wrap the file input and dropdown in a container
              const wrapper = document.createElement('div');
              wrapper.className = 'file-input-wrapper';
              fileInput.parentNode.insertBefore(wrapper, fileInput);
              wrapper.appendChild(fileInput);
              wrapper.appendChild(fileListContainer);

              const fileDropdown = createFileDropdown();
              fileListContainer.appendChild(fileDropdown);

              if (fromApprover) {
fileInput.disabled = true;
fileInput.style.backgroundColor = '#e9ecef';
fileDropdown.style.pointerEvents = 'none';
fileDropdown.style.opacity = '0.7';
fileDropdown.querySelector('.file-list').style.backgroundColor = '#e9ecef';
} else {
fileInput.disabled = false;
fileInput.style.backgroundColor = '';
fileDropdown.style.pointerEvents = 'auto';
fileDropdown.style.opacity = '1';
fileDropdown.querySelector('.file-list').style.backgroundColor = '';
}

            if (driver.DriverAttachments) {
                const fileNames = getAllFileNames(driver.DriverAttachments, 'driver', driver.ASGN_LINE_ID);
                fileDropdown.querySelector('.file-list').innerHTML = fileNames;
            }

              updateFileCount(fileInput, fileDropdown);
            addFileInputListeners();
          });
        }



        if (data.STATUS === 'Defleet') {
          freezeForm();
          updateEditButtonState(data.STATUS);
        } else {
          setupDeleteListeners();
          disableAllFields();
          updateSaveButtonVisibility(data.STATUS);
          disableEditingControls();
          showEditButton();
          isPopulatedData = true;
  
          const editButton = document.getElementById('editButton');
          if (editButton) {
            editButton.style.display = 'block';
            editButton.addEventListener('click', function(event) {
              if (this.disabled) {
                event.preventDefault();
                event.stopPropagation();
                return false;
              }
              handleEdit(data);
              enableEditingControls();
              this.style.display = 'none';
            });
          }
          
          if (data.STATUS === 'Draft') {
            handleTableFieldsForDraft(data);
        }



  
          isEditMode = false;
          updateEditButtonState(data.STATUS);
          afterPopulateForm();
          enableCommentsField();
        }
      }
    } catch (error) {
      console.error("Error fetching fleet details:", error);
    }
}



function enableCommentsField() {
  const commentsField = document.querySelector('textarea[name="COMMENTS"]');
  if (commentsField) {
      commentsField.disabled = false;
      commentsField.readOnly = false;
  }
}

document.addEventListener('DOMContentLoaded', function() {
  restoreFleetMasterState();
});

function handleEdit(data) {
  if (data.STATUS === 'Draft') {
    enableAllFields();
    handleTableFieldsForDraft(data);
  } else if (data.STATUS === 'Return for Correction') {
      handleRectificationEdit(data);
    } else if (data.STATUS === 'Approved') {
      handleApprovedEdit(data);
    } else {
      enableAllFields();
    }
  }



  function handleTableFieldsForDraft(data) {
  const isDraft = data.STATUS === 'Draft';
  
  // Define the arrays for disabled fields
  const disabledInsuranceFields = ['POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE'];
  const disabledRegistrationFields = ['REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO'];

  // Handle insurance table
  const insuranceTable = document.querySelector("#insuranceTable tbody");
  if (insuranceTable) {
    const insuranceRows = insuranceTable.querySelectorAll('tr');
    insuranceRows.forEach(row => {
      const inputs = row.querySelectorAll('input, select');
      inputs.forEach(input => {
        const fieldName = input.getAttribute('name');
        if (isDraft && disabledInsuranceFields.includes(fieldName)) {
          input.disabled = true;
          input.style.backgroundColor = '#e9ecef';
          input.style.color = '#495057';
          
          // Create hidden input to preserve the value
          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = fieldName;
          hiddenInput.value = input.value;
          input.parentNode.appendChild(hiddenInput);
        }
      });
    });
  }

  // Handle registration table
  const registrationTable = document.querySelector("#registrationTable tbody");
  if (registrationTable) {
    const registrationRows = registrationTable.querySelectorAll('tr');
    registrationRows.forEach(row => {
      const inputs = row.querySelectorAll('input, select');
      inputs.forEach(input => {
        const fieldName = input.getAttribute('name');
        if (isDraft && disabledRegistrationFields.includes(fieldName)) {
          input.disabled = true;
          input.style.backgroundColor = '#e9ecef';
          input.style.color = '#495057';
          
          // Create hidden input to preserve the value
          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = fieldName;
          hiddenInput.value = input.value;
          input.parentNode.appendChild(hiddenInput);
        }
      });
    });
  }
}

function enableNewFieldsOnly() {
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    if (input.value === '') {
      input.disabled = false;
    }
  });

  // Enable empty rows in tables
  const tables = document.querySelectorAll('table');
  tables.forEach(table => {
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      const inputs = row.querySelectorAll('input, select, textarea');
      let isEmpty = true;
      inputs.forEach(input => {
        if (input.value !== '') {
          isEmpty = false;
        }
      });
      if (isEmpty) {
        inputs.forEach(input => {
          input.disabled = false;
        });
      }
    });
  });

  // Enable all buttons
  const buttons = document.querySelectorAll('button');
  buttons.forEach(button => {
    button.disabled = false;
  });
}

function disableFleetMasterEditing() {
  const fleetMasterFields = document.querySelectorAll('#vehicleForm input:not([name="FLEET_CONTROL_NO"]), #vehicleForm select');
  fleetMasterFields.forEach(field => {
    field.disabled = true;
  });
  
  
} 
 

function enableFleetMasterEditing() {
  const hasApprovedInsuranceRow = data.insurances.some(insurance => insurance.FLEET_PROCESS === 'Approved');
  const hasApprovedPermitRow = data.permits.some(permit => permit.FLEET_PROCESS === 'Approved');
  const hasApprovedGpsRow = data.gps.some(gps => gps.FLEET_PROCESS === 'Approved');
  const hasApprovedRegistrationRow = data.registration.some(registration => registration.FLEET_PROCESS === 'Approved');
  const hasApprovedFuelRow = data.fuel.some(fuel => fuel.FLEET_PROCESS === 'Approved');
  const hasApprovedRoadtollRow = data.roadtoll.some(roadtoll => roadtoll.FLEET_PROCESS === 'Approved');
  const hasApprovedAllocationRow = data.allocation.some(allocation => allocation.FLEET_PROCESS === 'Approved');
  const hasApprovedDriverRow = data.driver.some(driver => driver.FLEET_PROCESS === 'Approved');

  if (hasApprovedInsuranceRow || hasApprovedPermitRow || hasApprovedGpsRow ||
      hasApprovedRegistrationRow || hasApprovedFuelRow || hasApprovedRoadtollRow ||
      hasApprovedAllocationRow || hasApprovedDriverRow) {
    disableFleetMasterEditing();
  } else {
    const fleetMasterFields = document.querySelectorAll('#vehicleForm input:not([name="FLEET_CONTROL_NO"]), #vehicleForm select');
    fleetMasterFields.forEach(field => {
      field.disabled = false;
    });
  }
}
function handleApprovedEdit(data) {
  const fleetMasterFields = [
    'FLEET_CREATION_DATE','STATUS','FLEET_CONTROL_NO'
  ];

  // Disable all populated fields
  const inputs = document.querySelectorAll( ' textarea');
  inputs.forEach(input => {
    const name = input.getAttribute('name');
    if (name === 'COMMENTS') {
      input.disabled = false;
    } else if (fleetMasterFields.includes(name) || name === 'FLEET_CONTROL_NO') {
      input.disabled = true;
      // Create a hidden input to send the value in the request
      const hiddenInput = document.createElement('input');
      hiddenInput.type = 'hidden';
      hiddenInput.name = name;
      hiddenInput.value = input.value;
      input.parentNode.appendChild(hiddenInput);
    } else if (input.value !== '') {
      input.disabled = true;
    } else {
      input.disabled = false;
    }
  });

  const fleetStatusInput = document.querySelector('[name="STATUS"]');
  if (fleetStatusInput) {
    // Make it appear disabled visually
    fleetStatusInput.style.backgroundColor = '#e9ecef';
    fleetStatusInput.style.color = '#495057';
    fleetStatusInput.readOnly = true; // Use readOnly instead of disabled

    // Create a hidden input for FleetStatus
    const hiddenStatusInput = document.createElement('input');
    hiddenStatusInput.type = 'hidden';
    hiddenStatusInput.name = 'STATUS';
    hiddenStatusInput.value = 'Pending for Approval'; // Always set to 'Pending' when submitting
    fleetStatusInput.parentNode.appendChild(hiddenStatusInput);
  }

  // Handle table rows
  const tables = ['insuranceTable', 'registrationTable', 'gpsTable', 'permitsTable', 'fuelTable', 'roadtollTable', 'driverTable', 'allocationTable'];
  const disabledInsuranceFields = ['POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE'];
  const disabledRegistrationFields = ['REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO'];

  
  tables.forEach(tableId => {
    const table = document.getElementById(tableId);
    if (table) {
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach((row, index) => {
        const inputs = row.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          if ((tableId === 'insuranceTable' && disabledInsuranceFields.includes(input.name)) ||
              (tableId === 'registrationTable' && disabledRegistrationFields.includes(input.name)) ||
              (tableId === 'driverTable' && disabledDriverFields.includes(input.name)) ||
              (tableId === 'allocationTable' && disabledAllocationFields.includes(input.name))) {
            input.disabled = true;
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = input.name;
            hiddenInput.value = input.value;
            input.parentNode.appendChild(hiddenInput);
          } else {
            input.disabled = false;
          }
        });
      });

      // Enable the last row if it's empty
      const lastRow = rows[rows.length - 1];
      if (lastRow) {
        const lastRowInputs = lastRow.querySelectorAll('input, select, textarea');
        let isLastRowEmpty = true;
        lastRowInputs.forEach(input => {
          if (input.value !== '') {
            isLastRowEmpty = false;
          }
        });
        if (isLastRowEmpty) {
          lastRowInputs.forEach(input => {
            input.disabled = false;
          });
        }
      }
    }
  });

  // Enable add row and remove row buttons
  document.getElementById('addRow').disabled = false;
  document.getElementById('removeRow').disabled = false;

  isEditMode = true;
}




function handleRectificationEdit(data) {
  const hasApprovedRow = ['insurances', 'permits', 'gps', 'registration', 'fuel', 'roadtoll', 'allocation', 'driver'].some(
    category => data[category].some(item => item.FLEET_PROCESS === 'Approved')
  );

  const fieldsToAlwaysDisable = ['FLEET_CONTROL_NO', 'FLEET_CREATION_DATE', 'STATUS'];

  // Handle main form fields
  const mainFormInputs = document.querySelectorAll('#vehicleForm input, #vehicleForm select, #vehicleForm textarea');
  mainFormInputs.forEach(input => {
    const name = input.getAttribute('name');
    
    if (fieldsToAlwaysDisable.includes(name)) {
      input.disabled = true;
    } else {
      input.disabled = false;
    }

    // Create hidden input for all fields to ensure data is sent in the request
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = name;
    hiddenInput.value = input.value;
    input.parentNode.appendChild(hiddenInput);
  });

  // Handle FleetStatus field
  const fleetStatusInput = document.querySelector('[name="STATUS"]');
  if (fleetStatusInput) {
    fleetStatusInput.style.backgroundColor = '#e9ecef';
    fleetStatusInput.style.color = '#495057';
    fleetStatusInput.readOnly = true;

    // Create a hidden input for FleetStatus
    const hiddenStatusInput = document.createElement('input');
    hiddenStatusInput.type = 'hidden';
    hiddenStatusInput.name = 'STATUS';
    hiddenStatusInput.value = 'Pending for Approval'; // Set to 'Pending' when submitting
    fleetStatusInput.parentNode.appendChild(hiddenStatusInput);
  }

  // Handle table rows
  const tables = ['insuranceTable', 'registrationTable', 'gpsTable', 'permitsTable', 'fuelTable', 'roadtollTable', 'driverTable', 'allocationTable'];
  const disabledInsuranceFields = ['POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE'];
  const disabledRegistrationFields = ['REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO'];

  
  
  tables.forEach(tableId => {
    const table = document.getElementById(tableId);
    if (table) {
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach((row, index) => {
        const inputs = row.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          const name = input.getAttribute('name');
          if ((tableId === 'insuranceTable' && disabledInsuranceFields.includes(name)) ||
              (tableId === 'registrationTable' && disabledRegistrationFields.includes(name))) {
            input.disabled = true;
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = name;
            hiddenInput.value = input.value;
            input.parentNode.appendChild(hiddenInput);
          } else {
            input.disabled = false;
          }
        });
        
        const processInput = row.querySelector('input[name="FLEET_PROCESS"]');
        const isApproved = processInput && processInput.value === 'Approved';
        if (isApproved) {
          row.classList.add('approved-row');
        } else {
          row.classList.remove('approved-row');
        }
      });
    }
  });
  

  // Enable add row and remove row buttons
  document.getElementById('addRow').disabled = false;
  document.getElementById('removeRow').disabled = false;

  isEditMode = true;

  const commentsField = document.querySelector('[name="COMMENTS"]');
  if (commentsField) {
    commentsField.addEventListener('input', function() {
      const hiddenComments = this.parentNode.querySelector('input[type="hidden"][name="COMMENTS"]');
      if (hiddenComments) {
        hiddenComments.value = this.value;
      }
    });
  }
}

function updateEditButtonState(fleetStatus) {
  const editButton = document.getElementById('editButton');
  const isApprover = new URLSearchParams(window.location.search).get('from_approver') === 'true';
  const cancelButton = document.getElementById('cancelForm');

  if (cancelButton) {
    cancelButton.disabled = false;
    cancelButton.style.pointerEvents = 'auto';
    cancelButton.style.opacity = '1';
    cancelButton.style.cursor = 'pointer';
    //cancelButton.style.backgroundColor = 'white';
    cancelButton.style.color = 'black';

  }
  if (isApprover) {
      // For approver, always show the approver buttons
      // if (!approverButtonsAdded) {
      //     showApproverButtons();
      // }

      // Enable or disable approver buttons based on fleet status
      const approverButtons = document.querySelectorAll('.approver-buttons button');
      approverButtons.forEach(button => {
          if (fleetStatus === 'Defleet') {
              button.disabled = true;
              button.style.pointerEvents = 'none';
              button.style.opacity = '0.5';
          } else {
              button.disabled = false;
              button.style.pointerEvents = 'auto';
              button.style.opacity = '1';
          }
      });

      enableSubmitButton();
      enableCommentsAndButtons();

      // Hide the regular edit button for approvers
      if (editButton) {
        editButton.style.display = 'none';
      }
    } else {
      // For requestor, handle as before
      if (editButton) {
            if (fleetStatus === 'Pending for Approval' || fleetStatus === 'Defleet') {
          editButton.disabled = true;
          editButton.style.pointerEvents = 'none';
          editButton.style.opacity = '0.5';
          const tabs = document.querySelectorAll('.tab');
          tabs.forEach(tab => {
            tab.style.pointerEvents = 'auto';
            tab.style.cursor = 'pointer';
          });
          
          initializeTabs();
            } else {
                editButton.disabled = false;
                editButton.style.pointerEvents = 'auto';
                editButton.style.opacity = '1';
            }
        }
    }

    // Always enable these buttons
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
  }




  function updateStatusDisplay(status) {
    const statusField = document.querySelector('input[name="STATUS"]');
    if (statusField) {
        statusField.value = status;
    }
    const statusDisplays = document.querySelectorAll('.status-display');
    statusDisplays.forEach(display => {
        display.textContent = status;
    });
  }