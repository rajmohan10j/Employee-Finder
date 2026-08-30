// ==========================================================================
// Candidate Tracker - Interactive Application Engine
// ==========================================================================

const API_BASE = '/api';

const state = {
    candidates: [],
    currentCandidate: null,
    reviewers: [],
    pendingReviews: [],
    stats: {},
    networkInfo: null,
    activeTab: 'candidates',
    theme: localStorage.getItem('app-theme') || 'dark-theme',
    zoom: parseFloat(localStorage.getItem('app-zoom')) || 1.0
};

// DOM Elements
const elements = {
    // Nav & Tabs
    navItems: document.querySelectorAll('.nav-item, .bottom-nav-item'),
    tabPanels: document.querySelectorAll('.tab-panel'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),

    // Size Controls
    btnSizeDown: document.getElementById('btn-size-down'),
    btnSizeReset: document.getElementById('btn-size-reset'),
    btnSizeUp: document.getElementById('btn-size-up'),
    
    // Stats
    statTotal: document.getElementById('stat-total'),
    statCalled: document.getElementById('stat-called'),
    statPendingCall: document.getElementById('stat-pending-call'),
    statClosed: document.getElementById('stat-closed'),
    statFollowups: document.getElementById('stat-followups'),
    statReviews: document.getElementById('stat-reviews'),
    statEscalated: document.getElementById('stat-escalated'),
    badgeTotalCandidates: document.getElementById('badge-total-candidates'),
    badgePendingReviews: document.getElementById('badge-pending-reviews'),
    dotPendingReviews: document.getElementById('dot-pending-reviews'),
    
    // Candidates List & Filter
    candidatesList: document.getElementById('candidates-list'),
    searchInput: document.getElementById('search-input'),
    btnClearSearch: document.getElementById('btn-clear-search'),
    filterStatus: document.getElementById('filter-status'),
    filterPortal: document.getElementById('filter-portal'),
    filterEscalation: document.getElementById('filter-escalation'),
    resultsCountText: document.getElementById('results-count-text'),
    
    // Review Stage & Reviewers
    reviewsList: document.getElementById('reviews-list'),
    reviewersList: document.getElementById('reviewers-list'),
    
    // Modals
    modalCandidateForm: document.getElementById('modal-candidate-form'),
    candidateForm: document.getElementById('candidate-form'),
    formModalTitle: document.getElementById('form-modal-title'),
    btnCloseCandidateModal: document.getElementById('btn-close-candidate-modal'),
    btnCancelCandidate: document.getElementById('btn-cancel-candidate'),
    btnStageReview: document.getElementById('btn-stage-review'),
    btnModalQuickClose: document.getElementById('btn-modal-quick-close'),
    
    modalShare: document.getElementById('modal-share'),
    sharePreviewText: document.getElementById('share-preview-text'),
    btnCloseShareModal: document.getElementById('btn-close-share-modal'),
    btnShareWhatsapp: document.getElementById('btn-share-whatsapp'),
    btnShareEmail: document.getElementById('btn-share-email'),
    btnShareCopy: document.getElementById('btn-share-copy'),
    btnShareCandidateModal: document.getElementById('btn-share-candidate-modal'),
    
    modalReviewerForm: document.getElementById('modal-reviewer-form'),
    reviewerForm: document.getElementById('reviewer-form'),
    btnAddReviewer: document.getElementById('btn-add-reviewer'),
    btnCloseReviewerModal: document.getElementById('btn-close-reviewer-modal'),
    btnCancelReviewer: document.getElementById('btn-cancel-reviewer'),

    // Import Excel Modal
    modalImportExcel: document.getElementById('modal-import-excel'),
    btnHeaderImport: document.getElementById('btn-header-import'),
    btnToolbarImport: document.getElementById('btn-toolbar-import'),
    btnSidebarImport: document.getElementById('btn-sidebar-import'),
    btnCloseImportModal: document.getElementById('btn-close-import-modal'),
    btnCancelImport: document.getElementById('btn-cancel-import'),
    btnSubmitImport: document.getElementById('btn-submit-import'),
    importFileInput: document.getElementById('import-file-input'),
    importModeSelect: document.getElementById('import-mode-select'),
    
    // Filters
    filterStatus: document.getElementById('filter-status'),
    filterPortal: document.getElementById('filter-portal'),
    filterEscalation: document.getElementById('filter-escalation'),
    
    // Buttons & Inputs
    btnAddCandidate: document.getElementById('btn-add-candidate'),
    btnRefresh: document.getElementById('btn-refresh'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    btnExportExcel: document.getElementById('btn-export-excel'),
    
    // Mobile QR
    mobileUrlInput: document.getElementById('mobile-url-input'),
    btnCopyUrl: document.getElementById('btn-copy-url'),
    qrcodeContainer: document.getElementById('qrcode-container'),
    
    // Candidate Form Fields
    fieldRowId: document.getElementById('field-row-id'),
    fieldCandidateName: document.getElementById('field-candidate-name'),
    fieldPortalSource: document.getElementById('field-portal-source'),
    fieldOpenToWork: document.getElementById('field-open-to-work'),
    fieldPhone: document.getElementById('field-phone'),
    fieldEmail: document.getElementById('field-email'),
    fieldLocation: document.getElementById('field-location'),
    fieldExperience: document.getElementById('field-experience'),
    fieldPdfFile: document.getElementById('field-pdf-file'),
    fieldResumeFile: document.getElementById('field-resume-file'),
    fieldProcessedTimestamp: document.getElementById('field-processed-timestamp'),
    fieldHrCalled: document.getElementById('field-hr-called'),
    fieldCallDate: document.getElementById('field-call-date'),
    fieldHrRemarks: document.getElementById('field-hr-remarks'),
    fieldFollowupDate: document.getElementById('field-followup-date'),
    fieldFollowupRemarks: document.getElementById('field-followup-remarks'),
    fieldEscalationLevel: document.getElementById('field-escalation-level'),
    fieldEscalationAction: document.getElementById('field-escalation-action'),
    fieldEscalationRemarks: document.getElementById('field-escalation-remarks'),
    fieldSubmitterName: document.getElementById('field-submitter-name'),
    fieldAssignReviewer: document.getElementById('field-assign-reviewer'),
    
    // Form Action Buttons
    btnQuickCall: document.getElementById('btn-quick-call'),
    btnQuickWa: document.getElementById('btn-quick-wa'),
    btnQuickEmail: document.getElementById('btn-quick-email'),
    btnViewPdf: document.getElementById('btn-view-pdf'),
    btnViewResume: document.getElementById('btn-view-resume'),
    
    // Toast Container
    toastContainer: document.getElementById('toast-container')
};

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(state.theme);
    applyZoom(state.zoom);
    setupEventListeners();
    fetchAllData();
    fetchNetworkInfo();
});

function applyTheme(theme) {
    state.theme = theme;
    document.body.className = theme;
    localStorage.setItem('app-theme', theme);
    if (elements.btnThemeToggle) {
        elements.btnThemeToggle.innerHTML = theme === 'dark-theme' 
            ? '<i class="fa-solid fa-sun"></i>' 
            : '<i class="fa-solid fa-moon"></i>';
    }
}

function applyZoom(zoom) {
    state.zoom = Math.min(1.4, Math.max(0.75, Math.round(zoom * 100) / 100));
    document.documentElement.style.setProperty('--app-zoom', state.zoom);
    localStorage.setItem('app-zoom', state.zoom);
    if (elements.btnSizeReset) {
        elements.btnSizeReset.querySelector('span').textContent = `${Math.round(state.zoom * 100)}%`;
    }
}

function setupEventListeners() {
    // Size Controls (Reduce / Increase text & box sizes)
    if (elements.btnSizeDown) {
        elements.btnSizeDown.addEventListener('click', () => {
            applyZoom(state.zoom - 0.1);
            showToast(`Scale reduced to ${Math.round(state.zoom * 100)}%`, 'info');
        });
    }

    if (elements.btnSizeUp) {
        elements.btnSizeUp.addEventListener('click', () => {
            applyZoom(state.zoom + 0.1);
            showToast(`Scale increased to ${Math.round(state.zoom * 100)}%`, 'info');
        });
    }

    if (elements.btnSizeReset) {
        elements.btnSizeReset.addEventListener('click', () => {
            applyZoom(1.0);
            showToast('Scale reset to 100%', 'info');
        });
    }

    // Navigation Tabs
    elements.navItems.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });

    // Theme Toggle
    elements.btnThemeToggle.addEventListener('click', () => {
        applyTheme(state.theme === 'dark-theme' ? 'light-theme' : 'dark-theme');
    });

    // Refresh Data
    elements.btnRefresh.addEventListener('click', () => {
        fetchAllData(true);
    });

    // Export Excel
    elements.btnExportExcel.addEventListener('click', () => {
        window.location.href = `${API_BASE}/export`;
        showToast('Exporting master Excel tracker...', 'info');
    });

    // Import Excel Modal triggers
    const openImportModal = () => {
        elements.importFileInput.value = '';
        elements.modalImportExcel.style.display = 'flex';
    };
    const closeImportModal = () => {
        elements.modalImportExcel.style.display = 'none';
    };

    if (elements.btnHeaderImport) elements.btnHeaderImport.addEventListener('click', openImportModal);
    if (elements.btnToolbarImport) elements.btnToolbarImport.addEventListener('click', openImportModal);
    if (elements.btnSidebarImport) elements.btnSidebarImport.addEventListener('click', openImportModal);
    if (elements.btnCloseImportModal) elements.btnCloseImportModal.addEventListener('click', closeImportModal);
    if (elements.btnCancelImport) elements.btnCancelImport.addEventListener('click', closeImportModal);
    if (elements.btnSubmitImport) elements.btnSubmitImport.addEventListener('click', handleExcelImport);

    // Search and Filters
    let searchDebounce = null;
    elements.searchInput.addEventListener('input', () => {
        const hasVal = elements.searchInput.value.trim().length > 0;
        elements.btnClearSearch.style.display = hasVal ? 'block' : 'none';
        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(fetchCandidates, 250);
    });

    elements.btnClearSearch.addEventListener('click', () => {
        elements.searchInput.value = '';
        elements.btnClearSearch.style.display = 'none';
        fetchCandidates();
    });

    elements.filterStatus.addEventListener('change', fetchCandidates);
    elements.filterPortal.addEventListener('change', fetchCandidates);
    if (elements.filterEscalation) {
        elements.filterEscalation.addEventListener('change', fetchCandidates);
    }

    // Candidate Form Open / Close
    elements.btnAddCandidate.addEventListener('click', () => openCandidateModal(null));
    elements.btnCloseCandidateModal.addEventListener('click', closeCandidateModal);
    elements.btnCancelCandidate.addEventListener('click', closeCandidateModal);
    
    // Dynamic Call Date requirement & auto-prefill on HR Called change
    const callDateRequiredIndicator = document.getElementById('call-date-required');
    if (elements.fieldHrCalled) {
        elements.fieldHrCalled.addEventListener('change', () => {
            const val = (elements.fieldHrCalled.value || '').trim().toLowerCase();
            const isCalled = val.startsWith('yes');
            if (callDateRequiredIndicator) {
                callDateRequiredIndicator.style.display = isCalled ? 'inline' : 'none';
            }
            if (isCalled) {
                // Auto-prefill today's date if empty
                if (!elements.fieldCallDate.value) {
                    elements.fieldCallDate.value = new Date().toISOString().split('T')[0];
                }
                // If marked Not Interested, suggest updating Open To Work
                if (val.includes('not interested')) {
                    if (elements.fieldOpenToWork && (elements.fieldOpenToWork.value === 'Actively Looking' || elements.fieldOpenToWork.value === 'Yes')) {
                        elements.fieldOpenToWork.value = 'Not Interested';
                    }
                }
            } else {
                elements.fieldCallDate.classList.remove('input-error');
            }
        });
    }

    if (elements.fieldCallDate) {
        elements.fieldCallDate.addEventListener('input', () => {
            if (elements.fieldCallDate.value) {
                elements.fieldCallDate.classList.remove('input-error');
            }
        });
    }

    // Direct Save (Default)
    elements.candidateForm.addEventListener('submit', (e) => {
        e.preventDefault();
        saveCandidateData(false);
    });

    // Staging / Submit for Review
    if (elements.btnStageReview) {
        elements.btnStageReview.addEventListener('click', () => {
            saveCandidateData(true);
        });
    }

    // Modal Quick Close (Not Interested)
    if (elements.btnModalQuickClose) {
        elements.btnModalQuickClose.addEventListener('click', async () => {
            const rowId = elements.fieldRowId.value;
            if (!rowId) {
                elements.fieldHrCalled.value = 'Closed - Not Interested';
                elements.fieldOpenToWork.value = 'Closed - Not Interested';
                if (!elements.fieldCallDate.value) {
                    elements.fieldCallDate.value = new Date().toISOString().split('T')[0];
                }
                if (!elements.fieldHrRemarks.value) {
                    elements.fieldHrRemarks.value = 'Candidate Not Interested / Closed';
                }
                showToast('Form marked as Closed / Not Interested. Click Save to create record.', 'info');
                return;
            }
            const name = elements.fieldCandidateName.value || 'Candidate';
            await window.handleQuickClose(rowId, name);
            closeCandidateModal();
        });
    }

    // Share Modals
    elements.btnCloseShareModal.addEventListener('click', closeShareModal);
    elements.btnShareCopy.addEventListener('click', handleShareCopy);
    elements.btnShareWhatsapp.addEventListener('click', handleShareWhatsApp);
    elements.btnShareEmail.addEventListener('click', handleShareEmail);
    elements.btnShareCandidateModal.addEventListener('click', () => {
        if (state.currentCandidate) {
            openShareModal(state.currentCandidate);
        } else {
            const tempCand = collectFormData();
            openShareModal(tempCand);
        }
    });

    // Quick contact buttons in candidate form
    if (elements.btnQuickCall) {
        elements.btnQuickCall.addEventListener('click', () => {
            const phone = elements.fieldPhone.value.trim();
            if (phone && phone !== 'Masked by Portal' && !phone.includes('Masked')) {
                window.open(`tel:${phone.replace(/[^0-9+]/g, '')}`);
            } else {
                showToast('No valid direct phone number available', 'error');
            }
        });
    }

    if (elements.btnQuickWa) {
        elements.btnQuickWa.addEventListener('click', () => {
            const phone = elements.fieldPhone.value.trim();
            const candName = elements.fieldCandidateName.value.trim();
            if (phone && phone !== 'Masked by Portal' && !phone.includes('Masked')) {
                const clean = phone.replace(/[^0-9]/g, '');
                const msg = encodeURIComponent(`Hi ${candName}, I am contacting you regarding an exciting career opportunity.`);
                window.open(`https://wa.me/${clean}?text=${msg}`, '_blank');
            } else {
                showToast('No valid direct phone number available for WhatsApp', 'error');
            }
        });
    }

    if (elements.btnQuickEmail) {
        elements.btnQuickEmail.addEventListener('click', () => {
            const email = elements.fieldEmail.value.trim();
            const candName = elements.fieldCandidateName.value.trim();
            if (email) {
                const subject = encodeURIComponent(`Career Opportunity - Discussion with ${candName}`);
                const body = encodeURIComponent(`Hi ${candName},\n\nWe came across your profile and would love to connect with you regarding job opportunities.\n\nBest regards,\nRaj`);
                window.open(`mailto:${email}?subject=${subject}&body=${body}`);
            } else {
                showToast('No valid email address entered', 'error');
            }
        });
    }

    if (elements.btnViewPdf) {
        elements.btnViewPdf.addEventListener('click', () => {
            const pdf = elements.fieldPdfFile.value.trim();
            if (pdf) {
                window.open(`${API_BASE}/resumes/${encodeURIComponent(pdf)}`, '_blank');
            } else {
                showToast('No PDF file name specified', 'error');
            }
        });
    }

    if (elements.btnViewResume) {
        elements.btnViewResume.addEventListener('click', () => {
            const res = elements.fieldResumeFile.value.trim();
            if (res) {
                window.open(`${API_BASE}/resumes/${encodeURIComponent(res)}`, '_blank');
            } else {
                showToast('No Resume file name specified', 'error');
            }
        });
    }

    // Reviewer Management
    if (elements.btnAddReviewer) elements.btnAddReviewer.addEventListener('click', openReviewerModal);
    if (elements.btnCloseReviewerModal) elements.btnCloseReviewerModal.addEventListener('click', closeReviewerModal);
    if (elements.btnCancelReviewer) elements.btnCancelReviewer.addEventListener('click', closeReviewerModal);
    if (elements.reviewerForm) elements.reviewerForm.addEventListener('submit', handleReviewerSave);

    // Copy Mobile URL
    if (elements.btnCopyUrl) {
        elements.btnCopyUrl.addEventListener('click', () => {
            const url = elements.mobileUrlInput.value;
            navigator.clipboard.writeText(url).then(() => {
                showToast('Mobile URL copied to clipboard!', 'success');
            });
        });
    }
}

function switchTab(tab) {
    state.activeTab = tab;
    
    // Update Nav states
    elements.navItems.forEach(item => {
        if (item.dataset.tab === tab) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update Panels
    elements.tabPanels.forEach(panel => {
        if (panel.id === `tab-${tab}`) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });

    const titles = {
        candidates: { title: 'Candidate Master Tracker', sub: 'Real-time box item editor and master database synchronization' },
        reviews: { title: 'Review & Commit Stage', sub: 'Audit and approve candidate changes before updating master Excel' },
        reviewers: { title: 'Reviewer Contact Registry', sub: 'Manage reviewers, team leads and designated stakeholders' },
        mobile: { title: 'Connect Android Phone', sub: 'Scan QR code to access full tracker app on mobile device' }
    };

    if (titles[tab]) {
        elements.pageTitle.textContent = titles[tab].title;
        elements.pageSubtitle.textContent = titles[tab].sub;
    }
}

// ==========================================================================
// API Calls & Data Fetching
// ==========================================================================
async function fetchAllData(showNotification = false) {
    try {
        await Promise.all([
            fetchStats(),
            fetchCandidates(),
            fetchReviewers(),
            fetchPendingReviews()
        ]);
        if (showNotification) {
            showToast('Data refreshed successfully from master Excel', 'success');
        }
    } catch (err) {
        showToast(`Error refreshing data: ${err.message}`, 'error');
    }
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        state.stats = data;

        if (elements.statTotal) elements.statTotal.textContent = data.total_candidates ?? data.total ?? 0;
        if (elements.statCalled) elements.statCalled.textContent = data.called_count ?? data.called ?? 0;
        if (elements.statPendingCall) elements.statPendingCall.textContent = data.pending_call_count ?? data.pending_call ?? 0;
        if (elements.statClosed) elements.statClosed.textContent = data.closed_count ?? 0;
        if (elements.statFollowups) elements.statFollowups.textContent = data.follow_ups_count ?? data.follow_ups ?? 0;
        if (elements.statReviews) elements.statReviews.textContent = data.pending_reviews_count ?? data.pending_reviews ?? 0;
        if (elements.statEscalated) elements.statEscalated.textContent = data.escalated_count ?? 0;

        if (elements.badgeTotalCandidates) elements.badgeTotalCandidates.textContent = data.total_candidates ?? data.total ?? 0;
        if (elements.badgePendingReviews) elements.badgePendingReviews.textContent = data.pending_reviews_count ?? 0;
        if (elements.dotPendingReviews) elements.dotPendingReviews.style.display = (data.pending_reviews_count > 0) ? 'block' : 'none';
    } catch (err) {
        console.error('Stats error:', err);
    }
}

async function fetchCandidates() {
    const query = elements.searchInput.value.trim();
    const status = elements.filterStatus.value;
    const portal = elements.filterPortal.value;
    const escalation = elements.filterEscalation ? elements.filterEscalation.value : 'All';

    const params = new URLSearchParams({ query, status, portal, escalation });
    try {
        const res = await fetch(`${API_BASE}/candidates?${params.toString()}`);
        const data = await res.json();
        if (data.success) {
            state.candidates = data.candidates;
            renderCandidatesList(data.candidates);
        }
    } catch (err) {
        showToast('Failed to load candidates', 'error');
    }
}

async function fetchReviewers() {
    try {
        const res = await fetch(`${API_BASE}/reviewers`);
        const data = await res.json();
        if (data.success) {
            state.reviewers = data.reviewers;
            renderReviewersList(data.reviewers);
            populateReviewerDropdown(data.reviewers);
        }
    } catch (err) {
        console.error('Reviewers error:', err);
    }
}

async function fetchPendingReviews() {
    try {
        const res = await fetch(`${API_BASE}/pending_reviews`);
        const data = await res.json();
        if (data.success) {
            state.pendingReviews = data.reviews;
            renderPendingReviews(data.reviews);
        }
    } catch (err) {
        console.error('Pending reviews error:', err);
    }
}

async function fetchNetworkInfo() {
    try {
        const res = await fetch(`${API_BASE}/network_info`);
        const data = await res.json();
        if (data.success) {
            state.networkInfo = data;
            const primaryUrl = data.primary_url;
            elements.mobileUrlInput.value = primaryUrl;
            
            elements.qrcodeContainer.innerHTML = '';
            new QRCode(elements.qrcodeContainer, {
                text: primaryUrl,
                width: 190,
                height: 190,
                colorDark: '#0b0f17',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.M
            });
        }
    } catch (err) {
        elements.mobileUrlInput.value = window.location.origin;
    }
}

// ==========================================================================
// Excel Import Logic
// ==========================================================================
async function handleExcelImport() {
    const file = elements.importFileInput.files[0];
    if (!file) {
        showToast('Please choose a .xlsx or .xls file to import', 'error');
        return;
    }

    const mode = elements.importModeSelect.value;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);

    elements.btnSubmitImport.disabled = true;
    elements.btnSubmitImport.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Importing...';

    try {
        const res = await fetch(`${API_BASE}/import`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message || `Imported ${data.imported_count} candidates successfully!`, 'success');
            elements.modalImportExcel.style.display = 'none';
            fetchAllData();
        } else {
            showToast(`Import error: ${data.error}`, 'error');
        }
    } catch (err) {
        showToast(`Failed to upload file: ${err.message}`, 'error');
    } finally {
        elements.btnSubmitImport.disabled = false;
        elements.btnSubmitImport.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Upload & Import Now';
    }
}

// ==========================================================================
// Rendering Candidates UI
// ==========================================================================
function renderCandidatesList(candidates) {
    elements.resultsCountText.textContent = `Showing ${candidates.length} candidates from master Excel tracker`;
    
    if (candidates.length === 0) {
        elements.candidatesList.innerHTML = `
            <div class="empty-state box-span-2" style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);">
                <i class="fa-solid fa-user-slash" style="font-size: 32px; margin-bottom: 12px; opacity:0.5;"></i>
                <p>No matching candidate records found.</p>
            </div>
        `;
        return;
    }

    elements.candidatesList.innerHTML = candidates.map(c => {
        const hrCalledRaw = (c['HR Called'] || '').trim();
        const openToWorkRaw = (c['Open To Work / Active'] || '').trim();
        const isNotInterested = hrCalledRaw.toLowerCase().includes('not interested') || openToWorkRaw.toLowerCase().includes('not interested') || hrCalledRaw.toLowerCase().includes('closed') || openToWorkRaw.toLowerCase().includes('closed');
        const isCalled = hrCalledRaw.toLowerCase().startsWith('yes') && !isNotInterested;
        
        let statusClass = 'pill-pending';
        let statusText = hrCalledRaw || 'Not Called';
        if (isNotInterested) {
            statusClass = 'pill-not-interested';
            statusText = 'Closed (Not Interested)';
        } else if (isCalled) {
            statusClass = 'pill-called';
            statusText = 'Called (Yes)';
        } else if (hrCalledRaw.toLowerCase().includes('busy') || hrCalledRaw.toLowerCase().includes('call later') || hrCalledRaw.toLowerCase().includes('call back')) {
            statusClass = 'pill-not-reachable';
            statusText = 'Busy / Call Later';
        } else if (hrCalledRaw.toLowerCase().includes('not reachable') || hrCalledRaw.toLowerCase().includes('rnr') || hrCalledRaw.toLowerCase().includes('not connected')) {
            statusClass = 'pill-not-reachable';
            statusText = 'Not Reachable';
        }

        const phone = c['Phone Number'] || 'Not provided';
        const isPhoneMasked = phone.includes('Masked') || phone.includes('Indeed');
        const email = c['Email'] || 'Not provided';
        const exp = c['Total Experience'] || 'Not specified';
        const loc = c['Location'] || 'Not specified';
        const portal = c['Portal Source'] || 'Other';
        const remarks = c['HR Remarks'] || c['HR Follow-up Remarks'] || '';

        const escLevel = (c['Escalation Level / Person'] || '').trim();
        const escAction = (c['Escalation Action Category'] || '').trim();
        const escRemarks = (c['Escalation Remarks'] || '').trim();
        const hasEscalation = escLevel && !escLevel.toLowerCase().includes('none') && escLevel !== '';

        let escBadgeClass = 'badge-escalation';
        if (escLevel.startsWith('L1')) escBadgeClass = 'badge-escalation badge-escalation-l1';
        else if (escLevel.startsWith('L2')) escBadgeClass = 'badge-escalation badge-escalation-l2';
        else if (escLevel.startsWith('L3')) escBadgeClass = 'badge-escalation badge-escalation-l3';
        else if (escLevel.startsWith('L4')) escBadgeClass = 'badge-escalation badge-escalation-l4';

        return `
            <div class="candidate-card" data-row-id="${c._row_id}" onclick="openCandidateModal(${c._row_id})" style="cursor: pointer;">
                <div class="card-top">
                    <h3 class="card-candidate-name">${escapeHtml(c['Candidate Name'] || 'Unnamed Candidate')}</h3>
                    <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                        ${hasEscalation ? `
                            <span class="${escBadgeClass}" onclick="event.stopPropagation(); quickOpenEscalation(${c._row_id})" title="Task Assigned to ${escapeHtml(escLevel)} (${escapeHtml(escAction)}) - Click to edit">
                                <i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(escLevel.split(' - ')[0] || escLevel)}: ${escapeHtml(escAction || 'Action')}
                            </span>
                        ` : `
                            <button type="button" class="btn-quick-esc" onclick="event.stopPropagation(); quickOpenEscalation(${c._row_id})" title="Click to Assign Task / Escalate to L1, L2, L3, or L4">
                                <i class="fa-solid fa-bolt"></i> Assign Task
                            </button>
                        `}
                        <span class="card-portal-badge">${escapeHtml(portal)}</span>
                    </div>
                </div>

                <div class="card-info-list">
                    <div class="card-info-row">
                        <i class="fa-solid fa-phone"></i>
                        <span>${escapeHtml(phone)}</span>
                    </div>
                    <div class="card-info-row">
                        <i class="fa-solid fa-envelope"></i>
                        <span>${escapeHtml(email)}</span>
                    </div>
                    <div class="card-info-row">
                        <i class="fa-solid fa-location-dot"></i>
                        <span>${escapeHtml(loc)}</span>
                    </div>
                    <div class="card-info-row">
                        <i class="fa-solid fa-briefcase"></i>
                        <span>Exp: ${escapeHtml(exp)} | ${escapeHtml(c['Open To Work / Active'] || 'Active')}</span>
                    </div>
                </div>

                ${remarks ? `
                    <div class="card-remarks-box">
                        <strong>HR Notes:</strong> ${escapeHtml(remarks)}
                    </div>
                ` : ''}

                ${hasEscalation ? `
                    <div class="card-escalation-box">
                        <strong>⚡ Task / Assigned To: ${escapeHtml(escLevel)} [${escapeHtml(escAction || 'Action Req')}]:</strong> ${escapeHtml(escRemarks || 'Action details required')}
                    </div>
                ` : ''}

                <div class="card-status-row">
                    <span class="status-pill ${statusClass}">
                        <i class="fa-solid ${isNotInterested ? 'fa-ban' : (isCalled ? 'fa-circle-check' : 'fa-clock')}"></i>
                        ${escapeHtml(statusText)}
                    </span>

                    <div class="card-actions">
                        ${!isNotInterested ? `
                            <button class="btn-card-action btn-action-close" style="color:#ef4444;" onclick="event.stopPropagation(); handleQuickClose(${c._row_id}, '${escapeHtml(c['Candidate Name'])}')" title="1-Click Mark Closed (Not Interested)">
                                <i class="fa-solid fa-ban"></i>
                            </button>
                        ` : ''}
                        ${!isPhoneMasked ? `
                            <button class="btn-card-action call" onclick="event.stopPropagation(); triggerCall('${escapeHtml(phone)}')" title="Direct Phone Call">
                                <i class="fa-solid fa-phone"></i>
                            </button>
                            <button class="btn-card-action wa" onclick="event.stopPropagation(); triggerWhatsApp('${escapeHtml(phone)}', '${escapeHtml(c['Candidate Name'])}')" title="Send WhatsApp">
                                <i class="fa-brands fa-whatsapp"></i>
                            </button>
                        ` : ''}
                        <button class="btn-card-action" onclick="event.stopPropagation(); openShareModalByRowId(${c._row_id})" title="Share with Lead / Next Level">
                            <i class="fa-solid fa-share-nodes"></i>
                        </button>
                        <button class="btn-card-action" onclick="event.stopPropagation(); openCandidateModal(${c._row_id})" title="Edit Box Items">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

window.triggerCall = function(phone) {
    if (phone && !phone.includes('Masked')) {
        window.open(`tel:${phone.replace(/[^0-9+]/g, '')}`);
    } else {
        showToast('Phone number is masked or unavailable', 'error');
    }
};

window.triggerWhatsApp = function(phone, name) {
    if (phone && !phone.includes('Masked')) {
        const clean = phone.replace(/[^0-9]/g, '');
        const msg = encodeURIComponent(`Hi ${name}, I am reaching out regarding an opportunity with our team.`);
        window.open(`https://wa.me/${clean}?text=${msg}`, '_blank');
    } else {
        showToast('Direct phone number is masked or unavailable', 'error');
    }
};

window.openShareModalByRowId = function(rowId) {
    const cand = state.candidates.find(c => c._row_id == rowId);
    if (cand) openShareModal(cand);
};

window.handleQuickClose = async function(rowId, name) {
    if (!confirm(`Mark "${name}" as Closed / Not Interested?\n\nThis will update Excel and set status to Closed immediately.`)) {
        return;
    }
    try {
        const res = await fetch(`${API_BASE}/candidates/${rowId}/quick_close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: 'Candidate Not Interested / Closed via 1-click' })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Marked "${name}" as Closed / Not Interested!`, 'success');
            fetchAllData(false);
        } else {
            showToast(`Error closing candidate: ${data.error}`, 'error');
        }
    } catch (err) {
        showToast(`Failed to update status: ${err.message}`, 'error');
    }
};

window.quickOpenEscalation = function(rowId) {
    openCandidateModal(rowId);
    setTimeout(() => {
        if (elements.fieldEscalationLevel) {
            elements.fieldEscalationLevel.scrollIntoView({ behavior: 'smooth', block: 'center' });
            elements.fieldEscalationLevel.focus();
        }
    }, 200);
};

// ==========================================================================
// Box Item Form Editor Logic
// ==========================================================================
window.openCandidateModal = function(rowId) {
    state.currentCandidate = rowId ? state.candidates.find(c => c._row_id == rowId) : null;
    
    elements.formModalTitle.textContent = state.currentCandidate 
        ? `Edit Candidate (Row #${rowId})` 
        : 'Add New Candidate to Master Database';

    if (state.currentCandidate) {
        const c = state.currentCandidate;
        elements.fieldRowId.value = c._row_id;
        elements.fieldCandidateName.value = c['Candidate Name'] || '';
        elements.fieldPortalSource.value = c['Portal Source'] || '';
        elements.fieldOpenToWork.value = c['Open To Work / Active'] || 'Actively Looking';
        elements.fieldPhone.value = c['Phone Number'] || '';
        elements.fieldEmail.value = c['Email'] || '';
        elements.fieldLocation.value = c['Location'] || '';
        elements.fieldExperience.value = c['Total Experience'] || '';
        elements.fieldPdfFile.value = c['PDF File Name'] || '';
        elements.fieldResumeFile.value = c['Resume File Name'] || '';
        elements.fieldProcessedTimestamp.value = c['Processed Timestamp'] || '';
        elements.fieldHrCalled.value = c['HR Called'] || 'Pending';
        elements.fieldCallDate.value = c['Date'] || '';
        elements.fieldHrRemarks.value = c['HR Remarks'] || '';
        elements.fieldFollowupDate.value = c['Follow-up Date'] || '';
        elements.fieldFollowupRemarks.value = c['HR Follow-up Remarks'] || '';
        if (elements.fieldEscalationLevel) elements.fieldEscalationLevel.value = c['Escalation Level / Person'] || 'None / No Escalation';
        if (elements.fieldEscalationAction) elements.fieldEscalationAction.value = c['Escalation Action Category'] || 'None';
        if (elements.fieldEscalationRemarks) elements.fieldEscalationRemarks.value = c['Escalation Remarks'] || '';
        elements.fieldAssignReviewer.value = 'Direct Commit';
    } else {
        elements.candidateForm.reset();
        elements.fieldRowId.value = '';
        elements.fieldProcessedTimestamp.value = new Date().toISOString().replace('T', ' ').substring(0, 19);
        if (elements.fieldEscalationLevel) elements.fieldEscalationLevel.value = 'None / No Escalation';
        if (elements.fieldEscalationAction) elements.fieldEscalationAction.value = 'None';
        if (elements.fieldEscalationRemarks) elements.fieldEscalationRemarks.value = '';
        elements.fieldAssignReviewer.value = 'Direct Commit';
    }

    // Reset validation styles & update required indicator
    if (elements.fieldCallDate) {
        elements.fieldCallDate.classList.remove('input-error');
    }
    const isCalled = (elements.fieldHrCalled.value || '').trim().toLowerCase().startsWith('yes');
    const callDateRequiredIndicator = document.getElementById('call-date-required');
    if (callDateRequiredIndicator) {
        callDateRequiredIndicator.style.display = isCalled ? 'inline' : 'none';
    }
    if (isCalled && !elements.fieldCallDate.value) {
        elements.fieldCallDate.value = new Date().toISOString().split('T')[0];
    }

    elements.modalCandidateForm.style.display = 'flex';
}

function closeCandidateModal() {
    elements.modalCandidateForm.style.display = 'none';
    state.currentCandidate = null;
}

function collectFormData() {
    return {
        'Candidate Name': elements.fieldCandidateName.value.trim(),
        'Phone Number': elements.fieldPhone.value.trim(),
        'Email': elements.fieldEmail.value.trim(),
        'Location': elements.fieldLocation.value.trim(),
        'Total Experience': elements.fieldExperience.value.trim(),
        'Open To Work / Active': elements.fieldOpenToWork.value,
        'Portal Source': elements.fieldPortalSource.value.trim(),
        'PDF File Name': elements.fieldPdfFile.value.trim(),
        'Processed Timestamp': elements.fieldProcessedTimestamp.value.trim(),
        'Resume File Name': elements.fieldResumeFile.value.trim(),
        'HR Called': elements.fieldHrCalled.value,
        'Date': elements.fieldCallDate.value,
        'HR Remarks': elements.fieldHrRemarks.value.trim(),
        'Follow-up Date': elements.fieldFollowupDate.value,
        'HR Follow-up Remarks': elements.fieldFollowupRemarks.value.trim(),
        'Escalation Level / Person': elements.fieldEscalationLevel ? elements.fieldEscalationLevel.value : 'None / No Escalation',
        'Escalation Action Category': elements.fieldEscalationAction ? elements.fieldEscalationAction.value : 'None',
        'Escalation Remarks': elements.fieldEscalationRemarks ? elements.fieldEscalationRemarks.value.trim() : '',
        '_submitted_by': elements.fieldSubmitterName.value.trim() || 'Raj',
        '_reviewer_assigned': elements.fieldAssignReviewer.value
    };
}

async function saveCandidateData(isStageForReview = false) {
    const hrCalledVal = (elements.fieldHrCalled.value || '').trim().toLowerCase();
    const isCalledYes = hrCalledVal.startsWith('yes');
    
    // MANDATORY VALIDATION: If HR Called is Yes, Call Date MUST be filled
    if (isCalledYes && !elements.fieldCallDate.value.trim()) {
        elements.fieldCallDate.classList.add('input-error');
        showToast('⚠️ Call Date is mandatory when HR Called is "Yes"! Please select the Call Date.', 'warning');
        elements.fieldCallDate.scrollIntoView({ behavior: 'smooth', block: 'center' });
        elements.fieldCallDate.focus();
        return;
    }
    elements.fieldCallDate.classList.remove('input-error');

    const rowId = elements.fieldRowId.value;
    const formData = collectFormData();

    try {
        let res;
        if (rowId) {
            // Update existing candidate
            res = await fetch(`${API_BASE}/candidates/${rowId}?stage_for_review=${isStageForReview}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            // Add new candidate
            res = await fetch(`${API_BASE}/candidates`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }

        const data = await res.json();
        if (data.success) {
            if (data.staged) {
                showToast('Changes submitted for Review & Approval', 'info');
            } else {
                showToast('Candidate changes saved directly to master Excel database!', 'success');
            }
            closeCandidateModal();
            fetchAllData();
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (err) {
        showToast(`Failed to save: ${err.message}`, 'error');
    }
}

// ==========================================================================
// Share / Next Level Workflow
// ==========================================================================
let currentShareSummary = '';

function openShareModal(cand) {
    const summary = generateShareSummary(cand);
    currentShareSummary = summary;
    elements.sharePreviewText.textContent = summary;
    elements.modalShare.style.display = 'flex';
}

function closeShareModal() {
    elements.modalShare.style.display = 'none';
}

function generateShareSummary(c) {
    const escLevel = (c['Escalation Level / Person'] || '').trim();
    const escAction = (c['Escalation Action Category'] || '').trim();
    const escRemarks = (c['Escalation Remarks'] || '').trim();
    const hasEsc = escLevel && !escLevel.toLowerCase().includes('none') && escLevel !== '';

    return `📌 *CANDIDATE PROFILE SUMMARY*
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 *Name/Role*: ${c['Candidate Name'] || 'N/A'}
📱 *Phone*: ${c['Phone Number'] || 'N/A'}
✉️ *Email*: ${c['Email'] || 'N/A'}
📍 *Location*: ${c['Location'] || 'N/A'}
💼 *Experience*: ${c['Total Experience'] || 'N/A'}
🌐 *Source*: ${c['Portal Source'] || 'N/A'} (${c['Open To Work / Active'] || 'Active'})

📞 *HR Status*: ${c['HR Called'] || 'Pending'}
📝 *HR Remarks*: ${c['HR Remarks'] || 'None'}
⏰ *Follow-up Date*: ${c['Follow-up Date'] || 'None'}
${c['HR Follow-up Remarks'] ? `📌 *Follow-up Note*: ${c['HR Follow-up Remarks']}\n` : ''}${hasEsc ? `⚡ *Task / Assigned To*: ${escLevel}\n📋 *Action Required*: ${escAction || 'Review'}\n${escRemarks ? `💬 *Action Details*: ${escRemarks}\n` : ''}` : ''}━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 *Shared via CandidateTracker System*`;
}

function handleShareCopy() {
    navigator.clipboard.writeText(currentShareSummary).then(() => {
        showToast('Candidate summary copied to clipboard!', 'success');
    });
}

function handleShareWhatsApp() {
    const encoded = encodeURIComponent(currentShareSummary);
    window.open(`https://wa.me/?text=${encoded}`, '_blank');
}

function handleShareEmail() {
    const subject = encodeURIComponent(`Candidate Profile Review - Next Level Escalation`);
    const body = encodeURIComponent(currentShareSummary);
    window.open(`mailto:?subject=${subject}&body=${body}`);
}

// ==========================================================================
// Review & Commit Workflow UI
// ==========================================================================
function renderPendingReviews(reviews) {
    const pending = reviews.filter(r => r.status === 'pending');
    
    if (pending.length === 0) {
        elements.reviewsList.innerHTML = `
            <div class="empty-state" style="text-align:center; padding: 40px; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
                <i class="fa-solid fa-circle-check" style="font-size: 36px; margin-bottom: 12px; color: var(--success); opacity:0.8;"></i>
                <h3>All Caught Up!</h3>
                <p>There are no pending changes awaiting review. All updates are committed to the master Excel file.</p>
            </div>
        `;
        return;
    }

    elements.reviewsList.innerHTML = pending.map(r => {
        const diffRows = Object.entries(r.diffs || {}).map(([k, v]) => `
            <tr>
                <td style="font-weight:600; width:30%;">${escapeHtml(k)}</td>
                <td style="width:35%;"><span class="diff-old">${escapeHtml(v.old || '(Empty)')}</span></td>
                <td style="width:35%;"><span class="diff-new">${escapeHtml(v.new || '(Empty)')}</span></td>
            </tr>
        `).join('');

        return `
            <div class="review-item-card" data-review-id="${r.id}">
                <div class="review-header">
                    <div>
                        <h3 style="font-size: 16px; font-weight:700;">${escapeHtml(r.candidate_name)}</h3>
                        <p class="text-muted" style="font-size: 12px;">
                            Submitted by <strong>${escapeHtml(r.submitted_by)}</strong> | Assigned Reviewer: <strong>${escapeHtml(r.reviewer_assigned)}</strong> | ${escapeHtml(r.timestamp)}
                        </p>
                    </div>
                    <span class="status-pill pill-pending">Pending Approval</span>
                </div>

                <table class="diff-table">
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Current Value</th>
                            <th>Proposed Update</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${diffRows}
                    </tbody>
                </table>

                <div class="modal-footer" style="padding: 12px 0 0 0; border-top: 1px solid var(--border-color);">
                    <button class="btn btn-secondary btn-sm" onclick="handleReviewAction('${r.id}', 'reject')">
                        <i class="fa-solid fa-xmark"></i> Reject
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="handleReviewAction('${r.id}', 'approve')">
                        <i class="fa-solid fa-check"></i> Approve & Commit to Excel
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

window.handleReviewAction = async function(reviewId, action) {
    try {
        const res = await fetch(`${API_BASE}/commit_review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ review_id: reviewId, action: action, reviewed_by: 'Raj (Admin)' })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, action === 'approve' ? 'success' : 'info');
            fetchAllData();
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (err) {
        showToast(`Failed action: ${err.message}`, 'error');
    }
};

// ==========================================================================
// Reviewers Contacts UI
// ==========================================================================
function renderReviewersList(reviewers) {
    if (reviewers.length === 0) {
        elements.reviewersList.innerHTML = `
            <div class="empty-state box-span-2" style="text-align:center; padding: 40px; color: var(--text-muted);">
                <p>No reviewer contacts registered yet.</p>
            </div>
        `;
        return;
    }

    elements.reviewersList.innerHTML = reviewers.map(r => `
        <div class="reviewer-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h3 style="font-size: 16px; font-weight:700;">${escapeHtml(r.name)}</h3>
                    <span style="font-size:12px; color:var(--primary); font-weight:600;">${escapeHtml(r.role || 'Reviewer')}</span>
                </div>
                <button class="btn-card-action" onclick="deleteReviewer('${r.id}')" title="Delete Reviewer" style="color:var(--danger);">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
            <div class="card-info-list" style="margin-top: 6px;">
                <div class="card-info-row">
                    <i class="fa-solid fa-phone"></i>
                    <span>${escapeHtml(r.phone)}</span>
                </div>
                <div class="card-info-row">
                    <i class="fa-solid fa-envelope"></i>
                    <span>${escapeHtml(r.email)}</span>
                </div>
            </div>
            <div style="display:flex; gap:6px; margin-top: 8px;">
                <button class="btn btn-secondary btn-sm w-full" onclick="triggerCall('${escapeHtml(r.phone)}')">
                    <i class="fa-solid fa-phone"></i> Call
                </button>
                <button class="btn btn-whatsapp btn-sm w-full" onclick="triggerWhatsApp('${escapeHtml(r.phone)}', '${escapeHtml(r.name)}')">
                    <i class="fa-brands fa-whatsapp"></i> WA
                </button>
            </div>
        </div>
    `).join('');
}

function populateReviewerDropdown(reviewers) {
    let options = '<option value="Direct Commit">None (Direct Save to Excel)</option>';
    reviewers.forEach(r => {
        options += `<option value="${escapeHtml(r.name)} (${escapeHtml(r.role)})">${escapeHtml(r.name)} - ${escapeHtml(r.role)}</option>`;
    });
    elements.fieldAssignReviewer.innerHTML = options;
}

function openReviewerModal() {
    elements.reviewerForm.reset();
    elements.modalReviewerForm.style.display = 'flex';
}

function closeReviewerModal() {
    elements.modalReviewerForm.style.display = 'none';
}

async function handleReviewerSave(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('rev-name').value.trim(),
        phone: document.getElementById('rev-phone').value.trim(),
        email: document.getElementById('rev-email').value.trim(),
        role: document.getElementById('rev-role').value.trim()
    };

    try {
        const res = await fetch(`${API_BASE}/reviewers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const resp = await res.json();
        if (resp.success) {
            showToast('Reviewer contact added successfully', 'success');
            closeReviewerModal();
            fetchReviewers();
        } else {
            showToast(`Error: ${resp.error}`, 'error');
        }
    } catch (err) {
        showToast(`Failed: ${err.message}`, 'error');
    }
}

window.deleteReviewer = async function(revId) {
    if (!confirm('Are you sure you want to remove this reviewer contact?')) return;
    try {
        const res = await fetch(`${API_BASE}/reviewers/${revId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('Reviewer removed', 'info');
            fetchReviewers();
        }
    } catch (err) {
        showToast('Failed to delete reviewer', 'error');
    }
};

// ==========================================================================
// Helper Utilities
// ==========================================================================
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        info: 'fa-circle-info'
    };
    
    toast.innerHTML = `
        <i class="fa-solid ${icons[type] || 'fa-bell'}"></i>
        <span>${escapeHtml(message)}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
