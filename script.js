function toggleTheme() {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        localStorage.theme = 'light';
    } else {
        html.classList.add('dark');
        localStorage.theme = 'dark';
    }
}

// Initialize theme based on preference
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark');
}

let currentCycle = 'monthly'; // Default billing cycle
let latestBreakdown = null;   // Store global calculation result to reuse when switching tabs

function switchBillingCycle(cycle) {
    currentCycle = cycle;
    
    // Update active tab styles
    ['hourly', 'monthly', 'yearly'].forEach(c => {
        const btn = document.getElementById(`tab-${c}`);
        if (c === cycle) {
            btn.className = "px-3 py-1.5 rounded-lg transition bg-white dark:bg-gray-800 text-aletGreen shadow-sm font-semibold";
        } else {
            btn.className = "px-3 py-1.5 rounded-lg transition text-gray-500 dark:text-gray-400";
        }
    });

    // Update total label and SMS visibility for hourly
    document.getElementById('total-label').innerText = `Total (${cycle.charAt(0).toUpperCase() + cycle.slice(1)}):`;
    
    // Trigger calculation display update with existing data
    updateDisplay();
}

async function calculate() {
    const vcpu = document.getElementById('vcpu').value;
    const ram = document.getElementById('ram').value;
    const storage = document.getElementById('storage').value;
    const sms = document.getElementById('sms').value;

    // Update labels dynamically
    document.getElementById('vcpu-val').innerText = vcpu + " Cores";
    document.getElementById('ram-val').innerText = ram + " GB";
    document.getElementById('storage-val').innerText = storage + " GB";
    document.getElementById('sms-val').innerText = Number(sms).toLocaleString() + " SMS";

    try {
        const response = await fetch('http://localhost:8000/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vcpu_cores: parseInt(vcpu),
                ram_gb: parseInt(ram),
                storage_gb: parseInt(storage),
                monthly_sms: parseInt(sms)
            })
        });

        const result = await response.json();
        if (result.status === 'success') {
            latestBreakdown = result.breakdown;
            updateDisplay();
        }
    } catch (error) {
        console.error('Backend connection error:', error);
    }
}

function updateDisplay() {
    if (!latestBreakdown) return;

    const data = latestBreakdown[currentCycle];
    
    document.getElementById('out-vcpu').innerText = '$' + data.vCPU_cost.toFixed(2);
    document.getElementById('out-ram').innerText = '$' + data.RAM_cost.toFixed(2);
    document.getElementById('out-storage').innerText = '$' + data.Storage_cost.toFixed(2);

    // SMS is only applicable for monthly and yearly, hide or show rate for hourly
    if (currentCycle === 'hourly') {
        document.getElementById('out-sms').innerText = '$0.00 (Mo. rate)';
        document.getElementById('out-total').innerText = '$' + data.total_hourly_cost.toFixed(4);
    } else if (currentCycle === 'monthly') {
        document.getElementById('out-sms').innerText = '$' + data.SMS_cost.toFixed(2);
        document.getElementById('out-total').innerText = '$' + data.total_monthly_cost.toFixed(2);
    } else if (currentCycle === 'yearly') {
        document.getElementById('out-sms').innerText = '$' + data.SMS_cost.toFixed(2);
        document.getElementById('out-total').innerText = '$' + data.total_yearly_cost.toFixed(2);
    }
}

// --- Custom Modern Alert Modal Functions ---
function showCustomAlert(message) {
    document.getElementById('alert-message').innerText = message;
    const modal = document.getElementById('custom-alert-modal');
    const box = document.getElementById('alert-modal-box');
    
    modal.classList.remove('opacity-0', 'pointer-events-none');
    box.classList.remove('scale-95');
    box.classList.add('scale-100');
}

function closeCustomAlert() {
    const modal = document.getElementById('custom-alert-modal');
    const box = document.getElementById('alert-modal-box');
    
    modal.classList.add('opacity-0', 'pointer-events-none');
    box.classList.remove('scale-100');
    box.classList.add('scale-95');
}

// --- PHASE 3: SERVER-SIDE PDF GENERATION INTEGRATION ---
async function generatePDFQuote() {
    const clientName = document.getElementById('client-name').value;
    const clientEmail = document.getElementById('client-email').value;
    const orgName = document.getElementById('org-name').value;

    if (!clientName || !clientEmail || !orgName) {
        showCustomAlert('Please fill in all quotation details (Client Name, Email, Organization)!');
        return;
    }

    const vcpu = document.getElementById('vcpu').value;
    const ram = document.getElementById('ram').value;
    const storage = document.getElementById('storage').value;
    const sms = document.getElementById('sms').value;

    try {
        // Send request to FastAPI backend (Server-Side PDF Generation)
        const response = await fetch('http://localhost:8000/api/generate-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_name: clientName,
                client_email: clientEmail,
                org_name: orgName,
                billing_cycle: currentCycle,
                resources: {
                    vcpu_cores: parseInt(vcpu),
                    ram_gb: parseInt(ram),
                    storage_gb: parseInt(storage),
                    monthly_sms: parseInt(sms)
                }
            })
        });

        if (!response.ok) throw new Error('Failed to generate PDF from server');

        // Receive the PDF binary and trigger automatic browser download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AletCloud_Quotation_${clientName.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('PDF Generation error:', error);
        showCustomAlert('Error generating PDF. Please make sure the backend server is running.');
    }
}

// Run calculation on initial load
calculate();