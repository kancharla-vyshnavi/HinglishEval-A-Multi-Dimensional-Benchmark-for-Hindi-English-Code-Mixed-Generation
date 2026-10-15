// HinglishEval Human Evaluation Platform - Frontend Logic
(function () {
  'use strict';

  // State
  let currentToken = '';
  let currentUser = null;
  let currentIndex = 1;
  let currentItem = null;
  let currentScores = {
    fluency: null,
    code_mixing_naturalness: null,
    hindi_grammar: null,
    prompt_adherence: null,
    spelling_consistency: null,
    overall: null
  };

  const DIMENSIONS = [
    {
      id: 'fluency',
      title: '1. Fluency',
      rubric: '1 = Fragmented/broken/looping words; 2 = Disjointed phrasing; 3 = Understandable but stiff; 4 = Smooth natural phrasing; 5 = Highly articulate flow.'
    },
    {
      id: 'code_mixing_naturalness',
      title: '2. Code-Mixing Naturalness',
      rubric: '1 = Monolingual rewrite or robotic dictionary substitution; 2 = Unnatural switching violating vernacular norms; 3 = Fair mixing with minor awkwardness; 4 = Fluid conversational code-switching; 5 = Highly authentic, colloquial bilingual Hinglish.'
    },
    {
      id: 'hindi_grammar',
      title: '3. Hindi Grammar',
      rubric: '1 = Severe agreement breakdown, corrupted postpositions; 2 = Multiple grammatical slips; 3 = Understandable syntax with minor inflection errors; 4 = Proper Hindi morphosyntax; 5 = Flawless grammar and idiomatic agreement.'
    },
    {
      id: 'prompt_adherence',
      title: '4. Prompt Adherence',
      rubric: '1 = Complete refusal, off-topic hallucination, or crash traceback; 2 = Tangential; 3 = Partially answers prompt; 4 = Directly addresses the user request; 5 = Exceptionally pertinent, complete response.'
    },
    {
      id: 'spelling_consistency',
      title: '5. Spelling Consistency',
      rubric: '1 = Phonetic chaos and unreadable Roman Hindi; 2 = Inconsistent spelling variations; 3 = Readable with minor phonetic quirks; 4 = Standard Romanized Hindi transliteration; 5 = Highly consistent, canonical spelling.'
    },
    {
      id: 'overall',
      title: '6. Overall Quality',
      rubric: '1 = Unusable/poor; 2 = Below acceptable threshold; 3 = Acceptable Hinglish output; 4 = Strong, well-formed generation; 5 = Publication-quality benchmark response.'
    }
  ];

  // DOM Elements
  const authModal = document.getElementById('auth-modal');
  const tokenInput = document.getElementById('token-input');
  const loginBtn = document.getElementById('login-btn');
  const annotatorNameEl = document.getElementById('annotator-name');
  const annotatorPill = document.getElementById('annotator-pill');
  const themeToggleBtn = document.getElementById('theme-toggle-btn');

  // Evaluation elements
  const evalView = document.getElementById('eval-view');
  const adminView = document.getElementById('admin-view');
  const progressText = document.getElementById('progress-text');
  const progressPercent = document.getElementById('progress-percent');
  const progressFill = document.getElementById('progress-fill');

  const itemIndexBadge = document.getElementById('item-index-badge');
  const itemStatusBadge = document.getElementById('item-status-badge');
  const promptContent = document.getElementById('prompt-content');
  const responseContent = document.getElementById('response-content');
  const sourceTextBox = document.getElementById('source-text-box');
  const sourceTextContent = document.getElementById('source-text-content');

  const dimensionsContainer = document.getElementById('dimensions-container');
  const notesTextarea = document.getElementById('notes-textarea');
  const prevBtn = document.getElementById('prev-btn');
  const saveNextBtn = document.getElementById('save-next-btn');
  const jumpInput = document.getElementById('jump-input');
  const jumpBtn = document.getElementById('jump-btn');
  const nextUnansweredBtn = document.getElementById('next-unanswered-btn');

  // Admin elements
  const exportBtn = document.getElementById('export-btn');
  const exportStatus = document.getElementById('export-status');
  const adminOverviewContainer = document.getElementById('admin-overview-container');

  // Toast container
  const toastContainer = document.getElementById('toast-container');

  // Initialize
  function init() {
    initTheme();
    renderDimensions();
    attachEventListeners();

    // Check URL parameters for token and item
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    const itemFromUrl = urlParams.get('item');

    if (tokenFromUrl) {
      currentToken = tokenFromUrl.trim();
      localStorage.setItem('hinglish_eval_token', currentToken);
    } else {
      currentToken = localStorage.getItem('hinglish_eval_token') || '';
    }

    if (itemFromUrl && parseInt(itemFromUrl, 10)) {
      currentIndex = Math.max(1, Math.min(500, parseInt(itemFromUrl, 10)));
    } else {
      const savedIdx = localStorage.getItem('hinglish_eval_last_idx');
      if (savedIdx) currentIndex = parseInt(savedIdx, 10) || 1;
    }

    if (currentToken) {
      authenticate(currentToken);
    } else {
      showAuthModal();
    }
  }

  // Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('hinglish_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('hinglish_theme', newTheme);
  }

  // Render Dimensions
  function renderDimensions() {
    dimensionsContainer.innerHTML = '';
    DIMENSIONS.forEach(dim => {
      const dimItem = document.createElement('div');
      dimItem.className = 'dimension-item';
      dimItem.id = `dim-container-${dim.id}`;

      dimItem.innerHTML = `
        <div class="dim-header">
          <span class="dim-title">${dim.title}</span>
          <button type="button" class="dim-info-btn" id="rubric-toggle-${dim.id}" title="Toggle scoring rubric">
            ℹ️ Rubric Guide
          </button>
        </div>
        <div class="dim-rubric-guide" id="rubric-${dim.id}">
          ${dim.rubric}
        </div>
        <div class="likert-selector" id="selector-${dim.id}">
          <button type="button" class="likert-btn" data-dim="${dim.id}" data-val="1" id="${dim.id}-1">1<br><small style="font-weight:400; font-size:0.7rem;">Poor</small></button>
          <button type="button" class="likert-btn" data-dim="${dim.id}" data-val="2" id="${dim.id}-2">2<br><small style="font-weight:400; font-size:0.7rem;">Fair</small></button>
          <button type="button" class="likert-btn" data-dim="${dim.id}" data-val="3" id="${dim.id}-3">3<br><small style="font-weight:400; font-size:0.7rem;">Good</small></button>
          <button type="button" class="likert-btn" data-dim="${dim.id}" data-val="4" id="${dim.id}-4">4<br><small style="font-weight:400; font-size:0.7rem;">Strong</small></button>
          <button type="button" class="likert-btn" data-dim="${dim.id}" data-val="5" id="${dim.id}-5">5<br><small style="font-weight:400; font-size:0.7rem;">Native</small></button>
        </div>
      `;

      dimensionsContainer.appendChild(dimItem);

      // Rubric toggle
      const rubricToggle = dimItem.querySelector(`#rubric-toggle-${dim.id}`);
      const rubricBox = dimItem.querySelector(`#rubric-${dim.id}`);
      rubricToggle.addEventListener('click', () => {
        rubricBox.classList.toggle('show');
      });

      // Likert buttons
      const buttons = dimItem.querySelectorAll('.likert-btn');
      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          const val = parseInt(btn.getAttribute('data-val'), 10);
          setScore(dim.id, val);
        });
      });
    });
  }

  function saveLocalDraft() {
    if (!currentItem) return;
    const draftKey = `hinglish_draft_${currentItem.assignment_id}`;
    const draftData = {
      scores: currentScores,
      notes: notesTextarea ? notesTextarea.value : ''
    };
    try {
      localStorage.setItem(draftKey, JSON.stringify(draftData));
    } catch (e) {}
  }

  function setScore(dimensionId, value) {
    currentScores[dimensionId] = value;

    // Update UI buttons
    const selector = document.getElementById(`selector-${dimensionId}`);
    const buttons = selector.querySelectorAll('.likert-btn');
    buttons.forEach(btn => {
      const btnVal = parseInt(btn.getAttribute('data-val'), 10);
      if (btnVal === value) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    });

    // Mark dimension valid
    const container = document.getElementById(`dim-container-${dimensionId}`);
    if (container) container.classList.add('valid');

    saveLocalDraft();
    validateForm();
  }

  function validateForm() {
    const allFilled = Object.values(currentScores).every(v => v !== null && v >= 1 && v <= 5);
    saveNextBtn.disabled = !allFilled;
    if (allFilled) {
      saveNextBtn.classList.add('ready');
    } else {
      saveNextBtn.classList.remove('ready');
    }
  }

  // Authentication
  async function authenticate(token) {
    try {
      const res = await fetch(`/api/session?token=${encodeURIComponent(token)}`);
      if (!res.ok) {
        throw new Error('Invalid token');
      }
      currentUser = await res.json();
      currentToken = token;
      localStorage.setItem('hinglish_eval_token', token);

      hideAuthModal();
      annotatorNameEl.textContent = currentUser.name;
      annotatorPill.style.display = 'flex';

      if (currentUser.role === 'admin') {
        showAdminView();
      } else {
        showEvalView();
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.get('item')) {
          try {
            const nextRes = await fetch(`/api/next_unanswered?current_index=1&token=${encodeURIComponent(currentToken)}`);
            if (nextRes.ok) {
              const nextData = await nextRes.json();
              if (nextData && nextData.next_index) {
                currentIndex = nextData.next_index;
              }
            }
          } catch (e) {
            console.warn('Auto-resume lookup fallback:', e);
          }
        }
        loadItem(currentIndex);
      }
      showToast(`Welcome, ${currentUser.name}!`, 'success');
    } catch (err) {
      showToast('Authentication failed. Please check your access token.', 'error');
      showAuthModal();
    }
  }

  function showAuthModal() {
    authModal.style.display = 'flex';
  }

  function hideAuthModal() {
    authModal.style.display = 'none';
  }

  function showEvalView() {
    evalView.style.display = 'flex';
    adminView.style.display = 'none';
  }

  function showAdminView() {
    evalView.style.display = 'none';
    adminView.style.display = 'flex';
    loadAdminOverview();
  }

  // Load Item
  async function loadItem(index) {
    if (index < 1 || index > 500) return;
    currentIndex = index;
    localStorage.setItem('hinglish_eval_last_idx', index);
    jumpInput.value = index;

    // Reset scores state
    currentScores = {
      fluency: null,
      code_mixing_naturalness: null,
      hindi_grammar: null,
      prompt_adherence: null,
      spelling_consistency: null,
      overall: null
    };
    notesTextarea.value = '';

    // Clear UI buttons
    document.querySelectorAll('.likert-btn').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.dimension-item').forEach(item => item.classList.remove('valid'));

    try {
      const res = await fetch(`/api/item?item_index=${index}&token=${encodeURIComponent(currentToken)}`);
      if (!res.ok) {
        throw new Error('Failed to load item');
      }
      const data = await res.json();
      currentItem = data.item;
      updateProgressUI(data.progress);

      // Render Item Stimulus
      const catLabel = currentItem.category ? ` • Category: ${currentItem.category}` : '';
      const remLabel = (currentItem.item_index >= 430) ? ` • Remaining #${currentItem.item_index - 429} of 71` : '';
      itemIndexBadge.textContent = `Response #${currentItem.item_index} of 500 (${currentItem.assignment_id})${catLabel}${remLabel}`;
      promptContent.textContent = currentItem.prompt;
      responseContent.textContent = currentItem.response;

      if (currentItem.source_text && currentItem.source_text.trim()) {
        sourceTextBox.style.display = 'block';
        sourceTextContent.textContent = currentItem.source_text;
      } else {
        sourceTextBox.style.display = 'none';
      }

      if (currentItem.is_rated && currentItem.current_ratings) {
        itemStatusBadge.textContent = 'Saved';
        itemStatusBadge.className = 'status-badge saved';

        // Pre-fill existing ratings for editing
        for (const [dim, val] of Object.entries(currentItem.current_ratings)) {
          if (dim === 'notes') {
            notesTextarea.value = val || '';
          } else if (val) {
            setScore(dim, val);
          }
        }
      } else {
        itemStatusBadge.textContent = 'Unrated';
        itemStatusBadge.className = 'status-badge unrated';

        // Check for local unsaved draft
        const draftKey = `hinglish_draft_${currentItem.assignment_id}`;
        const draftJson = localStorage.getItem(draftKey);
        if (draftJson) {
          try {
            const draftData = JSON.parse(draftJson);
            if (draftData.scores) {
              for (const [dim, val] of Object.entries(draftData.scores)) {
                if (val) setScore(dim, val);
              }
            }
            if (draftData.notes) {
              notesTextarea.value = draftData.notes;
            }
            itemStatusBadge.textContent = 'Draft (Unsaved)';
          } catch (e) {}
        }
      }

      prevBtn.disabled = currentIndex <= 1;
      validateForm();
    } catch (err) {
      showToast('Error loading response stimulus: ' + err.message, 'error');
    }
  }

  function updateProgressUI(progress) {
    if (!progress) return;
    progressText.textContent = `Completed: ${progress.total_completed} / ${progress.total_assigned} responses (${progress.remaining} remaining)`;
    progressPercent.textContent = `${progress.completion_percentage}%`;
    progressFill.style.width = `${progress.completion_percentage}%`;
  }

  // Save Rating
  async function saveRating() {
    if (!currentItem) return;
    const allFilled = Object.values(currentScores).every(v => v !== null && v >= 1 && v <= 5);
    if (!allFilled) {
      showToast('Please rate all 6 dimensions before saving.', 'error');
      return;
    }

    const payload = {
      assignment_id: currentItem.assignment_id,
      fluency: currentScores.fluency,
      code_mixing_naturalness: currentScores.code_mixing_naturalness,
      hindi_grammar: currentScores.hindi_grammar,
      prompt_adherence: currentScores.prompt_adherence,
      spelling_consistency: currentScores.spelling_consistency,
      overall: currentScores.overall,
      notes: notesTextarea.value.trim()
    };

    saveNextBtn.disabled = true;
    saveNextBtn.textContent = 'Saving...';

    try {
      const res = await fetch(`/api/rate?token=${encodeURIComponent(currentToken)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Save failed');
      }

      const resData = await res.json();
      showToast(resData.message || 'Saved successfully!', 'success');

      // Clear draft on successful persistent save
      try {
        localStorage.removeItem(`hinglish_draft_${currentItem.assignment_id}`);
      } catch (e) {}

      updateProgressUI(resData.progress);

      // Advance to next item if available
      if (currentIndex < 500) {
        loadItem(currentIndex + 1);
      } else {
        showToast('Congratulations! You have completed all 500 assignments!', 'success');
        loadItem(currentIndex);
      }
    } catch (err) {
      showToast('Error saving rating: ' + err.message, 'error');
    } finally {
      saveNextBtn.disabled = false;
      saveNextBtn.innerHTML = 'Save & Next ➔';
      validateForm();
    }
  }

  // Next Unanswered
  async function jumpToNextUnanswered() {
    try {
      const res = await fetch(`/api/next_unanswered?current_index=${currentIndex}&token=${encodeURIComponent(currentToken)}`);
      if (!res.ok) throw new Error('Failed to find next unanswered item');
      const data = await res.json();
      if (data.next_index === currentIndex && currentItem && currentItem.is_rated) {
        showToast('All items appear to be rated!', 'success');
      } else {
        loadItem(data.next_index);
      }
    } catch (err) {
      showToast('Error: ' + err.message, 'error');
    }
  }

  // Admin Overview
  async function loadAdminOverview() {
    try {
      const res = await fetch(`/api/admin/overview?token=${encodeURIComponent(currentToken)}`);
      if (!res.ok) throw new Error('Failed to load admin overview');
      const data = await res.json();

      adminOverviewContainer.innerHTML = `
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Annotator A (Lead Researcher)</span>
            <span class="status-badge saved">${data.progress_a.completion_percentage}% Done</span>
          </div>
          <div class="stat-numbers">
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_a.total_completed}</div>
              <div class="stat-num-lbl">Completed</div>
            </div>
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_a.remaining}</div>
              <div class="stat-num-lbl">Remaining</div>
            </div>
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_a.total_assigned}</div>
              <div class="stat-num-lbl">Total</div>
            </div>
          </div>
          <div class="progress-track" style="margin-top:0.5rem;">
            <div class="progress-fill" style="width:${data.progress_a.completion_percentage}%;"></div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Annotator B (Independent Evaluator)</span>
            <span class="status-badge saved">${data.progress_b.completion_percentage}% Done</span>
          </div>
          <div class="stat-numbers">
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_b.total_completed}</div>
              <div class="stat-num-lbl">Completed</div>
            </div>
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_b.remaining}</div>
              <div class="stat-num-lbl">Remaining</div>
            </div>
            <div class="stat-num-box">
              <div class="stat-num-val">${data.progress_b.total_assigned}</div>
              <div class="stat-num-lbl">Total</div>
            </div>
          </div>
          <div class="progress-track" style="margin-top:0.5rem;">
            <div class="progress-fill" style="width:${data.progress_b.completion_percentage}%;"></div>
          </div>
        </div>
      `;
    } catch (err) {
      showToast('Error loading admin statistics: ' + err.message, 'error');
    }
  }

  // Export Combined Dataset
  async function triggerExport() {
    exportBtn.disabled = true;
    exportBtn.textContent = 'Generating verified exports...';
    exportStatus.textContent = 'Combining databases and running strict validation checks...';

    try {
      const res = await fetch(`/api/export?token=${encodeURIComponent(currentToken)}`, {
        method: 'POST'
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Export failed');
      }
      const data = await res.json();
      exportStatus.innerHTML = `
        <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); padding:1rem; border-radius:8px; margin-top:1rem;">
          <h4 style="color:var(--success); margin-bottom:0.5rem;">✓ Combined Exports Generated Successfully</h4>
          <p style="font-size:0.85rem; margin-bottom:0.75rem;">${data.summary.summary_text}</p>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
            <a href="/api/download/combined_human_ratings_1000.csv?token=${encodeURIComponent(currentToken)}" class="btn-secondary" download>Download combined_human_ratings_1000.csv</a>
            <a href="/api/download/annotator_A_ratings.csv?token=${encodeURIComponent(currentToken)}" class="btn-secondary" download>Download annotator_A_ratings.csv</a>
            <a href="/api/download/annotator_B_ratings.csv?token=${encodeURIComponent(currentToken)}" class="btn-secondary" download>Download annotator_B_ratings.csv</a>
            <a href="/api/download/human_validation_report.md?token=${encodeURIComponent(currentToken)}" class="btn-secondary" download>Download Human Validation Report</a>
          </div>
        </div>
      `;
      showToast('Combined dataset exported successfully!', 'success');
    } catch (err) {
      exportStatus.innerHTML = `<p style="color:var(--danger); margin-top:0.5rem;">Export Error: ${err.message}</p>`;
      showToast('Export failed: ' + err.message, 'error');
    } finally {
      exportBtn.disabled = false;
      exportBtn.textContent = 'Run & Export Combined Human Ratings';
    }
  }

  // Event Listeners
  function attachEventListeners() {
    loginBtn.addEventListener('click', () => {
      const token = tokenInput.value.trim();
      if (token) authenticate(token);
    });

    tokenInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const token = tokenInput.value.trim();
        if (token) authenticate(token);
      }
    });

    themeToggleBtn.addEventListener('click', toggleTheme);
    if (notesTextarea) {
      notesTextarea.addEventListener('input', saveLocalDraft);
    }

    prevBtn.addEventListener('click', () => {
      if (currentIndex > 1) loadItem(currentIndex - 1);
    });

    saveNextBtn.addEventListener('click', saveRating);

    jumpBtn.addEventListener('click', () => {
      const target = parseInt(jumpInput.value, 10);
      if (target >= 1 && target <= 500) {
        loadItem(target);
      } else {
        showToast('Please enter an item number between 1 and 500.', 'error');
      }
    });

    jumpInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') jumpBtn.click();
    });

    nextUnansweredBtn.addEventListener('click', jumpToNextUnanswered);

    if (exportBtn) {
      exportBtn.addEventListener('click', triggerExport);
    }

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      // Ignore if typing in text inputs
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (e.key === 'Enter' && e.ctrlKey) {
          saveRating();
        }
        return;
      }

      if (e.altKey && (e.key === 's' || e.key === 'S')) {
        e.preventDefault();
        saveRating();
      } else if (e.altKey && (e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        if (currentIndex > 1) loadItem(currentIndex - 1);
      } else if (e.altKey && (e.key === 'u' || e.key === 'U')) {
        e.preventDefault();
        jumpToNextUnanswered();
      }
    });
  }

  // Toast Notification
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // Bootstrap
  document.addEventListener('DOMContentLoaded', init);
})();
