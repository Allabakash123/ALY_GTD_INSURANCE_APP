
let insuranceFileInfo = [];
let activeInsuranceSearchInput = null;

 

        function addInsuranceRow() {
          const tbody = document.querySelector('#insuranceTable tbody');
          const newRow = tbody.insertRow();
          
          newRow.innerHTML = `
            <td>
              <input type="text" 
                class="form-control insurance-search-input" 
                name="INSURANCE_COMPANY"
                required
                data-required="true"
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                style="background-color: #ffff76; color: black"/>
              <div class="insurance-search-results-container" style="display: none;">
                <div class="insurance-search-results-header">
                  <span>Insurance File Search Results</span>
                  <span class="insurance-close-icon">&times;</span>
                </div>
                <table class="insurance-search-results">
                  <thead>
                    <tr>
                      <th>Insurance Company</th>
                      <th>Policy No</th>
                      <th>Policy Date</th>
                      <th>Policy Expiry Date</th>
                    </tr>
                  </thead>
                  <tbody></tbody>
                </table>
              </div>
            </td>
            <td><input type="text" class="form-control" name="POLICY_NO" required data-required="true" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="POLICY_DATE" required data-required="true" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="POLICY_EXPIRY_DATE" required data-required="true" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="PLTS_INS_START_DATE" required data-required="true" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="PLTS_INS_EXPIRY_DATE" required data-required="true" style="background-color: #ffff76; color: black"/></td>
            <td><select class="form-control" name="CURRENT STATUS_LOOKUP_NAME" required data-required="true" style="background-color: #ffff76; color: black"><option value=""></option></select></td>
            <td><input type="file" class="form-control" name="InsurancePolicAattachment" /></td>
            <input type="hidden" name="insurance_id" value="new" />
            <input type="hidden" name="FLEET_PROCESS" value="Pending" />
          `;
        
          setupDropdownsForNewRow(newRow);
          setupValidation(newRow);
          addFileInputListeners();
          setupInsuranceSearchFunctionality(newRow);
        }
        

        function setupInsuranceSearchFunctionality(row) {
          const searchInput = row.querySelector('.insurance-search-input');
          if (!searchInput) {
            console.warn('Insurance search input not found in the row');
            return;
          }

          console.log('Setting up insurance search functionality for:', searchInput);

          searchInput.addEventListener('focus', (event) => {
            console.log('Focus event triggered on:', event.target);
            activeInsuranceSearchInput = searchInput;
          
            const fieldsToReset = ['INSURANCE_COMPANY', 'POLICY_NO', 'POLICY_DATE', 'POLICY_EXPIRY_DATE', ];
            fieldsToReset.forEach(fieldName => {
              const input = row.querySelector(`input[name="${fieldName}"]`);
              if (input) {
                input.readOnly = false;
                input.classList.remove('read-only-field');
              }
            });

            fetchAndPopulateInsuranceFileResults(searchInput);
          });

          searchInput.addEventListener('input', (event) => {
            console.log('Input event triggered on:', event.target);
            fetchAndPopulateInsuranceFileResults(searchInput);
          });
        }

        function initializeInsuranceFileInput() {
          console.log('Initializing insurance file input');
          const insuranceTable = document.getElementById('insuranceTable');
          if (insuranceTable) {
            const fileInputs = insuranceTable.querySelectorAll('input[type="file"]');
            console.log('Insurance file inputs:', fileInputs);
            fileInputs.forEach(input => {
              input.addEventListener('change', function() {
                console.log('Insurance file input changed');
                handleFileSelection(this);
              });
            });
          } else {
            console.warn('Insurance table not found');
          }
        }

        function reinitializeInsuranceFileInputs() {
          console.log('Reinitializing all insurance file inputs');
          addFileInputListeners();
    initializeInsuranceFileInput();
  }

  const originalAddInsuranceRow = addInsuranceRow;
  addInsuranceRow = function() {
    originalAddInsuranceRow();
    console.log('Insurance row added, reinitializing file inputs');
    reinitializeInsuranceFileInputs();
  };

  const insuranceTableObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        console.log('Insurance table changed, reinitializing file inputs');
        reinitializeInsuranceFileInputs();
      }
    });
  });

  document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    reinitializeInsuranceFileInputs();

    const insuranceTable = document.getElementById('insuranceTable');
    if (insuranceTable) {
      insuranceTableObserver.observe(insuranceTable, { childList: true, subtree: true });
    }
  });

  const globalInsuranceSearchResults = document.getElementById('globalInsuranceSearchResults');
  const closeInsuranceIcons = globalInsuranceSearchResults.querySelector('.insurance-close-icon');

  closeInsuranceIcons.addEventListener('click', (e) => {
    console.log('Close icon clicked');
    e.stopPropagation();
    hideInsuranceSearchResults();
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.insurance-search-input') && !event.target.closest('#globalInsuranceSearchResults')) {
      hideInsuranceSearchResults();
    }
  });

  async function fetchAndPopulateInsuranceFileResults(searchInput) {
    console.log('Fetching and populating insurance file results');
    try {
      await fetchInsuranceFileInfo();
      filterAndDisplayInsuranceFileResults(searchInput);
      showInsuranceSearchResults();
    } catch (error) {
      console.error('Error fetching insurance file info:', error);
    }
  }

  function filterAndDisplayInsuranceFileResults(searchInput) {
    console.log('Filtering and displaying insurance file results');
    const searchTerm = searchInput.value.toLowerCase();
    const filteredInfo = insuranceFileInfo.filter(info =>
      info.INSURANCE_COMPANY.toLowerCase().includes(searchTerm)
    );

    console.log('Filtered info:', filteredInfo);

    const searchResults = globalInsuranceSearchResults.querySelector('.insurance-search-results tbody');
    searchResults.innerHTML = '';
    filteredInfo.forEach((info) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${info.INSURANCE_COMPANY}</td>
        <td>${info.POLICY_NO}</td>
        <td>${info.POLICY_DATE}</td>
        <td>${info.POLICY_EXPIRY_DATE}</td>
      `;
      tr.addEventListener('click', function (e) {
        console.log('Search result clicked');
        e.stopPropagation();
        populateInsuranceFields(activeInsuranceSearchInput, info);
        hideInsuranceSearchResults();
      });
      searchResults.appendChild(tr);
    });
  }

  function showInsuranceSearchResults() {
    console.log('Showing insurance search results');
    globalInsuranceSearchResults.style.display = 'block';
  }

  function hideInsuranceSearchResults() {
    console.log('Hiding insurance search results');
    globalInsuranceSearchResults.style.display = 'none';
  }

  async function fetchInsuranceFileInfo() {
    if (insuranceFileInfo.length === 0) {
      console.log('Fetching insurance file info from API');
      try {
        const response = await fetch('http://127.0.0.1:8000/api/insurance-info');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        insuranceFileInfo = await response.json();
        console.log('Fetched insurance file info:', insuranceFileInfo);
      } catch (error) {
        console.error('Error fetching insurance file info:', error);
      }
    } else {
      console.log('Using cached insurance file info');
    }
    return insuranceFileInfo;
  }

  function populateInsuranceFields(searchInput, info) {
    console.log('Populating insurance fields with:', info);
    const row = searchInput.closest('tr');
  
    const fieldsToPopulate = [
      { name: 'INSURANCE_COMPANY', value: info.INSURANCE_COMPANY },
      { name: 'POLICY_NO', value: info.POLICY_NO },
      { name: 'POLICY_DATE', value: info.POLICY_DATE },
      { name: 'POLICY_EXPIRY_DATE', value: info.POLICY_EXPIRY_DATE },
    ];

    fieldsToPopulate.forEach(field => {
      const input = row.querySelector(`input[name="${field.name}"]`);
      if (input) {
        input.value = field.value;
        input.readOnly = true;
        input.classList.add('read-only-field');
      }
    });

    const insuranceCompanyInput = row.querySelector('input[name="INSURANCE_COMPANY"]');
    insuranceCompanyInput.addEventListener('focus', function() {
      fieldsToPopulate.forEach(field => {
        const input = row.querySelector(`input[name="${field.name}"]`);
        if (input) {
          input.readOnly = false;
          input.classList.remove('read-only-field');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded');
    const existingRows = document.querySelectorAll('#insuranceTable tbody tr');
    existingRows.forEach(row => setupInsuranceSearchFunctionality(row));
  });


  let trafficFileInfo = [];
  let activeSearchInput = null;

  // Function to add a new registration row with dynamic dropdowns
  function addRegistrationRow() {
          const tbody = document.querySelector('#registrationTable tbody');
          const newRow = tbody.insertRow();

          // Create the HTML for the new row with dropdowns
          newRow.innerHTML = `
            <td>
                  <input type="text" class="form-control traffic-search-input" name="EMIRATES_TRF_FILE_NO" required style="background-color: #ffff76; color: black"/>
                </td>  
            <td><input type="text" class="form-control" name="REGISTERED_EMIRATES" required /></td>
              
            <td><input type="text" class="form-control" name="FEDERAL_TRF_FILE_NO" required/></td>
            <td><input type="text" class="form-control" name="REG_COMPANY_NAME" required/></td>
            <td><input type="text" class="form-control" name="TRADE_LICENSE_NO" required/></td>
            <td><input type="text" class="form-control" name="REGISTRATION_NO1" style="background-color: #ffff76; color: black"/></td>
            <td><input type="text" class="form-control" name="REGISTRATION_NO" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="REGISTRATION_DATE" style="background-color: #ffff76; color: black"/></td>
            <td><input type="date" class="form-control" name="REG_EXPIRY_DATE" style="background-color: #ffff76; color: black" /></td>
            <td><select class="form-control" name="CURRENT STATUS_LOOKUP_NAME" style="background-color: #ffff76; color: black" ><option value=""></option></select> </td>
            <td><input type="file" class="form-control" name="RegCardAttachment"/></td>
            <input type="hidden" name="registration_id" value="new" />
          `;

          setupDropdownsForNewRow(newRow);
        setupValidation(newRow);
        addFileInputListeners();
        setupTrafficSearchFunctionality(newRow);
  }

  function setupTrafficSearchFunctionality(row) {
    const searchInput = row.querySelector('.traffic-search-input');
    if (!searchInput) {
      console.warn('Traffic search input not found in the row');
      return;
    }

    console.log('Setting up traffic search functionality for:', searchInput);

    searchInput.addEventListener('focus', (event) => {
      console.log('Focus event triggered on:', event.target);
      activeSearchInput = searchInput;
      
      // Reset read-only state for all fields in this row
      const fieldsToReset = ['EMIRATES_TRF_FILE_NO', 'REGISTERED_EMIRATES', 'FEDERAL_TRF_FILE_NO', 'REG_COMPANY_NAME', 'TRADE_LICENSE_NO'];
      fieldsToReset.forEach(fieldName => {
        const input = row.querySelector(`input[name="${fieldName}"]`);
        if (input) {
          input.readOnly = false;
          input.classList.remove('read-only-field');
        }
      });

      fetchAndPopulateTrafficFileResults(searchInput);
    });

    searchInput.addEventListener('input', (event) => {
      console.log('Input event triggered on:', event.target);
      fetchAndPopulateTrafficFileResults(searchInput);
    });
  }


  function setupValidation(row) {
    console.log('Setting up validation for row:', row);
    // Add your validation logic here if needed
  }
  
  function initializeRegistrationFileInput() {
    console.log('Initializing registration file input');
    const registrationTable = document.getElementById('registrationTable');
    if (registrationTable) {
      const fileInputs = registrationTable.querySelectorAll('input[type="file"]');
      console.log('Registration file inputs:', fileInputs);
      fileInputs.forEach(input => {
        input.addEventListener('change', function() {
          console.log('Registration file input changed');
          handleFileSelection(this);
        });
      });
    } else {
      console.warn('Registration table not found');
    }
  }
  
  function reinitializeFileInputs() {
    console.log('Reinitializing all file inputs');
    addFileInputListeners();
    initializeRegistrationFileInput();
  }
  
  // Modify the addRegistrationRow function
  const originalAddRegistrationRow = addRegistrationRow;
  addRegistrationRow = function() {
    originalAddRegistrationRow();
    console.log('Registration row added, reinitializing file inputs');
    reinitializeFileInputs();
  };
  
  // Add a mutation observer to watch for changes in the registration table
  const registrationTableObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        console.log('Registration table changed, reinitializing file inputs');
        reinitializeFileInputs();
      }
    });
  });
  
  document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    reinitializeFileInputs();
  
    const registrationTable = document.getElementById('registrationTable');
    if (registrationTable) {
      registrationTableObserver.observe(registrationTable, { childList: true, subtree: true });
    }
  });

  const globalSearchResults = document.getElementById('globalTrafficSearchResults');
  const closeIcons = globalSearchResults.querySelector('.traffic-close-icon');

  closeIcons.addEventListener('click', (e) => {
    console.log('Close icon clicked');
    e.stopPropagation();
    hideTrafficSearchResults();
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.traffic-search-input') && !event.target.closest('#globalTrafficSearchResults')) {
      hideTrafficSearchResults();
    }
  });

  async function fetchAndPopulateTrafficFileResults(searchInput) {
    console.log('Fetching and populating traffic file results');
    try {
      await fetchTrafficFileInfo();
      filterAndDisplayTrafficFileResults(searchInput);
      showTrafficSearchResults();
    } catch (error) {
      console.error('Error fetching traffic file info:', error);
    }
  }

  function filterAndDisplayTrafficFileResults(searchInput) {
    console.log('Filtering and displaying traffic file results');
    const searchTerm = searchInput.value.toLowerCase();
    const filteredInfo = trafficFileInfo.filter(info =>
      info.TRAFFIC_FILE_NO.toLowerCase().includes(searchTerm)
    );

    console.log('Filtered info:', filteredInfo);

    const searchResults = globalSearchResults.querySelector('.traffic-search-results tbody');
    searchResults.innerHTML = '';
    filteredInfo.forEach((info) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${info.TRAFFIC_FILE_NO}</td>
        <td>${info.COMPANY_NAME}</td>
        <td>${info.TRADE_LICENSE_NO}</td>
        <td>${info.EMIRATES}</td>
        <td>${info.FEDERAL_TRAFFIC_FILE_NO}</td>
      `;
      tr.addEventListener('click', function (e) {
        console.log('Search result clicked');
        e.stopPropagation();
        populateTrafficRegistrationFields(activeSearchInput, info);
        hideTrafficSearchResults();
      });
      searchResults.appendChild(tr);
    });
  }

  function showTrafficSearchResults() {
    console.log('Showing traffic search results');
    globalSearchResults.style.display = 'block';
  }

  function hideTrafficSearchResults() {
    console.log('Hiding traffic search results');
    globalSearchResults.style.display = 'none';
  }


  async function fetchTrafficFileInfo() {
    if (trafficFileInfo.length === 0) {
      console.log('Fetching traffic file info from API');
      try {
        const response = await fetch('http://127.0.0.1:8000/api/traffic-file-info');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        trafficFileInfo = await response.json();
        console.log('Fetched traffic file info:', trafficFileInfo);
      } catch (error) {
        console.error('Error fetching traffic file info:', error);
      }
    } else {
      console.log('Using cached traffic file info');
    }
    return trafficFileInfo;
  }

  

  function populateTrafficRegistrationFields(searchInput, info) {
    console.log('Populating traffic registration fields with:', info);
    const row = searchInput.closest('tr');
    
    // Populate and make fields read-only
    const fieldsToPopulate = [
      { name: 'EMIRATES_TRF_FILE_NO', value: info.TRAFFIC_FILE_NO },
      { name: 'REGISTERED_EMIRATES', value: info.EMIRATES },
      { name: 'FEDERAL_TRF_FILE_NO', value: info.FEDERAL_TRAFFIC_FILE_NO },
      { name: 'REG_COMPANY_NAME', value: info.COMPANY_NAME },
      { name: 'TRADE_LICENSE_NO', value: info.TRADE_LICENSE_NO }
    ];

    fieldsToPopulate.forEach(field => {
      const input = row.querySelector(`input[name="${field.name}"]`);
      if (input) {
        input.value = field.value;
        input.readOnly = true;
        input.classList.add('read-only-field');
      }
                                });

    // Add event listener to EmiratesTrafficFileNumber input
    const trafficFileInput = row.querySelector('input[name="EMIRATES_TRF_FILE_NO"]');
    trafficFileInput.addEventListener('focus', function() {
      // Remove read-only attribute when focused
      fieldsToPopulate.forEach(field => {
        const input = row.querySelector(`input[name="${field.name}"]`);
        if (input) {
          input.readOnly = false;
          input.classList.remove('read-only-field');
        }
      });
    });
  }


  // Make sure this function is called when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded');
    const existingRows = document.querySelectorAll('#registrationTable tbody tr');
    existingRows.forEach(row => setupTrafficSearchFunctionality(row));
  });



  function addRoadtollRow() {
      const tbody = document.querySelector('#roadtollTable tbody');
      const newRow = tbody.insertRow();
      newRow.innerHTML = `
        <td><select class="form-control" name="AE_EMIRATES_LOOKUP_NAME"><option value=""></option></select></td>
        <td><select class="form-control" name="TOLL TYPE_LOOKUP_NAME"><option value=""></option></select></td>
        <td><input type="number" class="form-control" name="ACCOUNT_NO" /></td>
        <td><input type="number" class="form-control" name="TAG_NO" /></td>
        <td><input type="date" class="form-control" name="ACTIVATION_DATE" /></td>
        
        <td><input type="date" class="form-control" name="ACTIVATION_END_DATE" /></td>
        <td><select class="form-control" name="CURRENT STATUS_LOOKUP_NAME"><option value=""></option></select></td>
        <td><input type="file" class="form-control" name="RoadtollAttachments" /></td>
        <input type="hidden" name="roadtoll_id" value="new" />
      `;

      setupDropdownsForNewRow(newRow);

      const inputs = newRow.querySelectorAll('input[required], select[required]');
      inputs.forEach(input => {
        input.addEventListener('blur', () => {
          validateRegistrationField(input);
        });
      });

      addFileInputListeners();
  }

  let driverInfo = [];
  let activeDriverSearchInput = null;

  function addDriverRow() {
    const tbody = document.querySelector('#driverTable tbody');
    const newRow = tbody.insertRow();
    newRow.innerHTML = `
        <td>
        <input type="text" class="form-control driver-search-input" name="EMPLOYEE_NO" style="background-color: #ffff76; color: black" required/>
        <div class="driver-search-wrapper">
          <div class="driver-search-results-container" style="display: none;">
            <div class="driver-search-results-header">
              <span>Driver Search Results</span>
              <span class="driver-close-icon">&times;</span>
            </div>
            <table class="driver-search-results">
              <thead>
                <tr>
                  <th>Emp No</th>
                  <th>Emp Name</th>
                  <th>Designation</th>
                  <th>Contact No</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </td>

        <td><input type="text" class="form-control" name="EMPLOYEE_NAME" style="background-color: #ffff76; color: black"/></td>
        <td><input type="text" class="form-control" name="DESIGNATION" style="background-color: #ffff76; color: black"/></td>
        <td><input type="text" class="form-control" name="CONTACT_NUMBER" style="background-color: #ffff76; color: black"/></td>
        <td><input type="date" class="form-control" name="ASSIGNMENT_DATE" style="background-color: #ffff76; color: black"/></td>
        <td><input type="date" class="form-control" name="ASSIGNMENT_END_DATE" style="background-color: #ffff76; color: black"/></td>
        <td><input type="text" class="form-control" name="TRAFFIC_CODE_NO" /></td>
        <td><input type="text" class="form-control" name="DRIVING_LICENSE_NO" /></td>
        <td><input type="text" class="form-control" name="LICENSE_TYPE" /></td>
        <td><input type="text" class="form-control" name="PLACE_OF_ISSUE" /></td>
        <td><input type="date" class="form-control" name="LICENSE_EXPIRY_DATE" /></td>
        <td><input type="text" class="form-control" name="GPS_TAG_NO" /></td>
        <td><input type="date" class="form-control" name="GPS_TAG_ASSIGN_DATE" /></td>
        <td><input type="file" class="form-control" name="DriverAttachments"/></td>
        <input type="hidden" name="driver_id" value="new" />
    `;

    setupDropdownsForNewRow(newRow);
      setupValidation(newRow);
      addFileInputListeners();
      setupDriverSearchFunctionality(newRow);
  }

  function setupDriverSearchFunctionality(row) {
      const searchInput = row.querySelector('.driver-search-input');
      if (!searchInput) {
          console.warn('Driver search input not found in the row');
          return;
      }

      console.log('Setting up driver search functionality for:', searchInput);

      searchInput.addEventListener('focus', (event) => {
          console.log('Focus event triggered on:', event.target);
          activeDriverSearchInput = searchInput;

          const fieldsToReset = ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER'];
          fieldsToReset.forEach(fieldName => {
              const input = row.querySelector(`input[name="${fieldName}"]`);
              if (input) {
                  input.readOnly = false;
                  input.classList.remove('read-only-field');
              }
          });

          fetchAndPopulateDriverResults(searchInput);
      });

      searchInput.addEventListener('input', (event) => {
          console.log('Input event triggered on:', event.target);
          fetchAndPopulateDriverResults(searchInput);
      });
  }

  function setupValidation(row) {
      console.log('Setting up validation for row:', row);
  }

  function initializeDriverFileInput() {
      console.log('Initializing driver file input');
      const driverTable = document.getElementById('driverTable');
      if (driverTable) {
          const fileInputs = driverTable.querySelectorAll('input[type="file"]');
          console.log('Driver file inputs:', fileInputs);
          fileInputs.forEach(input => {
              input.addEventListener('change', function() {
                  console.log('Driver file input changed');
                  handleFileSelection(this);
              });
          });
      } else {
          console.warn('Driver table not found');
      }
  }

  function reinitializeFileInputs() {
      console.log('Reinitializing all file inputs');
    addFileInputListeners();
      initializeDriverFileInput();
  }

  const originalAddDriverRow = addDriverRow;
  addDriverRow = function() {
      originalAddDriverRow();
      console.log('Driver row added, reinitializing file inputs');
      reinitializeFileInputs();
  };

  const driverTableObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
              console.log('Driver table changed, reinitializing file inputs');
              reinitializeFileInputs();
          }
      });
  });

  document.addEventListener('DOMContentLoaded', function() {
      console.log('DOM fully loaded');
      reinitializeFileInputs();

      const driverTable = document.getElementById('driverTable');
      if (driverTable) {
          driverTableObserver.observe(driverTable, { childList: true, subtree: true });
      }
  });

  const globalDriverSearchResults = document.getElementById('globalDriverSearchResults');
  const DrivercloseIcon = globalDriverSearchResults.querySelector('.driver-close-icon');

  DrivercloseIcon.addEventListener('click', (e) => {
      console.log('Close icon clicked');
      e.stopPropagation();
      hideDriverSearchResults();
  });

  document.addEventListener('click', (event) => {
      if (!event.target.closest('.driver-search-input') && !event.target.closest('#globalDriverSearchResults')) {
          hideDriverSearchResults();
      }
  });

  async function fetchAndPopulateDriverResults(searchInput) {
      console.log('Fetching and populating driver results');
      try {
          await fetchDriverInfo();
          filterAndDisplayDriverResults(searchInput);
          showDriverSearchResults();
      } catch (error) {
          console.error('Error fetching driver info:', error);
      }
  }

  function filterAndDisplayDriverResults(searchInput) {
      console.log('Filtering and displaying driver results');
      const searchTerm = searchInput.value.toLowerCase();
      const filteredInfo = driverInfo.filter(info =>
          info.EMPLOYEE_NO.toString().toLowerCase().includes(searchTerm)
      );

      console.log('Filtered info:', filteredInfo);

      const searchResults = globalDriverSearchResults.querySelector('.driver-search-results tbody');
      searchResults.innerHTML = '';
      filteredInfo.forEach((info) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
              <td>${info.EMPLOYEE_NO}</td>
              <td>${info.EMPLOYEE_NAME}</td>
              <td>${info.DESIGNATION}</td>
              <td>${info.CONTACT_NUMBER}</td>
          `;
          tr.addEventListener('click', function (e) {
              console.log('Search result clicked');
              e.stopPropagation();
              populateDriverFields(activeDriverSearchInput, info);
              hideDriverSearchResults();
          });
          searchResults.appendChild(tr);
      });
  }

  function showDriverSearchResults() {
      console.log('Showing driver search results');
      globalDriverSearchResults.style.display = 'block';
  }

  function hideDriverSearchResults() {
      console.log('Hiding driver search results');
      globalDriverSearchResults.style.display = 'none';
  }

  async function fetchDriverInfo() {
      if (driverInfo.length === 0) {
          console.log('Fetching driver info from API');
          try {
              const response = await fetch('http://127.0.0.1:8000/api/driver-info');
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              driverInfo = await response.json();
              console.log('Fetched driver info:', driverInfo);
          } catch (error) {
              console.error('Error fetching driver info:', error);
          }
      } else {
          console.log('Using cached driver info');
      }
      return driverInfo;
  }

  function populateDriverFields(searchInput, info) {
      console.log('Populating driver fields with:', info);
      const row = searchInput.closest('tr');

      const fieldsToPopulate = [
          { name: 'EMPLOYEE_NO', value: info.EMPLOYEE_NO },
          { name: 'EMPLOYEE_NAME', value: info.EMPLOYEE_NAME },
          { name: 'DESIGNATION', value: info.DESIGNATION },
          { name: 'CONTACT_NUMBER', value: info.CONTACT_NUMBER }
      ];

      fieldsToPopulate.forEach(field => {
          const input = row.querySelector(`input[name="${field.name}"]`);
          if (input) {
              input.value = field.value;
              input.readOnly = true;
              input.classList.add('read-only-field');
          }
      });

      const employeeInput = row.querySelector('input[name="EMPLOYEE_NO"]');
      employeeInput.addEventListener('focus', function() {
          fieldsToPopulate.forEach(field => {
              const input = row.querySelector(`input[name="${field.name}"]`);
              if (input) {
                  input.readOnly = false;
                  input.classList.remove('read-only-field');
              }
          });
      });
  }

  document.addEventListener('DOMContentLoaded', () => {
      console.log('DOM content loaded');
      const existingRows = document.querySelectorAll('#driverTable tbody tr');
      existingRows.forEach(row => setupDriverSearchFunctionality(row));
  });

  


  function addAllocationRow() {
    const tbody = document.querySelector('#allocationTable tbody');
    const newRow = tbody.insertRow();
    newRow.innerHTML = `
      <td><select class="form-control" name="COMPANY NAME_LOOKUP_NAME"style="background-color: #ffff76; color: black"><option value=""></option></select></td>
      <td><select class="form-control" name="DIVISIONS_LOOKUP_NAME"style="background-color: #ffff76; color: black"><option value=""></option></select></td>
      <td><select class="form-control" name="OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME"style="background-color: #ffff76; color: black"><option value=""></option></select></td>
      <td><select class="form-control" name="AE_EMIRATES_LOOKUP_NAME"style="background-color: #ffff76; color: black"><option value=""></option></select></td>
     
      <td><input type="date" class="form-control" name="ALLOCATION_DATE" style="background-color: #ffff76; color: black" /></td>
      
      <td><input type="date" class="form-control" name="ALLOCATION_END_DATE" /></td>
      <td><input type="file" class="form-control" name="attachment" /></td>
      <input type="hidden" name="allocation_id" value="new" />
    `;

    setupDropdownsForNewRow(newRow);

    const inputs = newRow.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        validateAllocationField(input);
      });
    });

    addFileInputListeners();
  }


  function addFuelRow() {
    const tbody = document.querySelector('#fuelTable tbody');
    const newRow = tbody.insertRow();
    newRow.innerHTML = `
      <td><select class="form-control" name="FUEL TYPE_LOOKUP_NAME"><option value=""></option></select></td>
      <td><input type="text" class="form-control" name="MONTHLY_FUEL_LIMIT"/></td>
      <td><select class="form-control" name="FUEL SERVICE TYPE_LOOKUP_NAME"><option value=""></option></select></td>
      <td><select class="form-control" name="FUEL SERVICE PROVIDER_LOOKUP_NAME"><option value=""></option></select></td>
      <td><input type="text" class="form-control" name="FUEL_DOCUMENT_NO"/></td>
      <td><input type="date" class="form-control" name="FUEL_DOCUMENT_DATE"/></td>
      <td><input type="date" class="form-control" name="FUEL_DOC_EXPIRY_DATE"/></td>
      <td><select class="form-control" name="CURRENT STATUS_LOOKUP_NAME"><option value=""></option></select></td>
      <td><input type="file" class="form-control" name="FuelDocumentAttachment"/></td>
      <input type="hidden" name="fuel_id" value="new" />
    `;

    setupDropdownsForNewRow(newRow);

    const inputs = newRow.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        validateFuelField(input);
      });
    });

    addFileInputListeners();
  }


  function addgpsRow() {
          const tbody = document.querySelector('#gpsTable tbody');
          const newRow = tbody.insertRow();
          newRow.innerHTML = `
              <td><input type="text" class="form-control" name="GPS_DEVICE_NO" /></td>
              <td><input type="date" class="form-control" name="GPS_INSTALLATION_DATE" /></td>
              <td><input type="text" class="form-control" name="GPS_SERVICE_PROVIDER" /></td>
              <td><input type="file" class="form-control" name="GpsAattachment" /></td>
            <input type="hidden" name="gps_id" value="new" />
          `;
          addFileInputListeners();
  }

  function addPermitRow() {
          const tbody = document.querySelector('#permitsTable tbody');
          const newRow = tbody.insertRow();
          newRow.innerHTML = `
              <td><select class="form-control" name="PERMIT_LOOKUP_NAME" onchange="togglePermitColour(this)"><option value=""></option></select></td>
              <td><select class="form-control" name="AE_EMIRATES_LOOKUP_NAME"><option value=""></option></select></td>
              <td><select class="form-control" name="ISSUING AUTHORITY_LOOKUP_NAME"><option value=""></option></select></td>
              <td><input type="text" class="form-control" name="PERMIT_NO" /></td>
              <td><input type="date" class="form-control" name="PERMIT_DATE" /></td>
              <td><input type="date" class="form-control" name="PERMIT_EXPIRY_DATE" /></td>
              <td><select class="form-control" name="CURRENT STATUS_LOOKUP_NAME"><option value=""></option></select></td>
              <td class="permit-colour-cell"></td>
              <td class="attachment-cell">
                  <input type="file" class="form-control" name="PermitAattachment" />
              </td>
              <input type="hidden" name="permit_id" value="new" />
          `;
          //  updatePermitColourHeader();
          togglePermitColour(newRow.querySelector('select[name="PERMIT_LOOKUP_NAME"]'));
          addFileInputListeners();
          setupDropdownsForNewRow(newRow);
        }

        function togglePermitColour(select) {
          const row = select.closest('tr');
          const permitColourCell = row.querySelector('.permit-colour-cell');

          if (select.value === 'Advertisement Card') {
              permitColourCell.innerHTML = '<input type="text" class="form-control" name="PermitColor" />';
              permitColourCell.classList.add('active');
              if (select.disabled) {
              permitColourCell.querySelector('input').disabled = true;
            }
          } else {
              permitColourCell.innerHTML = '';
              permitColourCell.classList.remove('active');
          }

          updatePermitColourHeader();
        }

        function updatePermitColourHeader() {
          const permitColourHeader = document.querySelector('.permit-colour-header');
          const visiblePermitColourInputs = document.querySelectorAll('.permit-colour-cell.active');

          permitColourHeader.classList.toggle('active', visiblePermitColourInputs.length > 0);
  }

  document.getElementById('addRow').addEventListener('click', function () {
    if (isPopulatedData && !isEditMode) {
      alert("Please enable editing first.");
        return;
    }
    const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');

      switch(activeTab) {
        case 'insurance':
          addInsuranceRow();
          break;
        case 'permits':
          addPermitRow();
          break;
        case 'gps':
          addgpsRow();
          break;
        case 'registration':
          addRegistrationRow();
          break;
        case 'fuel':
          addFuelRow();
          break;
        case 'roadtoll':
          addRoadtollRow();
          break;
        case 'driver':
          addDriverRow();
          break;
        case 'allocation':
          addAllocationRow();
          break;
      }
  });

  document.getElementById('removeRow').addEventListener('click', function() {
          if (isPopulatedData && !isEditMode) {
            alert("Please enable editing first.");
            return;
          }

          const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
          let tbody;


          console.log('Active tab:', activeTab);

          switch(activeTab) {
            case 'insurance':
              tbody = document.querySelector('#insuranceTable tbody');
              break;
            case 'permits':
              tbody = document.querySelector('#permitsTable tbody');
              break;
            case 'gps':
              tbody = document.querySelector('#gpsTable tbody');
              break;
            case 'registration':
              tbody = document.querySelector('#registrationTable tbody');
              break;
            case 'fuel':
              tbody = document.querySelector('#fuelTable tbody');
              break;
            case 'roadtoll':
              tbody = document.querySelector('#roadtollTable tbody');
              break;
            case 'driver':
              tbody = document.querySelector('#driverTable tbody');
              break;
            case 'allocation':
              tbody = document.querySelector('#allocationTable tbody');
              break;
          }

          console.log('Selected tbody:', tbody);

          if (tbody && tbody.rows.length > 0) {
            const lastRow = tbody.rows[tbody.rows.length - 1];
            const inputs = lastRow.querySelectorAll('input, select');
            let isEmpty = true;

            console.log('Number of inputs in last row:', inputs.length);

            for (let input of inputs) {
              console.log('Input value:', input.value);
              if (input.value.trim() !== '' && input.type !== 'hidden') {
                isEmpty = false;
                break;
              }
            }

            console.log('Is row empty:', isEmpty);

            if (isEmpty) {
              tbody.deleteRow(-1);
              console.log('Row deleted');
            } else {
              alert('Cannot delete row with data. Please clear the row first.');
            }
          } else {
            console.log('No rows to delete');
          }
  });

  document.getElementById('newForm').addEventListener('click', function() {
    clearForm();
    location.reload();
    isEditMode = true; // This will refresh the page
  });


  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
  }

  function setupDeleteListeners() {
    document.querySelectorAll('.remove-file').forEach(removeIcon => {
        removeIcon.addEventListener('click', debounce(function(event) {
            const modelName = event.target.dataset.model;
            const instanceId = event.target.dataset.instance;
            const fileIndex = event.target.dataset.index;
            const fileName = event.target.dataset.fileName;

            deleteFile(modelName, instanceId, fileIndex, fileName);
        }, 250));
    });
  }

//       async function deleteFile(modelName, instanceId, fileIndex, fileName) {
//   console.log(`Attempting to delete file: ${fileName} from ${modelName}`);
//   if (confirm(`Are you sure you want to delete ${fileName}?`)) {
//       try {
//           const response = await fetch(`/api/delete-file/${modelName}/${instanceId}/${fileIndex}`, {
//               method: 'DELETE',
//           });
//           const data = await response.json();
//           console.log('Server response:', data);
//           if (response.ok) {
//               console.log('File deletion successful on server');
//               const fileItems = document.querySelectorAll('.file-item');
//               const fileItem = Array.from(fileItems).find(item => {
//                   const removeIcon = item.querySelector('.remove-file');
//                   return removeIcon &&
//                         removeIcon.dataset.fileName === fileName &&
//                         removeIcon.dataset.model === modelName &&
//                         removeIcon.dataset.instance === instanceId;
//               });

//               console.log('File item to remove:', fileItem);
//               if (fileItem) {
//                   fileItem.remove();
//                   console.log('File item removed from DOM');
//               } else {
//                   console.log('File item not found in DOM');
//               }
//               alert("File deleted successfully");
//               document.dispatchEvent(new CustomEvent('fileDeleted', { detail: { modelName, instanceId, fileName } }));
//               console.log('Custom event dispatched');
//           } else {
//               console.error("Error deleting file:", data.message);
//               alert("Error deleting file. Please try again.");
//           }
//       } catch (error) {
//           console.error('Error:', error);
//           alert("An error occurred while deleting the file. Please try again.");
//       }
//     }
// }
async function deleteFile(modelName, instanceId, fileIndex, fileName) {
      console.log(`Attempting to delete file: ${fileName} from ${modelName}`);
      
      if (confirm(`Are you sure you want to delete ${fileName}?`)) {
          try {
              const response = await fetch(`/api/delete-file/${modelName}/${instanceId}/${fileIndex}`, {
                  method: 'DELETE',
                  headers: {
                      'Content-Type': 'application/json'
                  }
              });

              const data = await response.json();
              console.log('Server response:', data);

              if (response.ok) {
                  console.log('File deletion successful on server');
                  
                  // Find and remove the file item from DOM
                  const fileItems = document.querySelectorAll('.file-item');
                  const fileItem = Array.from(fileItems).find(item => {
                      const removeIcon = item.querySelector('.remove-file');
                      return removeIcon && 
                            removeIcon.dataset.fileName === fileName && 
                            removeIcon.dataset.model === modelName && 
                            removeIcon.dataset.instance === instanceId;
                  });

                  console.log('File item to remove:', fileItem);
                  if (fileItem) {
                      fileItem.remove();
                      console.log('File item removed from DOM');
                  } else {
                      console.log('File item not found in DOM');
                  }

                  // Show success notification
                  alert("File deleted successfully");

                  // Dispatch event for other components
                  document.dispatchEvent(new CustomEvent('fileDeleted', { 
                      detail: { 
                          modelName, 
                          instanceId, 
                          fileName,
                          fileIndex 
                      } 
                  }));
                  console.log('Custom event dispatched');

                  // Optional: Refresh the file list or specific section
                  // location.reload();
                  
              } else {
                  console.error("Error deleting file:", data.message);
                  alert("Error deleting file. Please try again.");
              }
          } catch (error) {
              console.error('Error:', error);
              alert("An error occurred while deleting the file. Please try again.");
          }
      }
  }



  function getActiveDataTables() {
    const activeTables = [];
    const tables = ['insurance', 'registration', 'gps', 'permits', 'fuel', 'roadtoll', 'driver', 'allocation'];

    tables.forEach(table => {
      if (document.querySelector(`#${table}Table tbody tr`)) {
        activeTables.push(table);
      }
    });

    return activeTables;
  }

  function validateGpsTable() {
    const gpsRows = document.querySelectorAll('#gpsTable tbody tr');
    let isValid = true;

    gpsRows.forEach((row) => {
      const fields = ['GPS_DEVICE_NO', 'GPS_INSTALLATION_DATE', 'GPS_SERVICE_PROVIDER'];
      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (!input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else {
          input.classList.remove('is-invalid');
        }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Gps Info.'
    };
  }


  function validateRegistrationField(input) {
    if (!input.value.trim()) {
      input.classList.add('is-invalid');
      if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('invalid-feedback')) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'invalid-feedback';
        errorMessage.textContent = `${input.name} is required`;
        input.parentNode.insertBefore(errorMessage, input.nextSibling);
      }
      return false;
    } else {
      input.classList.remove('is-invalid');
      if (input.nextElementSibling && input.nextElementSibling.classList.contains('invalid-feedback')) {
        input.nextElementSibling.remove();
      }
      return true;
    }
  }


  function validatePermitsTable() {
    const permitsRows = document.querySelectorAll('#permitsTable tbody tr');
    let isValid = true;

    permitsRows.forEach((row) => {
      const fields = [
        'PERMIT_LOOKUP_NAME',
        'AE_EMIRATES_LOOKUP_NAME',
        'ISSUING AUTHORITY_LOOKUP_NAME',
        'PERMIT_NO',
        'PERMIT_DATE',
        'PERMIT_EXPIRY_DATE',
        'CURRENT STATUS_LOOKUP_NAME'
      ];
      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (input && !input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else if (input) {
            input.classList.remove('is-invalid');
          }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Permit Info.'
    };
  }

  function validateFuelTable() {
    const fuelRows = document.querySelectorAll('#fuelTable tbody tr');
    let isValid = true;

    fuelRows.forEach((row) => {
      const fields = [
        'FUEL TYPE_LOOKUP_NAME',
        'MONTHLY_FUEL_LIMIT',
        'FUEL SERVICE TYPE_LOOKUP_NAME',
        'FUEL SERVICE PROVIDER_LOOKUP_NAME',
        'FUEL_DOCUMENT_NO',
        'FUEL_DOCUMENT_DATE',
        'FUEL_DOC_EXPIRY_DATE',
        'CURRENT STATUS_LOOKUP_NAME'
      ];

      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (input && !input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else if (input) {
          input.classList.remove('is-invalid');
        }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Fuel Info.'
    };
  }

  function validateRoadtollTable() {
    const roadtollRows = document.querySelectorAll('#roadtollTable tbody tr');
    let isValid = true;

    roadtollRows.forEach((row) => {
      const fields = ['EMIRATES', 'TOLL_TYPE', 'ACCOUNT_NO', 'TAG_NO', 'ACTIVATION_DATE','ACTIVATION_END_DATE', 'CURRENT_STATUS'];
      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (input && !input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else if (input) {
          input.classList.remove('is-invalid');
        }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Road-Toll Info.'
    };
  }

  function validateDriverTable() {
    const driverRows = document.querySelectorAll('#driverTable tbody tr');
    let isValid = true;

    driverRows.forEach((row) => {
      const fields = ['EMPLOYEE_NO', 'EMPLOYEE_NAME', 'DESIGNATION', 'CONTACT_NUMBER', 'ASSIGNMENT_DATE' ,'TRAFFIC_CODE_NO', 'DRIVING_LICENSE_NO', 'LICENSE_TYPE', 'PLACE_OF_ISSUE', 'LICENSE_EXPIRY_DATE', 'GPS_TAG_NO', 'GPS_TAG_ASSIGN_DATE'];
      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (!input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else {
          input.classList.remove('is-invalid');
        }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Driver Table.'
    };
  }

  function validateAllocationTable() {
    const allocationRows = document.querySelectorAll('#allocationTable tbody tr');
    let isValid = true;

    allocationRows.forEach((row) => {
      const fields = [
        'COMPANY NAME_LOOKUP_NAME',
        'DIVISIONS_LOOKUP_NAME',
        'OPERATING_LOCATION_ALLOCATION_LOOKUP_NAME',
        'AE_EMIRATES_LOOKUP_NAME',
       
        'ALLOCATION_DATE',
        'ALLOCATION_END_DATE'
      ];

      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
        if (input && !input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
        } else if (input) {
          input.classList.remove('is-invalid');
        }
      });
    });

    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Allocation Info.'
    };
  }

  function validateInsuranceTable() {
    const insuranceRows = document.querySelectorAll('#insuranceTable tbody tr');
    let isValid = true;
    insuranceRows.forEach((row) => {
      const fields = [
        'INSURANCE_COMPANY',
        'POLICY_NO',
        'POLICY_DATE',
        'POLICY_EXPIRY_DATE',
      ];

      fields.forEach(field => {
        const input = row.querySelector(`[name="${field}"]`);
  if (input && !input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
  } else if (input) {
            input.classList.remove('is-invalid');
          }
      });
    });
    return {
      isValid,
      errorMessage: isValid ? '' : 'Please fill in all required fields in the Insurance Info.'
    };
  }

  function validateRegistrationTable() {
          const registrationRows = document.querySelectorAll('#registrationTable tbody tr');
          let isValid = true;

          registrationRows.forEach((row) => {
            const fields = [
              'EMIRATES_TRF_FILE_NO',
              'REGISTERED_EMIRATES',
              'FEDERAL_TRF_FILE_NO',
              'REG_COMPANY_NAME',
              'TRADE_LICENSE_NO',
            ];

            fields.forEach(field => {
              const input = row.querySelector(`[name="${field}"]`);
              if (input && !input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
              } else if (input) {
                input.classList.remove('is-invalid');
              }
            });
          });

          return {
            isValid,
            errorMessage: isValid ? '' : 'Please fill in all required fields in the Registration Info.'
          };
  }