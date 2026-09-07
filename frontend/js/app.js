// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const chooseFileBtn = document.getElementById('chooseFileBtn');
const previewSection = document.getElementById('previewSection');
const imagePreview = document.getElementById('imagePreview');
const removeImageBtn = document.getElementById('removeImageBtn');
const fileName = document.getElementById('fileName');
const extractBtn = document.getElementById('extractBtn');
const demoBtn = document.getElementById('demoBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

let selectedFile = null;

// Event Listeners
chooseFileBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', handleFileSelect);

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    removeImage();
});

extractBtn.addEventListener('click', extractBill);

demoBtn.addEventListener('click', loadDemoBill);

// Functions
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Please select a valid image file (JPG, JPEG, PNG, or WEBP)');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        fileName.textContent = file.name;
        uploadArea.style.display = 'none';
        previewSection.style.display = 'block';
        extractBtn.disabled = false;
    };
    reader.readAsDataURL(file);
    
    hideError();
}

function removeImage() {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    fileName.textContent = '';
    uploadArea.style.display = 'block';
    previewSection.style.display = 'none';
    extractBtn.disabled = true;
    hideError();
}

async function extractBill() {
    if (!selectedFile) {
        showError('Please select an image first');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to extract bill data');
        }
        
        const billData = await response.json();
        
        // Store bill data in sessionStorage for review page
        sessionStorage.setItem('billData', JSON.stringify(billData));
        sessionStorage.setItem('billImage', imagePreview.src);
        
        // Navigate to review page
        window.location.href = 'review.html';
        
    } catch (error) {
        showError('Error extracting bill: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function loadDemoBill() {
    showLoading();
    hideError();
    
    try {
        const response = await fetch('/api/upload?demo=true', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load demo bill');
        }
        
        const billData = await response.json();
        
        // Store bill data in sessionStorage
        sessionStorage.setItem('billData', JSON.stringify(billData));
        sessionStorage.setItem('billImage', '');
        sessionStorage.setItem('isDemo', 'true');
        
        // Navigate to review page
        window.location.href = 'review.html';
        
    } catch (error) {
        showError('Error loading demo bill: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showLoading() {
    loading.style.display = 'block';
    extractBtn.disabled = true;
    demoBtn.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    extractBtn.disabled = !selectedFile;
    demoBtn.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}
