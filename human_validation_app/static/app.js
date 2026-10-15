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
    isSaving: false,
    unansweredData: null,
    unansweredFilterText: ""
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
    unansweredPill: document.getElementById("unanswered-pill"),
    unansweredPillCount: document.getElementById("unanswered-pill-count"),
    jumpIndexInput: document.getElementById("jump-index-input"),
    jumpGoBtn: document.getElementById("jump-go-btn"),
    resumeUnratedBtn: document.getElementById("resume-unrated-btn"),
    unansweredModalBtn: document.getElementById("unanswered-modal-btn"),
    unansweredCountBadge: document.getElementById("unanswered-count-badge"),

    // Unanswered Modal Elements
    unansweredModal: document.getElementById("unanswered-modal"),
    closeUnansweredBtn: document.getElementById("close-unanswered-btn"),
    dismissUnansweredBtn: document.getElementById("dismiss-unanswered-btn"),
    modalStatCompleted: document.getElementById("modal-stat-completed"),
    modalStatUnanswered: document.getElementById("modal-stat-unanswered"),
    modalStatTotal: document.getElementById("modal-stat-total"),
    modalStatPercent: document.getElementById("modal-stat-percent"),
    unansweredSearchInput: document.getElementById("unanswered-search-input"),
    clearSearchBtn: document.getElementById("clear-search-btn"),
    searchMetaText: document.getElementById("search-meta-text"),
    unansweredListContainer: document.getElementById("unanswered-list-container"),

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
    footerResumeBtn: document.getElementById("footer-resume-btn"),
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
    fetchUnansweredItems(false);

    // Initial load: either next unrated or item from URL hash
    const hash = window.location.hash.replace("#", "");
    const requestedIndex = parseInt(hash, 10);
    const isCompleted = userData.progress && userData.progress.completed_count >= state.totalItems;
    const nextUnrated = userData.progress && userData.progress.next_unrated_index ? userData.progress.next_unrated_index : 1;

    if (!isCompleted && requestedIndex === state.totalItems) {
      // Reached item 4000 earlier but responses remain unanswered -> jump directly to next unrated
      loadItem(nextUnrated);
    } else if (!isNaN(requestedIndex) && requestedIndex >= 1 && requestedIndex <= state.totalItems) {
      loadItem(requestedIndex);
    } else if (nextUnrated) {
      loadItem(nextUnrated);
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
    const unanswered = prog.unanswered_count !== undefined ? prog.unanswered_count : Math.max(0, total - completed);
    const pct = prog.percentage !== undefined ? prog.percentage : ((completed / total) * 100).toFixed(1);

    el.progressText.textContent = `${completed.toLocaleString()} / ${total.toLocaleString()} completed`;
    el.progressPercent.textContent = `${pct}%`;
    el.progressFill.style.width = `${pct}%`;

    if (el.unansweredCountBadge) {
      el.unansweredCountBadge.textContent = unanswered.toLocaleString();
    }
    if (el.unansweredPill && el.unansweredPillCount) {
      el.unansweredPillCount.textContent = unanswered.toLocaleString();
      el.unansweredPill.style.display = unanswered > 0 ? "inline-flex" : "none";
    }
    if (el.modalStatCompleted) el.modalStatCompleted.textContent = completed.toLocaleString();
    if (el.modalStatUnanswered) el.modalStatUnanswered.textContent = unanswered.toLocaleString();
    if (el.modalStatTotal) el.modalStatTotal.textContent = total.toLocaleString();
    if (el.modalStatPercent) el.modalStatPercent.textContent = `${pct}%`;
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
      fetchUnansweredItems(true).catch(() => {});
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

  // --- Unanswered Responses Management ---
  async function fetchUnansweredItems(renderIfOpen = true) {
    try {
      const data = await apiFetch("/api/responses/unanswered");
      state.unansweredData = data;

      // Update UI stats & badges
      updateProgressUI({
        completed_count: data.completed_count,
        total_count: data.total_count,
        unanswered_count: data.unanswered_count,
        percentage: data.percentage
      });

      if (renderIfOpen && el.unansweredModal && el.unansweredModal.style.display !== "none") {
        renderUnansweredList();
      }
      return data;
    } catch (err) {
      console.error("Failed to fetch unanswered items:", err);
      if (el.searchMetaText) {
        el.searchMetaText.textContent = `Error loading items: ${err.message}`;
      }
    }
  }

  function renderUnansweredList() {
    if (!state.unansweredData || !el.unansweredListContainer) return;

    const allItems = state.unansweredData.items || [];
    const filter = (state.unansweredFilterText || "").trim().toLowerCase();

    // Toggle clear search button
    if (el.clearSearchBtn) {
      el.clearSearchBtn.style.display = filter ? "block" : "none";
    }

    const filtered = filter
      ? allItems.filter(item => {
          const idxStr = String(item.item_index);
          const bId = (item.blinded_id || "").toLowerCase();
          const rId = (item.response_id || "").toLowerCase();
          const snip = (item.prompt_snippet || "").toLowerCase();
          return idxStr.includes(filter) || bId.includes(filter) || rId.includes(filter) || snip.includes(filter);
        })
      : allItems;

    if (el.searchMetaText) {
      if (allItems.length === 0) {
        el.searchMetaText.textContent = "All 4,000 responses completed!";
      } else if (filter) {
        el.searchMetaText.textContent = `Showing ${filtered.length.toLocaleString()} of ${allItems.length.toLocaleString()} unanswered responses`;
      } else {
        el.searchMetaText.textContent = `Total unanswered: ${allItems.length.toLocaleString()} responses across benchmark`;
      }
    }

    if (allItems.length === 0) {
      el.unansweredListContainer.innerHTML = `
        <div class="unanswered-empty-state">
          <div class="unanswered-empty-icon">🎉</div>
          <strong>Evaluation Complete!</strong>
          <span>All 4,000 responses have been evaluated across all six dimensions.</span>
        </div>
      `;
      return;
    }

    if (filtered.length === 0) {
      el.unansweredListContainer.innerHTML = `
        <div class="unanswered-empty-state">
          <div class="unanswered-empty-icon">🔍</div>
          <strong>No matches found</strong>
          <span>No unanswered responses match "${escapeHtml(filter)}".</span>
        </div>
      `;
      return;
    }

    const fragment = document.createDocumentFragment();

    filtered.forEach(item => {
      const row = document.createElement("div");
      row.className = "unanswered-item-row";
      row.setAttribute("role", "button");
      row.setAttribute("tabindex", "0");
      row.setAttribute("title", `Open Response #${item.item_index}`);

      const infoDiv = document.createElement("div");
      infoDiv.className = "unanswered-item-info";

      const headerDiv = document.createElement("div");
      headerDiv.className = "unanswered-item-header";

      const indexSpan = document.createElement("span");
      indexSpan.className = "unanswered-item-index";
      indexSpan.textContent = `Item #${item.item_index}`;

      const idSpan = document.createElement("span");
      idSpan.className = "unanswered-item-id";
      idSpan.textContent = item.blinded_id || `RESP_${String(item.item_index).padStart(4, '0')}`;

      headerDiv.appendChild(indexSpan);
      headerDiv.appendChild(idSpan);

      if (item.response_id && item.response_id !== item.blinded_id) {
        const canonicalSpan = document.createElement("span");
        canonicalSpan.className = "unanswered-canonical-id";
        canonicalSpan.textContent = `(${item.response_id})`;
        headerDiv.appendChild(canonicalSpan);
      }

      const promptDiv = document.createElement("div");
      promptDiv.className = "unanswered-prompt-snippet";
      promptDiv.textContent = item.prompt_snippet || "Prompt stimulus";

      infoDiv.appendChild(headerDiv);
      infoDiv.appendChild(promptDiv);

      const openBtn = document.createElement("button");
      openBtn.type = "button";
      openBtn.className = "btn-small btn-primary open-item-btn";
      openBtn.textContent = "Open →";

      row.appendChild(infoDiv);
      row.appendChild(openBtn);

      const handleSelect = () => {
        el.unansweredModal.style.display = "none";
        loadItem(item.item_index);
      };

      row.addEventListener("click", handleSelect);
      row.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleSelect();
        }
      });

      fragment.appendChild(row);
    });

    el.unansweredListContainer.innerHTML = "";
    el.unansweredListContainer.appendChild(fragment);
  }

  function escapeHtml(str) {
    return (str || "").replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
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

    // Unanswered Responses modal
    if (el.unansweredModalBtn) {
      el.unansweredModalBtn.addEventListener("click", async () => {
        el.unansweredModal.style.display = "flex";
        if (!state.unansweredData) {
          if (el.searchMetaText) el.searchMetaText.textContent = "Loading unanswered items from database...";
          await fetchUnansweredItems(true);
        } else {
          renderUnansweredList();
          fetchUnansweredItems(true);
        }
        if (el.unansweredSearchInput) {
          el.unansweredSearchInput.focus();
        }
      });
    }

    if (el.closeUnansweredBtn) {
      el.closeUnansweredBtn.addEventListener("click", () => {
        el.unansweredModal.style.display = "none";
      });
    }
    if (el.dismissUnansweredBtn) {
      el.dismissUnansweredBtn.addEventListener("click", () => {
        el.unansweredModal.style.display = "none";
      });
    }
    if (el.unansweredModal) {
      el.unansweredModal.addEventListener("click", (e) => {
        if (e.target === el.unansweredModal) el.unansweredModal.style.display = "none";
      });
    }

    if (el.unansweredSearchInput) {
      el.unansweredSearchInput.addEventListener("input", (e) => {
        state.unansweredFilterText = e.target.value;
        renderUnansweredList();
      });
    }

    if (el.clearSearchBtn) {
      el.clearSearchBtn.addEventListener("click", () => {
        el.unansweredSearchInput.value = "";
        state.unansweredFilterText = "";
        renderUnansweredList();
        el.unansweredSearchInput.focus();
      });
    }

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
        const res = await saveCurrentRating();
        const prog = res ? res.progress : (state.currentUser ? state.currentUser.progress : null);
        const completed = prog ? prog.completed_count : 0;
        const total = state.totalItems;

        if (completed >= total) {
          alert("Congratulations! You have completed all 4,000 responses! Evaluation is 100% complete.");
          return;
        }

        // If at the end of the item list (index 4,000) but responses remain incomplete:
        if (state.currentIndex >= total) {
          const nextUnrated = prog && prog.next_unrated_index ? prog.next_unrated_index : 1;
          alert(`Item #${state.currentIndex} saved! You have reached Item 4,000, but ${total - completed} responses remain unanswered. Jumping to your next unanswered response (#${nextUnrated})...`);
          loadItem(nextUnrated);
        } else {
          loadItem(state.currentIndex + 1);
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
        if (res.is_all_completed || (res.completed_count && res.completed_count >= state.totalItems)) {
          alert("All 4,000 responses are complete! No unanswered items remain.");
          return;
        }
        if (res.next_index === state.currentIndex) {
          alert(`You are already on the next unanswered response (#${res.next_index}).`);
        } else {
          loadItem(res.next_index);
        }
      } catch (err) {
        alert(`Could not fetch next unrated item: ${err.message}`);
      }
    });

    if (el.footerResumeBtn) {
      el.footerResumeBtn.addEventListener("click", () => {
        el.resumeUnratedBtn.click();
      });
    }

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
