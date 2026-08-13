const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:5000"
  : "https://pastoral-report-writer.vercel.app";

const LS_TUTOR_GROUP = "pastoralLastTutorGroup";
const LS_HOUSE = "pastoralLastHouse";
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
      },
      {
        id: "learner",
        question: "Where have they shown growth or resilience this term?",
      },
    ],
    [
      {
        id: "achievement",
        question: "What achievements, participation, or leadership stand out this term? (sports, music, House involvement, academic awards)",
      },
      {
        id: "achievement",
        question: "What cocurricular activities engage them? (sports, music, clubs, House events)",
      },
    ],
    [
      {
        id: "next_steps",
        question: "Has the student set any goals or talked about what they want to focus on next?",
      },
      {
        id: "next_steps",
        question: "What has been a highlight or memorable moment for this student this term?",
      },
    ],
  ],
  pyp: [
    [
      {
        id: "learner_social",
        question: "Who are they as a learner and socially? Which Learner Profile attributes (Inquirer, Thinker, Communicator, etc.) show?",
      },
      {
        id: "learner_social",
        question: "How do they approach group work and collaboration?",
      },
    ],
    [
      {
        id: "atl",
        question: "What Approaches to Learning strength do they show? (thinking, research, communication, social, self-management) — give an example.",
      },
      {
        id: "atl",
        question: "When do they show the most curiosity or engagement?",
      },
    ],
    [
      {
        id: "achievement",
        question: "What achievement or participation stand out? (co-curricular, camp, project, leadership, group task)",
      },
      {
        id: "achievement",
        question: "What's one challenge they're working through, and how are they tackling it?",
      },
    ],
    [
      {
        id: "next_steps",
        question: "What's the next step for them as a learner? How can school and parents support this?",
      },
      {
        id: "next_steps",
        question: "What would help them grow in independence or confidence?",
      },
    ],
  ],
};

const state = {
  reportType: null,
  pronoun: null,
  tutorGroup: null,
  house: null,
  index: 0,
  answers: {},
  questionVariant: {},
  previousDraft: null,
  lastTargetRange: null,
};

const screenWelcome = document.getElementById("screen-welcome");
const welcomeStartBtn = document.getElementById("welcome-start-btn");

const screenSelect = document.getElementById("screen-select");
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
const pronounNextBtn = document.getElementById("pronoun-next-btn");
const contextNextBtn = document.getElementById("context-next-btn");
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

const TOTAL_STEPS = 7;
const MIN_WORDS = 5;

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
      pronoun: state.pronoun,
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
  if (savedTutorGroup || savedHouse) {
    tutorGroupInput.value = savedTutorGroup || "";
    houseInput.value = savedHouse || "";
    contextRememberedNote.classList.remove("hidden");
  } else {
    contextRememberedNote.classList.add("hidden");
  }
}

document.querySelectorAll(".type-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.reportType = btn.dataset.type;
    state.index = 0;
    state.answers = {};
    state.questionVariant = {};
    showScreen(screenPronoun);
    setProgress(1);
  });
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
    state.pronoun = customPronounInput.value || "they/them";
  }
  prefillContext();
  showScreen(screenContext);
  setProgress(2);
});

contextNextBtn.addEventListener("click", () => {
  state.tutorGroup = tutorGroupInput.value.trim() || "(not specified)";
  state.house = houseInput.value.trim() || "(not specified)";
  if (state.tutorGroup !== "(not specified)") {
    localStorage.setItem(LS_TUTOR_GROUP, state.tutorGroup);
  }
  if (state.house !== "(not specified)") {
    localStorage.setItem(LS_HOUSE, state.house);
  }
  showScreen(screenQuestion);
  renderQuestion();
  saveAutosave();
});

function showScreen(screen) {
  [screenWelcome, screenSelect, screenPronoun, screenContext, screenQuestion, screenResult].forEach((s) => s.classList.add("hidden"));
  screen.classList.remove("hidden");
}

function currentQuestions() {
  return QUESTIONS[state.reportType];
}

function currentQuestion() {
  const questions = currentQuestions();
  const variantIdx = state.questionVariant[state.index] || 0;
  return questions[state.index][variantIdx];
}

function renderQuestion() {
  const questions = currentQuestions();
  const q = currentQuestion();

  progressText.textContent = `Question ${state.index + 1} of ${questions.length}`;
  questionText.textContent = q.question;
  answerInput.value = state.answers[q.id] || "";
  answerError.classList.add("hidden");

  backBtn.classList.toggle("hidden", state.index === 0);
  const isLast = state.index === questions.length - 1;
  nextBtn.classList.toggle("hidden", isLast);
  generateBtn.classList.toggle("hidden", !isLast);

  setProgress(3 + state.index);
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
  state.questionVariant[state.index] = 0;
  state.index += 1;
  renderQuestion();
  saveAutosave();
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
  showScreen(screenResult);
  setProgress(TOTAL_STEPS);
  generateDraft();
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
  state.reportType = saved.reportType;
  state.pronoun = saved.pronoun;
  state.tutorGroup = saved.tutorGroup;
  state.house = saved.house;
  state.index = saved.index;
  state.answers = saved.answers;
  state.questionVariant = saved.questionVariant;
  showScreen(screenQuestion);
  renderQuestion();
});

discardResumeBtn.addEventListener("click", () => {
  clearAutosave();
  resumeBanner.classList.add("hidden");
});

startOverBtn.addEventListener("click", () => {
  state.reportType = null;
  state.pronoun = null;
  state.tutorGroup = null;
  state.house = null;
  state.index = 0;
  state.answers = {};
  state.questionVariant = {};
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
  clearAutosave();
  showScreen(screenSelect);
  setProgress(0);
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
    const q = variantGroup[variantIdx];
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
        pronouns: state.pronoun,
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

welcomeStartBtn.addEventListener("click", () => {
  localStorage.setItem(LS_WELCOME_SEEN, "1");
  showScreen(screenSelect);
  checkResumeBanner();
});

if (localStorage.getItem(LS_WELCOME_SEEN)) {
  showScreen(screenSelect);
  checkResumeBanner();
}
