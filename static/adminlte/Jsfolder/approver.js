function showLoadingIndicator() {
  const loadingOverlay = document.createElement('div');
  loadingOverlay.id = 'loadingOverlay';
  loadingOverlay.style.position = 'fixed';
  loadingOverlay.style.top = '0';
  loadingOverlay.style.left = '0';
  loadingOverlay.style.width = '100%';
  loadingOverlay.style.height = '100%';
  loadingOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  loadingOverlay.style.display = 'flex';
  loadingOverlay.style.justifyContent = 'center';
  loadingOverlay.style.alignItems = 'center';
  loadingOverlay.style.zIndex = '9999';

  const spinner = document.createElement('div');
  spinner.className = 'spinner';
  spinner.style.width = '50px';
  spinner.style.height = '50px';
  spinner.style.border = '3px solid #f3f3f3';
  spinner.style.borderTop = '3px solid #3498db';
  spinner.style.borderRadius = '50%';
  spinner.style.animation = 'spin 1s linear infinite';

  loadingOverlay.appendChild(spinner);
  document.body.appendChild(loadingOverlay);
}

function hideLoadingIndicator() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
      loadingOverlay.remove();
  }
}

// Add this CSS to your stylesheet or in a <style> tag in your HTML
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
  }
`;
document.addEventListener('DOMContentLoaded', function() {
const fleetCreationDateInput = document.getElementById('fleetCreationDate');

// Set today's date as the default value
const today = new Date().toISOString().split('T')[0];
fleetCreationDateInput.value = today;

// Update the date value before form submission
document.getElementById('vehicleForm').addEventListener('submit', function(event) {
    const currentDate = new Date().toISOString().split('T')[0];
    fleetCreationDateInput.value = currentDate;
});

// Also update date when clicking submit button
document.getElementById('submitForm').addEventListener('click', function() {
    const currentDate = new Date().toISOString().split('T')[0];
    fleetCreationDateInput.value = currentDate;
});
});


    document.addEventListener('DOMContentLoaded', function() {
      const urlParams = new URLSearchParams(window.location.search);
      const fleetNumber = urlParams.get('fleet_number');
      const fromApprover = urlParams.get('from_approver');

      if (fleetNumber && fromApprover === 'true') {
        populateFormFields(fleetNumber,true);
      }
    });
    window.addEventListener('unhandledrejection', function(event) {
      console.error('Unhandled promise rejection:', event.reason);
    });




    async function handleRevert() {
      console.log("handleRevert function called");

      const fleetControlNumber = document.querySelector('[name="HEADER_ID"]').value;
      console.log("Fleet Control Number:", fleetControlNumber);
      const comment = document.querySelector('textarea[name="COMMENTS"]').value.trim();
      
      // Comment validation
      if (!comment) {
        alert('Please add comments before reverting this request');
        return;
      }

      if (confirm("Are you sure you want to revert this request?")) {
        try {
          showLoadingIndicator();
          console.log("Sending revert request...");
          const response = await fetch(`http://127.0.0.1:8000/api/revert-data/${fleetControlNumber}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          const result = await response.json();

          if (!response.ok) {
            if (response.status === 400 && result.message === "No approved data found for this HEADER_ID") {
              throw new Error("There are no approved records to revert.");
            } else {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
          }

          console.log("Revert response:", result);
          
          // Send email notification after successful revert
          try {
            await showComposeModal(
              fleetControlNumber,
              'Revert',  // Action type
              true,      // isApprover
              comment    // Comments
            );
            console.log("Email sent successfully for revert action");
          } catch (emailError) {
            console.error('Error sending revert notification email:', emailError);
            // Continue with the process even if email fails
          }

          alert(result.message);
          window.location.reload();
          console.log("Navigating to approver dashboard...");
          window.location.href = '/ALY_GTD/approver_dashboard/';
        } catch (error) {
          console.error('Error:', error);
          alert(`Failed to revert: ${error.message}`);
        } finally {
          hideLoadingIndicator();
        }
      } else {
        console.log("Revert cancelled by user");
      }
    }

    // Event listener for the revert button
    document.addEventListener('DOMContentLoaded', function() {
      const revertBtn = document.getElementById('revertBtn');
      if (revertBtn) {
        console.log("Attaching event listener to revert button");
        revertBtn.addEventListener('click', function(event) {
          console.log("Revert button clicked");
          handleRevert();
        });
      } else {
        console.error("Revert button not found in DOM");
      }
    });


    function clearCachedData() {
      localStorage.removeItem('currentFleetControlNumber');
      localStorage.removeItem('currentFleetStatus');
    }

    //approver handlings
    document.addEventListener("DOMContentLoaded", function () {
      setupDropdowns();
      hideCancelButton();
    });

    function afterPopulateForm() {
      disableAllFields();
      showEditButton();
      updateEditButtonState(document.querySelector('[name="STATUS"]').value);
      const status = document.querySelector('[name="STATUS"]').value;
      if (status && status.toLowerCase() !== 'draft') {
        document.querySelector('#cancelForm').style.display = 'block';
      } else {
          hideCancelButton();
        }
    }

    
    document.addEventListener('DOMContentLoaded', function() {
      const urlParams = new URLSearchParams(window.location.search);
      const fromApprover = urlParams.get('from_approver') === 'true';
      const isApprover = JSON.parse(document.getElementById('user_roles').textContent).is_approver;
      const fleetControlNumber = document.querySelector('[name="FLEET_CONTROL_NO"]').value;
      sessionStorage.setItem('originPage', fromApprover ? 'approver' : 'non-approver');
      if (fromApprover) {
        console.log("This is an Approver Page");
      } else {
        console.log("This is a Non-Approver Page");
      }
      if (fromApprover) {
          makeFieldsReadOnly(true);
          hideRegularButtons();
          if (isApprover) {
              showApproverButtons();
              document.getElementById('rectificationBtn').addEventListener('click', function() {
                const comment = document.querySelector('textarea[name="COMMENTS"]').value.trim();
                
                if (!comment) {
                  alert('Please add comments before returning for rectification');
                  return;
              }
                
                showLoadingIndicator();
                confirmAndSubmit('Return for Correction', true, comment);
            });

            document.getElementById('approveBtn').addEventListener('click', function() {
              const comment = document.querySelector('textarea[name="COMMENTS"]').value;
              showLoadingIndicator();
              confirmAndSubmit('Approved', true, comment);
            });

           
            document.getElementById('defleetBtn').addEventListener('click', function() {
              const comment = document.querySelector('textarea[name="COMMENTS"]').value;
              showLoadingIndicator();
              confirmAndSubmit('Defleet', true, comment);
            });


            
          }else {
          // Hide submit button for non-approvers
          document.getElementById('submitForm').style.display = 'none';
      }
          document.getElementById('submitForm').disabled = true;
      } else {
          makeFieldsReadOnly(false);
          document.getElementById('submitForm').addEventListener('click', function() {
              showComposeModal(fleetControlNumber);
          });
      }
    });
    

    function hideRegularButtons() {
      document.getElementById('newForm').style.display = 'none';
      document.getElementById('addRow').style.display = 'none';
      document.getElementById('removeRow').style.display = 'none';
    }

    // let approverButtonsAdded = false;
    function showApproverButtons() {
      // if (approverButtonsAdded) return;
      const approverButtons = `
          <div class="approver-buttons">
          <div class="container-button">
            <div class="container-btn">
              <button class="btn nav-btn approve" id="rectificationBtn">
                  <box-icon name='file-blank' color="blue" class="approver-icon"></box-icon>
                  <span style="font-size: 15px; color: black; margin-left: 5px;">Return for Correction</span>
              </button>
              <button class="btn nav-btn approve" id="approveBtn">
                  <box-icon name='check-circle' color="green" class="approver-icon"></box-icon>
                  <span style="font-size: 15px; color: black; margin-left: 5px;">Approved</span>
              </button>
            
             
              <button class="btn nav-btn approve" id="revertBtn">
                <box-icon name='undo' color="red" class="approver-icon"></box-icon>
                <span style="font-size: 15px; color: black; margin-left: 5px;">Revert</span>
              </button>
              </div>
              <div>
           

               <button class="btn nav-btn approve" id="defleetBtn">
                   <box-icon name="x-circle" color="red" class="del-icon"></box-icon>
                  <span style="font-size: 15px; color: black; margin-left: 5px;">Defleet</span>
              </button>
              </div>
          </div>
           </div>
      `;
      document.getElementById('submitForm').style.display = 'none'; // Hide the submit button
      document.getElementById('submitForm').insertAdjacentHTML('afterend', approverButtons);
      const revertBtn = document.getElementById('revertBtn');
      if (revertBtn) {
        console.log("Attaching event listener to revert button");
        revertBtn.addEventListener('click', function onRevertClick(event) {
          console.log("Revert button clicked");
          handleRevert();
        });
      } else {
        console.error("Revert button not found after adding to DOM");
      }
      // approverButtonsAdded = true; 
    }

    let formSubmitted = false;

    document.addEventListener('DOMContentLoaded', function() {
      const rectificationBtn = document.getElementById('rectificationBtn');
      const approveBtn = document.getElementById('approveBtn');
      const defleetBtn = document.getElementById('defleetBtn');
      const statusField = document.querySelector('input[name="STATUS"]');
     

      async function fetchEmailAddresses(lookupValue) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/related-data/?lookup_value=${lookupValue}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            const toEmail = data.find(item => item.LOOKUP_CODE === 'TO' && item.ACTIVE === 'Y')?.MEANING;
            const ccEmail = data.find(item => item.LOOKUP_CODE === 'CC' && item.ACTIVE === 'Y')?.MEANING;
            
            return { toEmail, ccEmail };
        } catch (error) {
            console.error(`Error fetching email addresses for ${lookupValue}:`, error);
            return null;
        }
      }
    
     
      // Function to show loading popup and handle email sending result
      function showEmailSendingPopup(emailSendingPromise) {
        // Create and show loading popup
        const popup = document.createElement('div');
        popup.className = 'email-sending-popup';
        popup.innerHTML = `
            <div class="email-sending-content">
                <div class="loading-spinner"></div>
                <p>Sending email...</p>
            </div>
        `;
        document.body.appendChild(popup);

        // Handle the email sending promise
        emailSendingPromise
            .then(result => {
                updatePopupContent(popup, 'success', 'Email sent successfully!');
            })
            .catch(error => {
                updatePopupContent(popup, 'error', 'Failed to send email. Please try again.');
                console.error('Email sending error:', error);
            })
            .finally(() => {
                // Remove popup after 3 seconds
                setTimeout(() => {
                    document.body.removeChild(popup);
                }, 3000);
            });
      }


      function updatePopupContent(popup, status, message) {
        const content = popup.querySelector('.email-sending-content');
        content.innerHTML = `
            <div class="${status}-icon"></div>
            <p>${message}</p>
        `;
      }

    

      document.getElementById('vehicleForm').addEventListener('submit', function(event) {
        if (formSubmitted) {
            event.preventDefault();
            alert('Submit successful');
            formSubmitted = false;
        }
      });
    });


    function makeFieldsReadOnly(isReadOnly) {
        const inputs = document.querySelectorAll('input:not([name="COMMENTS"]), select');
        inputs.forEach(input => {
            input.readOnly = isReadOnly;
            if (input.tagName === 'SELECT') {
                input.style.pointerEvents = isReadOnly ? 'none' : 'auto';
            }
        });
    }

    function enableCommentsAndButtons() {
        const allInputs = document.querySelectorAll('input, select, textarea');
        allInputs.forEach(input => {
            input.disabled = false;
            if (input.name !== "COMMENTS") {
                input.readOnly = true;
            }
        });

        const commentsField = document.querySelector('textarea[name="COMMENTS"]');
        if (commentsField) {
            commentsField.readOnly = false;
            commentsField.disabled = false;
        }

      // Enable file inputs and their associated elements
      const fileInputs = document.querySelectorAll('input[type="file"]');
      fileInputs.forEach(fileInput => {
          fileInput.disabled = false;
          fileInput.readOnly = false;

          // Enable the file list container if it exists
          const fileListContainer = fileInput.nextElementSibling;
          if (fileListContainer && fileListContainer.classList.contains('file-list')) {
              fileListContainer.style.pointerEvents = 'auto';
              fileListContainer.style.opacity = '1';
          }

          // Enable the remove file icons if they exist
          const removeIcons = fileInput.closest('td').querySelectorAll('.remove-file');
          removeIcons.forEach(icon => {
              icon.style.pointerEvents = 'auto';
              icon.style.opacity = '1';
          });
      });

      
        const submitButton = document.querySelector('button#submitForm');
        if (submitButton) {
            submitButton.disabled = false;
        }

        const approverButtons = document.querySelectorAll('.approver-buttons button');
        approverButtons.forEach(button => {
            button.disabled = false;
        });

        isEditMode = true;
    }

   
    function updateSaveButtonVisibility(status) {
      const saveButton = document.getElementById('saveform');
      if (saveButton) {
        saveButton.style.display = status === 'Draft' ? 'block' : 'none';
      }
    }
    const tablesToDisable = ['insuranceTable', 'registrationTable', 'gpsTable', 'permitsTable', 'fuelTable', 'roadtollTable', 'driverTable', 'allocationTable'];

   

        //edit button handlings

        let isEditMode = false;

        function disableAllFields() {
          updateEditButtonState(document.querySelector('[name="STATUS"]').value);
          const inputs = document.querySelectorAll('input, select, textarea');
          inputs.forEach(input => {
            input.disabled = true;
          });
          const commentsField = document.querySelector('textarea[name="COMMENTS"]');
          if (commentsField) {
              commentsField.disabled = false;
          }

          const permitColorInputs = document.querySelectorAll('.permit-colour-cell input[name="PermitColor"]');
          permitColorInputs.forEach(input => {
            input.disabled = true;
          });


          const buttons = document.querySelectorAll('button');
          buttons.forEach(button => {
            if (button.id !== 'editButton' && button.id !== 'newForm') {
              button.disabled = true;
            }
          });

          const removeIcons = document.querySelectorAll('.remove-file');
          removeIcons.forEach(icon => {
            icon.style.pointerEvents = 'none';
            icon.style.opacity = '0.5';
          });

          isEditMode = false;
        }

        function disableEditingControls() {
          document.getElementById('addRow').disabled = true;
          document.getElementById('removeRow').disabled = true;
          document.getElementById('submitForm').disabled = true;
        }

        function enableEditingControls() {
          document.getElementById('addRow').disabled = false;
          document.getElementById('removeRow').disabled = false;
          document.getElementById('submitForm').disabled = false;
        }

        function showEditButton() {
          document.getElementById('editButton').style.display = 'block';
        }

        function hideEditButton() {
          document.getElementById('editButton').style.display = 'none';
        }


        function disableEditingControls() {
          document.getElementById('addRow').disabled = true;
          document.getElementById('removeRow').disabled = true;
          document.getElementById('submitForm').disabled = true;
        }

        function enableEditingControls() {
          document.getElementById('addRow').disabled = false;
          document.getElementById('removeRow').disabled = false;
          document.getElementById('submitForm').disabled = false;
        }

        function showEditButton() {
          document.getElementById('editButton').style.display = 'block';
        }

        function hideEditButton() {
          document.getElementById('editButton').style.display = 'none';
        }

        let isPopulatedData = false;

        function enableAllFields() {
          const inputs = document.querySelectorAll('input, select, textarea');
          inputs.forEach(input => {
            input.disabled = false;
          });

          const buttons = document.querySelectorAll('button');
          buttons.forEach(button => {
            button.disabled = false;
          });

          const removeIcons = document.querySelectorAll('.remove-file');
          removeIcons.forEach(icon => {
            icon.style.pointerEvents = 'auto';
            icon.style.opacity = '1';
          });

          isEditMode = true;
        }
        function disableSpecificFields() {
          const fieldsToDisable = ['FLEET_CONTROL_NO', 'FLEET_CREATION_DATE', 'STATUS'];
          fieldsToDisable.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
              field.disabled = true;
              field.readOnly = true;
              
              if (fieldName === 'FLEET_CREATION_DATE') {
                field.style.pointerEvents = 'none';
                field.style.backgroundColor = '#e9ecef'; // Light gray background to indicate it's disabled
                
                // Remove the calendar icon if it's added via CSS
                field.style.backgroundImage = 'none';
                
                // If there's a separate calendar button, disable it
                const calendarButton = field.nextElementSibling;
                if (calendarButton && calendarButton.tagName === 'BUTTON') {
                  calendarButton.disabled = true;
                  calendarButton.style.display = 'none';
                }
              }
              
              console.log(`Field ${fieldName} disabled successfully`);
            } else {
              console.log(`Field ${fieldName} not found`);
            }
          });
        }
        const editButton = document.getElementById('editButton');
        if (editButton) {
          editButton.addEventListener('click', function() {

            const fromApprover = new URLSearchParams(window.location.search).get('from_approver') === 'true';
            if (fromApprover) {
                enableCommentsAndButtons();
            } else {
                enableAllFields();
              disableSpecificFields();
            }
            enableEditingControls();
            this.style.display = 'none';
          });
        }

      


        function navigateToAllActionHistory() {
          var fleetNumberElement = document.querySelector('[name="FLEET_CONTROL_NO"]');
          var headerIdElement = document.querySelector('#HEADER_ID');
          var fleetControlNo = document.querySelector('[name="FLEET_CONTROL_NO"]');
          
          var fleetNumber = fleetNumberElement ? fleetNumberElement.value : '';
          var headerId = headerIdElement ? headerIdElement.value : '';
          var controlNo = fleetControlNo ? fleetControlNo.value : '';
      
          // Check if fleet control number exists
          if (!controlNo || controlNo.trim() === '') {
              alert('Please ensure Fleet Control Number is generated before viewing action history.');
              return;
          }
      
          // Store the state and navigate
          sessionStorage.setItem('fleetMasterState', JSON.stringify({
              fleetNumber: controlNo,
              headerId: headerId
          }));
          
          var originPage = sessionStorage.getItem('originPage');
          
          var url = "{% url 'action_history' %}";
          window.location.href = url;
      }

        function navigateToAllAttachments() {
          var fleetNumberElement = document.querySelector('[name="FLEET_CONTROL_NO"]');
          var headerIdElement = document.querySelector('#HEADER_ID');
          var fleetNumber = fleetNumberElement ? fleetNumberElement.value : '';
          var headerId = headerIdElement ? headerIdElement.value : '';

          // Store both values in sessionStorage
          sessionStorage.setItem('fleetMasterState', JSON.stringify({
              fleetNumber: fleetNumber,
              headerId: headerId
          }));
          var originPage = sessionStorage.getItem('originPage');


          var url = "{% url 'all_attachment' %}";
          //url += "?fleet_number=" + encodeURIComponent(fleetNumber) + "&header_id=" + encodeURIComponent(headerId);
          url += "?fleet_number=" + encodeURIComponent(fleetNumber) + "&HEADER_ID=" + encodeURIComponent(headerId) + "&from_approver=" + (originPage === 'approver');

          window.location.href = url;
        }

        // Add this function to restore the state when the page loads
        function restoreFleetMasterState() {
          var storedState = sessionStorage.getItem('fleetMasterState');
          if (storedState) {
            var state = JSON.parse(storedState);
            if (state.headerId) {
              document.querySelector('#HEADER_ID').value = state.headerId;
              populateFormFields(state.headerId, false);
            } else if (state.fleetNumber) {
              document.querySelector('[name="FLEET_CONTROL_NO"]').value = state.fleetNumber;
              populateFormFields(state.fleetNumber, true);
            }
            sessionStorage.removeItem('fleetMasterState');
          }
        }


        function setupDropdowns() {
          document.querySelectorAll("select").forEach((dropdown) => {
              const lookupName = dropdown.getAttribute("name").replace('_LOOKUP_NAME', '').trim();
              if (lookupName) {
                  dropdown.addEventListener("click", () => fetchDropdownOptions(lookupName, dropdown));
              }
              dropdown.addEventListener("change", function () {
                  this.setAttribute("data-selected", this.value);
              });
          });
        }

        async function fetchDropdownOptions(lookupName, dropdown, selectedValue) {
            try {
                const response = await fetch(`/api/dropdown-options/?lookup_name=${lookupName}`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                populateDropdown(dropdown, data.meanings, selectedValue);
            } catch (error) {
                console.error("Error fetching dropdown options:", error);
            }
        }

        function populateDropdown(dropdown, options, selectedValue) {
            let existingOptions = Array.from(dropdown.options).map(option => option.value);

            options.forEach((option) => {
                if (!existingOptions.includes(option)) {
                    const opt = document.createElement("option");
                    opt.value = option;
                    opt.textContent = option;
                    dropdown.appendChild(opt);
                }
            });

            if (selectedValue) {
                dropdown.value = selectedValue;
            }
        }


        function setDropdownValue(dropdown, value) {
          if (!dropdown || !dropdown.options) {
              console.log(`Dropdown or options not available for value: ${value}`);
              return;
          }
      
          let options = Array.from(dropdown.options || []);
          let optionExists = options.some(option => option.value === value);
      
          if (!optionExists && value) {
              let newOption = new Option(value, value);
              dropdown.add(newOption);
          }
      
          if (value) {
              dropdown.value = value;
              dropdown.dispatchEvent(new Event('change'));
              console.log(`Set ${dropdown.name} to ${value}`);
          } else {
              console.log(`No value provided for ${dropdown.name}`);
          }
      }
      
          //tabs
          function initializeTabs() {
              document.querySelectorAll('.tab').forEach(tab => {
                  tab.addEventListener('click', () => {
                        document.querySelectorAll('.tab, .tab-content').forEach(el => el.classList.remove('active'));
                        tab.classList.add('active');
                        const contentId = tab.dataset.tab;
                        const content = document.getElementById(contentId);
                        if (content) {
                            content.classList.add('active');
                        } else {
                            console.error(`Tab content not found for id: ${contentId}`);
                        }
                    });
              });
          }
          function loadContent(page) {
            const contentDiv = document.querySelector('.height-100');
            fetch(page)
                .then(response => response.text())
                .then(html => {
                    contentDiv.innerHTML = html;
                    initializeTabs();
                })
                .catch(error => {
                    console.error('Error loading content:', error);
                    contentDiv.innerHTML = '<p>Error loading content.</p>';
                });
          }


          initializeTabs();
          clearForm();

            //search handlings
            const searchInput = document.getElementById('searchInput');
            const searchResultsContainer = document.querySelector('.search-results-container');
            const searchResults = document.querySelector('.search-results tbody');
            const closeIcon = document.querySelector('.close-icon');

            let fleetInfo = []; // Store the fetched data

            searchInput.addEventListener('focus', fetchAndPopulateSearchResults);
            searchInput.addEventListener('click', fetchAndPopulateSearchResults);
            searchInput.addEventListener('input', fetchAndPopulateSearchResults);
            searchInput.addEventListener('keydown', function(event) {
              if (event.key === 'Enter') {
                event.preventDefault();
                const firstResult = searchResults.querySelector('tr');
                if (firstResult) {
                  const selectedFleetNumber = firstResult.firstElementChild.textContent;
                  searchInput.value = selectedFleetNumber;
                  hideSearchResults();
                  populateFormFields(selectedFleetNumber);
                }
              }
            });


            async function fetchFleetInfo() {
              if (fleetInfo.length === 0) {
                const response = await fetch('http://127.0.0.1:8000/api/fleet-info');
                if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
                }
                fleetInfo = await response.json();
                console.log('Fetched fleet info:', fleetInfo);
              }
              return fleetInfo;
            }

            function filterAndDisplayResults() {
              const searchTerm = searchInput.value.toLowerCase();
              const filteredInfo = fleetInfo.filter(info => {
                const searchableFields = [
                  info.HEADER_ID,
                  info.FLEET_CONTROL_NO,
                  info.VIN_NO,
                  info.MANUFACTURER,
                  info.MODEL,
                  info.ENGINE_NO,
                  info.STATUS,
                  info.REGISTRATION_NO
                ].map(field => (field || '').toLowerCase());

                return searchableFields.some(field => field.includes(searchTerm));
              });

              console.log('Filtered info:', filteredInfo);

              searchResults.innerHTML = '';
              filteredInfo.forEach((info) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                  <td>${info.HEADER_ID}</td>

                  <td>${info.FLEET_CONTROL_NO}</td>
                  <td>${info.VIN_NO}</td>
                  <td>${info.MANUFACTURER}</td>
                  <td>${info.MODEL}</td>
                  <td>${info.ENGINE_NO}</td>
                  <td>${info.STATUS}</td>
                  <td>${info.REGISTRATION_NO}</td>
                `;

                tr.addEventListener('click', function (e) {
                  e.stopPropagation();
                  searchInput.value = info.FLEET_CONTROL_NO;
                  hideSearchResults();
                  populateFormFields(info.FLEET_CONTROL_NO);
                });
                searchResults.appendChild(tr);

                tr.addEventListener('click', function (e) {
                  e.stopPropagation();
                  searchInput.value = info.HEADER_ID;
                  hideSearchResults();
                  populateFormFields(info.HEADER_ID, true);
                });
                searchResults.appendChild(tr);
              });

            }


            function hideCancelButton() {
              const cancelButton = document.querySelector('#cancelForm');
              if (cancelButton) {
                  cancelButton.style.display = 'none';
              }
            }




            async function fetchAndPopulateSearchResults(event) {
              event.stopPropagation();
              try {
                await fetchFleetInfo();
                filterAndDisplayResults();
                showSearchResults();
              } catch (error) {
                console.error('Error fetching fleet info:', error);
              }
            }

            function showSearchResults() {
              searchResultsContainer.style.display = 'block';
            }

            function hideSearchResults() {
              searchResultsContainer.style.display = 'none';
            }

            closeIcon.addEventListener('click', function(e) {
              e.stopPropagation();
              hideSearchResults();
            });

            document.addEventListener('click', function(event) {
              if (!event.target.closest('.search-container')) {
                hideSearchResults();
              }
            });

            searchResults.addEventListener("click", function (e) {
              if (e.target.tagName === "TD") {
                const selectedFleetNumber = e.target.parentElement.firstElementChild.textContent;
                searchInput.value = selectedFleetNumber;
                hideSearchResults();
                populateFormFields(selectedFleetNumber);
              }
            });

            searchResults.addEventListener("click", function (e) {
              if (e.target.tagName === "LI") {
                const selectedFleetNumber = e.target.textContent;
                searchInput.value = selectedFleetNumber;
                searchResults.style.display = "none";
                populateFormFields(selectedFleetNumber);
              }
            });


            // Assuming populateFormFields function is defined elsewhere
            function populateFormFields(headerId) {
              // Implementation of populating form fields
              console.log('Populating form fields for:', fleetControlNumber);
            }
            function updateSaveButtonVisibility(status) {
              const saveButton = document.getElementById('saveform');
              if (saveButton) {
                saveButton.style.display = status === 'Draft' ? 'block' : 'none';
              }
            }

            function disablePopulatedFields() {
              const inputs = document.querySelectorAll('input, select, textarea');
              inputs.forEach(input => {
                if (input.value !== '') {
                  input.disabled = true;
                }
              });

              // Disable populated rows in tables
              const tables = document.querySelectorAll('table');
              tables.forEach(table => {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                  const inputs = row.querySelectorAll('input, select, textarea');
                  let isPopulated = false;
                  inputs.forEach(input => {
                    if (input.value !== '') {
                      isPopulated = true;
                    }
                  });
                  if (isPopulated) {
                    inputs.forEach(input => {
                      input.disabled = true;
                    });
                  }
                });
              });
            }





      
            document.querySelector('#searchInput').addEventListener('change', function() {
                const fleetNumber = this.value;
                if (fleetNumber) {
                    populateFormFields(fleetNumber);
                    // The afterPopulateForm function will handle showing/hiding the cancel button
                } else {
                    clearForm();
                    hideCancelButton(); // Hide cancel button when clearing the form
                }
            });