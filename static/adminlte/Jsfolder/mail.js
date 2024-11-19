async function confirmAndSubmit(action, isApprover, comment) {
  if (confirm(`Are you sure you want to ${action} this request?`)) {
      try {
          const form = document.getElementById('vehicleForm');
          const formData = new FormData(form);
          formData.append('ACTION', action);
          formData.append('COMMENTS', comment);
          console.log('FormData being sent:', Object.fromEntries(formData));
          console.log('Status before submission:', formData.get('STATUS'));


          let newStatus;
          switch(action) {
              case 'Return for Correction':
                  newStatus = 'Return for Correction';
                  break;
              case 'Approved':
                  newStatus = 'Approved';
                  break;
              case 'Defleet':
                  newStatus = 'Defleet';
                  break;
             
              default:
                  newStatus = 'Pending for Approval';
          }

          // Update the status field in the form
          const statusField = document.querySelector('input[name="STATUS"]');
          if (statusField) {
              statusField.value = newStatus;
          }

          formData.set('STATUS', newStatus);
          console.log('Status after updating:', formData.get('STATUS'));



          // Ensure all fields are included and complex fields are valid JSON
          const allInputs = form.querySelectorAll('input, select, textarea');
          allInputs.forEach(input => {
              if (input.name) {
                  let value = input.value || '[]';
                  if (value === '[]' || value === 'null' || value === '') {
                      value = JSON.stringify([]);
                  }
                  formData.set(input.name, value);
              }
          });

          // Explicitly handle complex fields
          ['insurances','registration' ,'fuel','permits', 'gps', 'roadtoll', 'driver', 'allocation'].forEach(field => {
              let value = formData.get(field);
              if (!value || value === '[]' || value === 'null') {
                  value = JSON.stringify([]);
              } else if (typeof value === 'string' && !value.startsWith('[')) {
                  // If it's not already a JSON array, wrap it in one
                  value = JSON.stringify([JSON.parse(value)]);
              }
              formData.set(field, value);
          });

          console.log('FormData being sent:', Object.fromEntries(formData));

          const response = await fetch('http://127.0.0.1:8000/api/fleet-master', {
              method: 'POST',
              body: formData
          });

          if (!response.ok) {
              const errorText = await response.text();
              throw new Error(`Server error: ${response.status} ${response.statusText}\n${errorText}`);
          }

          const result = await response.json();
          console.log('Form submission result:', result);

                                        
          updateStatusDisplay(newStatus);
          if (result.message.includes('successfully')) {
            showLoadingIndicator();
            console.log('Before clearing approver comments:', document.querySelector('textarea[name="COMMENTS"]').value);
            const commentsField = document.querySelector('textarea[name="COMMENTS"]');
            if (commentsField) {
                commentsField.value = '';
                console.log('After clearing approver comments:', commentsField.value);
            }
           
            await sendApproverActionEmail(action, isApprover, comment, formData.get('FLEET_CONTROL_NO'));
            window.location.href = '/ALY_GTD/approver_dashboard/';
        } else {
            throw new Error('Form submission failed');
        }
      } catch (error) {
          console.error('Error:', error);
          alert(`Failed to process the request: ${error.message}`);
      } finally {
          hideLoadingIndicator();
      }
  }
}


async function sendApproverActionEmail(action, isApprover, comment, fleetControlNumber) {
  try {
      await showComposeModal(fleetControlNumber, action, isApprover, comment);
      console.log('Email sent successfully after form submission');
  } catch (error) {
      console.error('Error sending email:', error);
      alert('Form submission was successful, but there was an error sending the email.');
  }
}



async function sendEmailAutomatically(fleetControlNumber, fleetData, isNewSubmission) {
  console.log('Starting sendEmailAutomatically function');
  const response = await fetch(`http://127.0.0.1:8000/api/fleet-master/${fleetControlNumber}`);
  const completeFleetData = await response.json();
   console.log('Complete fleet Data:', JSON.stringify(completeFleetData, null, 2));
 
  const lookupValue = isNewSubmission ? 'NEW_FLEET_MASTER' : 'EDIT_FLEET_MASTER';
  console.log(`Using lookup value: ${lookupValue}`);
  const action = isNewSubmission ? 'New' : 'Modified';
  console.log(`Current Action: ${action}`);

  const emailAddresses = await fetchEmailAddresses(lookupValue);
  console.log('Fetched email addresses:', emailAddresses);

  if (!emailAddresses) {
    console.error('Failed to fetch email addresses');
    return;
  }

  const { toEmail, ccEmail } = emailAddresses;
  console.log(`To Email: ${toEmail}, CC Email: ${ccEmail}`);

  if (!toEmail) {
    console.error('No valid TO email address found');
    return;
  }

  const vinNo = completeFleetData.VIN_NO || 'N/A';
  const registrationNo1 = completeFleetData.registration && completeFleetData.registration[0] ? completeFleetData.registration[0].REGISTRATION_NO1 || 'N/A' : 'N/A';

  const subject = isNewSubmission
    ? `Action required: New Fleet Details ${fleetControlNumber}/${vinNo}/${registrationNo1} requires your approval`
    : `Action required: Modified Fleet Details ${fleetControlNumber}/${vinNo}/${registrationNo1} requires your approval`;
  console.log(`Email subject: ${subject}`);

  let comparisonData = null;
  if (!isNewSubmission) {
    console.log('This is an edit submission, fetching comparison data');
    try {
      const headerId = completeFleetData.HEADER_ID;
      console.log(`Using HEADER_ID for comparison: ${headerId}`);
      const comparisonResponse = await fetch(`http://127.0.0.1:8000/api/compare-data/${headerId}`);
      console.log('Comparison data API response status:', comparisonResponse.status);

      if (!comparisonResponse.ok) {
        throw new Error(`HTTP error! status: ${comparisonResponse.status}`);
      }
      console.log('Comparison data being sent:', comparisonData);


      comparisonData = await comparisonResponse.json();
      console.log('Comparison data received:', comparisonData);
    } catch (error) {
      console.error('Error fetching comparison data:', error);
    }
  }

  const formData = new FormData();
  formData.append('recipient', toEmail);
  formData.append('cc', ccEmail || '');
  formData.append('bcc', '');
  formData.append('subject', subject);
  formData.append('data', JSON.stringify(completeFleetData));
  formData.append('custom_message', isNewSubmission ? 'New fleet Details submission for your approval' : 'Updated fleet details for your approval');
  formData.append('is_new_submission', isNewSubmission);
  formData.append('action', action); 
  
  if (comparisonData) {
    formData.append('comparison_data', JSON.stringify(comparisonData));
  }

  console.log('FormData created with basic information');

  console.log('Sending email...');
  try {
    showEmailSendingPopup(
      fetch('http://127.0.0.1:8000/api/send-email', {
        method: 'POST',
        body: formData
      }).then(response => {
        console.log('Email API response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      }).then(result => {
        if (result.status === 'success') {
          console.log('Email sent successfully!');
        } else {
          throw new Error(result.message);
        }
      })
    );
  } catch (error) {
    console.error('Error sending email:', error);
   // alert(`Failed to send email: ${error.message}`);
  }

  console.log('sendEmailAutomatically function completed');
}


                                        
// Add this function if it's not already defined
async function sendCancellationEmail(fleetControlNumber) {
  try {
      const emailAddresses = await fetchEmailAddresses('CANCEL_FLEET_MASTER');
      if (!emailAddresses || !emailAddresses.toEmail) {
          throw new Error('No valid email addresses found for CANCEL_FLEET_MASTER');
      }

      const fleetResponse = await fetch(`http://127.0.0.1:8000/api/fleet-master/${fleetControlNumber}`);
      const fleetData = await fleetResponse.json();

      const vinNo = fleetData.VIN_NO || 'N/A';
      const REGISTRATION_NO1 = fleetData.registration[0]?.REGISTRATION_NO1 || 'N/A';

      const subject = `Action Required : Cancellation Request for Fleet Details : ${fleetControlNumber}/${vinNo}/${REGISTRATION_NO1}`;
      const action = 'Sending for Cancellation';
      const formData = new FormData();
      formData.append('recipient', emailAddresses.toEmail);
      formData.append('cc', emailAddresses.ccEmail || '');
      formData.append('subject', subject);
      formData.append('custom_message', 'A cancellation request has been submitted for the following fleet:');
      formData.append('data', JSON.stringify(fleetData));
      formData.append('data', JSON.stringify({...fleetData, ACTION: action}));
      formData.append('action', action);

      showEmailSendingPopup(
          fetch('http://127.0.0.1:8000/api/send-email', {
              method: 'POST',
              body: formData
          }).then(response => {
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.json();
          }).then(result => {
              if (result.status !== 'success') {
                  throw new Error(result.message);
              }
              console.log('Cancellation email sent successfully');
          })
      );
  } catch (error) {
      console.error('Error:', error);
      alert(`Failed to send cancellation email: ${error.message}`);
  }
}


const cancelBtn = document.getElementById('cancelForm');

if (cancelBtn) {
  cancelBtn.addEventListener('click', function() {
      const statusInput = document.querySelector('input[name="STATUS"]');
      const comment = document.querySelector('textarea[name="COMMENTS"]').value.trim();
        
      // First check for comments
      if (!comment) {
          alert('Please add comments before requesting cancellation');
          return;
      }
      
      // Check all statuses from different tables
      const insuranceStatuses = Array.from(document.querySelectorAll('#insuranceTable tbody tr select[name="CURRENT STATUS_LOOKUP_NAME"]'))
          .filter(select => select.closest('tr').style.display !== 'none')
          .map(select => select.value);
          
      const registrationStatuses = Array.from(document.querySelectorAll('#registrationTable tbody tr select[name="CURRENT STATUS_LOOKUP_NAME"]'))
          .filter(select => select.closest('tr').style.display !== 'none')
          .map(select => select.value);
          
      const roadtollStatuses = Array.from(document.querySelectorAll('#roadtollTable tbody tr select[name="CURRENT STATUS_LOOKUP_NAME"]'))
          .filter(select => select.closest('tr').style.display !== 'none')
          .map(select => select.value);
          
      const permitStatuses = Array.from(document.querySelectorAll('#permitsTable tbody tr select[name="CURRENT STATUS_LOOKUP_NAME"]'))
          .filter(select => select.closest('tr').style.display !== 'none')
          .map(select => select.value);
          
      const fuelStatuses = Array.from(document.querySelectorAll('#fuelTable tbody tr select[name="CURRENT STATUS_LOOKUP_NAME"]'))
          .filter(select => select.closest('tr').style.display !== 'none')
          .map(select => select.value);
          
      const hasActiveStatus = [...insuranceStatuses, ...registrationStatuses, ...roadtollStatuses, ...permitStatuses, ...fuelStatuses]
          .some(status => status === 'Active');
          
      if (hasActiveStatus) {
          alert('Cannot cancel the form while any record status is active');
          return;
      }
        
      statusInput.value = 'Request For Cancellation';
      
      if (confirm('Are you sure you want to request cancellation for this fleet?')) {
          // Instead of calling submitForm directly, we'll set a flag and trigger the submit button
          window.isRequestingCancellation = true;
          document.getElementById('submitForm').click();
      } else {
          statusInput.value = ''; 
      }
  });
}


function showEmailSendingPopup(emailSendingPromise) {
  // Create and show loading indicator
  const loadingIndicator = document.createElement('div');
  loadingIndicator.className = 'loading-indicator';
  loadingIndicator.style.position = 'fixed';
  loadingIndicator.style.top = '50%';
  loadingIndicator.style.left = '50%';
  loadingIndicator.style.transform = 'translate(-50%, -50%)';
  loadingIndicator.style.zIndex = '1000';
  
  // Add your preferred loading indicator styles here
  // For example, a simple spinning circle:
  loadingIndicator.style.width = '40px';
  loadingIndicator.style.height = '40px';
  loadingIndicator.style.border = '4px solid #f3f3f3';
  loadingIndicator.style.borderTop = '4px solid #3498db';
  loadingIndicator.style.borderRadius = '50%';
  loadingIndicator.style.animation = 'spin 1s linear infinite';

  // Add keyframe animation for spin
  const style = document.createElement('style');
  style.textContent = `
      @keyframes spin {
          0% { transform: translate(-50%, -50%) rotate(0deg); }
          100% { transform: translate(-50%, -50%) rotate(360deg); }
      }
  `;
  document.head.appendChild(style);

  document.body.appendChild(loadingIndicator);

  // Handle the email sending promise
  emailSendingPromise
      .then(result => {
          // Handle success (you might want to show a success icon briefly)
      })
      .catch(error => {
          console.error('Email sending error:', error);
          // Handle error (you might want to show an error icon briefly)
      })
      .finally(() => {
          // Remove loading indicator
          document.body.removeChild(loadingIndicator);
          document.head.removeChild(style);
      });
}



let storedEmailAddresses = null;

async function fetchAndStoreEmailAddresses() {
  if (!storedEmailAddresses) {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/related-data/?lookup_name=EMAIL_SETUPS');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      storedEmailAddresses = await response.json();
    } catch (error) {
      console.error('Error fetching email addresses:', error);
      storedEmailAddresses = null;
    }
  }
  return storedEmailAddresses;
}


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


async function showComposeModal(fleetControlNumber, action = '', isApprover = false,comment = '') {
  console.log('Action received in showComposeModal:', action);

  const emailAddresses = await fetchAndStoreEmailAddresses();
  
  let toEmail = '';
  let ccEmails = '';

  if (emailAddresses) {
    const toEmailObj = emailAddresses.find(item => item.LOOKUP_CODE === 'TO' && item.ACTIVE === 'Y');
    const ccEmailsObj = emailAddresses.find(item => item.LOOKUP_CODE === 'CC' && item.ACTIVE === 'Y');

    if (toEmailObj) toEmail = toEmailObj.MEANING;
    if (ccEmailsObj) ccEmails = ccEmailsObj.MEANING;
  }

  try {
      const response = await fetch(`http://127.0.0.1:8000/api/fleet-master/${fleetControlNumber}`);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      data.COMMENTS = comment;
      const vinNo = data.VIN_NO || 'N/A';

      let subject;
      const fleetInfo = `${fleetControlNumber}/${vinNo}`;
      let newStatus = '';
      if (isApprover && action) {
          switch(action) {
              case 'Return for Correction':
                  newStatus = 'Return for Correction';
                  data.ACTION = 'Return for Correction';
                  subject = `Fleet Details: ${fleetInfo} request is return for correction.`;
                  break;
              case 'Approved':
                  newStatus = 'Approved';
                  data.ACTION = 'Approved';
                  subject = `Fleet Details: ${fleetInfo} has been approved`;
                  break;
              case 'Revert':
                  newStatus = 'Rejected';
                  data.ACTION = 'Rejected';
                  subject = `Fleet Details ${fleetInfo} requested has been rejected`;
                  break;
              case 'Defleet':
                  newStatus = 'Defleet';
                  data.ACTION = 'Defleet';
                  subject = `Fleet Details: ${fleetInfo} request has been defleeted`;
                  break;
              default:
                  newStatus = data.STATUS;
                  data.ACTION = data.ACTION || 'New';
                  subject = `A New Fleet ${fleetInfo} requires approval`;
              }
            } else {
              if (!isApprover) {
                    if (data.STATUS === 'Return for Correction') {
                        data.ACTION = 'Modified';
                    } else if (data.STATUS === 'Pending for Approval' && !data.ACTION) {
                        data.ACTION = 'New';
                    } else {
                        data.ACTION = data.ACTION || data.STATUS;
                    }
                  }
                subject = `Action required: ${data.ACTION} Fleet Details ${fleetInfo} requires your approval`;
            }

      data.STATUS = newStatus;
      console.log('Subject set:', subject);

      const formData = new FormData();
      formData.append('data', JSON.stringify(data));
      formData.append('recipient', toEmail);
      formData.append('cc', ccEmails);
      formData.append('subject', subject);
      formData.append('data', JSON.stringify(data));
      formData.append('is_approver_action', isApprover.toString());
      formData.append('action', data.ACTION);
      formData.append('is_new_submission', (!isApprover).toString());

      const emailResponse = await fetch('http://127.0.0.1:8000/api/send-email', {
        method: 'POST',
        body: formData
      });

      if (!emailResponse.ok) {
          throw new Error(`HTTP error! status: ${emailResponse.status}`);
      }

      const result = await emailResponse.json();

      if (result.status === 'success') {
        console.log('Email sent successfully!');
        if (window.submitFormAfterEmail) {
          window.submitFormAfterEmail();
        }
      } else {
        throw new Error(result.message);
      }
                    } catch (error) {
      console.error('Error fetching vehicle info or sending email:', error);
      //alert(`Failed to send email: ${error.message}`);
      }
}
