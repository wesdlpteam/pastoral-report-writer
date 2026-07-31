const QUESTIONS = {
  tutor: [
    {
      id: "person",
      question: "What's this student like as a person?",
      chips: [
        "Resilient",
        "Quiet / reserved",
        "Friendly and outgoing",
        "Organised",
        "Still building confidence",
        "Kind to peers",
      ],
    },
    {
      id: "learner",
      question: "How are they doing as a learner?",
      chips: [
        "Strong academic progress",
        "Developing steadily",
        "Needs more consistency",
        "Asks great questions",
        "Working hard to catch up",
      ],
    },
    {
      id: "participant",
      question: "How do they take part in Tutor Group?",
      chips: [
        "Actively engaged",
        "Quiet but present",
        "Supportive of peers",
        "Still settling in",
        "Takes on a leadership role",
      ],
    },
    {
      id: "summary",
      question: "Anything else to add? (optional)",
      chips: [],
    },
  ],
  pyp: [
    {
      id: "learner_social",
      question: "Who are they as a learner and socially?",
      chips: [
        "Curious and inquisitive",
        "Confident in social settings",
        "Quiet but kind",
        "Works well in groups",
        "Prefers working independently",
      ],
    },
    {
      id: "atl",
      question: "What's an Approaches to Learning strength, with an example?",
      chips: [
        "Strong thinking skills",
        "Strong research skills",
        "Strong communication skills",
        "Strong social skills",
        "Strong self-management skills",
      ],
    },
    {
      id: "achievement",
      question: "Any achievement or participation to highlight?",
      chips: [
        "Co-curricular activity",
        "Camp / Education Outdoors",
        "Passion project",
        "Leadership role",
        "Group task success",
      ],
    },
    {
      id: "next_steps",
      question: "What's the next step for them as a learner?",
      chips: [],
    },
  ],
};

const state = {
  reportType: null,
  index: 0,
  answers: {},
  selectedChips: {},
};

const screenSelect = document.getElementById("screen-select");
const screenQuestion = document.getElementById("screen-question");
const screenResult = document.getElementById("screen-result");

const progressText = document.getElementById("progress-text");
const questionText = document.getElementById("question-text");
const chipContainer = document.getElementById("chip-container");
const freetextInput = document.getElementById("freetext-input");
const backBtn = document.getElementById("back-btn");
const nextBtn = document.getElementById("next-btn");
const generateBtn = document.getElementById("generate-btn");

const errorBanner = document.getElementById("error-banner");
const loadingText = document.getElementById("loading-text");
const draftText = document.getElementById("draft-text");
const wordCountText = document.getElementById("word-count-text");
const regenerateBtn = document.getElementById("regenerate-btn");
const copyBtn = document.getElementById("copy-btn");
const startOverBtn = document.getElementById("start-over-btn");

document.querySelectorAll(".type-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.reportType = btn.dataset.type;
    state.index = 0;
    state.answers = {};
    state.selectedChips = {};
    showScreen(screenQuestion);
    renderQuestion();
  });
});

function showScreen(screen) {
  [screenSelect, screenQuestion, screenResult].forEach((s) => s.classList.add("hidden"));
  screen.classList.remove("hidden");
}

function currentQuestions() {
  return QUESTIONS[state.reportType];
}

function renderQuestion() {
  const questions = currentQuestions();
  const q = questions[state.index];

  progressText.textContent = `Question ${state.index + 1} of ${questions.length}`;
  questionText.textContent = q.question;

  chipContainer.innerHTML = "";
  const selected = state.selectedChips[q.id] || [];
  q.chips.forEach((chipLabel) => {
    const chipEl = document.createElement("button");
    chipEl.type = "button";
    chipEl.className = "chip";
    chipEl.textContent = chipLabel;
    if (selected.includes(chipLabel)) {
      chipEl.classList.add("selected");
    }
    chipEl.addEventListener("click", () => toggleChip(q.id, chipLabel, chipEl));
    chipContainer.appendChild(chipEl);
  });

  freetextInput.value = state.answers[`${q.id}__freetext`] || "";

  backBtn.classList.toggle("hidden", state.index === 0);
  const isLast = state.index === questions.length - 1;
  nextBtn.classList.toggle("hidden", isLast);
  generateBtn.classList.toggle("hidden", !isLast);
}

function toggleChip(questionId, chipLabel, chipEl) {
  const selected = state.selectedChips[questionId] || [];
  const idx = selected.indexOf(chipLabel);
  if (idx === -1) {
    selected.push(chipLabel);
    chipEl.classList.add("selected");
  } else {
    selected.splice(idx, 1);
    chipEl.classList.remove("selected");
  }
  state.selectedChips[questionId] = selected;
}

function saveCurrentAnswer() {
  const q = currentQuestions()[state.index];
  state.answers[`${q.id}__freetext`] = freetextInput.value;
  const chips = state.selectedChips[q.id] || [];
  const freetext = freetextInput.value.trim();

  let combined = "";
  if (chips.length && freetext) {
    combined = `${chips.join(", ")}. ${freetext}`;
  } else if (chips.length) {
    combined = chips.join(", ");
  } else {
    combined = freetext;
  }
  state.answers[q.id] = combined;
}

backBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  state.index -= 1;
  renderQuestion();
});

nextBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  state.index += 1;
  renderQuestion();
});

generateBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  showScreen(screenResult);
  generateDraft();
});

regenerateBtn.addEventListener("click", () => {
  generateDraft();
});

copyBtn.addEventListener("click", () => {
  draftText.select();
  navigator.clipboard.writeText(draftText.value);
});

startOverBtn.addEventListener("click", () => {
  state.reportType = null;
  state.index = 0;
  state.answers = {};
  state.selectedChips = {};
  showScreen(screenSelect);
});

async function generateDraft() {
  errorBanner.classList.add("hidden");
  draftText.classList.add("hidden");
  wordCountText.classList.add("hidden");
  regenerateBtn.classList.add("hidden");
  copyBtn.classList.add("hidden");
  loadingText.classList.remove("hidden");

  const payloadAnswers = {};
  currentQuestions().forEach((q) => {
    payloadAnswers[q.id] = state.answers[q.id] || "";
  });

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report_type: state.reportType, answers: payloadAnswers }),
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.error || "Something went wrong generating the draft.");
    }

    draftText.value = body.draft;
    wordCountText.textContent = `${body.word_count} words (target: ${body.target_range[0]}-${body.target_range[1]})`;
    wordCountText.classList.toggle("in-range", body.in_range);
    wordCountText.classList.toggle("out-of-range", !body.in_range);

    draftText.classList.remove("hidden");
    wordCountText.classList.remove("hidden");
    regenerateBtn.classList.remove("hidden");
    copyBtn.classList.remove("hidden");
  } catch (err) {
    errorBanner.textContent = err.message;
    errorBanner.classList.remove("hidden");
  } finally {
    loadingText.classList.add("hidden");
  }
}
