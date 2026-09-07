// DOM Elements
const billTotal = document.getElementById('billTotal');
const membersBreakdown = document.getElementById('membersBreakdown');
const verificationBillTotal = document.getElementById('verificationBillTotal');
const verificationSharesTotal = document.getElementById('verificationSharesTotal');
const verificationDifference = document.getElementById('verificationDifference');
const verificationStatus = document.getElementById('verificationStatus');
const newBillBtn = document.getElementById('newBillBtn');
const backBtn = document.getElementById('backBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCalculationResult();
});

// Load calculation result from sessionStorage
function loadCalculationResult() {
    const storedResult = sessionStorage.getItem('calculationResult');
    
    if (!storedResult) {
        window.location.href = 'index.html';
        return;
    }
    
    const result = JSON.parse(storedResult);
    
    // Display bill total
    billTotal.textContent = `₹${result.bill_total}`;
    
    // Render member breakdowns
    renderMemberBreakdowns(result.members);
    
    // Display verification
    verificationBillTotal.textContent = `₹${result.bill_total}`;
    verificationSharesTotal.textContent = `₹${result.shares_total}`;
    verificationDifference.textContent = `₹${result.difference}`;
    
    // Set verification status
    if (result.difference === 0) {
        verificationStatus.textContent = '✓ Shares match bill total';
        verificationStatus.className = 'verification-status success';
    } else {
        verificationStatus.textContent = `⚠ Difference detected: ₹${result.difference}`;
        verificationStatus.className = 'verification-status warning';
    }
}

// Render member breakdowns
function renderMemberBreakdowns(members) {
    membersBreakdown.innerHTML = members.map(member => `
        <div class="member-card">
            <h3>${member.member_name}</h3>
            
            <div class="member-items">
                ${member.items.map(item => `
                    <div class="member-item">
                        <span class="member-item-name">${item.name} (Qty: ${item.quantity})</span>
                        <span class="member-item-amount">₹${item.share.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            
            <div class="member-summary">
                <div class="summary-row">
                    <span>Food subtotal</span>
                    <span>₹${member.food_subtotal}</span>
                </div>
                <div class="summary-row">
                    <span>GST</span>
                    <span>₹${member.tax_share}</span>
                </div>
                <div class="summary-row">
                    <span>Service charge</span>
                    <span>₹${member.service_charge_share}</span>
                </div>
                ${member.discount_share > 0 ? `
                    <div class="summary-row">
                        <span>Discount</span>
                        <span>-₹${member.discount_share}</span>
                    </div>
                ` : ''}
                <div class="summary-row total">
                    <span>TOTAL</span>
                    <span>₹${member.total}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// New bill button
newBillBtn.addEventListener('click', () => {
    // Clear sessionStorage
    sessionStorage.clear();
    window.location.href = 'index.html';
});

// Back button
backBtn.addEventListener('click', () => {
    window.location.href = 'review.html';
});
