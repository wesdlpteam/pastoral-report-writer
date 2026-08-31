const API_URL = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  ? "http://localhost:5000"
  : "https://pastoral-report-writer.vercel.app";

const LS_TUTOR_GROUP = "pastoralLastTutorGroup";
const LS_HOUSE = "pastoralLastHouse";
const LS_YEAR_LEVEL = "pastoralLastYearLevel";
const LS_AUTOSAVE = "pastoralAutosave";
const LS_WELCOME_SEEN = "pastoralWelcomeSeen";

const QUESTIONS = {
  tutor: [
    [
      {
        id: "person",
        question: "Tell me about this student as a person. Which ROAR values (Respect, Opportunity, Achievement, Resilience) stand out?",
      },
      {
        id: "person",
        question: "How do they interact with peers? What makes them a valued member of the Tutor Group?",
      },
    ],
    [
      {
        id: "learner",
        question: "How are they progressing academically? What's their approach to learning and seeking feedback?",
        mypQuestion: "How are they progressing academically? Which Learner Profile attribute (e.g. Inquirer, Thinker, Communicator) or ATL skill (e.g. Research, Self-management) stands out in their approach to learning?",
      },
      {
        id: "learner",
        question: "Where have they shown growth or resilience this term?",
        mypQuestion: "Where have they shown growth or resilience this term? Does this connect to a Learner Profile attribute or ATL skill they're developing?",
      },
    ],
    [
      {
        id: "participant",
        question: "How does this student engage with the Tutor Group? Do they contribute to discussions and activities, or support their peers?",
      },
      {
        id: "participant",
        question: "What role do they play within the Tutor Group community? (e.g. supportive peer, active participant, quiet contributor)",
      },
    ],
    [
      {
        id: "summary",
        question: "What's a fitting summarising comment for this student? (their development, engagement with peers, leadership, Education Outdoors, or goals for next term)",
      },
      {
        id: "summary",
        question: "What has been a highlight, memorable moment, or general observation about this student this term?",
      },
    ],
  ],
};

const state = {
  reportType: null,
  formalName: null,
  preferredName: null,
  pronoun: null,
  yearLevel: null,
  tutorGroup: null,
  house: null,
  index: 0,
  answers: {},
  questionVariant: {},
  followupAsked: {},
  previousDraft: null,
  lastTargetRange: null,
};

const screenWelcome = document.getElementById("screen-welcome");
const startGuidedBtn = document.getElementById("start-guided-btn");
const startCheckBtn = document.getElementById("start-check-btn");

const screenCheckInput = document.getElementById("screen-check-input");
const checkTextInput = document.getElementById("check-text-input");
const checkInputError = document.getElementById("check-input-error");
const checkBackBtn = document.getElementById("check-back-btn");
const checkSubmitBtn = document.getElementById("check-submit-btn");

const screenCheckResult = document.getElementById("screen-check-result");
const checkErrorBanner = document.getElementById("check-error-banner");
const checkLoadingText = document.getElementById("check-loading-text");
const checkResultContent = document.getElementById("check-result-content");
const checkOriginalTextEl = document.getElementById("check-original-text");
const checkCorrectedTextEl = document.getElementById("check-corrected-text");
const checkChangesWrapper = document.getElementById("check-changes-wrapper");
const checkChangesList = document.getElementById("check-changes-list");
const checkNoChangesNote = document.getElementById("check-no-changes-note");
const checkCopyBtn = document.getElementById("check-copy-btn");
const checkAnotherBtn = document.getElementById("check-another-btn");

const screenName = document.getElementById("screen-name");
const formalNameInput = document.getElementById("formal-name-input");
const preferredNameInput = document.getElementById("preferred-name-input");
const nameNextBtn = document.getElementById("name-next-btn");
const nameError = document.getElementById("name-error");

const screenPronoun = document.getElementById("screen-pronouns");
const screenContext = document.getElementById("screen-context");
const screenQuestion = document.getElementById("screen-question");
const screenResult = document.getElementById("screen-result");

const progressText = document.getElementById("progress-text");
const questionText = document.getElementById("question-text");
const answerInput = document.getElementById("answer-input");
const answerError = document.getElementById("answer-error");
const backBtn = document.getElementById("back-btn");
const anotherBtn = document.getElementById("another-btn");
const nextBtn = document.getElementById("next-btn");
const generateBtn = document.getElementById("generate-btn");
const questionNavButtons = document.getElementById("question-nav-buttons");
const followupPanel = document.getElementById("followup-panel");
const followupLoading = document.getElementById("followup-loading");
const followupContent = document.getElementById("followup-content");
const followupQuestionEl = document.getElementById("followup-question");
const followupSuggestionsEl = document.getElementById("followup-suggestions");
const followupInput = document.getElementById("followup-input");
const followupContinueBtn = document.getElementById("followup-continue-btn");
const pronounNextBtn = document.getElementById("pronoun-next-btn");
const contextNextBtn = document.getElementById("context-next-btn");
const yearLevelSelect = document.getElementById("year-level-select");
const tutorGroupInput = document.getElementById("tutor-group-input");
const houseInput = document.getElementById("house-input");
const contextRememberedNote = document.getElementById("context-remembered-note");

const resumeBanner = document.getElementById("resume-banner");
const resumeBtn = document.getElementById("resume-btn");
const discardResumeBtn = document.getElementById("discard-resume-btn");

const errorBanner = document.getElementById("error-banner");
const loadingText = document.getElementById("loading-text");
const toneNote = document.getElementById("tone-note");
const notesDetails = document.getElementById("notes-details");
const notesList = document.getElementById("notes-list");
const updateNotesBtn = document.getElementById("update-notes-btn");
const draftText = document.getElementById("draft-text");
const wordCountText = document.getElementById("word-count-text");
const shortenBtn = document.getElementById("shorten-btn");
const lengthenBtn = document.getElementById("lengthen-btn");
const checklistNote = document.getElementById("checklist-note");
const copyBtn = document.getElementById("copy-btn");
const regenerateBtn = document.getElementById("regenerate-btn");
const usePreviousBtn = document.getElementById("use-previous-btn");
const startOverBtn = document.getElementById("start-over-btn");
const otherPronounDiv = document.getElementById("other-pronoun");
const customPronounInput = document.getElementById("custom-pronoun");
const progressTrack = document.getElementById("progress-track");
const progressFill = document.getElementById("progress-fill");

const TOTAL_STEPS = 8;
const MIN_WORDS = 5;
const THIN_ANSWER_WORDS = 15;

const BAD_WORDS = [
  "fuck", "fucking", "fucker", "shit", "shitty", "bitch", "bastard",
  "asshole", "ass", "dick", "piss", "cunt", "cock", "prick", "wanker",
  "twat", "slut", "whore", "retard", "retarded", "faggot", "fag",
  "nigger", "nigga", "spastic", "crap", "bloody", "bugger", "arse",
  "douche", "douchebag", "motherfucker",
];

function countWords(text) {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

function findBadWords(text) {
  const lower = text.toLowerCase();
  return BAD_WORDS.filter((word) => new RegExp(`\\b${word}\\b`, "i").test(lower));
}

const KEYBOARD_MASH_PATTERNS = ["asdf", "qwert", "zxcv", "hjkl", "jklm", "qazwsx", "wasdw"];
const VOWELS = new Set(["a", "e", "i", "o", "u", "y"]);

function isGibberishWord(word) {
  const clean = word.replace(/[^a-zA-Z]/g, "").toLowerCase();
  if (clean.length < 3) return false;
  if (/(.)\1{3,}/.test(clean)) return true;
  if (clean.length >= 4 && ![...clean].some((c) => VOWELS.has(c))) return true;
  return KEYBOARD_MASH_PATTERNS.some((pattern) => clean.includes(pattern));
}

function findGibberishWords(text) {
  return text.split(/\s+/).filter(isGibberishWord);
}

function hasLowWordDiversity(text) {
  const words = text.toLowerCase().split(/\s+/).filter(Boolean);
  if (words.length < 5) return false;
  const distinct = new Set(words).size;
  return distinct / words.length <= 0.4;
}

function setProgress(stepIndex) {
  const pct = Math.min(1, Math.max(0, stepIndex / TOTAL_STEPS));
  progressFill.style.transform = `scaleX(${pct})`;
  progressTrack.setAttribute("aria-valuenow", Math.round(pct * 100));
}

function saveAutosave() {
  if (!state.reportType) return;
  localStorage.setItem(
    LS_AUTOSAVE,
    JSON.stringify({
      reportType: state.reportType,
      formalName: state.formalName,
      preferredName: state.preferredName,
      pronoun: state.pronoun,
      yearLevel: state.yearLevel,
      tutorGroup: state.tutorGroup,
      house: state.house,
      index: state.index,
      answers: state.answers,
      questionVariant: state.questionVariant,
    })
  );
}

function clearAutosave() {
  localStorage.removeItem(LS_AUTOSAVE);
}

function loadAutosave() {
  try {
    const raw = localStorage.getItem(LS_AUTOSAVE);
    return raw ? JSON.parse(raw) : null;
  } catch (err) {
    return null;
  }
}

function prefillContext() {
  const savedTutorGroup = localStorage.getItem(LS_TUTOR_GROUP);
  const savedHouse = localStorage.getItem(LS_HOUSE);
  const savedYearLevel = localStorage.getItem(LS_YEAR_LEVEL);
  if (savedTutorGroup || savedHouse || savedYearLevel) {
    tutorGroupInput.value = savedTutorGroup || "";
    houseInput.value = savedHouse || "";
    yearLevelSelect.value = savedYearLevel || "";
    contextRememberedNote.classList.remove("hidden");
  } else {
    contextRememberedNote.classList.add("hidden");
  }
}

nameNextBtn.addEventListener("click", () => {
  const formalName = formalNameInput.value.trim();
  const preferredName = preferredNameInput.value.trim();

  if (!formalName) {
    nameError.textContent = "Please enter the student's formal name.";
    nameError.classList.remove("hidden");
    return;
  }
  if (findBadWords(formalName).length || findGibberishWords(formalName).length) {
    nameError.textContent = "Please check the formal name doesn't include swearing or nonsense text.";
    nameError.classList.remove("hidden");
    return;
  }
  if (preferredName && (findBadWords(preferredName).length || findGibberishWords(preferredName).length)) {
    nameError.textContent = "Please check the preferred name doesn't include swearing or nonsense text.";
    nameError.classList.remove("hidden");
    return;
  }

  nameError.classList.add("hidden");
  state.formalName = formalName;
  state.preferredName = preferredName || null;
  showScreen(screenPronoun);
  setProgress(2);
});

document.querySelectorAll(".pronoun-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".pronoun-btn").forEach((b) => b.classList.remove("selected"));
    btn.classList.add("selected");
    state.pronoun = btn.dataset.pronoun;

    if (state.pronoun === "other") {
      otherPronounDiv.classList.remove("hidden");
    } else {
      otherPronounDiv.classList.add("hidden");
    }
    pronounNextBtn.disabled = false;
  });
});

pronounNextBtn.addEventListener("click", () => {
  if (state.pronoun === "other") {
    state.pronoun = customPronounInput.value.trim().slice(0, 30) || "they/them";
  }
  prefillContext();
  showScreen(screenContext);
  setProgress(3);
});

contextNextBtn.addEventListener("click", () => {
  state.tutorGroup = tutorGroupInput.value.trim() || "(not specified)";
  state.house = houseInput.value.trim() || "(not specified)";
  state.yearLevel = yearLevelSelect.value || null;
  if (state.tutorGroup !== "(not specified)") {
    localStorage.setItem(LS_TUTOR_GROUP, state.tutorGroup);
  }
  if (state.house !== "(not specified)") {
    localStorage.setItem(LS_HOUSE, state.house);
  }
  if (state.yearLevel) {
    localStorage.setItem(LS_YEAR_LEVEL, state.yearLevel);
  }
  showScreen(screenQuestion);
  renderQuestion();
  saveAutosave();
});

function showScreen(screen) {
  [
    screenWelcome,
    screenCheckInput,
    screenCheckResult,
    screenName,
    screenPronoun,
    screenContext,
    screenQuestion,
    screenResult,
  ].forEach((s) => s.classList.add("hidden"));
  screen.classList.remove("hidden");
}

function currentQuestions() {
  return QUESTIONS[state.reportType] || QUESTIONS.tutor;
}

const MYP_YEAR_LEVELS = ["7", "8", "9", "10"];

function getDisplayQuestion(q) {
  if (MYP_YEAR_LEVELS.includes(state.yearLevel) && q.mypQuestion) {
    return { ...q, question: q.mypQuestion };
  }
  return q;
}

function currentQuestion() {
  const questions = currentQuestions();
  if (!Number.isInteger(state.index) || state.index < 0 || state.index >= questions.length) {
    state.index = 0;
  }
  const variants = questions[state.index];
  const rawVariantIdx = state.questionVariant[state.index];
  const variantIdx =
    Number.isInteger(rawVariantIdx) && rawVariantIdx >= 0 && rawVariantIdx < variants.length
      ? rawVariantIdx
      : 0;
  return getDisplayQuestion(variants[variantIdx]);
}

function renderQuestion() {
  const questions = currentQuestions();
  const q = currentQuestion();

  progressText.textContent = `Question ${state.index + 1} of ${questions.length}`;
  questionText.textContent = q.question;
  answerInput.value = state.answers[q.id] || "";
  answerError.classList.add("hidden");
  hideFollowupPanel();

  backBtn.classList.toggle("hidden", state.index === 0);
  const isLast = state.index === questions.length - 1;
  nextBtn.classList.toggle("hidden", isLast);
  generateBtn.classList.toggle("hidden", !isLast);

  setProgress(4 + state.index);
}

anotherBtn.addEventListener("click", () => {
  const q = currentQuestion();
  state.answers[q.id] = answerInput.value;
  const questions = currentQuestions();
  const variants = questions[state.index];
  const currentVariant = state.questionVariant[state.index] || 0;
  const nextVariant = (currentVariant + 1) % variants.length;
  state.questionVariant[state.index] = nextVariant;
  renderQuestion();
  saveAutosave();
});

backBtn.addEventListener("click", () => {
  const q = currentQuestion();
  state.answers[q.id] = answerInput.value;
  state.questionVariant[state.index] = 0;
  state.index -= 1;
  renderQuestion();
  saveAutosave();
});

function validateAnswer(textValue) {
  if (!textValue) {
    return "Please enter an answer before continuing.";
  }
  if (countWords(textValue) < MIN_WORDS) {
    return `Please write at least ${MIN_WORDS} words.`;
  }
  if (findBadWords(textValue).length) {
    return "Please rewrite this without inappropriate language.";
  }
  if (findGibberishWords(textValue).length) {
    return "This doesn't look like a real answer. Please write a genuine response.";
  }
  if (hasLowWordDiversity(textValue)) {
    return "This looks like repeated filler text. Please write a genuine response.";
  }
  return null;
}

let followupPendingQuestionId = null;
let followupPendingProceed = null;

function showFollowupPanel() {
  questionNavButtons.classList.add("hidden");
  followupPanel.classList.remove("hidden");
  followupLoading.classList.remove("hidden");
  followupContent.classList.add("hidden");
  followupInput.value = "";
}

function hideFollowupPanel() {
  followupPanel.classList.add("hidden");
  questionNavButtons.classList.remove("hidden");
}

async function maybeShowFollowup(q, textValue, proceed) {
  if (state.followupAsked[q.id] || countWords(textValue) >= THIN_ANSWER_WORDS) {
    proceed();
    return;
  }

  followupPendingQuestionId = q.id;
  followupPendingProceed = proceed;
  showFollowupPanel();

  try {
    const response = await fetch(`${API_URL}/api/followup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        report_type: state.reportType,
        question_id: q.id,
        answer: textValue,
        pronouns: state.pronoun,
      }),
    });
    if (!response.ok) throw new Error("followup request failed");
    const body = await response.json();

    followupQuestionEl.textContent = body.question;
    followupSuggestionsEl.innerHTML = "";
    (body.suggestions || []).forEach((suggestion) => {
      const li = document.createElement("li");
      li.textContent = suggestion;
      followupSuggestionsEl.appendChild(li);
    });

    followupLoading.classList.add("hidden");
    followupContent.classList.remove("hidden");
  } catch (err) {
    state.followupAsked[q.id] = true;
    hideFollowupPanel();
    const resume = followupPendingProceed;
    followupPendingQuestionId = null;
    followupPendingProceed = null;
    if (resume) resume();
  }
}

followupContinueBtn.addEventListener("click", () => {
  const extra = followupInput.value.trim();
  if (
    extra &&
    (findBadWords(extra).length ||
      findGibberishWords(extra).length ||
      hasLowWordDiversity(extra))
  ) {
    answerError.textContent =
      "Please check what you added doesn't include swearing or nonsense text.";
    answerError.classList.remove("hidden");
    return;
  }
  answerError.classList.add("hidden");

  if (followupPendingQuestionId) {
    if (extra) {
      state.answers[followupPendingQuestionId] =
        `${state.answers[followupPendingQuestionId]} ${extra}`.trim();
    }
    state.followupAsked[followupPendingQuestionId] = true;
  }
  hideFollowupPanel();
  const resume = followupPendingProceed;
  followupPendingQuestionId = null;
  followupPendingProceed = null;
  if (resume) resume();
});

nextBtn.addEventListener("click", () => {
  const q = currentQuestion();
  const textValue = answerInput.value.trim();
  const error = validateAnswer(textValue);
  if (error) {
    answerError.textContent = error;
    answerError.classList.remove("hidden");
    return;
  }
  state.answers[q.id] = textValue;
  maybeShowFollowup(q, textValue, () => {
    state.questionVariant[state.index] = 0;
    state.index += 1;
    renderQuestion();
    saveAutosave();
  });
});

generateBtn.addEventListener("click", () => {
  const q = currentQuestion();
  const textValue = answerInput.value.trim();
  const error = validateAnswer(textValue);
  if (error) {
    answerError.textContent = error;
    answerError.classList.remove("hidden");
    return;
  }
  state.answers[q.id] = textValue;
  maybeShowFollowup(q, textValue, () => {
    showScreen(screenResult);
    setProgress(TOTAL_STEPS);
    generateDraft();
  });
});

regenerateBtn.addEventListener("click", () => {
  generateDraft();
});

shortenBtn.addEventListener("click", () => {
  generateDraft("shorter");
});

lengthenBtn.addEventListener("click", () => {
  generateDraft("longer");
});

usePreviousBtn.addEventListener("click", () => {
  if (!state.previousDraft) return;
  const current = {
    draft: draftText.value,
    wordCount: parseInt(wordCountText.textContent, 10) || 0,
    targetRange: state.lastTargetRange,
    inRange: wordCountText.classList.contains("in-range"),
  };
  applyDraftResult(state.previousDraft);
  state.previousDraft = current;
});

copyBtn.addEventListener("click", () => {
  draftText.select();
  navigator.clipboard.writeText(draftText.value);
  copyBtn.textContent = "Copied!";
  setTimeout(() => {
    copyBtn.textContent = "Copy to clipboard";
  }, 2000);
});

resumeBtn.addEventListener("click", () => {
  const saved = loadAutosave();
  resumeBanner.classList.add("hidden");
  if (!saved) return;
  state.reportType = "tutor";
  state.formalName = saved.formalName || null;
  state.preferredName = saved.preferredName || null;
  state.pronoun = saved.pronoun || null;
  state.yearLevel = saved.yearLevel || null;
  state.tutorGroup = saved.tutorGroup || null;
  state.house = saved.house || null;
  state.index = Number.isInteger(saved.index) ? saved.index : 0;
  state.answers = saved.answers && typeof saved.answers === "object" ? saved.answers : {};
  state.questionVariant =
    saved.questionVariant && typeof saved.questionVariant === "object" ? saved.questionVariant : {};
  state.followupAsked = {};
  showScreen(screenQuestion);
  renderQuestion();
});

discardResumeBtn.addEventListener("click", () => {
  clearAutosave();
  resumeBanner.classList.add("hidden");
});

startOverBtn.addEventListener("click", () => {
  state.reportType = "tutor";
  state.formalName = null;
  state.preferredName = null;
  state.pronoun = null;
  state.yearLevel = null;
  state.tutorGroup = null;
  state.house = null;
  state.index = 0;
  state.answers = {};
  state.questionVariant = {};
  state.followupAsked = {};
  state.previousDraft = null;
  state.lastTargetRange = null;
  document.querySelectorAll(".pronoun-btn").forEach((b) => b.classList.remove("selected"));
  regenerateBtn.classList.add("hidden");
  usePreviousBtn.classList.add("hidden");
  shortenBtn.classList.add("hidden");
  lengthenBtn.classList.add("hidden");
  checklistNote.classList.add("hidden");
  notesDetails.classList.add("hidden");
  resumeBanner.classList.add("hidden");
  formalNameInput.value = "";
  preferredNameInput.value = "";
  clearAutosave();
  showScreen(screenName);
  setProgress(1);
});

function applyDraftResult(result) {
  draftText.value = result.draft;
  wordCountText.textContent = `${result.wordCount} words (target: ${result.targetRange[0]}-${result.targetRange[1]})`;
  wordCountText.classList.toggle("in-range", result.inRange);
  wordCountText.classList.toggle("out-of-range", !result.inRange);
  state.lastTargetRange = result.targetRange;
  updateAdjustButtons(result);
}

function updateAdjustButtons(result) {
  const tooLong = !result.inRange && result.wordCount > result.targetRange[1];
  const tooShort = !result.inRange && result.wordCount < result.targetRange[0];
  shortenBtn.classList.toggle("hidden", !tooLong);
  lengthenBtn.classList.toggle("hidden", !tooShort);
}

function renderNotesList(payloadAnswers) {
  const questions = currentQuestions();
  notesList.innerHTML = "";
  questions.forEach((variantGroup, idx) => {
    const variantIdx = state.questionVariant[idx] || 0;
    const q = getDisplayQuestion(variantGroup[variantIdx]);
    const value = payloadAnswers[q.id] || "";

    const dt = document.createElement("dt");
    dt.textContent = q.question;

    const dd = document.createElement("dd");
    const textarea = document.createElement("textarea");
    textarea.className = "notes-edit-input";
    textarea.rows = 3;
    textarea.value = value;
    textarea.dataset.questionId = q.id;
    dd.appendChild(textarea);

    notesList.appendChild(dt);
    notesList.appendChild(dd);
  });
  notesDetails.classList.remove("hidden");
}

updateNotesBtn.addEventListener("click", () => {
  const textareas = notesList.querySelectorAll("textarea[data-question-id]");
  const errors = Array.from(textareas).map((textarea) => validateAnswer(textarea.value.trim()));
  const firstError = errors.find((e) => e);
  if (firstError) {
    errorBanner.textContent = `Every note needs an answer: ${firstError}`;
    errorBanner.classList.remove("hidden");
    notesDetails.open = true;
    return;
  }

  textareas.forEach((textarea) => {
    state.answers[textarea.dataset.questionId] = textarea.value.trim();
  });
  notesDetails.open = true;
  generateDraft();
});

async function generateDraft(adjust) {
  errorBanner.classList.add("hidden");
  toneNote.classList.add("hidden");
  loadingText.classList.remove("hidden");

  const isRegenerate = !draftText.classList.contains("hidden");
  let currentResult = null;
  if (isRegenerate) {
    currentResult = {
      draft: draftText.value,
      wordCount: parseInt(wordCountText.textContent, 10) || 0,
      targetRange: state.lastTargetRange || [0, 0],
      inRange: wordCountText.classList.contains("in-range"),
    };
  }

  draftText.classList.add("hidden");
  wordCountText.classList.add("hidden");
  copyBtn.classList.add("hidden");
  shortenBtn.classList.add("hidden");
  lengthenBtn.classList.add("hidden");

  const payloadAnswers = {};
  const questions = currentQuestions();
  questions.forEach((variantGroup, idx) => {
    const variantIdx = state.questionVariant[idx] || 0;
    const q = variantGroup[variantIdx];
    payloadAnswers[q.id] = state.answers[q.id] || "";
  });

  try {
    const response = await fetch(`${API_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        report_type: state.reportType,
        formal_name: state.formalName,
        preferred_name: state.preferredName,
        pronouns: state.pronoun,
        year_level: state.yearLevel,
        tutor_group: state.tutorGroup,
        house: state.house,
        answers: payloadAnswers,
        adjust: adjust || undefined,
      }),
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.error || "Something went wrong generating the draft.");
    }

    if (currentResult) {
      state.previousDraft = currentResult;
      usePreviousBtn.classList.remove("hidden");
    }

    applyDraftResult({
      draft: body.draft,
      wordCount: body.word_count,
      targetRange: body.target_range,
      inRange: body.in_range,
    });

    draftText.classList.remove("hidden");
    wordCountText.classList.remove("hidden");
    copyBtn.classList.remove("hidden");
    regenerateBtn.classList.remove("hidden");
    checklistNote.classList.remove("hidden");
    renderNotesList(payloadAnswers);
    clearAutosave();

    if (body.tempered_words && body.tempered_words.length) {
      toneNote.textContent = `Heads up: your notes included stronger language (${body.tempered_words.join(", ")}). The AI has softened this in the draft below, please check the wording.`;
      toneNote.classList.remove("hidden");
    }
  } catch (err) {
    errorBanner.textContent = err.message;
    errorBanner.classList.remove("hidden");
  } finally {
    loadingText.classList.add("hidden");
  }
}

function checkResumeBanner() {
  const saved = loadAutosave();
  if (saved && saved.answers && Object.values(saved.answers).some((v) => String(v).trim())) {
    resumeBanner.classList.remove("hidden");
  }
}

startGuidedBtn.addEventListener("click", () => {
  localStorage.setItem(LS_WELCOME_SEEN, "1");
  state.reportType = "tutor";
  showScreen(screenName);
  setProgress(1);
  checkResumeBanner();
});

startCheckBtn.addEventListener("click", () => {
  localStorage.setItem(LS_WELCOME_SEEN, "1");
  showScreen(screenCheckInput);
  setProgress(0);
});

checkBackBtn.addEventListener("click", () => {
  showScreen(screenWelcome);
  setProgress(0);
});

checkSubmitBtn.addEventListener("click", () => {
  const text = checkTextInput.value.trim();
  const wordCount = countWords(text);

  if (!text) {
    checkInputError.textContent = "Please paste the report text to check.";
    checkInputError.classList.remove("hidden");
    return;
  }
  if (wordCount < 15) {
    checkInputError.textContent = "Please paste at least 15 words.";
    checkInputError.classList.remove("hidden");
    return;
  }
  if (wordCount > 400) {
    checkInputError.textContent = "Please paste no more than 400 words at a time.";
    checkInputError.classList.remove("hidden");
    return;
  }
  if (findBadWords(text).length) {
    checkInputError.textContent = "Please remove inappropriate language before checking.";
    checkInputError.classList.remove("hidden");
    return;
  }

  checkInputError.classList.add("hidden");
  runStyleCheck(text);
});

async function runStyleCheck(text) {
  showScreen(screenCheckResult);
  checkErrorBanner.classList.add("hidden");
  checkResultContent.classList.add("hidden");
  checkCopyBtn.classList.add("hidden");
  checkAnotherBtn.classList.add("hidden");
  checkLoadingText.classList.remove("hidden");

  try {
    const response = await fetch(`${API_URL}/api/style_check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.error || "Something went wrong checking the report.");
    }

    renderCheckResult(body);
  } catch (err) {
    checkErrorBanner.textContent = err.message;
    checkErrorBanner.classList.remove("hidden");
  } finally {
    checkLoadingText.classList.add("hidden");
  }
}

function renderCheckResult(result) {
  checkOriginalTextEl.textContent = result.original_text || "";
  checkCorrectedTextEl.value = result.corrected_text || "";

  const changes = result.changes || [];
  checkChangesList.innerHTML = "";

  if (changes.length === 0) {
    checkChangesWrapper.classList.add("hidden");
    checkNoChangesNote.classList.remove("hidden");
  } else {
    checkChangesWrapper.classList.remove("hidden");
    checkNoChangesNote.classList.add("hidden");
    changes.forEach((change) => {
      const li = document.createElement("li");

      const originalSpan = document.createElement("span");
      originalSpan.className = "change-original";
      originalSpan.textContent = change.original || "";

      const correctedSpan = document.createElement("span");
      correctedSpan.className = "change-corrected";
      correctedSpan.textContent = ` → ${change.corrected || ""}`;

      const reasonSpan = document.createElement("span");
      reasonSpan.className = "change-reason";
      reasonSpan.textContent = change.reason || "";

      li.appendChild(originalSpan);
      li.appendChild(correctedSpan);
      li.appendChild(reasonSpan);
      checkChangesList.appendChild(li);
    });
  }

  checkResultContent.classList.remove("hidden");
  checkCopyBtn.classList.remove("hidden");
  checkAnotherBtn.classList.remove("hidden");
}

checkCopyBtn.addEventListener("click", () => {
  checkCorrectedTextEl.select();
  navigator.clipboard.writeText(checkCorrectedTextEl.value);
  checkCopyBtn.textContent = "Copied!";
  setTimeout(() => {
    checkCopyBtn.textContent = "Copy corrected text";
  }, 2000);
});

checkAnotherBtn.addEventListener("click", () => {
  checkTextInput.value = "";
  checkInputError.classList.add("hidden");
  showScreen(screenCheckInput);
});
