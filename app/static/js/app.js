// Global variables for charts and data
let guideChart = null;
let currentResults = null;
let currentChartType = 'scatter';
let currentData = null

// FASTA handling utils
const FASTA_UTILS = {
    isValidFastaFormat: function(text) {
        if (!text.startsWith('>')) return false;
        const lines = text.trim().split('\n');
        let hasSequence = false;
        
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line && !line.startsWith('>')) {
                hasSequence = true;
                break;
            }
        }
        return hasSequence;
    },

    parseFasta: function(fastaText) {
        const sequences = [];
        const lines = fastaText.trim().split('\n');
        let currentHeader = '';
        let currentSequence = '';
        let lineNumber = 0;

        try {
            lines.forEach((line, index) => {
                lineNumber = index + 1;
                line = line.trim();

                if (line.startsWith('>')) {
                    // Save previous sequence if exists
                    if (currentHeader && currentSequence) {
                        sequences.push({
                            header: currentHeader,
                            sequence: currentSequence,
                            length: currentSequence.length,
                            gc_content: this.calculateGCContent(currentSequence)
                        });
                    }
                    currentHeader = line.substring(1).trim();
                    currentSequence = '';
                } else if (line) {
                    // Validate sequence characters
                    const invalidChars = line.toUpperCase().match(/[^ATGCN]/g);
                    if (invalidChars) {
                        throw new Error(`Invalid characters found on line ${lineNumber}: ${invalidChars.join(', ')}`);
                    }
                    currentSequence += line.toUpperCase();
                }
            });

            // Add the last sequence
            if (currentHeader && currentSequence) {
                sequences.push({
                    header: currentHeader,
                    sequence: currentSequence,
                    length: currentSequence.length,
                    gc_content: this.calculateGCContent(currentSequence)
                });
            }

            return {
                success: true,
                sequences: sequences,
                summary: {
                    totalSequences: sequences.length,
                    averageLength: this.calculateAverageLength(sequences),
                    averageGC: this.calculateAverageGC(sequences)
                }
            };

        } catch (error) {
            return {
                success: false,
                error: error.message,
                lineNumber: lineNumber
            };
        }
    },

    calculateGCContent: function(sequence) {
        const gcCount = (sequence.match(/[GC]/g) || []).length;
        return ((gcCount / sequence.length) * 100).toFixed(2);
    },

    calculateAverageLength: function(sequences) {
        const total = sequences.reduce((sum, seq) => sum + seq.length, 0);
        return Math.round(total / sequences.length);
    },

    calculateAverageGC: function(sequences) {
        const total = sequences.reduce((sum, seq) => sum + parseFloat(seq.gc_content), 0);
        return (total / sequences.length).toFixed(2);
    }
};

// DOM Elements
const form = document.getElementById('analysisForm');
const helpToggle = document.getElementById('helpToggle');
const helpText = document.getElementById('helpText');
const errorAlert = document.getElementById('errorAlert');
const errorText = document.getElementById('errorText');
const resultsSection = document.getElementById('results');
const downloadBtn = document.getElementById('downloadBtn');

// Toggle help text
helpToggle.addEventListener('click', () => {
    helpText.classList.toggle('hidden');
});

// Format guide toggle
document.getElementById('formatToggle').addEventListener('click', () => {
    document.getElementById('formatGuide').classList.toggle('hidden');
});

// Sequence validation
function validateSequence(sequence) {
    const validBases = new Set(['A', 'T', 'G', 'C', 'N']);
    return sequence.split('').every(base => validBases.has(base.toUpperCase()));
}

// Loading CRISPR systems on page load
async function loadSystems() {
    try {
        const response = await fetch('/systems');
        const data = await response.json();
        const systemSelect = document.getElementById('system');
        
        Object.entries(data.systems).forEach(([key, value]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${key} - ${value.description}`;
            systemSelect.appendChild(option);
        });
    } catch (error) {
        showError('Failed to load CRISPR systems');
    }
}

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const sequenceInput = document.getElementById('sequence').value;
    const system = document.getElementById('system').value;
    
    // Process sequence (handle both FASTA and regular format)
    let sequence = sequenceInput;
    if (sequenceInput.startsWith('>')) {
        const result = FASTA_UTILS.parseFasta(sequenceInput);
        if (!result.success) {
            showError(result.error);
            return;
        }
        // Using the first sequence by default
        sequence = result.sequences[0].sequence;
    }

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Analyzing...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sequence, system }),
        });
        
        const result = await response.json();
        
        if (result.error) {
            showError(result.error);
        } else {
            hideError();
            currentResults = result.data;
            displayResults(result.data);
            downloadBtn.classList.remove('hidden');
        }
    } catch (error) {
        showError('An error occurred while analyzing the sequence');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

// Handle sequence input
document.getElementById('sequence').addEventListener('input', function(e) {
    const input = e.target.value.trim();
    
    if (input.startsWith('>')) {
        const result = FASTA_UTILS.parseFasta(input);
        if (result.success) {
            hideError();
        } else {
            showError(result.error);
        }
    } else {
        if (validateSequence(input)) {
            hideError();
        } else {
            showError('Invalid sequence format. Please use only A, T, G, C, or N.');
        }
    }
});

// Download results
downloadBtn.addEventListener('click', () => {
    if (!currentResults) return;
    
    const blob = new Blob([JSON.stringify(currentResults, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'crispr_analysis_results.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Display results
function displayResults(data) {
    resultsSection.classList.remove('hidden');
    
    // Display statistics
    const stats = data.statistics;
    document.getElementById('statistics').innerHTML = `
        <div class="p-4 bg-gray-50 rounded-lg">
            <h3 class="font-semibold text-gray-700">Total Guides</h3>
            <p class="text-2xl font-bold text-gray-900">${stats.total_guides}</p>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
            <h3 class="font-semibold text-gray-700">Average GC Content</h3>
            <p class="text-2xl font-bold text-gray-900">${stats.average_gc}%</p>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
            <h3 class="font-semibold text-gray-700">Average Efficiency</h3>
            <p class="text-2xl font-bold text-gray-900">${stats.average_efficiency}</p>
        </div>
    `;
    
    // Update chart
    updateChart(data.visualization_data);
    
    // Display guide list
    const guideList = document.getElementById('guideList');
    guideList.innerHTML = data.guides.map(guide => `
        <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${guide.sequence}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${guide.position}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${guide.pam}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${guide.gc_content.toFixed(1)}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${guide.efficiency_score}</td>
        </tr>
    `).join('');
}

// Update chart
function updateChart(visualizationData) {
    const ctx = document.getElementById('guideChart').getContext('2d');
    
    if (guideChart) {
        guideChart.destroy();
    }
    
    guideChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Guide Efficiency vs Position',
                data: visualizationData.positions.map((pos, i) => ({
                    x: pos,
                    y: visualizationData.scores[i]
                })),
                backgroundColor: 'rgba(17, 24, 39, 0.5)',  // gray-900 with transparency
                borderColor: 'rgba(17, 24, 39, 1)'        // gray-900
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Position in Sequence'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Efficiency Score'
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Error handling
function showError(message) {
    errorText.textContent = message;
    errorAlert.classList.remove('hidden');
}

function hideError() {
    errorAlert.classList.add('hidden');
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    loadSystems();
});