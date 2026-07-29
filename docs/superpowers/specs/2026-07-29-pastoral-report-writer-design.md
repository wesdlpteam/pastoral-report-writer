# Pastoral Report Writing Companion — Design Spec

Date: 2026-07-29
Status: Approved by user, ready for implementation planning

## 1. Purpose

Save Wesley College teachers time writing pastoral report comments (Years 7–12 Tutor Reports and PYP Semester Reports) by interviewing them with a short, low-effort Q&A, then drafting a comment in Wesley's house style and word-count range using AI. The teacher edits/copies the draft and adds the student's name themselves in Word — the tool never handles the student's name or any other identifying detail.

## 2. Users and context

- Primary user: Wesley College teachers writing pastoral report comments, once per student per reporting period (potentially 15–25 times in a sitting for a Tutor Group).
- Non-technical users. The interface must be self-explanatory with no setup beyond opening a URL in a browser.
- Source-of-truth documents (already reviewed, live in `Pastoral Report Writer/`):
  - `Years 7 to12 Tutor Report Guidelines - 2026.pdf` — structure, word count (100–150 words), four-part sentence structure (person / learner / participant / summary), plus three generic sample comments.
  - `PYP Semester Report Guidelines.pdf` — structure, word count (180–300 words), Learner Profile / Approaches to Learning language, personal profile comment inclusions.
  - `Style-Guide-April-2023.pdf` — Wesley Editorial Style Guide (capitals, apostrophes, abbreviations, inclusive language, numbers, dates). Applies to final report text generally; the AI draft should follow it where relevant (e.g. no unnecessary capitals, avoid contractions, "Year 9" not "Y9").
  - Six sample docx files (`BR Sample Reports`, `Gannon Pastoral data`, `Saville examples`, `grace samples`, `russell sample`, `sparrow examples`) — real Tutor Report comment examples in Wesley's actual voice, used as style calibration. All already use a `[student name]` placeholder instead of the real student name. Two files (`grace samples.docx`, `sparrow examples.docx`) had one stray real first name each ("Alistair", "Chloe") that must be scrubbed to `[student name]` before any use in the app or its prompts.
  - No sample corpus exists for PYP comments — PYP drafting relies on the structural rules in the PYP guideline PDF only. This is a known limitation; real PYP samples can be added later if supplied.

## 3. Core flow

1. Teacher opens the local web page in a browser.
2. Teacher picks report type: **Tutor Report (Years 7–12)** or **PYP Semester Report (Prep–6)**.
3. Tool asks a fixed sequence of questions for that type, one at a time, with a progress indicator ("Question 3 of 5"). Each question offers quick-pick chips for common answers plus a free-text box for specifics. Teacher can select multiple chips and/or type free text per question.
4. After the last question, teacher clicks **Generate**. Answers are sent to the backend, which builds a prompt (report-type rules + style examples + the teacher's answers) and calls the OpenAI API.
5. Draft comment appears in an editable text box, with:
   - Live word count against the report type's range (100–150 or 180–300), flagged visually if outside range (advisory, not blocking — it's a draft).
   - **Regenerate** button — re-runs generation from the same answers for a fresh version.
   - **Copy** button — copies the draft text to clipboard.
6. Teacher edits as needed, copies the draft, pastes into Word/Synergetic, and adds the student's name and final polish there.
7. Nothing is saved. Closing or refreshing the tab clears everything — there is no database, no login, no history.

## 4. Question sets

### Tutor Report (Years 7–12)
Matches the four required sentence themes from the guideline PDF:
1. **Student as a person** — chips: e.g. "resilient", "quiet/reserved", "friendly and outgoing", "organised", "still building confidence" + free text for specifics/examples.
2. **Student as a learner** — chips: e.g. "strong academic progress", "developing steadily", "needs more consistency", "asks great questions" + free text.
3. **Student as a Tutor Group participant** — chips: e.g. "actively engaged", "quiet but present", "supportive of peers", "still settling in" + free text.
4. **Summarising note** — free text only (e.g. reflection stage, leadership, camp, Education Outdoors, any closing observation). Optional field.

### PYP Semester Report (Prep–6)
Matches the inclusions list from the PYP guideline PDF:
1. **Who they are as a learner and socially** — chips + free text.
2. **Approaches to Learning strength** (thinking / research / communication / social / self-management skills) — chips drawn from the ATL sub-skill names + free text for a concrete example.
3. **Achievement or participation example** (co-curricular, passion project, camp, leadership, significant group task) — free text.
4. **Next steps for the child as a learner** — free text (what the school will support, how parents could assist).

## 5. AI drafting

- Backend (Python/Flask) builds a system prompt per report type containing:
  - The relevant structural/word-count rules extracted from the guideline PDFs.
  - Relevant style points from the Editorial Style Guide (capitalisation, no contractions, Year format, etc).
  - For Tutor Reports only: 4–6 cleaned example comments (from the six sample docx files, `[student name]` placeholder preserved, stray real names scrubbed) as few-shot style calibration.
  - An explicit instruction never to invent a student name — always use `[student name]` as the placeholder in the output.
- User prompt is built from the teacher's chip + free-text answers.
- Model: OpenAI, default `gpt-4o-mini` (cost-effective, good enough for this task), configurable via environment variable so it can be swapped later without code changes.
- API key read from environment variable / local `.env` file, never hardcoded, never sent to the frontend.

## 6. Privacy and data handling

- The student's real name is never entered anywhere in the tool, never sent to OpenAI, never logged.
- Only the teacher's behaviour/learning descriptions (chips + free text) are sent to the AI API.
- No persistence: no database, no server-side logging of answers or drafts beyond what's needed to serve the single request-response.
- `.env` file (holding the OpenAI key) is git-ignored.

## 7. Architecture

```
Pastoral Engine/
  Pastoral Report Writer/        (existing training material — untouched)
  report-writer-app/             (new)
    app.py                       (Flask app: serves frontend, /api/generate endpoint)
    style_examples.py            (cleaned excerpts from the sample docx files)
    prompts.py                   (system prompt templates per report type)
    static/
      index.html
      style.css                  (Wesley brand tokens: purple #4F2759, gold #C59F40, neutrals, highlighter tints)
      script.js                  (Q&A flow, chip selection, calls /api/generate, renders draft)
    requirements.txt
    .env.example                 (placeholder showing required env var names, no real key)
    .gitignore                   (.env, __pycache__, etc)
```

- Flask serves the static frontend and exposes one endpoint, `POST /api/generate`, which accepts `{report_type, answers}` and returns `{draft, word_count}`.
- Frontend is plain HTML/CSS/JS — no build step, no framework — appropriate for a single-page tool of this size and for a non-technical maintainer.
- Runs locally for now (`python app.py`, open `localhost:5000` in browser). Not yet hosted for other teachers — that's a future step once the prototype is validated.

## 8. Visual design

- Wesley brand palette used directly: purple `#4F2759` (primary/interactive), gold `#C59F40` (accent), black/white, neutrals `#EFEDED`/`#E6E2DD`/`#DAD7D1`, highlighter tints for chip backgrounds (with AA-safe ink substitutes where tints are used with text).
- Applied as bold, solid colour blocking (e.g. a full-bleed purple header band, solid gold accents on active states) rather than a washed-out gradient or timid single-accent-on-white look.
- Graphik font, falling back to system UI font (`Segoe UI`/system-ui) since Graphik isn't guaranteed on teacher machines.
- One question visible at a time, generous spacing, clear progress indicator — avoids feeling like a long form.
- No invented off-brand color palette, no generic AI-default fonts (Inter/Roboto) or clichés (gradient text, side-stripe cards, uppercase eyebrow labels).

## 9. Error handling

- OpenAI API call fails (network/timeout/rate limit): show a plain-English error message with a **Try again** button; teacher's answers remain intact so nothing is lost.
- Teacher tries to generate with required questions unanswered: inline validation message, generation blocked until addressed (chips optional if free text given, but at least one input required per question).
- Draft outside word-count range: shown as an advisory note near the word count (not blocking) since the teacher edits before use.

## 10. Testing plan

- Manual end-to-end walkthrough of both report types in a real browser.
- Confirm word counts for generated drafts land in or near the target range across several runs.
- Confirm no student-identifying data appears in the request sent to OpenAI (inspect the actual payload).
- Confirm `.env` is git-ignored and the key never appears in any committed file.
- Visual check against Wesley brand tokens and against the "no generic AI look" requirement.

## 11. Out of scope (for this version)

- Multi-teacher hosting/login/accounts.
- Saving/history of past drafts.
- PYP style-example corpus (none supplied yet).
- Direct integration with Synergetic/WiSE (teacher copies/pastes manually).
- Voice input.
