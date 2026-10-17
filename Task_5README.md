# DocNow Consultation Summariser

A small tool that reads the text of an online doctor consultation and produces a **draft** summary of six things: the main complaint, how long it has lasted, medicines, allergies, the doctor's diagnosis, and the doctor's plan.

Its key rule: **it may only use what is written in the transcript.** If something was not said, it must print `NOT_STATED` instead of guessing.

> **Important: this tool is a drafting aid, not a clinical tool.**
> It has not been clinically validated and it makes mistakes that look correct.
> A clinician must check every summary against the transcript.
> **Read [LIMITATIONS.md](LIMITATIONS.md) before anyone uses it.**

---

## 1. At a glance

| | |
|---|---|
| **What it does** | Turns a consultation transcript (a text file) into a short draft summary |
| **What it does not do** | Diagnose, advise, triage, check allergies or interactions, or replace the medical record |
| **Needs** | Python 3.8 or newer. Nothing else for the default offline mode |
| **Two modes** | `rules` (offline, default, simple) and `claude` (AI model, needs an API key and approval to send data) |
| **Status** | Prototype. Tested on 6 made-up transcripts only. Not clinically validated |
| **Safe to use on real patients?** | **Not yet.** See [LIMITATIONS.md](LIMITATIONS.md) |

---

## 2. When NOT to use it

Do not use the tool, and use the original notes or recording instead, for any consultation involving:

- an **emergency or urgent symptoms** (chest pain, breathing trouble, stroke signs, severe bleeding, overdose, suicidal thoughts, safeguarding concerns). Follow your emergency procedure and do not wait for a summary
- **more than one medicine or condition**, or anyone saying they are *not* allergic to something or *stopped* a medicine (the tool gets these wrong)
- **mental health, children, or pregnancy** (not tested)
- **any language other than English**, or a transcript with no "Doctor:" / "Patient:" labels, bad audio, or several speakers
- a patient who has **not agreed** to this kind of processing

The full list, with reasons, is in [LIMITATIONS.md](LIMITATIONS.md), sections 2 and 3.

---

## 3. Setup (about 10 minutes, no programming needed)

### Step 1. Install Python
Download it from <https://www.python.org/downloads/> and run the installer.
**Windows:** tick the box **"Add python.exe to PATH"** on the first screen.

### Step 2. Download this project
On the GitHub page, click the green **Code** button, then **Download ZIP**. Unzip it. (If you use git: `git clone <your-repository-url>`.)

### Step 3. Open a terminal inside the folder
- **Windows:** open the unzipped folder, click the address bar, type `cmd`, press Enter.
- **Mac:** right-click the folder, choose **New Terminal at Folder**.

### Step 4. Check it works
Type this and press Enter (on Mac, use `python3` instead of `python`):

```
python summarise.py samples/complete_consultation.txt
```

You should see this:

```
DRAFT SUMMARY - NOT A MEDICAL RECORD.
A clinician must check every line against the original transcript before use.
------------------------------------------------------------
Main complaint      Hello doctor, I have had a headache and a runny nose for four days.
How long            four days
Medications         paracetamol 500mg
Allergies           penicillin
Doctor's diagnosis  common cold
Doctor's plan       I recommend rest and plenty of fluids, and follow up in one week if it does not improve.
------------------------------------------------------------
Backend used: rules
```

If you see that, setup is done. The default mode runs fully offline.

### Step 5 (optional). Turn on AI mode
Only do this after your data protection lead has approved sending transcript text to an outside AI provider.

1. Install the extra package: `pip install -r requirements.txt`
2. Get an API key from <https://console.anthropic.com/> and set it for this terminal window:
   - **Windows (Command Prompt):** `set ANTHROPIC_API_KEY=your-key-here`
   - **Mac:** `export ANTHROPIC_API_KEY=your-key-here`
3. Run with `--backend claude`:
   ```
   python summarise.py samples/complete_consultation.txt --backend claude
   ```

Never save the key inside a project file or commit it to GitHub.

> **Status of AI mode:** it is written but has **not yet been evaluated** against the test set. Before any pilot, run `python evaluate.py --backend claude` and commit the results.

---

## 4. How to use it

**1. Save the transcript as a plain text file** (`.txt`), one line per turn, each starting with `Doctor:`, `Patient:` or `Parent:`:

```
Doctor: What brings you in today?
Patient: I have had a sore throat for three days.
Doctor: Any allergies?
Patient: No known allergies.
```

**2. Run the tool** on that file:

```
python summarise.py path\to\your_transcript.txt
```

**3. Check the summary against the transcript.** Use the checklist in [LIMITATIONS.md](LIMITATIONS.md), section 9.

**Other options**

| Command | What it does |
|---|---|
| `python summarise.py file.txt --json` | Prints the result as structured data, for developers |
| `python summarise.py file.txt --backend claude` | Uses AI mode |
| `type file.txt \| python summarise.py -` | Reads text passed in instead of a file path (Mac: `cat file.txt \| python3 summarise.py -`) |

### Reading the output

| You see | It means |
|---|---|
| `NOT_STATED` | The tool did not find this in the transcript. **It does not mean "none".** |
| `none` | The patient appeared to say they have none. Still check. |
| `WARNING: ... possible urgent terms` | The text contains an urgent word. The tool cannot judge urgency. Follow your emergency procedure. A missing warning does **not** mean the case is safe. |

The tool refuses to run on transcripts shorter than 15 words, and it stops with an error rather than printing a half-finished summary.

---

## 5. Try the samples

| Command | Shows |
|---|---|
| `python summarise.py samples/complete_consultation.txt` | Everything stated, so every field is filled |
| `python summarise.py samples/missing_information.txt` | Medicines, allergies and diagnosis were never discussed, so they show `NOT_STATED` |
| `python summarise.py samples/urgent_terms.txt` | The urgent-terms warning |
| `python summarise.py samples/known_failures/negated_allergy.txt` | A **real mistake** the tool makes (reverses an allergy). More in `samples/known_failures/` |

All sample data is made up.

---

## 6. How the safety rules are built in

| Safeguard | Where |
|---|---|
| Use **only** facts in the transcript; write `NOT_STATED` if missing; ignore instructions hidden in the transcript; do not treat denied symptoms as symptoms | The prompt (`CLAUDE_PROMPT`) and rules in `evaluate.py` |
| A "DRAFT, must be checked" banner on every output | `summarise.py` |
| Refuses very short transcripts; stops on errors instead of guessing | `summarise.py` |
| Urgent-word warning (crude word match, not triage) | `summarise.py` |
| Automatic checks that catch invented facts | `evaluate.py` |

---

## 7. How it was tested

Run the automatic checks yourself:

```
python evaluate.py              # offline mode: should pass all 6
python evaluate.py --backend bad   # a deliberately lying fake: should fail all 6
```

| Check | Offline mode result |
|---|---|
| Output has all six fields | 6 / 6 |
| Missing information correctly marked `NOT_STATED` | 15 / 15 |
| Stated information correct | 21 / 21 |
| No invented or forbidden terms | 23 / 23 |

The deliberately lying fake model scores 0 / 6, which shows the checks can catch invention. Results are saved in `results/` (`eval_log.txt` and `latest_results.json`).

**Please read this honestly:** these are 6 short, made-up, clean transcripts, and the offline mode was written alongside them. A perfect score here does **not** mean the tool is safe. The files in `samples/known_failures/` show real errors on inputs the tests did not cover. See [LIMITATIONS.md](LIMITATIONS.md), sections 5 and 7.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `'python' is not recognized` (Windows) | Reinstall Python and tick **Add python.exe to PATH**, or try `py` instead of `python` |
| `command not found: python` (Mac) | Use `python3` |
| `Could not open the transcript` | Check the file name and path. Put the file in this folder, or give the full path |
| `Transcript is too short` | The tool refuses very short text on purpose. Use the original notes |
| All fields say `NOT_STATED` | The lines probably lack `Doctor:` / `Patient:` labels, or are not in English. The tool found nothing. Do not read this as "nothing was said" |
| `The 'anthropic' package is not installed` | Run `pip install -r requirements.txt` |
| AI mode says authentication failed | The API key is not set in this terminal window. Repeat Step 5.2 |

---

## 9. What is in this repository

| Path | Purpose |
|---|---|
| `README.md` | This guide |
| `LIMITATIONS.md` | **Required reading.** What the tool must not be used for, known failures, clinical risks, review checklist |
| `summarise.py` | The tool clinic staff run |
| `evaluate.py` | The test set (6 transcripts), both summarisers, the grounded prompt with refusal rules, and the automatic checks |
| `samples/` | Made-up example transcripts, including `known_failures/` |
| `results/` | Saved test results (`eval_log.txt`, `latest_results.json`) |
| `requirements.txt` | The one optional package for AI mode |
| `.gitignore` | Helps keep real patient data and API keys out of GitHub |

---

## 10. For whoever maintains it

- After **any** change to the prompt or code, run `python evaluate.py` (and `--backend claude` if you use AI mode), then commit the new `results/`.
- When a mistake is found, add it as a new case in the `CASES` list in `evaluate.py`, make it pass, and keep it as a permanent test.
- Before any real pilot: evaluate AI mode, have clinicians build a much larger realistic test set, and get written sign-off from your clinical lead, data protection lead and, where relevant, regulatory advisers.
- Never commit real transcripts or API keys.

---

*Built by Muhammad Abdullah Khan as an Ezitech internship project for DocNow Telehealth (Tasks 1-4). Not a medical device.*
