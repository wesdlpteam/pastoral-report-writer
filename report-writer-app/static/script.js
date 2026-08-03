const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:5000"
  : "https://pastoral-report-writer.vercel.app";

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
};

const screenSelect = document.getElementById("screen-select");
const screenPronoun = document.getElementById("screen-pronouns");
const screenContext = document.getElementById("screen-context");
const screenQuestion = document.getElementById("screen-question");
const screenResult = document.getElementById("screen-result");

const progressText = document.getElementById("progress-text");
const questionText = document.getElementById("question-text");
const answerInput = document.getElementById("answer-input");
const backBtn = document.getElementById("back-btn");
const anotherBtn = document.getElementById("another-btn");
const skipBtn = document.getElementById("skip-btn");
const nextBtn = document.getElementById("next-btn");
const generateBtn = document.getElementById("generate-btn");
const pronounNextBtn = document.getElementById("pronoun-next-btn");
const contextNextBtn = document.getElementById("context-next-btn");
const tutorGroupInput = document.getElementById("tutor-group-input");
const houseInput = document.getElementById("house-input");

const errorBanner = document.getElementById("error-banner");
const loadingText = document.getElementById("loading-text");
const draftText = document.getElementById("draft-text");
const wordCountText = document.getElementById("word-count-text");
const copyBtn = document.getElementById("copy-btn");
const startOverBtn = document.getElementById("start-over-btn");
const otherPronounDiv = document.getElementById("other-pronoun");
const customPronounInput = document.getElementById("custom-pronoun");
const progressTrack = document.getElementById("progress-track");
const progressFill = document.getElementById("progress-fill");

const TOTAL_STEPS = 7;

function setProgress(stepIndex) {
  const pct = Math.min(1, Math.max(0, stepIndex / TOTAL_STEPS));
  progressFill.style.transform = `scaleX(${pct})`;
  progressTrack.setAttribute("aria-valuenow", Math.round(pct * 100));
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
  showScreen(screenContext);
  setProgress(2);
});

contextNextBtn.addEventListener("click", () => {
  state.tutorGroup = tutorGroupInput.value.trim() || "(not specified)";
  state.house = houseInput.value.trim() || "(not specified)";
  showScreen(screenQuestion);
  renderQuestion();
});

function showScreen(screen) {
  [screenSelect, screenPronoun, screenContext, screenQuestion, screenResult].forEach((s) => s.classList.add("hidden"));
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
});

backBtn.addEventListener("click", () => {
  const q = currentQuestion();
  state.answers[q.id] = answerInput.value;
  state.questionVariant[state.index] = 0;
  state.index -= 1;
  renderQuestion();
});

skipBtn.addEventListener("click", () => {
  const q = currentQuestion();
  state.answers[q.id] = "";
  state.questionVariant[state.index] = 0;
  state.index += 1;
  if (state.index < currentQuestions().length) {
    renderQuestion();
  } else {
    showScreen(screenResult);
    setProgress(TOTAL_STEPS);
    generateDraft();
  }
});

nextBtn.addEventListener("click", () => {
  const q = currentQuestion();
  const textValue = answerInput.value.trim();
  if (!textValue) {
    errorBanner.textContent = "Please enter text or skip this question.";
    errorBanner.classList.remove("hidden");
    return;
  }
  state.answers[q.id] = textValue;
  state.questionVariant[state.index] = 0;
  state.index += 1;
  renderQuestion();
});

generateBtn.addEventListener("click", () => {
  const q = currentQuestion();
  const textValue = answerInput.value.trim();
  if (!textValue) {
    errorBanner.textContent = "Please enter text or skip this question.";
    errorBanner.classList.remove("hidden");
    return;
  }
  state.answers[q.id] = textValue;
  showScreen(screenResult);
  setProgress(TOTAL_STEPS);
  generateDraft();
});

copyBtn.addEventListener("click", () => {
  draftText.select();
  navigator.clipboard.writeText(draftText.value);
  copyBtn.textContent = "Copied!";
  setTimeout(() => {
    copyBtn.textContent = "Copy to clipboard";
  }, 2000);
});

startOverBtn.addEventListener("click", () => {
  state.reportType = null;
  state.pronoun = null;
  state.tutorGroup = null;
  state.house = null;
  state.index = 0;
  state.answers = {};
  state.questionVariant = {};
  tutorGroupInput.value = "";
  houseInput.value = "";
  document.querySelectorAll(".pronoun-btn").forEach((b) => b.classList.remove("selected"));
  showScreen(screenSelect);
  setProgress(0);
});

async function generateDraft() {
  errorBanner.classList.add("hidden");
  draftText.classList.add("hidden");
  wordCountText.classList.add("hidden");
  copyBtn.classList.add("hidden");
  loadingText.classList.remove("hidden");

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
      }),
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
    copyBtn.classList.remove("hidden");
  } catch (err) {
    errorBanner.textContent = err.message;
    errorBanner.classList.remove("hidden");
  } finally {
    loadingText.classList.add("hidden");
  }
}
