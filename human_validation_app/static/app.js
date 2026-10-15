/**
 * HinglishEval Human Validation Application
 * Production client managing double-blind evaluation, state persistence,
 * verified server autosave, resume navigation, and offline recovery.
 */

(() => {
  "use strict";

  // Application State
  const state = {
    currentUser: null,
    currentItem: null,
    currentIndex: 1,
    totalItems: 4000,
    saveTimeout: null,
    hasPendingChanges: false,
    isSaving: false
  };

  // DOM Elements
  const el = {
    appContainer: document.getElementById("app-container"),
    loginModal: document.getElementById("login-modal"),
    loginForm: document.getElementById("login-form"),
    accessCodeInput: document.getElementById("access-code-input"),
    loginError: document.getElementById("login-error"),
    loginSubmitBtn: document.getElementById("login-submit-btn"),
    
    annotatorPill: document.getElementById("annotator-pill"),
    annotatorLabel: document.getElementById("annotator-label"),
    logoutBtn: document.getElementById("logout-btn"),
    themeToggleBtn: document.getElementById("theme-toggle-btn"),
    rubricBtn: document.getElementById("rubric-btn"),
    rubricModal: document.getElementById("rubric-modal"),
    closeRubricBtn: document.getElementById("close-rubric-btn"),
    dismissRubricBtn: document.getElementById("dismiss-rubric-btn"),
    
    progressText: document.getElementById("progress-text"),
    progressPercent: document.getElementById("progress-percent"),
    progressFill: document.getElementById("progress-fill"),
    jumpIndexInput: document.getElementById("jump-index-input"),
    jumpGoBtn: document.getElementById("jump-go-btn"),
    resumeUnratedBtn: document.getElementById("resume-unrated-btn"),
    
    itemBadge: document.getElementById("item-badge"),
    completionBadge: document.getElementById("completion-badge"),
    sourceBox: document.getElementById("source-box"),
    sourceTextContent: document.getElementById("source-text-content"),
    promptContent: document.getElementById("prompt-content"),
    responseContent: document.getElementById("response-content"),
    
    saveStatusBadge: document.getElementById("save-status-badge"),
    saveStatusText: document.getElementById("save-status-text"),
    ratingForm: document.getElementById("rating-form"),
    notesInput: document.getElementById("notes-input"),
    prevItemBtn: document.getElementById("prev-item-btn"),
    saveNextBtn: document.getElementById("save-next-btn"),
    navStatusMsg: document.getElementById("nav-status-msg")
  };

  const DIMENSIONS = [
    "fluency",
    "code_mixing_naturalness",
    "hindi_grammar",
    "prompt_adherence",
    "spelling_consistency",
    "overall"
  ];

  // --- API Helper ---
  async function apiFetch(endpoint, options = {}) {
    options.headers = options.headers || {};
    if (!options.headers["Content-Type"] && !(options.body instanceof FormData)) {
      options.headers["Content-Type"] = "application/json";
    }
    // Include credentials for HTTP-only cookies
    options.credentials = "same-origin";

    const response = await fetch(endpoint, options);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || "Request failed");
    }
    return response.json();
  }

  // --- Theme Management ---
  function initTheme() {
    const saved = localStorage.getItem("hinglisheval_theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("hinglisheval_theme", next);
  }

  // --- UI Save Indicator State ---
  function setSaveStatus(type, message) {
    el.saveStatusBadge.className = `save-status-badge ${type}`;
    if (type === "saved") {
      el.saveStatusBadge.querySelector(".save-icon").textContent = "✓";
      el.saveStatusText.textContent = message || "Saved";
    } else if (type === "saving") {
      el.saveStatusBadge.querySelector(".save-icon").textContent = "⏳";
      el.saveStatusText.textContent = "Saving...";
    } else if (type === "failed") {
      el.saveStatusBadge.querySelector(".save-icon").textContent = "⚠️";
      el.saveStatusText.textContent = message || "Save Failed";
    }
  }

  // --- Authentication ---
  async function checkAuth() {
    try {
      // Check query parameter ?token= for direct links
      const urlParams = new URLSearchParams(window.location.search);
      const tokenParam = urlParams.get("token");
      if (tokenParam) {
        await handleLogin(tokenParam);
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
      }

      const data = await apiFetch("/api/me");
      state.currentUser = data;
      onAuthSuccess(data);
    } catch {
      showLoginModal();
    }
  }

  function showLoginModal() {
    el.appContainer.style.display = "none";
    el.annotatorPill.style.display = "none";
    el.logoutBtn.style.display = "none";
    el.loginModal.style.display = "flex";
    el.accessCodeInput.focus();
  }

  function onAuthSuccess(userData) {
    el.loginModal.style.display = "none";
    el.annotatorPill.style.display = "flex";
    el.annotatorLabel.textContent = userData.display_name;
    el.logoutBtn.style.display = "inline-flex";
    el.appContainer.style.display = "flex";

    updateProgressUI(userData.progress);

    // Initial load: either next unrated or item from URL hash
    const hash = window.location.hash.replace("#", "");
    const requestedIndex = parseInt(hash, 10);
    if (!isNaN(requestedIndex) && requestedIndex >= 1 && requestedIndex <= state.totalItems) {
      loadItem(requestedIndex);
    } else if (userData.progress && userData.progress.next_unrated_index) {
      loadItem(userData.progress.next_unrated_index);
    } else {
      loadItem(1);
    }
  }

  async function handleLogin(code) {
    el.loginError.style.display = "none";
    el.loginSubmitBtn.disabled = true;
    el.loginSubmitBtn.textContent = "Authenticating...";

    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ access_code: code })
      });
      state.currentUser = data.user;
      state.currentUser.progress = data.progress;
      onAuthSuccess(state.currentUser);
    } catch (err) {
      el.loginError.textContent = err.message;
      el.loginError.style.display = "block";
    } finally {
      el.loginSubmitBtn.disabled = false;
      el.loginSubmitBtn.textContent = "Sign In & Start Rating";
    }
  }

  async function handleLogout() {
    if (state.hasPendingChanges) {
      if (!confirm("You have unsaved changes. Are you sure you want to sign out?")) {
        return;
      }
    }
    await apiFetch("/api/auth/logout", { method: "POST" }).catch(() => {});
    state.currentUser = null;
    showLoginModal();
  }

  // --- Progress UI Update ---
  function updateProgressUI(prog) {
    if (!prog) return;
    const completed = prog.completed_count || 0;
    const total = prog.total_count || state.totalItems;
    const pct = prog.percentage !== undefined ? prog.percentage : ((completed / total) * 100).toFixed(1);

    el.progressText.textContent = `${completed.toLocaleString()} / ${total.toLocaleString()} completed`;
    el.progressPercent.textContent = `${pct}%`;
    el.progressFill.style.width = `${pct}%`;
  }

  // --- Stimulus & Annotation Loading ---
  async function loadItem(index) {
    if (state.hasPendingChanges) {
      await saveCurrentRating();
    }

    state.currentIndex = index;
    el.jumpIndexInput.value = index;
    window.location.hash = `#${index}`;

    // Update navigation button states
    el.prevItemBtn.disabled = index <= 1;
    el.saveNextBtn.textContent = index >= state.totalItems ? "Save & Finish" : "Save & Next →";

    try {
      const data = await apiFetch(`/api/responses/by_index/${index}`);
      state.currentItem = data.item;
      renderItem(data.item, data.existing_annotation);
      updateProgressUI(data.progress);
    } catch (err) {
      alert(`Error loading response #${index}: ${err.message}`);
    }
  }

  function renderItem(item, annotation) {
    el.itemBadge.textContent = `Response #${item.item_index} of ${state.totalItems} (${item.blinded_id || ('RESP_' + String(item.item_index).padStart(4, '0'))})`;
    el.promptContent.textContent = item.prompt;
    el.responseContent.textContent = item.response;

    if (item.source_text && item.source_text.trim()) {
      el.sourceTextContent.textContent = item.source_text;
      el.sourceBox.style.display = "flex";
    } else {
      el.sourceBox.style.display = "none";
    }

    // Reset radio buttons
    DIMENSIONS.forEach(dim => {
      const radios = el.ratingForm.elements[dim];
      if (radios) {
        if (radios instanceof RadioNodeList) {
          radios.value = "";
        } else {
          radios.checked = false;
        }
      }
    });
    el.notesInput.value = "";

    // Populate with existing annotation if any
    if (annotation) {
      DIMENSIONS.forEach(dim => {
        const val = annotation[dim];
        if (val) {
          const radio = el.ratingForm.querySelector(`input[name="${dim}"][value="${val}"]`);
          if (radio) radio.checked = true;
        }
      });
      el.notesInput.value = annotation.notes || "";

      if (annotation.is_completed) {
        el.completionBadge.className = "completion-badge complete";
        el.completionBadge.textContent = "Complete";
      } else {
        el.completionBadge.className = "completion-badge incomplete";
        el.completionBadge.textContent = "Incomplete";
      }

      setSaveStatus("saved", `Saved (${formatTime(annotation.updated_at)})`);
    } else {
      el.completionBadge.className = "completion-badge incomplete";
      el.completionBadge.textContent = "Unrated";
      setSaveStatus("saved", "Ready");
    }

    state.hasPendingChanges = false;
  }

  function formatTime(isoString) {
    if (!isoString) return "";
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return "";
    }
  }

  // --- Autosave Implementation ---
  function getFormData() {
    const payload = {
      response_id: state.currentItem ? state.currentItem.response_id : "",
      notes: el.notesInput.value.trim()
    };

    DIMENSIONS.forEach(dim => {
      const checked = el.ratingForm.querySelector(`input[name="${dim}"]:checked`);
      payload[dim] = checked ? parseInt(checked.value, 10) : null;
    });

    return payload;
  }

  async function saveCurrentRating() {
    if (!state.currentItem) return;

    const payload = getFormData();
    setSaveStatus("saving", "Saving...");
    state.isSaving = true;

    try {
      const res = await apiFetch("/api/annotations/save", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      setSaveStatus("saved", `Saved at ${res.saved_at}`);
      state.hasPendingChanges = false;
      state.isSaving = false;

      // Update completion badge
      if (res.is_completed) {
        el.completionBadge.className = "completion-badge complete";
        el.completionBadge.textContent = "Complete";
      } else {
        el.completionBadge.className = "completion-badge incomplete";
        el.completionBadge.textContent = "Incomplete";
      }

      updateProgressUI(res.progress);
      return res;
    } catch (err) {
      setSaveStatus("failed", "Save Failed — Click to retry");
      state.isSaving = false;
      state.hasPendingChanges = true;
      throw err;
    }
  }

  function triggerAutosave(immediate = false) {
    state.hasPendingChanges = true;
    setSaveStatus("saving", "Saving...");

    if (state.saveTimeout) {
      clearTimeout(state.saveTimeout);
    }

    if (immediate) {
      saveCurrentRating().catch(err => {
        console.error("Immediate save error:", err);
      });
    } else {
      state.saveTimeout = setTimeout(() => {
        saveCurrentRating().catch(err => {
          console.error("Debounced save error:", err);
        });
      }, 350);
    }
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Theme toggle
    el.themeToggleBtn.addEventListener("click", toggleTheme);

    // Rubric modal
    el.rubricBtn.addEventListener("click", () => el.rubricModal.style.display = "flex");
    el.closeRubricBtn.addEventListener("click", () => el.rubricModal.style.display = "none");
    el.dismissRubricBtn.addEventListener("click", () => el.rubricModal.style.display = "none");
    el.rubricModal.addEventListener("click", (e) => {
      if (e.target === el.rubricModal) el.rubricModal.style.display = "none";
    });

    // Login
    el.loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const code = el.accessCodeInput.value.trim();
      if (code) handleLogin(code);
    });

    // Logout
    el.logoutBtn.addEventListener("click", handleLogout);

    // Form inputs: Radio clicks trigger immediate autosave
    DIMENSIONS.forEach(dim => {
      const inputs = el.ratingForm.querySelectorAll(`input[name="${dim}"]`);
      inputs.forEach(input => {
        input.addEventListener("change", () => triggerAutosave(true));
      });
    });

    // Notes: Debounced autosave on typing, immediate on blur
    el.notesInput.addEventListener("input", () => triggerAutosave(false));
    el.notesInput.addEventListener("blur", () => {
      if (state.hasPendingChanges) triggerAutosave(true);
    });

    // Retry save when clicking failed status badge
    el.saveStatusBadge.addEventListener("click", () => {
      if (state.hasPendingChanges || el.saveStatusBadge.classList.contains("failed")) {
        triggerAutosave(true);
      }
    });

    // Navigation buttons
    el.prevItemBtn.addEventListener("click", () => {
      if (state.currentIndex > 1) {
        loadItem(state.currentIndex - 1);
      }
    });

    el.saveNextBtn.addEventListener("click", async () => {
      try {
        await saveCurrentRating();
        if (state.currentIndex < state.totalItems) {
          loadItem(state.currentIndex + 1);
        } else {
          alert("Congratulations! You have reached the end of the 4,000 responses. Check your progress bar for total completion.");
        }
      } catch (err) {
        alert(`Cannot proceed: Save failed (${err.message}). Please check your connection and retry.`);
      }
    });

    // Jump navigation
    el.jumpGoBtn.addEventListener("click", () => {
      const val = parseInt(el.jumpIndexInput.value, 10);
      if (!isNaN(val) && val >= 1 && val <= state.totalItems) {
        loadItem(val);
      } else {
        alert(`Please enter a valid item index between 1 and ${state.totalItems}`);
      }
    });

    el.jumpIndexInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        el.jumpGoBtn.click();
      }
    });

    // Resume next unrated
    el.resumeUnratedBtn.addEventListener("click", async () => {
      try {
        const res = await apiFetch("/api/responses/next_unrated");
        loadItem(res.next_index);
      } catch (err) {
        alert(`Could not fetch next unrated item: ${err.message}`);
      }
    });

    // Keyboard navigation (Alt + Left / Alt + Right)
    window.addEventListener("keydown", (e) => {
      if (e.altKey && e.key === "ArrowRight") {
        e.preventDefault();
        el.saveNextBtn.click();
      } else if (e.altKey && e.key === "ArrowLeft") {
        e.preventDefault();
        el.prevItemBtn.click();
      }
    });

    // Offline & Beforeunload protection
    window.addEventListener("beforeunload", (e) => {
      if (state.hasPendingChanges || state.isSaving) {
        e.preventDefault();
        e.returnValue = "You have unsaved ratings. Are you sure you want to leave?";
        return e.returnValue;
      }
    });

    window.addEventListener("offline", () => {
      setSaveStatus("failed", "Network Offline");
    });

    window.addEventListener("online", () => {
      if (state.hasPendingChanges) {
        triggerAutosave(true);
      } else {
        setSaveStatus("saved", "Back Online");
      }
    });
  }

  // Initialization
  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupEventListeners();
    checkAuth();
  });

})();
