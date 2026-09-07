// DOM Elements
const billImage = document.getElementById('billImage');
const restaurantName = document.getElementById('restaurantName');
const billDate = document.getElementById('billDate');
const billNumber = document.getElementById('billNumber');
const itemsTableBody = document.getElementById('itemsTableBody');
const addItemBtn = document.getElementById('addItemBtn');
const subtotal = document.getElementById('subtotal');
const tax = document.getElementById('tax');
const serviceCharge = document.getElementById('serviceCharge');
const discount = document.getElementById('discount');
const printedTotal = document.getElementById('printedTotal');
const calculatedSubtotal = document.getElementById('calculatedSubtotal');
const printedSubtotal = document.getElementById('printedSubtotal');
const calculatedTotal = document.getElementById('calculatedTotal');
const validationPrintedTotal = document.getElementById('validationPrintedTotal');
const validationMessage = document.getElementById('validationMessage');
const membersList = document.getElementById('membersList');
const newMemberName = document.getElementById('newMemberName');
const addMemberBtn = document.getElementById('addMemberBtn');
const assignmentList = document.getElementById('assignmentList');
const calculateBtn = document.getElementById('calculateBtn');
const backBtn = document.getElementById('backBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

// State
let billData = null;
let members = [];
let items = [];
let assignments = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadBillData();
    initializeMembers();
    renderMembers();
    renderItems();
    renderAssignments();
    updateValidation();
});

// Load bill data from sessionStorage
function loadBillData() {
    const storedBillData = sessionStorage.getItem('billData');
    const storedBillImage = sessionStorage.getItem('billImage');
    
    if (!storedBillData) {
        window.location.href = 'index.html';
        return;
    }
    
    billData = JSON.parse(storedBillData);
    items = JSON.parse(JSON.stringify(billData.items));
    
    // Set bill image if available
    if (storedBillImage) {
        billImage.src = storedBillImage;
    } else {
        billImage.style.display = 'none';
    }
    
    // Populate form fields
    restaurantName.value = billData.restaurant_name;
    billDate.value = billData.date;
    billNumber.value = billData.bill_number || '';
    subtotal.value = billData.subtotal;
    tax.value = billData.tax;
    serviceCharge.value = billData.service_charge;
    discount.value = billData.discount;
    printedTotal.value = billData.printed_total;
}

// Initialize with default members
function initializeMembers() {
    members = [
        { id: 'member-1', name: 'Rahul' },
        { id: 'member-2', name: 'Priya' },
        { id: 'member-3', name: 'Aman' }
    ];
}

// Render members list
function renderMembers() {
    membersList.innerHTML = members.map(member => `
        <div class="member-tag">
            <span>${member.name}</span>
            <button class="remove-member" onclick="removeMember('${member.id}')">×</button>
        </div>
    `).join('');
    
    renderAssignments();
}

// Add member
addMemberBtn.addEventListener('click', () => {
    const name = newMemberName.value.trim();
    
    if (!name) {
        showError('Please enter a member name');
        return;
    }
    
    if (members.length >= 7) {
        showError('Maximum 7 members allowed');
        return;
    }
    
    if (members.some(m => m.name.toLowerCase() === name.toLowerCase())) {
        showError('Member name already exists');
        return;
    }
    
    const newMember = {
        id: `member-${Date.now()}`,
        name: name
    };
    
    members.push(newMember);
    newMemberName.value = '';
    renderMembers();
    hideError();
});

// Remove member
function removeMember(memberId) {
    if (members.length <= 2) {
        showError('Minimum 2 members required');
        return;
    }
    
    members = members.filter(m => m.id !== memberId);
    renderMembers();
    hideError();
}

// Render items table
function renderItems() {
    itemsTableBody.innerHTML = items.map((item, index) => `
        <tr data-item-id="${item.id}">
            <td>
                <input type="text" value="${item.name}" onchange="updateItem('${item.id}', 'name', this.value)">
            </td>
            <td>
                <input type="number" value="${item.quantity}" min="1" onchange="updateItem('${item.id}', 'quantity', this.value)">
            </td>
            <td>
                <input type="number" value="${item.unit_price}" step="0.01" min="0" onchange="updateItem('${item.id}', 'unit_price', this.value)">
            </td>
            <td>
                <input type="number" value="${item.total}" step="0.01" min="0" readonly>
            </td>
            <td>
                <span class="confidence-${getConfidenceClass(item.confidence)}">${getConfidenceLabel(item.confidence)}</span>
            </td>
            <td>
                <button class="btn btn-danger" onclick="removeItem('${item.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
    
    updateValidation();
}

// Add new item
addItemBtn.addEventListener('click', () => {
    const newItem = {
        id: `item-${Date.now()}`,
        name: 'New Item',
        quantity: 1,
        unit_price: 0,
        total: 0,
        confidence: 0
    };
    
    items.push(newItem);
    renderItems();
});

// Update item
function updateItem(itemId, field, value) {
    const item = items.find(i => i.id === itemId);
    if (item) {
        if (field === 'quantity') {
            item[field] = parseInt(value) || 1;
        } else if (field === 'unit_price') {
            item[field] = parseFloat(value) || 0;
        } else {
            item[field] = value;
        }
        
        // Recalculate total
        item.total = item.quantity * item.unit_price;
        
        renderItems();
    }
}

// Remove item
function removeItem(itemId) {
    if (items.length <= 1) {
        showError('At least one item is required');
        return;
    }
    
    items = items.filter(i => i.id !== itemId);
    renderItems();
    hideError();
}

// Get confidence class
function getConfidenceClass(confidence) {
    if (confidence >= 0.90) return 'high';
    if (confidence >= 0.70) return 'medium';
    return 'low';
}

// Get confidence label
function getConfidenceLabel(confidence) {
    if (confidence >= 0.90) return 'HIGH';
    if (confidence >= 0.70) return 'MEDIUM';
    return 'LOW';
}

// Render assignments
function renderAssignments() {
    assignmentList.innerHTML = items.map(item => `
        <div class="assignment-item">
            <div class="assignment-item-header">
                <div>
                    <div class="assignment-item-name">${item.name}</div>
                    <div class="assignment-item-details">
                        Qty: ${item.quantity} × ₹${item.unit_price} = ₹${item.total}
                    </div>
                </div>
            </div>
            <div class="assignment-members">
                ${members.map(member => `
                    <div class="member-checkbox">
                        <input type="checkbox" 
                               id="assign-${item.id}-${member.id}"
                               onchange="updateAssignment('${item.id}', '${member.id}', this.checked)">
                        <label for="assign-${item.id}-${member.id}">${member.name}</label>
                    </div>
                `).join('')}
            </div>
            <div class="everyone-checkbox">
                <div class="member-checkbox">
                    <input type="checkbox" 
                           id="assign-${item.id}-everyone"
                           onchange="assignToEveryone('${item.id}', this.checked)">
                    <label for="assign-${item.id}-everyone">Everyone</label>
                </div>
            </div>
        </div>
    `).join('');
}

// Update assignment
function updateAssignment(itemId, memberId, isChecked) {
    const assignment = assignments.find(a => a.item_id === itemId);
    
    if (isChecked) {
        if (assignment) {
            if (!assignment.member_ids.includes(memberId)) {
                assignment.member_ids.push(memberId);
            }
        } else {
            assignments.push({
                item_id: itemId,
                member_ids: [memberId]
            });
        }
    } else {
        if (assignment) {
            assignment.member_ids = assignment.member_ids.filter(id => id !== memberId);
            if (assignment.member_ids.length === 0) {
                assignments = assignments.filter(a => a.item_id !== itemId);
            }
        }
    }
}

// Assign to everyone
function assignToEveryone(itemId, isChecked) {
    const everyoneCheckbox = document.getElementById(`assign-${itemId}-everyone`);
    
    members.forEach(member => {
        const checkbox = document.getElementById(`assign-${itemId}-${member.id}`);
        if (checkbox) {
            checkbox.checked = isChecked;
            updateAssignment(itemId, member.id, isChecked);
        }
    });
}

// Update validation
function updateValidation() {
    const calcSubtotal = items.reduce((sum, item) => sum + item.total, 0);
    const calcTotal = calcSubtotal + parseFloat(tax.value || 0) + parseFloat(serviceCharge.value || 0) - parseFloat(discount.value || 0);
    
    calculatedSubtotal.textContent = `₹${calcSubtotal.toFixed(2)}`;
    printedSubtotal.textContent = `₹${parseFloat(subtotal.value || 0).toFixed(2)}`;
    calculatedTotal.textContent = `₹${calcTotal.toFixed(2)}`;
    validationPrintedTotal.textContent = `₹${parseFloat(printedTotal.value || 0).toFixed(2)}`;
    
    // Check for mismatches
    const subtotalDiff = Math.abs(calcSubtotal - parseFloat(subtotal.value || 0));
    const totalDiff = Math.abs(calcTotal - parseFloat(printedTotal.value || 0));
    
    if (subtotalDiff > 0.01 || totalDiff > 0.01) {
        validationMessage.className = 'validation-message warning';
        validationMessage.innerHTML = '⚠ Printed total mismatch detected. Please review the values.';
    } else {
        validationMessage.className = 'validation-message success';
        validationMessage.innerHTML = '✓ Totals match';
    }
}

// Listen for charge changes
[subtotal, tax, serviceCharge, discount, printedTotal].forEach(input => {
    input.addEventListener('change', updateValidation);
});

// Calculate fair share
calculateBtn.addEventListener('click', async () => {
    // Validate
    if (members.length < 2) {
        showError('At least 2 members are required');
        return;
    }
    
    if (assignments.length === 0) {
        showError('Please assign items to members');
        return;
    }
    
    // Check for unassigned items
    const assignedItemIds = assignments.map(a => a.item_id);
    const unassignedItems = items.filter(i => !assignedItemIds.includes(i.id));
    
    if (unassignedItems.length > 0) {
        showError('Some items are not assigned to any member');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        const payload = {
            bill: {
                restaurant_name: restaurantName.value,
                date: billDate.value,
                bill_number: billNumber.value,
                items: items,
                subtotal: parseFloat(subtotal.value),
                tax: parseFloat(tax.value),
                service_charge: parseFloat(serviceCharge.value),
                discount: parseFloat(discount.value),
                printed_total: parseFloat(printedTotal.value)
            },
            members: members,
            assignments: assignments
        };
        
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error('Failed to calculate shares');
        }
        
        const result = await response.json();
        
        // Store result in sessionStorage
        sessionStorage.setItem('calculationResult', JSON.stringify(result));
        
        // Navigate to result page
        window.location.href = 'result.html';
        
    } catch (error) {
        showError('Error calculating shares: ' + error.message);
    } finally {
        hideLoading();
    }
});

// Back button
backBtn.addEventListener('click', () => {
    window.location.href = 'index.html';
});

// Loading functions
function showLoading() {
    loading.style.display = 'block';
    calculateBtn.disabled = true;
    backBtn.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    calculateBtn.disabled = false;
    backBtn.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}
