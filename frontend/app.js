let currentExtractionResult = null;

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
});

async function checkHealth() {
    try {
        const res = await fetch('/api/v1/health');
        const data = await res.json();
        document.getElementById('provider-info').innerText = `Provider: ${data.llm_provider.toUpperCase()} (${data.model_name})`;
    } catch (e) {
        document.getElementById('system-status').innerText = '● Engine Offline';
        document.getElementById('system-status').style.color = '#ef4444';
    }
}

function setupEventListeners() {
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    const dropZone = document.getElementById('drop-zone');
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    // Download JSON
    document.getElementById('download-json-btn').addEventListener('click', () => {
        if (!currentExtractionResult) return;
        const blob = new Blob([JSON.stringify(currentExtractionResult, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `qms_${currentExtractionResult.document_metadata.filename.replace('.pdf', '')}.json`;
        a.click();
    });
}

async function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Please select a valid PDF file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    document.getElementById('loading-container').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');

    try {
        const res = await fetch('/api/v1/policies/extract', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        currentExtractionResult = data;
        renderDashboard(data);
    } catch (e) {
        alert(`Extraction Error: ${e.message}`);
    } finally {
        document.getElementById('loading-container').classList.add('hidden');
    }
}

function renderDashboard(data) {
    document.getElementById('dashboard').classList.remove('hidden');

    // Metrics Card
    document.getElementById('insurer-name').innerText = data.insurer_details.insurer_name || 'Not Inferred';
    document.getElementById('tpa-name').innerText = data.insurer_details.tpa_name || 'Direct / None';
    document.getElementById('policy-number').innerText = data.policy_metadata.policy_number || 'N/A';
    document.getElementById('policyholder-name').innerText = data.policy_metadata.policyholder_name || 'N/A';
    
    const start = data.policy_metadata.start_date || '?';
    const end = data.policy_metadata.end_date || '?';
    document.getElementById('policy-period').innerText = `${start} to ${end}`;
    
    const confPct = Math.round((data.extraction_metadata.overall_confidence || 0) * 100);
    document.getElementById('overall-confidence').innerText = `${confPct}% Confidence`;

    // Render Benefit Grids
    renderBenefitGrid(data.hospitalization, 'hosp-grid');
    renderBenefitGrid(data.maternity, 'mat-grid');
    renderBenefitGrid(data.waiting_periods, 'wait-grid');
    renderBenefitGrid(data.other_benefits, 'other-grid');

    // Render Demographics
    renderDemographics(data.demographics, data.policy_structure, 'demo-container');

    // Render JSON
    document.getElementById('json-viewer').innerText = JSON.stringify(data, null, 2);
}

function renderBenefitGrid(benefitGroup, elementId) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';

    for (const [key, benefit] of Object.entries(benefitGroup)) {
        if (typeof benefit !== 'object' || !benefit.status) continue;

        const title = key.replace(/_/g, ' ').toUpperCase();
        const statusClass = `status-${benefit.status}`;
        
        let detailsText = benefit.conditions || 'No specific condition clauses parsed';
        if (benefit.percentage) detailsText = `Percentage: ${benefit.percentage}% SI | ` + detailsText;
        if (benefit.days) detailsText = `Duration: ${benefit.days} Days | ` + detailsText;

        const card = document.createElement('div');
        card.className = 'benefit-card';
        card.innerHTML = `
            <div>
                <div class="benefit-title">
                    <span>${title}</span>
                    <span class="status-tag ${statusClass}">${benefit.status}</span>
                </div>
                <div class="benefit-body">${detailsText}</div>
            </div>
            <div class="benefit-meta">
                <span>Conf: ${Math.round((benefit.confidence || 0) * 100)}%</span>
                <span class="evidence-link" onclick='showEvidence(${JSON.stringify(benefit.evidence || [])})'>
                    ${(benefit.evidence && benefit.evidence.length > 0) ? `Evidence (${benefit.evidence.length})` : 'No Evidence'}
                </span>
            </div>
        `;
        container.appendChild(card);
    }
}

function renderDemographics(demographics, structure, elementId) {
    const container = document.getElementById(elementId);
    container.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-box"><span class="metric-label">Employees Covered</span><span class="metric-value">${structure.employee_covered ? 'Yes' : 'No'} (${demographics.employees_count || 'N/A'})</span></div>
            <div class="metric-box"><span class="metric-label">Spouses Covered</span><span class="metric-value">${structure.spouse_covered ? 'Yes' : 'No'} (${demographics.spouses_count || 'N/A'})</span></div>
            <div class="metric-box"><span class="metric-label">Children Covered</span><span class="metric-value">${structure.children_covered ? 'Yes' : 'No'} (${demographics.children_count || 'N/A'})</span></div>
            <div class="metric-box"><span class="metric-label">Parents Covered</span><span class="metric-value">${structure.parents_covered ? 'Yes' : 'No'} (${demographics.parents_count || 'N/A'})</span></div>
            <div class="metric-box"><span class="metric-label">Total Lives Covered</span><span class="metric-value highlight">${demographics.total_lives_covered || 'Not Stated'}</span></div>
        </div>
    `;
}

function showEvidence(evidenceList) {
    const modal = document.getElementById('evidence-modal');
    const modalBody = document.getElementById('modal-body');
    if (!evidenceList || evidenceList.length === 0) {
        modalBody.innerHTML = '<p>No evidence text quote found in document for this field.</p>';
    } else {
        modalBody.innerHTML = evidenceList.map(ev => `
            <div style="background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem;">
                <strong style="color: var(--accent-cyan)">Page ${ev.page}:</strong>
                <p style="margin-top: 0.4rem; font-style: italic; color: var(--text-main)">"${ev.text}"</p>
            </div>
        `).join('');
    }
    modal.classList.remove('hidden');
}

function closeEvidenceModal() {
    document.getElementById('evidence-modal').classList.add('hidden');
}
