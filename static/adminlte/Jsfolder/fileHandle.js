function getAllFileNames(fileData, modelName, instanceId) {
  if (typeof fileData === 'string' || Array.isArray(fileData)) {
      const files = typeof fileData === 'string' ? JSON.parse(fileData) : fileData;
      return files.map((file, index) => {
          const fileName = file.trim().split('/').pop().replace(/["'\[\]]/g, '');
          // Set model name to 'VEHICLE' for vehicle documents
          const actualModelName = modelName || 'VEHICLE';
          return createFileItem(fileName, actualModelName, instanceId, index);
      }).join('');
  }
  return '';
}



function handleFileSelection(fileInput) {
  const newFiles = fileInput.files;
  let fileListContainer = fileInput.nextElementSibling;
  let fileDropdown;

  if (!fileListContainer || !fileListContainer.classList.contains('file-list-container')) {
    fileListContainer = document.createElement('div');
    fileListContainer.className = 'file-list-container';
    fileInput.parentNode.insertBefore(fileListContainer, fileInput.nextSibling);

    const wrapper = document.createElement('div');
    wrapper.className = 'file-input-wrapper';
    fileInput.parentNode.insertBefore(wrapper, fileInput);
    wrapper.appendChild(fileInput);
    wrapper.appendChild(fileListContainer);

    fileDropdown = createFileDropdown();
    fileListContainer.appendChild(fileDropdown);
  } else {
    fileDropdown = fileListContainer.querySelector('.file-dropdown');
  }

  const existingFiles = Array.from(fileDropdown.querySelectorAll('.file-item')).map(item => item.dataset.fileName);
  const newFileNames = Array.from(newFiles).map(file => file.name);
  
  // Only add files that don't already exist
  const filesToAdd = newFileNames.filter(fileName => !existingFiles.includes(fileName));

  for (let i = 0; i < filesToAdd.length; i++) {
    const fileName = filesToAdd[i];
    const fileItem = createFileItem(fileName, '', '', existingFiles.length + i);
    fileDropdown.querySelector('.file-list').insertAdjacentHTML('beforeend', fileItem);
  }

  // Combine existing files and new files without duplicates
  const allFiles = [...new Set([...existingFiles, ...filesToAdd])];

  updateFileInput(fileInput, allFiles);
  addRemoveFileListeners(fileDropdown, fileInput);
  updateFileCount(fileInput, fileDropdown);
}






function createFileItem(fileName, modelName, instanceId, index) {
const actualInstanceId = instanceId || document.querySelector('[name="HEADER_ID"]')?.value;

return `
<div class="file-item" data-file-name="${fileName}">
<div class="file-content">
<i class="fa-solid fa-paperclip file-icon"></i>
<span class="file-name">${fileName}</span>
</div>
<div class="remove-file-container">
<i class="fas fa-times remove-file" 
data-file-name="${fileName}" 
data-model="${modelName}" 
data-instance="${actualInstanceId}" 
data-index="${index}"></i>
</div>
</div>
`;
}

function toggleFileList(event) {
  const fileList = event.currentTarget.nextElementSibling;
  fileList.style.display = fileList.style.display === 'none' ? 'block' : 'none';
}

function createFileDropdown() {
  const dropdown = document.createElement('div');
  dropdown.className = 'file-dropdown';
  dropdown.innerHTML = `
    <div class="dropdown-toggle">
      <i class="fas fa-chevron-down"></i> <span class="file-count">file(s)</span>
    </div>
    <div class="file-list" style="display: none;"></div>
  `;
  dropdown.querySelector('.dropdown-toggle').addEventListener('click', toggleFileList);
  return dropdown;
}



function updateFileCount(fileInput, fileDropdown) {
  const fileCount = fileDropdown.querySelectorAll('.file-item').length;
  const fileCountSpan = fileDropdown.querySelector('.file-count');
  fileCountSpan.textContent = `${fileCount} file(s)`;

  const fileList = fileDropdown.querySelector('.file-list');
  if (fileCount > 2) {
    fileList.style.maxHeight = '150px';
    fileList.style.overflowY = 'auto';
  } else {
    fileList.style.maxHeight = 'none';
    fileList.style.overflowY = 'visible';
  }
}










function addRemoveFileListeners(fileListContainer, fileInput) {
  fileListContainer.querySelectorAll('.remove-file').forEach(removeIcon => {
    removeIcon.addEventListener('click', function() {
      const fileName = this.dataset.fileName;
      const modelName = this.dataset.model;
      const instanceId = this.dataset.instance;
      const index = this.dataset.index;

      if (modelName && instanceId) {
        deleteFile(modelName, instanceId, index, fileName);
      } else {
      const fileItem = this.closest('.file-item');
      fileItem.remove();

        const existingFiles = Array.from(fileListContainer.querySelectorAll('.file-item')).map(item => item.dataset.fileName);
      updateFileInput(fileInput, existingFiles);
        updateFileCount(fileInput, fileListContainer.querySelector('.file-dropdown'));
      }
    });
  });
}




function updateFileInput(fileInput, fileNames) {
  const dt = new DataTransfer();
  const existingFiles = Array.from(fileInput.files);

  fileNames.forEach(fileName => {
    const file = existingFiles.find(f => f.name === fileName);
    if (file && file.size > 0) {
      dt.items.add(file);
    } else if (fileName.trim() !== '') {
      // Create a placeholder file for existing filenames
      dt.items.add(new File([], fileName, { type: 'application/octet-stream' }));
    }
  });

  fileInput.files = dt.files;
} 






function addFileInputListeners() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    input.addEventListener('change', function () {
      handleFileSelection(this);
    });
  });
}


function handleFileSelectionWrapper() {
  handleFileSelection(this);
} 
    
  
    function setupDropdownsForNewRow(row) {
        setupTrafficSearchFunctionality(row);

        row.querySelectorAll("select").forEach((dropdown) => {
        const lookupName = dropdown.getAttribute("name").replace('_LOOKUP_NAME', '').trim();
        if (lookupName) {
          // Fetch dropdown options when clicked
          dropdown.addEventListener("click", () => fetchDropdownOptions(lookupName, dropdown));
        }
        // Store the selected value as a data attribute for later use
        dropdown.addEventListener("change", function () {
          this.setAttribute("data-selected", this.value);
        });
      });
    }
