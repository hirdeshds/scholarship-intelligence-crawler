let allScholarships = [];
let currentStatusFilter = 'ALL';
let currentSourceFilter = 'ALL';
let currentSearchQuery = '';

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
});

async function loadDashboardData() {
    await fetchStats();
    await fetchScholarships();
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('stat-total').innerText = data.total_discovered || 0;
        document.getElementById('stat-verified').innerText = data.verified || 0;
        document.getElementById('stat-review').innerText = data.review_required || 0;
        document.getElementById('stat-active').innerText = data.active || 0;
        document.getElementById('stat-expired').innerText = data.expired || 0;
        document.getElementById('stat-updated').innerText = data.recently_updated || 0;
        document.getElementById('stat-confidence').innerText = (data.average_confidence || 0) + '%';
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

async function fetchScholarships() {
    try {
        let url = `/api/scholarships?`;
        if (currentStatusFilter !== 'ALL') url += `status=${encodeURIComponent(currentStatusFilter)}&`;
        if (currentSourceFilter !== 'ALL') url += `source_type=${encodeURIComponent(currentSourceFilter)}&`;
        if (currentSearchQuery) url += `q=${encodeURIComponent(currentSearchQuery)}&`;

        const response = await fetch(url);
        allScholarships = await response.json();
        renderTable(allScholarships);
    } catch (err) {
        console.error("Error fetching scholarships:", err);
    }
}

function renderTable(data) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">
                    No scholarships found matching criteria.
                </td>
            </tr>
        `;
        return;
    }

    data.forEach(item => {
        const tr = document.createElement('tr');
        
        let scoreClass = 'score-high';
        if (item.confidence_score < 80.0) scoreClass = 'score-low';
        else if (item.confidence_score < 95.0) scoreClass = 'score-medium';

        let badgeClass = 'badge-verified';
        if (item.status === 'REVIEW_REQUIRED') badgeClass = 'badge-review';
        else if (item.status === 'EXPIRED') badgeClass = 'badge-expired';

        tr.innerHTML = `
            <td>
                <div style="font-weight: 600; color: var(--text-primary);">${item.name}</div>
                <div style="font-size: 11px; color: var(--text-muted); font-family: monospace;">ID #${item.id}</div>
            </td>
            <td>${item.provider}</td>
            <td><span class="source-tag">${item.source_type}</span></td>
            <td style="color: var(--accent-green); font-weight: 600;">${item.amount}</td>
            <td style="font-size: 13px;">${item.closing_date}</td>
            <td>
                <span class="score-badge ${scoreClass}">${item.confidence_score}%</span>
            </td>
            <td>
                <span class="badge ${badgeClass}">${item.status}</span>
            </td>
            <td>
                <button class="btn btn-outline" style="padding: 6px 12px; font-size: 12px;" onclick="openDetailsModal(${item.id})">
                    <i class="fa-solid fa-eye"></i> Details
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setStatusFilter(status) {
    currentStatusFilter = status;
    updatePillActiveState('status-pills', status);
    fetchScholarships();
}

function setSourceFilter(source) {
    currentSourceFilter = source;
    updatePillActiveState('source-pills', source);
    fetchScholarships();
}

function updatePillActiveState(groupId, targetValue) {
    const container = document.getElementById(groupId);
    const pills = container.querySelectorAll('.pill');
    pills.forEach(pill => {
        if (pill.innerText.trim().toUpperCase() === targetValue.toUpperCase() || 
            (targetValue === 'ALL' && pill.innerText.includes('All'))) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
    });
}

function handleSearch() {
    currentSearchQuery = document.getElementById('search-input').value;
    fetchScholarships();
}

async function triggerCrawl() {
    const btn = document.getElementById('btn-crawl');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Crawling...`;

    try {
        const response = await fetch('/api/crawl', { method: 'POST' });
        const res = await response.json();
        await loadDashboardData();
    } catch (err) {
        console.error("Crawl failed:", err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Run Crawler Cycle`;
    }
}

async function triggerSeed() {
    const btn = document.getElementById('btn-seed');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Resetting...`;

    try {
        const response = await fetch('/api/seed', { method: 'POST' });
        const res = await response.json();
        await loadDashboardData();
    } catch (err) {
        console.error("Seed failed:", err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-rotate-left"></i> Reset Seed Data`;
    }
}

async function openDetailsModal(id) {
    try {
        const response = await fetch(`/api/scholarships/${id}`);
        const data = await response.json();

        document.getElementById('modal-title').innerText = data.name;
        document.getElementById('modal-provider').innerText = `${data.provider} • Source: ${data.source_type}`;

        const body = document.getElementById('modal-body-content');
        
        let reasonsHtml = '';
        if (data.confidence_reasons && data.confidence_reasons.length > 0) {
            reasonsHtml = data.confidence_reasons.map(r => `
                <div class="reason-item">
                    <i class="fa-solid ${r.passed ? 'fa-check-circle reason-pass' : 'fa-times-circle reason-fail'}"></i>
                    <span>[+${r.weight}%] ${r.description}</span>
                </div>
            `).join('');
        }

        let changesHtml = '<tr><td colspan="5" style="color: var(--text-muted);">No modifications detected yet.</td></tr>';
        if (data.change_history && data.change_history.length > 0) {
            changesHtml = data.change_history.map(c => `
                <tr>
                    <td style="font-weight: 600; color: var(--accent-indigo);">${c.field_name}</td>
                    <td style="color: var(--accent-rose);">${c.old_value || 'None'}</td>
                    <td style="color: var(--accent-green);">${c.new_value}</td>
                    <td>${c.date_detected}</td>
                    <td style="font-size: 11px;">${c.evidence_text || 'Source verified'}</td>
                </tr>
            `).join('');
        }

        body.innerHTML = `
            <div class="score-explanation-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 12px; color: var(--text-muted); uppercase;">System Verification Score</span>
                        <h3 style="font-size: 24px; color: ${data.confidence_score >= 95 ? 'var(--accent-green)' : 'var(--accent-amber)'};">
                            ${data.confidence_score}% Confidence
                        </h3>
                    </div>
                    <span class="badge ${data.status === 'VERIFIED' ? 'badge-verified' : (data.status === 'EXPIRED' ? 'badge-expired' : 'badge-review')}">
                        ${data.status}
                    </span>
                </div>
                <h4>Why this score? (Evidence-Based Rule Assessment)</h4>
                <div>${reasonsHtml}</div>
            </div>

            <div style="display: flex; gap: 12px; margin-bottom: 8px;">
                <a href="${data.official_source_url}" target="_blank" class="btn btn-outline" style="font-size: 12px;">
                    <i class="fa-solid fa-external-link"></i> Official Primary Source URL
                </a>
                ${data.application_url && data.application_url !== 'Not specified' ? `
                    <a href="${data.application_url}" target="_blank" class="btn btn-primary" style="font-size: 12px;">
                        <i class="fa-solid fa-paper-plane"></i> Direct Application Link
                    </a>
                ` : ''}
            </div>

            <div class="detail-grid">
                <div class="detail-item"><div class="detail-label">Scholarship Benefit</div><div class="detail-value">${data.amount}</div></div>
                <div class="detail-item"><div class="detail-label">Closing Deadline</div><div class="detail-value">${data.closing_date}</div></div>
                <div class="detail-item full-width"><div class="detail-label">Eligibility Summary</div><div class="detail-value">${data.eligibility}</div></div>
                <div class="detail-item"><div class="detail-label">Academic Requirements</div><div class="detail-value">${data.academic_reqs}</div></div>
                <div class="detail-item"><div class="detail-label">Course / Level</div><div class="detail-value">${data.course_level}</div></div>
                <div class="detail-item"><div class="detail-label">Income Criteria</div><div class="detail-value">${data.income_criteria}</div></div>
                <div class="detail-item"><div class="detail-label">Age Limit</div><div class="detail-value">${data.age_criteria}</div></div>
                <div class="detail-item"><div class="detail-label">Gender Criteria</div><div class="detail-value">${data.gender_criteria}</div></div>
                <div class="detail-item"><div class="detail-label">Category Eligibility</div><div class="detail-value">${data.category_criteria}</div></div>
                <div class="detail-item"><div class="detail-label">Domicile Requirement</div><div class="detail-value">${data.domicile_reqs}</div></div>
                <div class="detail-item"><div class="detail-label">Institution Requirement</div><div class="detail-value">${data.institution_reqs}</div></div>
                <div class="detail-item full-width"><div class="detail-label">Documents Required</div><div class="detail-value">${data.documents_req}</div></div>
                <div class="detail-item full-width"><div class="detail-label">Selection Process</div><div class="detail-value">${data.selection_process}</div></div>
            </div>

            <div>
                <h4 style="font-size: 13px; color: var(--text-secondary); margin-bottom: 6px;">Traceable Source Evidence</h4>
                <div class="evidence-box">"${data.evidence_text}"</div>
            </div>

            <div>
                <h4 style="font-size: 13px; color: var(--text-secondary); margin-bottom: 6px;">Change Detection History Audit Trail</h4>
                <table class="audit-table">
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Old Value</th>
                            <th>New Value</th>
                            <th>Date Detected</th>
                            <th>Evidence</th>
                        </tr>
                    </thead>
                    <tbody>${changesHtml}</tbody>
                </table>
            </div>
        `;

        document.getElementById('detail-modal').classList.add('active');
    } catch (err) {
        console.error("Failed to fetch scholarship details:", err);
    }
}

function closeModal() {
    document.getElementById('detail-modal').classList.remove('active');
}
