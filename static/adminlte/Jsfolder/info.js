function setupInsuranceFleetSearchFunctionality(row) {
    // Create overlay and container if they don't exist
    if (!document.querySelector('.insurance-search-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'insurance-search-overlay';
        document.body.appendChild(overlay);
    }

    if (!document.querySelector('.insurance-search-container')) {
        const container = document.createElement('div');
        container.className = 'insurance-search-container';
        container.innerHTML = `
            <div class="insurance-search-header">
                <h3>Select Insurance Company</h3>
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
        `;
        document.body.appendChild(container);
    }

    const insuranceFleetCompanyInput = row.querySelector('[name="INSURANCE_COMPANY"]');
    const policyNoInput = row.querySelector('[name="POLICY_NO"]');
    const policyDateInput = row.querySelector('[name="POLICY_DATE"]');
    const policyExpiryDateInput = row.querySelector('[name="POLICY_EXPIRY_DATE"]');

    const overlay = document.querySelector('.insurance-search-overlay');
    const container = document.querySelector('.insurance-search-container');
    const closeIcon = container.querySelector('.insurance-close-icon');
    const resultsTable = container.querySelector('.insurance-search-results tbody');

    // Add loading state
    let isLoading = false;

    insuranceFleetCompanyInput.addEventListener('click', async () => {
        if (isLoading) return;
        
        try {
            isLoading = true;
            insuranceFleetCompanyInput.style.cursor = 'wait';
            
            const response = await fetch('http://127.0.0.1:8000/api/insurance-info');
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();

            resultsTable.innerHTML = '';
            data.forEach(info => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${info.INSURANCE_COMPANY || ''}</td>
                    <td>${info.POLICY_NO || ''}</td>
                    <td>${info.POLICY_DATE || ''}</td>
                    <td>${info.POLICY_EXPIRY_DATE || ''}</td>
                `;
                
                row.addEventListener('click', () => {
                  insuranceFleetCompanyInput.value = info.INSURANCE_COMPANY || '';
                    policyNoInput.value = info.POLICY_NO || '';
                    policyDateInput.value = info.POLICY_DATE || '';
                    policyExpiryDateInput.value = info.POLICY_EXPIRY_DATE || '';
                    
                    // Make fields readonly
                    policyNoInput.readOnly = true;
                    policyDateInput.readOnly = true;
                    policyExpiryDateInput.readOnly = true;
                    
                    hidePopup();
                });
                
                resultsTable.appendChild(row);
            });

            showPopup();
        } catch (error) {
            console.error('Error fetching insurance info:', error);
            alert('Failed to load insurance companies. Please try again.');
        } finally {
            isLoading = false;
            insuranceFleetCompanyInput.style.cursor = 'pointer';
        }
    });

    function showPopup() {
        overlay.style.display = 'block';
        container.style.display = 'block';
        setTimeout(() => container.style.opacity = '1', 0);
    }

    function hidePopup() {
        container.style.opacity = '0';
        overlay.style.display = 'none';
        container.style.display = 'none';
    }

    // Close popup handlers
    closeIcon.addEventListener('click', hidePopup);
    overlay.addEventListener('click', hidePopup);

    // Prevent popup close when clicking inside container
    container.addEventListener('click', (e) => e.stopPropagation());

    // Keyboard accessibility
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && container.style.display === 'block') {
            hidePopup();
        }
    });

    // Add visual feedback for input
    insuranceFleetCompanyInput.addEventListener('mouseover', () => {
        if (!isLoading) {
          insuranceFleetCompanyInput.style.backgroundColor = '#f8f9fa';
        }
    });

    insuranceFleetCompanyInput.addEventListener('mouseout', () => {
        insuranceFleetCompanyInput.style.backgroundColor = '#ffff76';
    });
}


function setupDriverSearchFunctionality(row) {
  if (!document.querySelector('.driver-search-overlay')) {
      const overlay = document.createElement('div');
      overlay.className = 'driver-search-overlay';
      document.body.appendChild(overlay);
  }

  if (!document.querySelector('.driver-search-container')) {
      const container = document.createElement('div');
      container.className = 'driver-search-container';
      container.innerHTML = `
          <div class="driver-search-header">
              <h3>Select Driver Information</h3>
              <span class="driver-close-icon">&times;</span>
          </div>
          <table class="driver-search-results">
              <thead>
                  <tr>
                      <th>Employee No</th>
                      <th>Employee Name</th>
                      <th>Designation</th>
                      <th>Contact Number</th>
                  </tr>
              </thead>
              <tbody></tbody>
          </table>
      `;
      document.body.appendChild(container);
  }

  const employeeNoInput = row.querySelector('[name="EMPLOYEE_NO"]');
  const employeeNameInput = row.querySelector('[name="EMPLOYEE_NAME"]');
  const designationInput = row.querySelector('[name="DESIGNATION"]');
  const contactNumberInput = row.querySelector('[name="CONTACT_NUMBER"]');

  const overlay = document.querySelector('.driver-search-overlay');
  const container = document.querySelector('.driver-search-container');
  const closeIcon = container.querySelector('.driver-close-icon');
  const resultsTable = container.querySelector('.driver-search-results tbody');

  let isLoading = false;

  employeeNoInput.addEventListener('click', async () => {
      if (isLoading) return;
      
      try {
          isLoading = true;
          employeeNoInput.style.cursor = 'wait';
          
          const response = await fetch('http://127.0.0.1:8000/api/driver-info');
          if (!response.ok) throw new Error('Network response was not ok');
          
          const data = await response.json();

          resultsTable.innerHTML = '';
          data.forEach(info => {
              const row = document.createElement('tr');
              row.innerHTML = `
                  <td>${info.EMPLOYEE_NO || ''}</td>
                  <td>${info.EMPLOYEE_NAME || ''}</td>
                  <td>${info.DESIGNATION || ''}</td>
                  <td>${info.CONTACT_NUMBER || ''}</td>
              `;
              
              row.addEventListener('click', () => {
                  employeeNoInput.value = info.EMPLOYEE_NO || '';
                  employeeNameInput.value = info.EMPLOYEE_NAME || '';
                  designationInput.value = info.DESIGNATION || '';
                  contactNumberInput.value = info.CONTACT_NUMBER || '';
                  
                  // Make fields readonly
                  employeeNameInput.readOnly = true;
                  designationInput.readOnly = true;
                  contactNumberInput.readOnly = true;
                  
                  hidePopup();
              });
              
              resultsTable.appendChild(row);
          });

          showPopup();
      } catch (error) {
          console.error('Error fetching driver info:', error);
          alert('Failed to load driver information. Please try again.');
      } finally {
          isLoading = false;
          employeeNoInput.style.cursor = 'pointer';
      }
  });

  function showPopup() {
      overlay.style.display = 'block';
      container.style.display = 'block';
      setTimeout(() => container.style.opacity = '1', 0);
  }

  function hidePopup() {
      container.style.opacity = '0';
      overlay.style.display = 'none';
      container.style.display = 'none';
  }

  closeIcon.addEventListener('click', hidePopup);
  overlay.addEventListener('click', hidePopup);
  container.addEventListener('click', (e) => e.stopPropagation());

  document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && container.style.display === 'block') {
          hidePopup();
      }
  });

  employeeNoInput.addEventListener('mouseover', () => {
      if (!isLoading) {
          employeeNoInput.style.backgroundColor = '#f8f9fa';
      }
  });

  employeeNoInput.addEventListener('mouseout', () => {
      employeeNoInput.style.backgroundColor = '#ffff76';
  });
}



function setupRegistrationSearchFunctionality(row) { if (!document.querySelector('.registration-search-overlay')) { const overlay = document.createElement('div'); overlay.className = 'registration-search-overlay'; document.body.appendChild(overlay); }


  if (!document.querySelector('.registration-search-container')) {
    const container = document.createElement('div');
    container.className = 'registration-search-container';
    container.innerHTML = `
        <div class="registration-search-header">
            <h3>Select Traffic File Information</h3>
            <span class="registration-close-icon">&times;</span>
        </div>
        <table class="registration-search-results">
            <thead>
                <tr>
                    <th>Traffic File No</th>
                    <th>Company Name</th>
                    <th>Trade License No</th>
                    <th>Emirates</th>
                    <th>Federal Traffic File No</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `;
    document.body.appendChild(container);
}

      const emiratesFileInput = row.querySelector('[name="EMIRATES_TRF_FILE_NO"]');
      const registeredEmiratesInput = row.querySelector('[name="REGISTERED_EMIRATES"]');
      const federalFileInput = row.querySelector('[name="FEDERAL_TRF_FILE_NO"]');
      const companyNameInput = row.querySelector('[name="REG_COMPANY_NAME"]');
      const tradeLicenseInput = row.querySelector('[name="TRADE_LICENSE_NO"]');

      const overlay = document.querySelector('.registration-search-overlay');
      const container = document.querySelector('.registration-search-container');
      const closeIcon = container.querySelector('.registration-close-icon');
      const resultsTable = container.querySelector('.registration-search-results tbody');

      let isLoading = false;

      emiratesFileInput.addEventListener('click', async () => {
          if (isLoading) return;
          
          try {
              isLoading = true;
              emiratesFileInput.style.cursor = 'wait';
              
              const response = await fetch('http://127.0.0.1:8000/api/traffic-file-info');
              if (!response.ok) throw new Error('Network response was not ok');
              
              const data = await response.json();

              resultsTable.innerHTML = '';
              data.forEach(info => {
                  const row = document.createElement('tr');
                  row.innerHTML = `
                      <td>${info.TRAFFIC_FILE_NO || ''}</td>
                      <td>${info.COMPANY_NAME || ''}</td>
                      <td>${info.TRADE_LICENSE_NO || ''}</td>
                      <td>${info.EMIRATES || ''}</td>
                      <td>${info.FEDERAL_TRAFFIC_FILE_NO || ''}</td>
                  `;
                  
                  row.addEventListener('click', () => {
                      emiratesFileInput.value = info.TRAFFIC_FILE_NO || '';
                      registeredEmiratesInput.value = info.EMIRATES || '';
                      federalFileInput.value = info.FEDERAL_TRAFFIC_FILE_NO || '';
                      companyNameInput.value = info.COMPANY_NAME || '';
                      tradeLicenseInput.value = info.TRADE_LICENSE_NO || '';
                      
                      // Make fields readonly
                      registeredEmiratesInput.readOnly = true;
                      federalFileInput.readOnly = true;
                      companyNameInput.readOnly = true;
                      tradeLicenseInput.readOnly = true;
                      
                      hidePopup();
                  });
                  
                  resultsTable.appendChild(row);
              });

              showPopup();
          } catch (error) {
              console.error('Error fetching traffic file info:', error);
              alert('Failed to load traffic file information. Please try again.');
          } finally {
              isLoading = false;
              emiratesFileInput.style.cursor = 'pointer';
          }
      });

      function showPopup() {
          overlay.style.display = 'block';
          container.style.display = 'block';
          setTimeout(() => container.style.opacity = '1', 0);
      }

      function hidePopup() {
          container.style.opacity = '0';
          overlay.style.display = 'none';
          container.style.display = 'none';
      }

      closeIcon.addEventListener('click', hidePopup);
      overlay.addEventListener('click', hidePopup);
      container.addEventListener('click', (e) => e.stopPropagation());

      document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && container.style.display === 'block') {
              hidePopup();
          }
      });

      emiratesFileInput.addEventListener('mouseover', () => {
          if (!isLoading) {
              emiratesFileInput.style.backgroundColor = '#f8f9fa';
          }
      });

      emiratesFileInput.addEventListener('mouseout', () => {
          emiratesFileInput.style.backgroundColor = '#ffff76';
      });
    }
