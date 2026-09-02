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
    statEscalationBreakdown: document.getElementById('stat-escalation-breakdown'),
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

    // Security Confirm Close Modal
    modalConfirmClose: document.getElementById('modal-confirm-close'),
    confirmCloseCandidateName: document.getElementById('confirm-close-candidate-name'),
    btnCancelConfirmClose: document.getElementById('btn-cancel-confirm-close'),
    btnCancelConfirmCloseX: document.getElementById('btn-cancel-confirm-close-x'),
    btnConfirmCloseExecute: document.getElementById('btn-confirm-close-execute'),
    
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
    fieldCurrentRole: document.getElementById('field-current-role'),
    fieldDomainIndustry: document.getElementById('field-domain-industry'),
    fieldEducation: document.getElementById('field-education'),
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
    // Audience Segmentation & Conversion Intelligence fields
    fieldAge: document.getElementById('field-age'),
    fieldEmploymentSector: document.getElementById('field-employment-sector'),
    fieldRetirementStatus: document.getElementById('field-retirement-status'),
    fieldCallResponse: document.getElementById('field-call-response'),
    fieldInterviewAgreed: document.getElementById('field-interview-agreed'),
    fieldAdvisoryInterest: document.getElementById('field-advisory-interest'),
    fieldSubmitterName: document.getElementById('field-submitter-name'),
    fieldAssignReviewer: document.getElementById('field-assign-reviewer'),
    // Analytics panel & Drilldown
    analyticsPanel: document.getElementById('tab-analytics'),
    modalAnalyticsDrilldown: document.getElementById('modal-analytics-drilldown'),
    btnCloseDrilldownModal: document.getElementById('btn-close-drilldown-modal'),
    drilldownTableBody: document.getElementById('drilldown-table-body'),
    drilldownSearchInput: document.getElementById('drilldown-search-input'),
    
    // Form Action Buttons
    btnQuickCall: document.getElementById('btn-quick-call'),
    btnQuickWa: document.getElementById('btn-quick-wa'),
    btnQuickEmail: document.getElementById('btn-quick-email'),
    btnViewPdf: document.getElementById('btn-view-pdf'),
    btnViewResume: document.getElementById('btn-view-resume'),
    // Backups & Versions
    btnHeaderBackup: document.getElementById('btn-header-backup'),
    btnRefreshBackups: document.getElementById('btn-refresh-backups'),
    btnTriggerManualBackup: document.getElementById('btn-trigger-manual-backup'),
    statBackupSessionsCount: document.getElementById('stat-backup-sessions-count'),
    statBackupSessionsLast: document.getElementById('stat-backup-sessions-last'),
    statBackupDailyCount: document.getElementById('stat-backup-daily-count'),
    statBackupDailyLast: document.getElementById('stat-backup-daily-last'),
    statBackupWeeklyCount: document.getElementById('stat-backup-weekly-count'),
    statBackupWeeklyLast: document.getElementById('stat-backup-weekly-last'),
    statBackupMonthlyCount: document.getElementById('stat-backup-monthly-count'),
    statBackupMonthlyLast: document.getElementById('stat-backup-monthly-last'),
    backupsTableBody: document.getElementById('backups-table-body'),
    backupsTableCount: document.getElementById('backups-table-count'),
    badgeBackupsCount: document.getElementById('badge-backups-count'),

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

    elements.filterStatus.addEventListener('change', () => {
        syncCardHighlightsFromDropdowns();
        fetchCandidates();
    });
    elements.filterPortal.addEventListener('change', fetchCandidates);
    if (elements.filterEscalation) {
        elements.filterEscalation.addEventListener('change', () => {
            syncCardHighlightsFromDropdowns();
            fetchCandidates();
        });
    }

    // Interactive Metric Cards click-to-filter
    initMetricCardFilters();

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

    // Modal Quick Close (Not Interested) - Opens Security Double-Confirmation
    if (elements.btnModalQuickClose) {
        elements.btnModalQuickClose.addEventListener('click', (e) => {
            e.preventDefault();
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
            window.handleQuickClose(rowId, name);
        });
    }

    // Security Confirm Close Modal Listeners
    if (elements.btnCancelConfirmClose) {
        elements.btnCancelConfirmClose.addEventListener('click', () => {
            window.closeConfirmCloseModal();
        });
    }
    if (elements.btnCancelConfirmCloseX) {
        elements.btnCancelConfirmCloseX.addEventListener('click', () => {
            window.closeConfirmCloseModal();
        });
    }
    if (elements.btnConfirmCloseExecute) {
        elements.btnConfirmCloseExecute.addEventListener('click', async () => {
            if (!state.pendingCloseCandidate) return;
            const { rowId, name } = state.pendingCloseCandidate;
            window.closeConfirmCloseModal();

            try {
                const res = await fetch(`${API_BASE}/candidates/${rowId}/quick_close`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason: 'Candidate Not Interested / Closed via 1-click' })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Marked "${name}" as Closed / Not Interested!`, 'success');
                    closeCandidateModal();
                    fetchAllData(false);
                } else {
                    showToast(`Error closing candidate: ${data.error}`, 'error');
                }
            } catch (err) {
                showToast(`Failed to update status: ${err.message}`, 'error');
            }
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

    // Backup Triggers
    if (elements.btnHeaderBackup) {
        elements.btnHeaderBackup.addEventListener('click', () => {
            triggerManualBackup('manual', 'header_checkpoint');
        });
    }
    if (elements.btnTriggerManualBackup) {
        elements.btnTriggerManualBackup.addEventListener('click', () => {
            triggerManualBackup('manual', 'manual_checkpoint');
        });
    }
    if (elements.btnRefreshBackups) {
        elements.btnRefreshBackups.addEventListener('click', () => {
            fetchBackups(false);
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
        analytics: { title: 'Conversion Intelligence Analytics', sub: 'Track response rates, interview agreements, and advisory role acceptance' },
        mobile: { title: 'Connect Android Phone', sub: 'Scan QR code to access full tracker app on mobile device' },
        backups: { title: 'Automated GFS Backups & Version Control', sub: 'Grandfather-Father-Son point-in-time recovery & version history' }
    };

    if (titles[tab]) {
        elements.pageTitle.textContent = titles[tab].title;
        elements.pageSubtitle.textContent = titles[tab].sub;
    }

    if (tab === 'backups') {
        fetchBackups(true);
    } else if (tab === 'mobile') {
        fetchNetworkInfo();
    } else if (tab === 'analytics') {
        loadAnalytics();
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
            fetchPendingReviews(),
            fetchBackups(true),
            fetchNetworkInfo()
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

        // Render dynamic Task / Assigned To Breakdown Chips (by Person & Level)
        renderEscalationBreakdownChips(data.escalation_breakdown || {});
    } catch (err) {
        console.error('Stats error:', err);
    }
}

function renderEscalationBreakdownChips(breakdown) {
    if (!elements.statEscalationBreakdown) return;
    const entries = Object.entries(breakdown);

    if (entries.length === 0) {
        elements.statEscalationBreakdown.innerHTML = '<span style="font-size:10px; color:var(--text-muted); font-style:italic;">No active tasks</span>';
        return;
    }

    elements.statEscalationBreakdown.innerHTML = entries.map(([personLevel, count]) => {
        let levelClass = 'chip-l1';
        if (personLevel.startsWith('L2')) levelClass = 'chip-l2';
        else if (personLevel.startsWith('L3')) levelClass = 'chip-l3';
        else if (personLevel.startsWith('L4')) levelClass = 'chip-l4';

        const shortName = personLevel.replace(' - ', ' • ');
        return `
            <span class="escalation-chip ${levelClass}" data-level="${escapeHtml(personLevel)}" title="Click to filter candidates assigned to ${escapeHtml(personLevel)}">
                <span>${escapeHtml(shortName)}</span>
                <span class="chip-count">${count}</span>
            </span>
        `;
    }).join('');

    // Attach click listeners to chips
    elements.statEscalationBreakdown.querySelectorAll('.escalation-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            e.stopPropagation();
            const levelVal = chip.dataset.level;
            const isAlreadyActive = chip.classList.contains('active-chip');

            // Reset other chips and cards
            document.querySelectorAll('.metric-card.interactive-card').forEach(c => c.classList.remove('active-filter-card'));
            elements.statEscalationBreakdown.querySelectorAll('.escalation-chip').forEach(ch => ch.classList.remove('active-chip'));

            if (isAlreadyActive) {
                // Toggle off -> reset escalation filter to All
                if (elements.filterEscalation) elements.filterEscalation.value = 'All';
            } else {
                const parentCard = document.getElementById('card-stat-escalated');
                if (parentCard) parentCard.classList.add('active-filter-card');
                chip.classList.add('active-chip');

                if (elements.filterEscalation) {
                    let matched = false;
                    for (let opt of elements.filterEscalation.options) {
                        if (opt.value.toLowerCase() === levelVal.toLowerCase() || opt.value.toLowerCase().includes(levelVal.toLowerCase())) {
                            elements.filterEscalation.value = opt.value;
                            matched = true;
                            break;
                        }
                    }
                    if (!matched) {
                        const newOpt = document.createElement('option');
                        newOpt.value = levelVal;
                        newOpt.textContent = levelVal;
                        elements.filterEscalation.appendChild(newOpt);
                        elements.filterEscalation.value = levelVal;
                    }
                }
                if (elements.filterStatus) elements.filterStatus.value = 'All';
            }

            switchTab('candidates');
            fetchCandidates();
        });
    });

    syncCardHighlightsFromDropdowns();
}

function initMetricCardFilters() {
    const cards = document.querySelectorAll('.metric-card.interactive-card');
    cards.forEach(card => {
        card.addEventListener('click', (e) => {
            // If clicked on an escalation breakdown chip, let the chip handler process it
            if (e.target.closest('.escalation-chip')) return;

            const filterType = card.dataset.filterType;
            const filterVal = card.dataset.filterVal;
            const isCurrentlyActive = card.classList.contains('active-filter-card');

            // Reset visual states
            cards.forEach(c => c.classList.remove('active-filter-card'));
            if (elements.statEscalationBreakdown) {
                elements.statEscalationBreakdown.querySelectorAll('.escalation-chip').forEach(ch => ch.classList.remove('active-chip'));
            }

            if (isCurrentlyActive && filterVal !== 'All') {
                // Toggle OFF -> reset to All
                if (elements.filterStatus) elements.filterStatus.value = 'All';
                if (elements.filterEscalation) elements.filterEscalation.value = 'All';
            } else {
                // Activate this card
                card.classList.add('active-filter-card');

                if (filterType === 'status') {
                    if (elements.filterStatus) elements.filterStatus.value = filterVal;
                    if (elements.filterEscalation) elements.filterEscalation.value = 'All';
                } else if (filterType === 'escalation') {
                    if (elements.filterEscalation) elements.filterEscalation.value = filterVal;
                    if (elements.filterStatus) elements.filterStatus.value = 'All';
                }
            }

            switchTab('candidates');
            fetchCandidates();
        });
    });
}

function syncCardHighlightsFromDropdowns() {
    const cards = document.querySelectorAll('.metric-card.interactive-card');
    cards.forEach(c => c.classList.remove('active-filter-card'));
    if (elements.statEscalationBreakdown) {
        elements.statEscalationBreakdown.querySelectorAll('.escalation-chip').forEach(ch => ch.classList.remove('active-chip'));
    }

    const statusVal = elements.filterStatus ? elements.filterStatus.value : 'All';
    const escVal = elements.filterEscalation ? elements.filterEscalation.value : 'All';

    if (escVal && escVal !== 'All' && escVal !== 'None') {
        const cardEsc = document.getElementById('card-stat-escalated');
        if (cardEsc) cardEsc.classList.add('active-filter-card');
        if (elements.statEscalationBreakdown) {
            elements.statEscalationBreakdown.querySelectorAll('.escalation-chip').forEach(ch => {
                if (ch.dataset.level && ch.dataset.level.toLowerCase() === escVal.toLowerCase()) {
                    ch.classList.add('active-chip');
                }
            });
        }
    } else if (statusVal && statusVal !== 'All') {
        const card = document.querySelector(`.metric-card.interactive-card[data-filter-val="${statusVal}"]`);
        if (card) card.classList.add('active-filter-card');
    }
}

async function fetchCandidates() {
    const query = elements.searchInput ? elements.searchInput.value.trim() : '';
    const status = elements.filterStatus ? elements.filterStatus.value : 'All';
    const portal = elements.filterPortal ? elements.filterPortal.value : 'All';
    const escalation = elements.filterEscalation ? elements.filterEscalation.value : 'All';

    syncCardHighlightsFromDropdowns();

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
    if (!elements.mobileUrlInput || !elements.qrcodeContainer) return;
    try {
        const res = await fetch(`${API_BASE}/network_info`);
        const data = await res.json();
        if (data.success) {
            state.networkInfo = data;
            let primaryUrl = data.primary_url;
            
            // If current browser host is already on LAN, prioritize current origin
            if (window.location.hostname !== '127.0.0.1' && window.location.hostname !== 'localhost' && window.location.port === '5000') {
                primaryUrl = window.location.origin;
            }

            elements.mobileUrlInput.value = primaryUrl;
            
            elements.qrcodeContainer.innerHTML = '';
            if (typeof QRCode !== 'undefined') {
                new QRCode(elements.qrcodeContainer, {
                    text: primaryUrl,
                    width: 190,
                    height: 190,
                    colorDark: '#0b0f17',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.M
                });
            }
        }
    } catch (err) {
        if (elements.mobileUrlInput) {
            elements.mobileUrlInput.value = window.location.origin;
        }
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

        const currentRole = c['Current Position / Role'] || '';
        const domainIndustry = c['Domain / Industry'] || '';
        const education = c['Education Background'] || '';

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
                    ${currentRole ? `
                        <div class="card-info-row" style="color:#93c5fd; font-weight:600;">
                            <i class="fa-solid fa-user-tie" style="color:#60a5fa;"></i>
                            <span>${escapeHtml(currentRole)}</span>
                        </div>
                    ` : ''}
                    ${domainIndustry ? `
                        <div class="card-info-row" style="color:#fde047;">
                            <i class="fa-solid fa-industry" style="color:#facc15;"></i>
                            <span>${escapeHtml(domainIndustry)}</span>
                        </div>
                    ` : ''}
                    ${education ? `
                        <div class="card-info-row" style="color:#c4b5fd;">
                            <i class="fa-solid fa-graduation-cap" style="color:#a78bfa;"></i>
                            <span>${escapeHtml(education)}</span>
                        </div>
                    ` : ''}
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

window.openConfirmCloseModal = function(rowId, name) {
    state.pendingCloseCandidate = { rowId, name };
    if (elements.confirmCloseCandidateName) {
        elements.confirmCloseCandidateName.textContent = name ? `"${name}"` : 'this candidate';
    }
    if (elements.modalConfirmClose) {
        elements.modalConfirmClose.style.display = 'flex';
    }
};

window.closeConfirmCloseModal = function() {
    state.pendingCloseCandidate = null;
    if (elements.modalConfirmClose) {
        elements.modalConfirmClose.style.display = 'none';
    }
};

window.handleQuickClose = function(rowId, name) {
    window.openConfirmCloseModal(rowId, name);
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
        if (elements.fieldCurrentRole) elements.fieldCurrentRole.value = c['Current Position / Role'] || '';
        if (elements.fieldDomainIndustry) elements.fieldDomainIndustry.value = c['Domain / Industry'] || '';
        if (elements.fieldEducation) elements.fieldEducation.value = c['Education Background'] || '';
        elements.fieldPdfFile.value = c['PDF File Name'] || '';
        elements.fieldResumeFile.value = c['Resume File Name'] || '';
        elements.fieldProcessedTimestamp.value = c['Processed Timestamp'] || '';
        elements.fieldHrCalled.value = c['HR Called'] || 'Pending';
        elements.fieldCallDate.value = c['Date'] || '';
        elements.fieldHrRemarks.value = c['HR Remarks'] || '';
        elements.fieldFollowupDate.value = c['Follow-up Date'] || '';
        if (elements.fieldEscalationLevel) {
            const rawLevel = (c['Escalation Level / Person'] || '').trim();
            let matched = false;
            if (rawLevel) {
                for (let opt of elements.fieldEscalationLevel.options) {
                    if (opt.value.toLowerCase() === rawLevel.toLowerCase() || 
                        opt.value.toLowerCase().startsWith(rawLevel.toLowerCase()) || 
                        rawLevel.toLowerCase().startsWith(opt.value.toLowerCase().split(' - ')[0])) {
                        elements.fieldEscalationLevel.value = opt.value;
                        matched = true;
                        break;
                    }
                }
            }
            if (!matched) elements.fieldEscalationLevel.value = rawLevel || 'None / No Escalation';
        }

        if (elements.fieldEscalationAction) {
            const rawAction = (c['Escalation Action Category'] || '').trim();
            let matchedAction = false;
            if (rawAction) {
                for (let opt of elements.fieldEscalationAction.options) {
                    if (opt.value.toLowerCase() === rawAction.toLowerCase()) {
                        elements.fieldEscalationAction.value = opt.value;
                        matchedAction = true;
                        break;
                    }
                }
            }
            if (!matchedAction) elements.fieldEscalationAction.value = rawAction || 'None';
        }

        if (elements.fieldEscalationRemarks) elements.fieldEscalationRemarks.value = c['Escalation Remarks'] || '';
        // Audience Segmentation (P1/P2) & Conversion Intelligence fields
        if (elements.fieldAge) elements.fieldAge.value = c['Age'] || '';
        if (elements.fieldEmploymentSector) elements.fieldEmploymentSector.value = c['Employment Sector'] || '';
        if (elements.fieldRetirementStatus) elements.fieldRetirementStatus.value = c['Retirement Status'] || '';
        if (elements.fieldCallResponse) elements.fieldCallResponse.value = c['Call Response'] || '';
        if (elements.fieldInterviewAgreed) elements.fieldInterviewAgreed.value = c['Interview / Meeting Agreed'] || '';
        if (elements.fieldAdvisoryInterest) elements.fieldAdvisoryInterest.value = c['Advisory Role Interest'] || '';
        elements.fieldAssignReviewer.value = 'Direct Commit';
    } else {
        elements.candidateForm.reset();
        elements.fieldRowId.value = '';
        if (elements.fieldCurrentRole) elements.fieldCurrentRole.value = '';
        if (elements.fieldDomainIndustry) elements.fieldDomainIndustry.value = '';
        if (elements.fieldEducation) elements.fieldEducation.value = '';
        if (elements.fieldAge) elements.fieldAge.value = '';
        if (elements.fieldEmploymentSector) elements.fieldEmploymentSector.value = '';
        if (elements.fieldRetirementStatus) elements.fieldRetirementStatus.value = '';
        elements.fieldProcessedTimestamp.value = new Date().toISOString().replace('T', ' ').substring(0, 19);
        if (elements.fieldEscalationLevel) elements.fieldEscalationLevel.value = 'None / No Escalation';
        if (elements.fieldEscalationAction) elements.fieldEscalationAction.value = 'None';
        if (elements.fieldEscalationRemarks) elements.fieldEscalationRemarks.value = '';
        if (elements.fieldCallResponse) elements.fieldCallResponse.value = '';
        if (elements.fieldInterviewAgreed) elements.fieldInterviewAgreed.value = '';
        if (elements.fieldAdvisoryInterest) elements.fieldAdvisoryInterest.value = '';
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
        'Current Position / Role': elements.fieldCurrentRole ? elements.fieldCurrentRole.value.trim() : '',
        'Domain / Industry': elements.fieldDomainIndustry ? elements.fieldDomainIndustry.value.trim() : '',
        'Education Background': elements.fieldEducation ? elements.fieldEducation.value.trim() : '',
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
        'Age': elements.fieldAge ? elements.fieldAge.value.trim() : '',
        'Employment Sector': elements.fieldEmploymentSector ? elements.fieldEmploymentSector.value : '',
        'Retirement Status': elements.fieldRetirementStatus ? elements.fieldRetirementStatus.value : '',
        'Call Response': elements.fieldCallResponse ? elements.fieldCallResponse.value : '',
        'Interview / Meeting Agreed': elements.fieldInterviewAgreed ? elements.fieldInterviewAgreed.value : '',
        'Advisory Role Interest': elements.fieldAdvisoryInterest ? elements.fieldAdvisoryInterest.value : '',
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
        if (err.message && err.message.includes('Failed to fetch')) {
            showToast('⚠️ Unable to connect to local server (Failed to fetch). Please ensure the local server is running on port 5000.', 'error');
        } else {
            showToast(`Failed to save: ${err.message}`, 'error');
        }
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
${c['Current Position / Role'] ? `👔 *Current Role*: ${c['Current Position / Role']}\n` : ''}${c['Domain / Industry'] ? `🏢 *Domain/Industry*: ${c['Domain / Industry']}\n` : ''}${c['Education Background'] ? `🎓 *Education*: ${c['Education Background']}\n` : ''}🌐 *Source*: ${c['Portal Source'] || 'N/A'} (${c['Open To Work / Active'] || 'Active'})

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

// ==========================================================================
// Backups & GFS Version Control Functions
// ==========================================================================
async function fetchBackups(silent = false) {
    try {
        const res = await fetch(`${API_BASE}/backups`);
        const resp = await res.json();
        if (resp.success && resp.data) {
            const data = resp.data;
            state.backupSummary = data;
            state.backups = data.all_backups || [];

            // Update Tier Summary Cards
            const tiers = data.tiers || {};
            if (elements.statBackupSessionsCount) elements.statBackupSessionsCount.textContent = tiers.sessions?.count || 0;
            if (elements.statBackupSessionsLast) elements.statBackupSessionsLast.textContent = tiers.sessions?.last_backup || 'None';

            if (elements.statBackupDailyCount) elements.statBackupDailyCount.textContent = tiers.daily?.count || 0;
            if (elements.statBackupDailyLast) elements.statBackupDailyLast.textContent = tiers.daily?.last_backup || 'None';

            if (elements.statBackupWeeklyCount) elements.statBackupWeeklyCount.textContent = tiers.weekly?.count || 0;
            if (elements.statBackupWeeklyLast) elements.statBackupWeeklyLast.textContent = tiers.weekly?.last_backup || 'None';

            if (elements.statBackupMonthlyCount) elements.statBackupMonthlyCount.textContent = tiers.monthly?.count || 0;
            if (elements.statBackupMonthlyLast) elements.statBackupMonthlyLast.textContent = tiers.monthly?.last_backup || 'None';

            // Render Table
            renderBackupsTable(state.backups);
            if (!silent) {
                showToast('Backup history refreshed', 'info');
            }
        }
    } catch (err) {
        console.error('Fetch backups error:', err);
    }
}

function renderBackupsTable(backups) {
    if (!elements.backupsTableBody) return;
    
    if (elements.backupsTableCount) {
        elements.backupsTableCount.textContent = `${backups.length} snapshot(s) found`;
    }

    if (!backups || backups.length === 0) {
        elements.backupsTableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center; padding:24px; color:var(--text-muted);">
                    <i class="fa-solid fa-folder-open" style="font-size:24px; margin-bottom:8px; display:block; opacity:0.5;"></i>
                    No backup snapshots recorded yet.
                </td>
            </tr>
        `;
        return;
    }

    elements.backupsTableBody.innerHTML = backups.map(b => {
        const tierClass = `badge-${b.tier.toLowerCase()}`;
        return `
            <tr>
                <td>
                    <div style="font-weight:600; color:var(--text-primary); font-family:'JetBrains Mono', monospace; font-size:12px;">
                        <i class="fa-solid fa-file-excel" style="color:#22c55e; margin-right:6px;"></i>${escapeHtml(b.filename)}
                    </div>
                </td>
                <td>
                    <span class="backup-badge ${tierClass}">${escapeHtml(b.tier)}</span>
                </td>
                <td style="font-size:12px; color:var(--text-secondary); font-family:'JetBrains Mono', monospace;">
                    ${escapeHtml(b.modified_time)}
                </td>
                <td style="font-size:12px; color:var(--text-muted);">
                    ${escapeHtml(b.size_formatted || `${(b.size_bytes / 1024).toFixed(1)} KB`)}
                </td>
                <td style="text-align:right;">
                    <button class="btn btn-secondary btn-sm" onclick="restoreBackup('${escapeHtml(b.relative_path)}', '${escapeHtml(b.filename)}')" title="Rollback master database to this point">
                        <i class="fa-solid fa-rotate-left"></i> Restore
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function triggerManualBackup(tier = 'manual', prefix = 'manual_checkpoint') {
    try {
        showToast('Creating backup snapshot...', 'info');
        const res = await fetch(`${API_BASE}/backups/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tier, prefix })
        });
        const resp = await res.json();
        if (resp.success) {
            showToast(`Snapshot created: ${resp.result?.filename || 'Success'}`, 'success');
            fetchBackups(true);
        } else {
            showToast(`Backup failed: ${resp.error}`, 'error');
        }
    } catch (err) {
        showToast(`Backup error: ${err.message}`, 'error');
    }
}

window.restoreBackup = async function(relativePath, filename) {
    if (!confirm(`Are you sure you want to restore master data from '${filename}'?\n\nA safety backup of your current tracker state will automatically be saved before restoring.`)) {
        return;
    }

    try {
        showToast(`Restoring master data from '${filename}'...`, 'info');
        const res = await fetch(`${API_BASE}/backups/restore`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath: relativePath })
        });
        const resp = await res.json();
        if (resp.success) {
            showToast(resp.message || 'Master database restored successfully!', 'success');
            await fetchAllData(false);
        } else {
            showToast(`Restore failed: ${resp.error}`, 'error');
        }
    } catch (err) {
        showToast(`Restore error: ${err.message}`, 'error');
    }
};


// ==========================================================================
// Analytics — Conversion Intelligence & Audience Analytics (Unified Engine)
// ==========================================================================
const _analyticsCharts = {};
window._analyticsMetricMode = 'count'; // 'count' or 'pct'
window._lastAnalyticsData = null;
window._activeDrilldownCohort = [];

function _destroyChart(id) {
    if (_analyticsCharts[id]) {
        _analyticsCharts[id].destroy();
        delete _analyticsCharts[id];
    }
}

const CHART_COLORS = {
    primary:    'rgba(99, 102, 241, 0.85)',
    p1:         'rgba(16, 185, 129, 0.9)',
    p2:         'rgba(59, 130, 246, 0.85)',
    unclass:    'rgba(156, 163, 175, 0.75)',
    success:    'rgba(52, 211, 153, 0.85)',
    warning:    'rgba(245, 158, 11, 0.85)',
    danger:     'rgba(239, 68, 68, 0.85)',
    info:       'rgba(56, 189, 248, 0.85)',
    purple:     'rgba(168, 85, 247, 0.85)',
    teal:       'rgba(20, 184, 166, 0.85)',
    orange:     'rgba(249, 115, 22, 0.85)',
};

const RESP_COLORS = {
    'Positive':     'rgba(52, 211, 153, 0.85)',
    'Neutral':      'rgba(245, 158, 11, 0.85)',
    'Negative':     'rgba(239, 68, 68, 0.85)',
    'No Response':  'rgba(99, 102, 241, 0.7)',
    'Pending':      'rgba(156, 163, 175, 0.5)',
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
        padding: { top: 22, right: 28, left: 6, bottom: 6 }
    },
    plugins: {
        legend: {
            labels: { color: '#9ca3af', font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
            backgroundColor: 'rgba(15,15,25,0.95)',
            titleColor: '#f9fafb',
            bodyColor: '#d1d5db',
            borderColor: 'rgba(99,102,241,0.4)',
            borderWidth: 1
        }
    },
    scales: {
        x: {
            ticks: { color: '#9ca3af', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' }
        },
        y: {
            grace: '20%',
            ticks: { color: '#9ca3af', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' }
        }
    }
};

// Global Chart.js Plugin: Renders exact Count and Percentage (%) on/above all graph elements
const chartValueLabelsPlugin = {
    id: 'chartValueLabelsPlugin',
    afterDatasetsDraw(chart) {
        const { ctx } = chart;
        const chartType = chart.config.type;
        const isHorizontal = chart.config.options?.indexAxis === 'y';
        const isStacked = chart.config.options?.scales?.x?.stacked || chart.config.options?.scales?.y?.stacked;
        const isPctMode = (window._analyticsMetricMode === 'pct');

        // Precompute total for percentage calculation
        let datasetTotals = chart.data.datasets.map(ds =>
            (ds.data || []).reduce((acc, v) => acc + (Number(v) || 0), 0)
        );
        let globalTotal = datasetTotals.reduce((a, b) => a + b, 0);

        chart.data.datasets.forEach((dataset, datasetIndex) => {
            const meta = chart.getDatasetMeta(datasetIndex);
            if (meta.hidden) return;

            const dsTotal = datasetTotals[datasetIndex] || 1;
            const refTotal = isStacked ? globalTotal : dsTotal;

            meta.data.forEach((element, index) => {
                const rawVal = dataset.data[index];
                const val = Number(rawVal) || 0;
                if (val <= 0) return;

                // Calculate percentage
                const pct = refTotal > 0 ? Math.round((val / refTotal) * 100) : 0;

                // Format text: e.g. "55 (42%)" or "42% (55)"
                let labelText = '';
                if (isPctMode) {
                    labelText = isStacked ? `${val}` : `${pct}% (${val})`;
                } else {
                    labelText = isStacked ? `${val}` : `${val} (${pct}%)`;
                }

                ctx.save();
                ctx.font = 'bold 10px "Plus Jakarta Sans", sans-serif';

                if (chartType === 'bar') {
                    if (isHorizontal) {
                        ctx.fillStyle = '#f3f4f6';
                        ctx.textAlign = 'left';
                        ctx.textBaseline = 'middle';
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
                        ctx.shadowBlur = 3;
                        ctx.fillText(labelText, element.x + 5, element.y);
                    } else {
                        ctx.fillStyle = '#f3f4f6';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'bottom';
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
                        ctx.shadowBlur = 3;
                        ctx.fillText(labelText, element.x, element.y - 4);
                    }
                } else if (chartType === 'doughnut' || chartType === 'pie') {
                    if (pct >= 4) {
                        const pos = element.tooltipPosition();
                        ctx.fillStyle = '#ffffff';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                        ctx.shadowBlur = 5;
                        ctx.fillText(`${val} (${pct}%)`, pos.x, pos.y);
                    }
                }

                ctx.restore();
            });
        });
    }
};

try {
    if (window.Chart && !window._chartValueLabelsRegistered) {
        Chart.register(chartValueLabelsPlugin);
        window._chartValueLabelsRegistered = true;
    }
} catch (e) {
    console.warn('Could not register chartValueLabelsPlugin:', e);
}

function _makeBarChart(canvasId, labels, datasets, options = {}) {
    _destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const isHoriz = options.indexAxis === 'y';
        const mergedScales = {
            x: {
                ticks: { color: '#9ca3af', font: { size: 10 } },
                grid: { color: 'rgba(255,255,255,0.05)' },
                ...(isHoriz ? { grace: '22%' } : {}),
                ...(options.scales?.x || {})
            },
            y: {
                ticks: { color: '#9ca3af', font: { size: 10 } },
                grid: { color: 'rgba(255,255,255,0.05)' },
                ...(isHoriz ? {} : { grace: '22%' }),
                ...(options.scales?.y || {})
            }
        };

        const mergedOptions = {
            ...CHART_DEFAULTS,
            ...options,
            layout: {
                padding: { top: 22, right: (isHoriz ? 40 : 16), left: 6, bottom: 6 }
            },
            scales: mergedScales
        };

        _analyticsCharts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets },
            options: mergedOptions
        });
    } catch (e) {
        console.warn(`Chart render warning for ${canvasId}:`, e);
    }
}

function _makeDoughnutChart(canvasId, labels, data, colors) {
    _destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    try {
        const total = data.reduce((a, b) => a + (Number(b) || 0), 0) || 1;
        _analyticsCharts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{ data, backgroundColor: colors, borderColor: 'rgba(0,0,0,0.3)', borderWidth: 2, hoverOffset: 6 }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: { padding: 6 },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#e2e8f0',
                            font: { size: 10, weight: '500' },
                            boxWidth: 12,
                            padding: 6,
                            generateLabels: function(chart) {
                                const chartData = chart.data;
                                if (chartData.labels.length && chartData.datasets.length) {
                                    const ds = chartData.datasets[0];
                                    return chartData.labels.map((label, i) => {
                                        const val = ds.data[i] || 0;
                                        const pct = Math.round((val / total) * 100);
                                        return {
                                            text: `${label}: ${val} (${pct}%)`,
                                            fillStyle: ds.backgroundColor[i],
                                            hidden: isNaN(val) || val === 0,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: CHART_DEFAULTS.plugins.tooltip
                }
            }
        });
    } catch (e) {
        console.warn(`Doughnut render warning for ${canvasId}:`, e);
    }
}

function updateAudienceKpis(d) {
    const aud = d.audience_summary || {};
    const counts = aud.overall_counts || {};
    const comp = d.data_completeness || {};

    const p1Confirmed = counts['P1 - Preferred (Confirmed)'] || 0;
    const p1Inferred = counts['P1 - Candidate (Inferred)'] || 0;
    const p2Count = counts['P2 - Expansion'] || 0;
    const unclassCount = counts['Unclassified'] || 0;
    const totalRecs = comp.total_records || 1;

    const elP1Count = document.getElementById('kpi-p1-count');
    const elP1Sub = document.getElementById('kpi-p1-sub');
    if (elP1Count) elP1Count.textContent = `${p1Confirmed + p1Inferred}`;
    if (elP1Sub) elP1Sub.innerHTML = `<span>${p1Confirmed} Confirmed</span> • <span style="color:#fbbf24;">${p1Inferred} Review Queue</span>`;

    const elP2Count = document.getElementById('kpi-p2-count');
    const elP2Sub = document.getElementById('kpi-p2-sub');
    if (elP2Count) elP2Count.textContent = `${p2Count}`;
    if (elP2Sub) elP2Sub.textContent = `${Math.round((p2Count / totalRecs) * 100)}% of total pool`;

    const elUnclassCount = document.getElementById('kpi-unclass-count');
    const elUnclassSub = document.getElementById('kpi-unclass-sub');
    if (elUnclassCount) elUnclassCount.textContent = `${unclassCount}`;
    if (elUnclassSub) elUnclassSub.textContent = `${Math.round((unclassCount / totalRecs) * 100)}% awaiting data enrichment`;

    // Data Completeness Fill
    const agePct = comp.explicit_age_pct || 0;
    const secPct = comp.explicit_sector_pct || 0;
    const retPct = comp.explicit_ret_pct || 0;
    const avgCompleteness = Math.round((agePct + secPct + retPct) / 3);

    const elFill = document.getElementById('kpi-completeness-fill');
    if (elFill) elFill.style.width = `${avgCompleteness}%`;

    const elBadge = document.getElementById('kpi-quality-badge');
    if (elBadge) elBadge.textContent = `${avgCompleteness}% Complete`;

    const elDetails = document.getElementById('kpi-quality-details');
    if (elDetails) {
        elDetails.innerHTML = `Explicit: Age <strong>${agePct}%</strong> • Sector <strong>${secPct}%</strong> • Retired <strong>${retPct}%</strong>`;
    }

    const elProv = document.getElementById('kpi-provenance-note');
    if (elProv) {
        const confResponses = comp.explicit_call_responses || 0;
        const infResponses = comp.inferred_call_responses || 0;
        elProv.innerHTML = `Call Outcomes: <span style="color:#34d399;">${confResponses} Confirmed</span> • <span style="color:#fbbf24;">${infResponses} Inferred Proxies</span>`;
    }

    const elAsOf = document.getElementById('analytics-asof-badge');
    if (elAsOf && d.as_of) {
        elAsOf.innerHTML = `<i class="fa-solid fa-clock"></i> As-Of: ${d.as_of}`;
    }
}

function renderFunnel(funnel) {
    const container = document.getElementById('analytics-funnel');
    if (!container || !funnel) return;

    const rates = funnel.rates || {};
    const steps = [
        { label: 'Total Sourced', key: 'sourced', count: funnel.sourced || 0, rateLabel: '100%', subtext: 'Base sourcing pool', color: '#6366f1', icon: 'fa-users' },
        { label: 'Outreach Attempted', key: 'called', count: funnel.called || 0, rateLabel: rates.outreach_rate || '0%', subtext: `${funnel.called}/${funnel.sourced} Sourced`, color: '#38bdf8', icon: 'fa-phone-volume' },
        { label: 'Reached / Connected', key: 'reached', count: funnel.reached || 0, rateLabel: rates.reach_rate || '0%', subtext: `${funnel.reached}/${funnel.called} Attempted`, color: '#2dd4bf', icon: 'fa-comments' },
        { 
            label: 'Positive Response', 
            key: 'positive_response', 
            count: funnel.positive_response || 0, 
            rateLabel: rates.positive_rate || '0%', 
            subtext: `${funnel.positive_response}/${funnel.called} Attempted (${funnel.positive_explicit || 0} explicit, ${funnel.positive_inferred || 0} inferred)`,
            color: '#34d399',
            icon: 'fa-thumbs-up'
        },
        { label: 'Interview / Meet Agreed', key: 'interview_agreed', count: funnel.interview_agreed || 0, rateLabel: rates.interview_agreement_rate || '0%', subtext: `${funnel.interview_agreed}/${funnel.called} Attempted`, color: '#f59e0b', icon: 'fa-handshake' },
        { label: 'Advisory Interested', key: 'advisory_interested', count: funnel.advisory_interested || 0, rateLabel: rates.advisory_interest_rate || '0%', subtext: `${funnel.advisory_interested}/${funnel.sourced} Sourced`, color: '#a855f7', icon: 'fa-lightbulb' },
        { label: 'Advisory Formally Accepted', key: 'advisory_agreed', count: funnel.advisory_agreed || 0, rateLabel: rates.advisory_acceptance_rate || '0%', subtext: `${funnel.advisory_agreed}/${funnel.sourced} Sourced (Ultimate Goal)`, color: '#10b981', icon: 'fa-trophy' },
    ];

    const max = funnel.sourced || 1;
    let html = '';
    steps.forEach((step, i) => {
        const pctOfMax = max > 0 ? Math.round((step.count / max) * 100) : 0;
        const width = Math.max(16, pctOfMax);
        html += `
            <div class="funnel-step funnel-stage-card" onclick="openAnalyticsDrilldown('${step.key}')" title="Click to view candidate records at Stage ${i + 1}: ${step.label}">
                <div class="funnel-stage-left">
                    <span class="funnel-stage-badge" style="background:${step.color}20; color:${step.color}; border:1px solid ${step.color}55;">
                        <i class="fa-solid ${step.icon}"></i> Stage ${i + 1}
                    </span>
                    <span class="funnel-stage-name">${step.label}</span>
                </div>
                <div class="funnel-stage-center">
                    <div class="funnel-track">
                        <div class="funnel-fill-bar" style="width:${width}%; background: linear-gradient(90deg, ${step.color}, ${step.color}bb);">
                            <span class="funnel-bar-count">${step.count.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                <div class="funnel-stage-right">
                    <div class="funnel-metric-pct" style="color:${step.color};">${step.rateLabel}</div>
                    <div class="funnel-denominator-sub">${step.subtext}</div>
                </div>
            </div>`;
        if (i < steps.length - 1) {
            html += `<div class="funnel-arrow"><i class="fa-solid fa-chevron-down"></i></div>`;
        }
    });

    container.innerHTML = html;
}

function renderAnalyticsCharts(d) {
    if (!d) return;
    const isPct = (window._analyticsMetricMode === 'pct');

    // ---- REPORT 1: Audience & Profile Coverage ----
    // 1. Audience Segmentation
    const audCounts = d.audience_summary?.overall_counts || {};
    const audLabels = Object.keys(audCounts);
    const audVals = Object.values(audCounts);
    _makeDoughnutChart('chart-audience-dist', audLabels, audVals, [CHART_COLORS.p1, CHART_COLORS.warning, CHART_COLORS.p2, CHART_COLORS.unclass]);

    // 2. Experience Distribution
    const expLabels = Object.keys(d.exp_distribution || {});
    const expVals = Object.values(d.exp_distribution || {});
    const expTotal = expVals.reduce((a, b) => a + b, 0) || 1;
    const expDisplay = isPct ? expVals.map(v => Math.round((v / expTotal) * 100)) : expVals;
    _makeBarChart('chart-exp-dist', expLabels, [{
        label: isPct ? 'Percentage (%)' : 'Candidates',
        data: expDisplay,
        backgroundColor: [CHART_COLORS.primary, CHART_COLORS.info, CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.orange, CHART_COLORS.danger],
        borderRadius: 6
    }], { plugins: { legend: { display: false } } });

    // 3. Age-Band Distribution
    const ageLabels = Object.keys(d.age_distribution || {});
    const ageVals = Object.values(d.age_distribution || {});
    const ageTotal = ageVals.reduce((a, b) => a + b, 0) || 1;
    const ageDisplay = isPct ? ageVals.map(v => Math.round((v / ageTotal) * 100)) : ageVals;
    _makeBarChart('chart-age-dist', ageLabels, [{
        label: isPct ? 'Percentage (%)' : 'Candidates',
        data: ageDisplay,
        backgroundColor: [CHART_COLORS.info, CHART_COLORS.primary, CHART_COLORS.p1, CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.unclass],
        borderRadius: 6
    }], { plugins: { legend: { display: false } } });

    // 4. Sector / Industry Distribution
    const secLabels = Object.keys(d.sector_distribution || {});
    const secVals = Object.values(d.sector_distribution || {});
    _makeBarChart('chart-sector-dist', secLabels, [{
        label: 'Candidates',
        data: secVals,
        backgroundColor: CHART_COLORS.p2,
        borderRadius: 4
    }], {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }, y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } } }
    });

    // 5. Portal Distribution
    const pLabels = Object.keys(d.portal_distribution || {});
    const pVals = Object.values(d.portal_distribution || {});
    _makeDoughnutChart('chart-portal-dist', pLabels, pVals, Object.values(CHART_COLORS).slice(0, pLabels.length));

    // 6. Top Domains
    const domLabels = Object.keys(d.domain_distribution || {});
    const domVals = Object.values(d.domain_distribution || {});
    _makeBarChart('chart-domain-dist', domLabels, [{
        label: 'Sourced',
        data: domVals,
        backgroundColor: CHART_COLORS.primary,
        borderRadius: 4
    }], {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }, y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } } }
    });

    // ---- REPORT 2: Response Performance ----
    const respKeys = ['Positive', 'Neutral', 'Negative', 'No Response', 'Pending'];

    // 1. Response by Target Audience Segment
    const segResp = d.resp_by_segment || {};
    const segKeys = Object.keys(segResp);
    const segDatasets = respKeys.map(rk => ({
        label: rk,
        data: segKeys.map(sk => {
            const val = segResp[sk]?.[rk] || 0;
            const total = segResp[sk]?.total || 1;
            return isPct ? Math.round((val / total) * 100) : val;
        }),
        backgroundColor: RESP_COLORS[rk],
        borderRadius: 3
    }));
    _makeBarChart('chart-resp-segment', segKeys, segDatasets, {
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 2. Response by Experience Band
    const expBands = Object.keys(d.resp_by_exp || {});
    const reDatasets = respKeys.map(rk => ({
        label: rk,
        data: expBands.map(b => {
            const val = d.resp_by_exp[b]?.[rk] || 0;
            const total = d.resp_by_exp[b]?.total || 1;
            return isPct ? Math.round((val / total) * 100) : val;
        }),
        backgroundColor: RESP_COLORS[rk],
        borderRadius: 3
    }));
    _makeBarChart('chart-resp-exp', expBands, reDatasets, {
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 3. Response by Domain
    const rdDomains = Object.keys(d.resp_by_domain || {});
    const rdDatasets = respKeys.map(rk => ({
        label: rk,
        data: rdDomains.map(dom => {
            const val = d.resp_by_domain[dom]?.[rk] || 0;
            const total = d.resp_by_domain[dom]?.total || 1;
            return isPct ? Math.round((val / total) * 100) : val;
        }),
        backgroundColor: RESP_COLORS[rk],
        borderRadius: 3
    }));
    _makeBarChart('chart-resp-domain', rdDomains, rdDatasets, {
        indexAxis: 'y',
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 4. Response by Location
    const rlCities = Object.keys(d.resp_by_location || {});
    const rlDatasets = respKeys.map(rk => ({
        label: rk,
        data: rlCities.map(c => d.resp_by_location[c]?.[rk] || 0),
        backgroundColor: RESP_COLORS[rk],
        borderRadius: 3
    }));
    _makeBarChart('chart-resp-location', rlCities, rlDatasets, {
        indexAxis: 'y',
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } }
        },
        plugins: { legend: { display: false }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // ---- REPORT 3: Interview Agreement ----
    // 1. Mode split doughnut
    const ivModeLabels = Object.keys(d.interview_mode_split || {}).filter(k => (d.interview_mode_split[k] || 0) > 0);
    const ivModeVals = ivModeLabels.map(k => d.interview_mode_split[k]);
    _makeDoughnutChart('chart-interview-mode', ivModeLabels, ivModeVals,
        [CHART_COLORS.success, CHART_COLORS.info, CHART_COLORS.warning, CHART_COLORS.danger, CHART_COLORS.purple, CHART_COLORS.teal]);

    // 2. Agreement by Segment
    const ivSeg = d.interview_by_segment || {};
    const ivSegKeys = Object.keys(ivSeg);
    const ivSegAgreed = ivSegKeys.map(k => ivSeg[k]?.agreed || 0);
    const ivSegOther = ivSegKeys.map(k => Math.max(0, (ivSeg[k]?.total || 0) - (ivSeg[k]?.agreed || 0)));
    _makeBarChart('chart-interview-segment', ivSegKeys, [
        { label: 'Agreed to Meet', data: ivSegAgreed, backgroundColor: CHART_COLORS.success, borderRadius: 4 },
        { label: 'Pending / Not Agreed', data: ivSegOther, backgroundColor: 'rgba(156,163,175,0.25)', borderRadius: 4 }
    ], {
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 3. Agreement by Experience
    const ivExpBands = Object.keys(d.interview_by_exp || {});
    const ivExpAgreed = ivExpBands.map(b => d.interview_by_exp[b]?.agreed || 0);
    const ivExpTotal = ivExpBands.map(b => Math.max(0, (d.interview_by_exp[b]?.total || 0) - (d.interview_by_exp[b]?.agreed || 0)));
    _makeBarChart('chart-interview-exp', ivExpBands, [
        { label: 'Agreed', data: ivExpAgreed, backgroundColor: CHART_COLORS.success, borderRadius: 4 },
        { label: 'Others', data: ivExpTotal, backgroundColor: 'rgba(156,163,175,0.25)', borderRadius: 4 }
    ], {
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 4. Agreement by Domain
    const ivDoms = Object.keys(d.interview_by_domain || {});
    const ivDomsAgreed = ivDoms.map(k => d.interview_by_domain[k]?.agreed || 0);
    const ivDomsOther = ivDoms.map(k => Math.max(0, (d.interview_by_domain[k]?.total || 0) - (d.interview_by_domain[k]?.agreed || 0)));
    _makeBarChart('chart-interview-domain', ivDoms, [
        { label: 'Agreed', data: ivDomsAgreed, backgroundColor: CHART_COLORS.success, borderRadius: 4 },
        { label: 'Others', data: ivDomsOther, backgroundColor: 'rgba(156,163,175,0.2)', borderRadius: 4 }
    ], {
        indexAxis: 'y',
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // ---- REPORT 4: Advisory Progression & Acceptance ----
    // 1. Advisory Stage Doughnut
    const advLabels = Object.keys(d.advisory_counts || {}).filter(k => (d.advisory_counts[k] || 0) > 0);
    const advVals = advLabels.map(k => d.advisory_counts[k]);
    _makeDoughnutChart('chart-advisory-dist', advLabels, advVals,
        [CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.danger, CHART_COLORS.purple, CHART_COLORS.teal]);

    // 2. Advisory Progression by Segment
    const advSeg = d.advisory_by_segment || {};
    const advSegKeys = Object.keys(advSeg);
    const advSegAgreed = advSegKeys.map(k => advSeg[k]?.agreed || 0);
    const advSegInterested = advSegKeys.map(k => advSeg[k]?.interested || 0);
    _makeBarChart('chart-advisory-segment', advSegKeys, [
        { label: 'Formally Agreed', data: advSegAgreed, backgroundColor: CHART_COLORS.p1, borderRadius: 4 },
        { label: 'Interested (Info Needed)', data: advSegInterested, backgroundColor: CHART_COLORS.warning, borderRadius: 4 }
    ], {
        scales: {
            x: { stacked: false, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 3. Advisory by Experience
    const advExpBands = Object.keys(d.advisory_by_exp || {});
    const advExpAgreed = advExpBands.map(b => d.advisory_by_exp[b]?.agreed || 0);
    const advExpInterested = advExpBands.map(b => d.advisory_by_exp[b]?.interested || 0);
    _makeBarChart('chart-advisory-exp', advExpBands, [
        { label: 'Formally Agreed', data: advExpAgreed, backgroundColor: CHART_COLORS.purple, borderRadius: 4 },
        { label: 'Interested', data: advExpInterested, backgroundColor: CHART_COLORS.warning, borderRadius: 4 }
    ], {
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });

    // 4. Advisory by Domain
    const advDoms = Object.keys(d.advisory_by_domain || {});
    const advDomsAgreed = advDoms.map(k => d.advisory_by_domain[k]?.agreed || 0);
    const advDomsInterested = advDoms.map(k => d.advisory_by_domain[k]?.interested || 0);
    _makeBarChart('chart-advisory-domain', advDoms, [
        { label: 'Agreed', data: advDomsAgreed, backgroundColor: CHART_COLORS.purple, borderRadius: 4 },
        { label: 'Interested', data: advDomsInterested, backgroundColor: CHART_COLORS.warning, borderRadius: 4 }
    ], {
        indexAxis: 'y',
        scales: {
            x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { stacked: true, ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } }
        },
        plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 }, boxWidth: 10 } }, tooltip: CHART_DEFAULTS.plugins.tooltip }
    });
}

window.toggleMetricMode = function() {
    window._analyticsMetricMode = (window._analyticsMetricMode === 'count') ? 'pct' : 'count';
    const btnText = document.getElementById('toggle-metric-text');
    if (btnText) {
        btnText.textContent = (window._analyticsMetricMode === 'count') ? '% View' : 'Count View';
    }
    if (window._lastAnalyticsData) {
        renderAnalyticsCharts(window._lastAnalyticsData);
    }
};

window.resetAnalyticsFilters = function() {
    const seg = document.getElementById('filter-analytics-segment');
    const port = document.getElementById('filter-analytics-portal');
    const prov = document.getElementById('filter-analytics-provenance');
    if (seg) seg.value = 'all';
    if (port) port.value = 'all';
    if (prov) prov.value = 'all';
    loadAnalytics();
};

window.exportAnalyticsReport = function() {
    if (!window._lastAnalyticsData) {
        showToast('No analytics data available to export', 'warning');
        return;
    }
    try {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(window._lastAnalyticsData, null, 2));
        const dlAnchor = document.createElement('a');
        dlAnchor.setAttribute("href", dataStr);
        dlAnchor.setAttribute("download", `conversion_intelligence_report_${new Date().toISOString().slice(0,10)}.json`);
        document.body.appendChild(dlAnchor);
        dlAnchor.click();
        dlAnchor.remove();
        showToast('Analytics summary report downloaded successfully', 'success');
    } catch (e) {
        showToast(`Failed to export report: ${e.message}`, 'error');
    }
};

window.openAnalyticsDrilldown = function(filterType = 'all') {
    if (!window._lastAnalyticsData || !window._lastAnalyticsData.candidates_drilldown) {
        showToast('Drill-down data not ready yet. Please refresh.', 'warning');
        return;
    }
    const all = window._lastAnalyticsData.candidates_drilldown || [];
    let cohort = [];
    let title = 'Cohort Candidates Drill-Down';

    if (filterType === 'p1') {
        cohort = all.filter(c => c.segment.includes('P1'));
        title = 'P1 Preferred Candidates (Confirmed & Review Queue)';
    } else if (filterType === 'p2') {
        cohort = all.filter(c => c.segment.includes('P2'));
        title = 'P2 Controlled Expansion Candidates';
    } else if (filterType === 'unclassified') {
        cohort = all.filter(c => c.segment.includes('Unclassified'));
        title = 'Unclassified Candidates (Incomplete Attributes)';
    } else if (filterType === 'called') {
        cohort = all.filter(c => c.call_response !== 'Pending');
        title = 'Outreach Attempted Candidates';
    } else if (filterType === 'positive_response') {
        cohort = all.filter(c => c.call_response === 'Positive');
        title = 'Positive Response Candidates';
    } else if (filterType === 'interview_agreed') {
        cohort = all.filter(c => (c.interview_agreed || '').startsWith('Yes'));
        title = 'Interview / Meeting Agreed Candidates';
    } else if (filterType === 'advisory_agreed') {
        cohort = all.filter(c => c.advisory_interest === 'Agreed');
        title = 'Advisory Formally Accepted Candidates';
    } else if (filterType === 'advisory_interested') {
        cohort = all.filter(c => c.advisory_interest === 'Interested - More Info Needed');
        title = 'Advisory Interested Candidates';
    } else {
        cohort = all;
        title = 'All Active Cohort Candidates';
    }

    window._activeDrilldownCohort = cohort;
    const modalTitle = document.getElementById('drilldown-modal-title');
    if (modalTitle) modalTitle.textContent = title;

    const modalSummary = document.getElementById('drilldown-summary-text');
    if (modalSummary) modalSummary.textContent = `Showing ${cohort.length} matching candidate records. PII (phone/email) is protected.`;

    const searchInput = document.getElementById('drilldown-search-input');
    if (searchInput) searchInput.value = '';

    renderDrilldownRows(cohort);

    const modal = document.getElementById('modal-analytics-drilldown');
    if (modal) modal.style.display = 'flex';
};

function renderDrilldownRows(list) {
    const tbody = document.getElementById('drilldown-table-body');
    if (!tbody) return;

    if (!list || list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No candidates match this segment.</td></tr>`;
        return;
    }

    tbody.innerHTML = list.map(c => {
        let segBadge = '<span class="kpi-badge">Unclassified</span>';
        if (c.segment.includes('P1 - Preferred')) {
            segBadge = '<span class="kpi-badge" style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid #10b981;">P1 Confirmed</span>';
        } else if (c.segment.includes('P1')) {
            segBadge = '<span class="kpi-badge" style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid #f59e0b;">P1 Inferred</span>';
        } else if (c.segment.includes('P2')) {
            segBadge = '<span class="kpi-badge" style="background:rgba(59,130,246,0.2); color:#60a5fa; border:1px solid #3b82f6;">P2 Expansion</span>';
        }

        let respBadge = `<span class="pill-pending">${escapeHtml(c.call_response || 'Pending')}</span>`;
        if (c.call_response === 'Positive') {
            const provBadge = c.call_provenance === 'explicit' ? '✅ Explicit' : '🔍 Inferred';
            respBadge = `<span class="pill-called" title="${provBadge}">Positive (${provBadge})</span>`;
        } else if (c.call_response === 'Negative') {
            respBadge = `<span class="pill-not-interested">Negative</span>`;
        }

        return `
            <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 10px 12px; font-weight:600; color:var(--text-primary);">
                    ${escapeHtml(c.name || 'Unnamed')}
                </td>
                <td style="padding: 10px 12px;">${segBadge}</td>
                <td style="padding: 10px 12px;">
                    <div style="font-weight:500;">${escapeHtml(c.domain || 'Domain N/A')}</div>
                    <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(c.role || '')}</div>
                </td>
                <td style="padding: 10px 12px;">
                    <div>${escapeHtml(c.exp_band || '')}</div>
                    <div style="font-size:11px; color:var(--text-muted);">Age: ${escapeHtml(String(c.age))}</div>
                </td>
                <td style="padding: 10px 12px;">${respBadge}</td>
                <td style="padding: 10px 12px; text-align:right;">
                    <button class="btn btn-secondary btn-sm" onclick="closeAnalyticsDrilldown(); openCandidateModal(${c.id});" title="Open candidate details">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i> Open
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

window.closeAnalyticsDrilldown = function() {
    const modal = document.getElementById('modal-analytics-drilldown');
    if (modal) modal.style.display = 'none';
};

function filterDrilldownTable(query) {
    if (!window._activeDrilldownCohort) return;
    if (!query) {
        renderDrilldownRows(window._activeDrilldownCohort);
        return;
    }
    const q = query.toLowerCase();
    const filtered = window._activeDrilldownCohort.filter(c => 
        (c.name || '').toLowerCase().includes(q) ||
        (c.role || '').toLowerCase().includes(q) ||
        (c.domain || '').toLowerCase().includes(q) ||
        (c.city || '').toLowerCase().includes(q) ||
        (c.segment || '').toLowerCase().includes(q)
    );
    renderDrilldownRows(filtered);
}

// ==========================================================================
// Analytics Section Visibility & Multi-Select Controller
// ==========================================================================
window.selectReportView = function(viewKey) {
    const pills = document.querySelectorAll('#analytics-view-pills .pill-btn');
    pills.forEach(p => p.classList.remove('active'));

    const activePill = document.getElementById(`pill-view-${viewKey}`);
    if (activePill) activePill.classList.add('active');

    const sections = {
        funnel: document.getElementById('sec-analytics-funnel'),
        rep1: document.getElementById('sec-analytics-rep1'),
        rep2: document.getElementById('sec-analytics-rep2'),
        rep3: document.getElementById('sec-analytics-rep3'),
        rep4: document.getElementById('sec-analytics-rep4')
    };

    const checkboxes = {
        funnel: document.getElementById('chk-show-funnel'),
        rep1: document.getElementById('chk-show-rep1'),
        rep2: document.getElementById('chk-show-rep2'),
        rep3: document.getElementById('chk-show-rep3'),
        rep4: document.getElementById('chk-show-rep4')
    };

    if (viewKey === 'all') {
        Object.keys(sections).forEach(k => {
            if (sections[k]) sections[k].style.display = 'block';
            if (checkboxes[k]) checkboxes[k].checked = true;
        });
    } else {
        Object.keys(sections).forEach(k => {
            const isMatch = (k === viewKey);
            if (sections[k]) sections[k].style.display = isMatch ? 'block' : 'none';
            if (checkboxes[k]) checkboxes[k].checked = isMatch;
        });
    }

    // Trigger resize on visible charts so canvas fills container properly
    setTimeout(() => {
        Object.values(_analyticsCharts).forEach(ch => {
            if (ch && typeof ch.resize === 'function') ch.resize();
        });
    }, 100);
};

window.updateMultiReportVisibility = function() {
    const sections = {
        funnel: document.getElementById('sec-analytics-funnel'),
        rep1: document.getElementById('sec-analytics-rep1'),
        rep2: document.getElementById('sec-analytics-rep2'),
        rep3: document.getElementById('sec-analytics-rep3'),
        rep4: document.getElementById('sec-analytics-rep4')
    };

    const checkboxes = {
        funnel: document.getElementById('chk-show-funnel'),
        rep1: document.getElementById('chk-show-rep1'),
        rep2: document.getElementById('chk-show-rep2'),
        rep3: document.getElementById('chk-show-rep3'),
        rep4: document.getElementById('chk-show-rep4')
    };

    let checkedCount = 0;
    let singleKey = null;

    Object.keys(checkboxes).forEach(k => {
        const isChecked = checkboxes[k] ? checkboxes[k].checked : true;
        if (sections[k]) sections[k].style.display = isChecked ? 'block' : 'none';
        if (isChecked) {
            checkedCount++;
            singleKey = k;
        }
    });

    const pills = document.querySelectorAll('#analytics-view-pills .pill-btn');
    pills.forEach(p => p.classList.remove('active'));

    if (checkedCount === 5) {
        const pAll = document.getElementById('pill-view-all');
        if (pAll) pAll.classList.add('active');
    } else if (checkedCount === 1 && singleKey) {
        const pSingle = document.getElementById(`pill-view-${singleKey}`);
        if (pSingle) pSingle.classList.add('active');
    }

    // Resize visible charts
    setTimeout(() => {
        Object.values(_analyticsCharts).forEach(ch => {
            if (ch && typeof ch.resize === 'function') ch.resize();
        });
    }, 100);
};

window.toggleReportMultiSelectMenu = function() {
    const menu = document.getElementById('report-multi-select-menu');
    if (!menu) return;
    menu.style.display = (menu.style.display === 'none' || !menu.style.display) ? 'flex' : 'none';
};

window.setAllReportCheckboxes = function(checked) {
    ['chk-show-funnel', 'chk-show-rep1', 'chk-show-rep2', 'chk-show-rep3', 'chk-show-rep4'].forEach(id => {
        const chk = document.getElementById(id);
        if (chk) chk.checked = checked;
    });
    updateMultiReportVisibility();
};

// ==========================================================================
// Interactive Excel-Style Slicers & Scenario Modeling Engine
// ==========================================================================
window._slicerState = {
    sector: 'all',
    exp: 'all',
    segment: 'all'
};

window.toggleSlicerFilter = function(category, val) {
    window._slicerState[category] = val;
    const groupEl = document.getElementById(`slicer-group-${category}`);
    if (groupEl) {
        groupEl.querySelectorAll('.slicer-tile').forEach(btn => {
            if (btn.dataset.filter === val) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
    applyInteractiveSlicers();
};

window.resetInteractiveSlicers = function() {
    window._slicerState = {
        sector: 'all',
        exp: 'all',
        segment: 'all'
    };
    const ageInput = document.getElementById('slicer-min-age');
    const expInput = document.getElementById('slicer-min-exp');
    const kwInput = document.getElementById('slicer-keyword');
    if (ageInput) ageInput.value = '';
    if (expInput) expInput.value = '';
    if (kwInput) kwInput.value = '';

    ['sector', 'exp', 'segment'].forEach(cat => {
        const groupEl = document.getElementById(`slicer-group-${cat}`);
        if (groupEl) {
            groupEl.querySelectorAll('.slicer-tile').forEach(btn => {
                if (btn.dataset.filter === 'all') btn.classList.add('active');
                else btn.classList.remove('active');
            });
        }
    });

    applyInteractiveSlicers();
};

function recalculateAnalyticsFromCohort(cohort, baselineTotal) {
    const total = cohort.length;

    const counts = {
        'P1 - Preferred (Confirmed)': 0,
        'P1 - Candidate (Inferred)': 0,
        'P2 - Expansion': 0,
        'Unclassified': 0
    };

    const exp_dist = { '0–5 yrs': 0, '5–10 yrs': 0, '10–15 yrs': 0, '15–20 yrs': 0, '20+ yrs': 0, 'Unknown': 0 };
    const age_dist = { '< 45 yrs': 0, '45–50 yrs': 0, '51–55 yrs': 0, '56–60 yrs': 0, '60+ yrs': 0, 'Unknown': 0 };
    const sector_dist = {};
    const portal_dist = {};
    const domain_dist = {};
    const loc_dist = {};

    let calledCount = 0;
    let reachedCount = 0;
    let positiveCount = 0;
    let interviewAgreedCount = 0;
    let advisoryInterestedCount = 0;
    let advisoryAgreedCount = 0;

    const resp_by_segment = {};
    const resp_by_exp = {};
    const resp_by_domain = {};
    const resp_by_location = {};

    const interview_by_segment = {};
    const interview_by_exp = {};
    const interview_by_domain = {};
    const interview_mode_split = { 'In-Person': 0, 'Virtual / Video': 0, 'Undecided / Flexible': 0 };

    const advisory_counts = {
        'Agreed': 0,
        'Interested - More Info Needed': 0,
        'Declined': 0,
        'Not Discussed': 0,
        'Follow-Up Required': 0
    };
    const advisory_by_segment = {};
    const advisory_by_exp = {};
    const advisory_by_domain = {};

    cohort.forEach(c => {
        // Audience Segment
        const seg = c.segment || 'Unclassified';
        if (counts[seg] !== undefined) counts[seg]++;
        else counts['Unclassified']++;

        // Exp band
        const eb = c.exp_band || 'Unknown';
        exp_dist[eb] = (exp_dist[eb] || 0) + 1;

        // Age band
        let ab = 'Unknown';
        const ageNum = parseInt(c.age, 10);
        if (!isNaN(ageNum)) {
            if (ageNum < 45) ab = '< 45 yrs';
            else if (ageNum <= 50) ab = '45–50 yrs';
            else if (ageNum <= 55) ab = '51–55 yrs';
            else if (ageNum <= 60) ab = '56–60 yrs';
            else ab = '60+ yrs';
        }
        age_dist[ab] = (age_dist[ab] || 0) + 1;

        // Sector
        const sec = c.sector || 'Unknown';
        sector_dist[sec] = (sector_dist[sec] || 0) + 1;

        // Portal
        const p = c.portal || 'Unknown';
        portal_dist[p] = (portal_dist[p] || 0) + 1;

        // Domain
        const d = c.domain || 'Unknown';
        domain_dist[d] = (domain_dist[d] || 0) + 1;

        // City
        const loc = c.city || 'Unknown';
        loc_dist[loc] = (loc_dist[loc] || 0) + 1;

        // Call Response
        const cr = (c.call_response || '').trim();
        const isCalled = cr !== '' && cr !== 'Pending';
        if (isCalled) calledCount++;
        if (['Positive', 'Neutral', 'Negative'].includes(cr)) reachedCount++;
        if (cr === 'Positive') positiveCount++;

        // Response performance maps
        [
            [resp_by_segment, seg],
            [resp_by_exp, eb],
            [resp_by_domain, d],
            [resp_by_location, loc]
        ].forEach(([map, key]) => {
            if (!map[key]) map[key] = { total: 0, positive: 0, neutral: 0, negative: 0, rate: '0%' };
            if (isCalled) {
                map[key].total++;
                if (cr === 'Positive') map[key].positive++;
                else if (cr === 'Neutral') map[key].neutral++;
                else if (cr === 'Negative') map[key].negative++;
                map[key].rate = `${Math.round((map[key].positive / Math.max(1, map[key].total)) * 100)}%`;
            }
        });

        // Interview readiness
        const ia = (c.interview_agreed || '').trim();
        if (ia === 'Agreed' || ia === 'Yes') interviewAgreedCount++;
        if (ia.includes('In-Person')) interview_mode_split['In-Person']++;
        else if (ia.includes('Virtual') || ia.includes('Video')) interview_mode_split['Virtual / Video']++;
        else if (ia) interview_mode_split['Undecided / Flexible']++;

        [
            [interview_by_segment, seg],
            [interview_by_exp, eb],
            [interview_by_domain, d]
        ].forEach(([map, key]) => {
            if (!map[key]) map[key] = { total: 0, agreed: 0, rate: '0%' };
            if (isCalled) {
                map[key].total++;
                if (ia === 'Agreed' || ia === 'Yes') map[key].agreed++;
                map[key].rate = `${Math.round((map[key].agreed / Math.max(1, map[key].total)) * 100)}%`;
            }
        });

        // Advisory
        const adv = (c.advisory_interest || '').trim();
        if (adv === 'Agreed') advisoryAgreedCount++;
        else if (adv.includes('Interested')) advisoryInterestedCount++;

        if (advisory_counts[adv] !== undefined) advisory_counts[adv]++;
        else if (adv) advisory_counts['Interested - More Info Needed']++;
        else advisory_counts['Not Discussed']++;

        [
            [advisory_by_segment, seg],
            [advisory_by_exp, eb],
            [advisory_by_domain, d]
        ].forEach(([map, key]) => {
            if (!map[key]) map[key] = { total: 0, agreed: 0, interested: 0 };
            map[key].total++;
            if (adv === 'Agreed') map[key].agreed++;
            else if (adv.includes('Interested')) map[key].interested++;
        });
    });

    const rates = {
        outreach_rate: calledCount > 0 ? `${Math.round((calledCount / Math.max(1, total)) * 100)}%` : '0%',
        reach_rate: calledCount > 0 ? `${Math.round((reachedCount / calledCount) * 100)}%` : '0%',
        positive_rate: calledCount > 0 ? `${Math.round((positiveCount / calledCount) * 100)}%` : '0%',
        interview_agreement_rate: calledCount > 0 ? `${Math.round((interviewAgreedCount / calledCount) * 100)}%` : '0%',
        advisory_interest_rate: total > 0 ? `${Math.round((advisoryInterestedCount / total) * 100)}%` : '0%',
        advisory_acceptance_rate: total > 0 ? `${Math.round((advisoryAgreedCount / total) * 100)}%` : '0%'
    };

    return {
        success: true,
        audience_summary: {
            overall_counts: counts,
            filtered_count: total
        },
        data_completeness: window._lastAnalyticsData?.data_completeness || { total_records: baselineTotal },
        as_of: new Date().toLocaleTimeString(),
        funnel: {
            sourced: total,
            called: calledCount,
            reached: reachedCount,
            positive_response: positiveCount,
            positive_explicit: positiveCount,
            positive_inferred: 0,
            interview_agreed: interviewAgreedCount,
            advisory_interested: advisoryInterestedCount,
            advisory_agreed: advisoryAgreedCount,
            rates: rates
        },
        exp_distribution: exp_dist,
        age_distribution: age_dist,
        sector_distribution: sector_dist,
        portal_distribution: portal_dist,
        domain_distribution: domain_dist,
        location_distribution: loc_dist,
        resp_by_segment: resp_by_segment,
        resp_by_exp: resp_by_exp,
        resp_by_domain: resp_by_domain,
        resp_by_location: resp_by_location,
        interview_by_segment: interview_by_segment,
        interview_by_exp: interview_by_exp,
        interview_by_domain: interview_by_domain,
        interview_mode_split: interview_mode_split,
        advisory_counts: advisory_counts,
        advisory_by_segment: advisory_by_segment,
        advisory_by_exp: advisory_by_exp,
        advisory_by_domain: advisory_by_domain
    };
}

window.applyInteractiveSlicers = function() {
    if (!window._masterAnalyticsRecords || !window._masterAnalyticsRecords.length) {
        if (window._lastAnalyticsData?.candidates_drilldown) {
            window._masterAnalyticsRecords = window._lastAnalyticsData.candidates_drilldown;
        } else {
            return;
        }
    }

    const minAgeInput = document.getElementById('slicer-min-age');
    const minExpInput = document.getElementById('slicer-min-exp');
    const kwInput = document.getElementById('slicer-keyword');

    const minAgeVal = minAgeInput ? parseInt(minAgeInput.value, 10) : NaN;
    const minExpVal = minExpInput ? parseFloat(minExpInput.value) : NaN;
    const kwVal = kwInput ? kwInput.value.trim().toLowerCase() : '';
    const sectorFilter = window._slicerState.sector;
    const expFilter = window._slicerState.exp;
    const segFilter = window._slicerState.segment;

    const all = window._masterAnalyticsRecords;
    const filtered = all.filter(c => {
        // Min Age
        if (!isNaN(minAgeVal) && minAgeVal > 0) {
            const ageNum = parseInt(c.age, 10);
            if (isNaN(ageNum) || ageNum < minAgeVal) return false;
        }
        // Min Experience
        if (!isNaN(minExpVal) && minExpVal > 0) {
            const eb = c.exp_band || '';
            let y = 0;
            if (eb.includes('20+')) y = 20;
            else if (eb.includes('15–20')) y = 15;
            else if (eb.includes('10–15')) y = 10;
            else if (eb.includes('5–10')) y = 5;
            else if (eb.includes('0–5')) y = 1;
            if (y < minExpVal) return false;
        }
        // Keyword Search
        if (kwVal) {
            const blob = `${c.name || ''} ${c.role || ''} ${c.domain || ''} ${c.city || ''} ${c.sector || ''}`.toLowerCase();
            if (!blob.includes(kwVal)) return false;
        }
        // Sector Slicer
        if (sectorFilter !== 'all') {
            if ((c.sector || '').toLowerCase() !== sectorFilter.toLowerCase()) return false;
        }
        // Experience Slicer
        if (expFilter !== 'all') {
            if ((c.exp_band || '') !== expFilter) return false;
        }
        // Audience Slicer
        if (segFilter !== 'all') {
            if (segFilter === 'P1' && !(c.segment || '').startsWith('P1')) return false;
            if (segFilter === 'P2' && !(c.segment || '').startsWith('P2')) return false;
            if (segFilter === 'Unclassified' && !(c.segment || '').startsWith('Unclassified')) return false;
        }
        return true;
    });

    const badge = document.getElementById('slicer-active-count');
    if (badge) {
        const pct = Math.round((filtered.length / Math.max(1, all.length)) * 100);
        badge.textContent = `${filtered.length} of ${all.length} Candidates (${pct}%)`;
    }

    const computed = recalculateAnalyticsFromCohort(filtered, all.length);
    updateAudienceKpis(computed);
    renderFunnel(computed.funnel);
    renderAnalyticsCharts(computed);
};

window.loadAnalytics = async function() {
    try {
        const segFilter = document.getElementById('filter-analytics-segment')?.value || 'all';
        const portalFilter = document.getElementById('filter-analytics-portal')?.value || 'all';
        const provFilter = document.getElementById('filter-analytics-provenance')?.value || 'all';

        const params = new URLSearchParams({
            segment: segFilter,
            portal: portalFilter,
            provenance: provFilter
        });

        const res = await fetch(`${API_BASE}/analytics?${params.toString()}`);
        const d = await res.json();
        if (!d.success) return;

        window._lastAnalyticsData = d;
        window._masterAnalyticsRecords = d.candidates_drilldown || [];

        // If slicer was previously manipulated, apply slicers; otherwise render base
        const hasActiveSlicer = window._slicerState.sector !== 'all' ||
            window._slicerState.exp !== 'all' ||
            window._slicerState.segment !== 'all' ||
            (document.getElementById('slicer-min-age')?.value) ||
            (document.getElementById('slicer-min-exp')?.value) ||
            (document.getElementById('slicer-keyword')?.value);

        if (hasActiveSlicer) {
            applyInteractiveSlicers();
        } else {
            // 1. Audience Segmentation KPIs
            updateAudienceKpis(d);

            // 2. Master Funnel
            renderFunnel(d.funnel);

            // 3. Visual Reports (Report 1 to 4)
            renderAnalyticsCharts(d);

            const badge = document.getElementById('slicer-active-count');
            if (badge) {
                badge.textContent = `${window._masterAnalyticsRecords.length} of ${window._masterAnalyticsRecords.length} Candidates (100%)`;
            }
        }

    } catch (err) {
        console.error('Analytics load error:', err);
        showToast('Failed to load analytics data', 'error');
    }
};

// Event listener bindings for Drilldown modal & Multi-select menu (null-safe)
document.addEventListener('DOMContentLoaded', () => {
    const btnCloseDrill = document.getElementById('btn-close-drilldown-modal');
    if (btnCloseDrill) btnCloseDrill.addEventListener('click', closeAnalyticsDrilldown);

    const drillModal = document.getElementById('modal-analytics-drilldown');
    if (drillModal) {
        drillModal.addEventListener('click', (e) => {
            if (e.target === drillModal) closeAnalyticsDrilldown();
        });
    }

    const searchInput = document.getElementById('drilldown-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterDrilldownTable(e.target.value.trim().toLowerCase());
        });
    }

    // Close multi-select menu when clicking outside
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('report-multi-select-menu');
        const btn = document.getElementById('btn-toggle-multi-select');
        if (menu && menu.style.display === 'flex') {
            if (!menu.contains(e.target) && !btn.contains(e.target)) {
                menu.style.display = 'none';
            }
        }
    });
});


