// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const crimeInput = document.getElementById('crimeInput');
const predictBtn = document.getElementById('predictBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const refinedDesc = document.getElementById('refinedDesc');
const predictions = document.getElementById('predictions');

// Event Listeners
predictBtn.addEventListener('click', handlePredict);
clearBtn.addEventListener('click', handleClear);

// Handle Enter key (Ctrl+Enter to submit)
crimeInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        handlePredict();
    }
});

// Predict BNS Sections
async function handlePredict() {
    const crimeDescription = crimeInput.value.trim();

    // Validation
    if (!crimeDescription) {
        showError('Please enter a crime description');
        return;
    }

    // Reset UI
    hideError();
    hideResults();
    showLoading();
    predictBtn.disabled = true;

    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                crime_description: crimeDescription
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        // Display results
        displayResults(data);

    } catch (err) {
        console.error('Prediction error:', err);
        showError(`Failed to predict sections: ${err.message}`);
        showEmptyState();
    } finally {
        hideLoading();
        predictBtn.disabled = false;
    }
}

// Display Results
function displayResults(data) {
    // Show refined description
    refinedDesc.textContent = data.refined_description;

    // Clear previous predictions
    predictions.innerHTML = '';

    // No predictions
    if (!data.predictions || data.predictions.length === 0) {
        predictions.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <p>No applicable BNS sections found.</p>
                <p class="text-sm mt-2">Try rephrasing the crime description.</p>
            </div>
        `;
        showResults();
        return;
    }

    // Render predictions
    data.predictions.forEach((pred, index) => {
        const predElement = createPredictionCard(pred, index);
        predictions.appendChild(predElement);
    });

    showResults();
}

// Create Prediction Card
function createPredictionCard(pred, index) {
    const card = document.createElement('div');
    card.className = 'border-l-4 p-4 rounded-lg transition-all hover:shadow-md';

    // Color coding by confidence
    const confidence = pred.confidence || 0;
    let borderColor = 'border-gray-400';
    let bgColor = 'bg-gray-50';
    let badgeColor = 'bg-gray-100 text-gray-800';

    if (confidence >= 0.9) {
        borderColor = 'border-green-500';
        bgColor = 'bg-green-50';
        badgeColor = 'bg-green-100 text-green-800';
    } else if (confidence >= 0.8) {
        borderColor = 'border-blue-500';
        bgColor = 'bg-blue-50';
        badgeColor = 'bg-blue-100 text-blue-800';
    } else if (confidence >= 0.7) {
        borderColor = 'border-yellow-500';
        bgColor = 'bg-yellow-50';
        badgeColor = 'bg-yellow-100 text-yellow-800';
    }

    card.className += ` ${borderColor} ${bgColor}`;

    // Rank badge
    const rankLabel = index === 0 ? 'Primary Offense' :
                      index === 1 ? 'Aggravating Factor' :
                      'Related Offense';

    card.innerHTML = `
        <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
                <span class="text-2xl font-bold text-gray-700">${index + 1}</span>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">
                        Section ${pred.section_number}
                    </h3>
                    <p class="text-sm text-gray-600 mt-1">${pred.section_title || 'N/A'}</p>
                </div>
            </div>
            <div class="text-right">
                <span class="${badgeColor} px-3 py-1 rounded-full text-xs font-semibold">
                    ${rankLabel}
                </span>
                <div class="text-sm font-semibold mt-2" style="color: ${getConfidenceColor(confidence)}">
                    ${(confidence * 100).toFixed(0)}% Confidence
                </div>
            </div>
        </div>

        <div class="mb-3">
            <p class="text-sm text-gray-700 leading-relaxed">
                <span class="font-semibold">Reasoning:</span> ${pred.reasoning || 'N/A'}
            </p>
        </div>

        <details class="mt-3">
            <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-800 font-medium">
                View Section Details
            </summary>
            <div class="mt-3 p-3 bg-white rounded border text-sm">
                <p class="text-gray-700 leading-relaxed">${pred.section_text || 'N/A'}</p>
                ${pred.metadata ? `
                    <div class="mt-3 flex gap-4 text-xs">
                        <span class="bg-gray-100 px-2 py-1 rounded">
                            Category: ${pred.metadata.category || 'N/A'}
                        </span>
                        <span class="bg-gray-100 px-2 py-1 rounded">
                            Severity: ${pred.metadata.severity || 'N/A'}
                        </span>
                    </div>
                ` : ''}
            </div>
        </details>
    `;

    return card;
}

// Get confidence color
function getConfidenceColor(confidence) {
    if (confidence >= 0.9) return '#059669'; // green
    if (confidence >= 0.8) return '#2563eb'; // blue
    if (confidence >= 0.7) return '#d97706'; // yellow
    return '#6b7280'; // gray
}

// Clear Input
function handleClear() {
    crimeInput.value = '';
    hideError();
    hideResults();
    showEmptyState();
    crimeInput.focus();
}

// UI Helper Functions
function showLoading() {
    loading.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showError(message) {
    error.classList.remove('hidden');
    errorMessage.textContent = message;
}

function hideError() {
    error.classList.add('hidden');
}

function showResults() {
    results.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function showEmptyState() {
    emptyState.classList.remove('hidden');
}

// Focus input on load
window.addEventListener('load', () => {
    crimeInput.focus();
});
