# Spice Route Restaurant: LLM Evaluation Dashboard

**Task 1: the test-case dataset. Task 2: send every question to an LLM and save the raw answers. Task 3: score the answers.**

Spice Route wants to know how well a small language model answers common guest questions (menu recommendations, reservation rules, dietary needs). To measure that, we need a fixed set of questions and, for each one, the **exact answer the restaurant wants to give**. This repository holds that set, plus the short script that creates it.

| File | What it is |
|---|---|
| `test_cases.json` | The dataset: **29 guest questions**, each with its ideal answer |
| `generate_test_cases.py` | The script that writes and checks `test_cases.json` (the questions and answers are written inside it) |
| `run_evaluation.py` | **Task 2.** Sends each question to an LLM and writes `raw_results.json` |
| `restaurant_info.txt` | Sample fact sheet given to the model so it can answer from facts |
| `scoring.py` | **Task 3.** Scores `raw_results.json` and writes `scores.csv` and `summary.json` |
| `scores.csv`, `summary.json` | Per-case scores and overall metrics (created by `scoring.py`) |
| `raw_results.json` | The model's raw answers (created by running `run_evaluation.py`) |
| `requirements.txt` | Only needed for the local model |

> **All restaurant facts here are invented sample data** (opening hours, prices, dishes, policies, phone number, address). They exist so the evaluation tool can be built and tested. Before the results are used to judge a model, Spice Route must replace the answers with its real policies (see [Add or change cases](#add-or-change-cases)). The email domain `spiceroute.example` and the 555 phone number are deliberately not real.

---

## Quick start

You need **Python 3.8 or newer** (3.11 recommended). There is nothing to install.

```
python generate_test_cases.py
```

On Mac or Linux, use `python3`. You should see:

```
Saved 29 test cases to .../test_cases.json

29 test cases:
  hours         3
  location      1
  reservations  5
  ...
All checks passed. (Sample restaurant facts: replace with Spice Route's real policies.)
```

The file is rewritten identically every time (no randomness), so it is safe to run again whenever you change a case.

---

## What is in `test_cases.json`

A list of test cases. One entry looks like this:

```json
{
  "id": "SR-010",
  "category": "dietary",
  "question": "What vegan options do you have?",
  "expected_answer": "Our vegan dishes are Chana Masala, Dal Tadka, Aloo Gobi, Vegetable Samosa and Tandoori Roti, all marked (VG) on the menu. Please note that our naan, Dal Makhani and paneer dishes contain dairy, so they are not vegan.",
  "key_facts": ["Chana Masala", "Dal Tadka", "Aloo Gobi", "Vegetable Samosa", "Tandoori Roti", "naan"]
}
```

| Field | Meaning |
|---|---|
| `id` | Unique ID (`SR-001`, `SR-002`, ...), assigned automatically in order |
| `question` | What a guest would type |
| `expected_answer` | The exact answer the restaurant wants to give: 1 to 3 plain sentences |
| `category` | Topic group, used to break down the results by topic later |
| `key_facts` | Short phrases a correct answer **must contain** (numbers, times, dish names). The scoring module in a later task uses them to judge accuracy, next to a semantic-similarity score |

The evaluation script (Task 2) only needs `id`, `question` and `expected_answer`; `category` and `key_facts` are extra information for scoring and for the charts.

### The 29 test cases

They cover the topics guests ask about most: opening hours, location and parking, reservations, dietary needs and allergies, menu recommendations, pricing, payment, services (takeaway, delivery, private events, accessibility), house policies, and one question the restaurant cannot answer (to check that a model does not invent an answer).

| ID | Category | Question |
|---|---|---|
| SR-001 | hours | What are your opening hours? |
| SR-002 | hours | Are you open on public holidays? |
| SR-003 | hours | What time is the last order? |
| SR-004 | location | Where are you located, and is there parking? |
| SR-005 | reservations | How do I make a reservation? |
| SR-006 | reservations | Do I need a reservation, or can I just walk in? |
| SR-007 | reservations | How long will you hold my table if I am running late? |
| SR-008 | reservations | What is your cancellation policy? |
| SR-009 | reservations | Do you take large group bookings? |
| SR-010 | dietary | What vegan options do you have? |
| SR-011 | dietary | Do you have vegetarian dishes? |
| SR-012 | dietary | Is your food halal? |
| SR-013 | dietary | Do you have gluten-free options? |
| SR-014 | dietary | I have a nut allergy. Is it safe to eat here? |
| SR-015 | menu | What do you recommend for a first-time visitor? |
| SR-016 | menu | What is your signature dish? |
| SR-017 | menu | Which dishes are not too spicy? |
| SR-018 | menu | Do you have a kids' menu? |
| SR-019 | pricing | How much does a typical meal cost per person? |
| SR-020 | pricing | Do you offer a lunch deal? |
| SR-021 | payment | What payment methods do you accept? |
| SR-022 | payment | Do you add a service charge? |
| SR-023 | services | Do you offer takeaway or delivery? |
| SR-024 | services | Can I bring my own birthday cake? |
| SR-025 | services | Do you have a private room for events? |
| SR-026 | services | Is the restaurant wheelchair accessible? |
| SR-027 | policies | Do you serve alcohol? |
| SR-028 | policies | Are pets allowed? |
| SR-029 | out_of_scope | Can you recommend a good hotel nearby? |

---

## How the data was made

1. **Research.** I looked at common restaurant FAQ pages and sample FAQ lists to see which topics guests ask about most: hours, booking rules, dietary needs, allergies, kids, payment, takeaway, events, accessibility, house rules. Then I wrote my own questions in plain guest language. Nothing was copied from another restaurant.
2. **Answers.** For each question I wrote the answer a restaurant would want to give: short, friendly, with the concrete facts a guest needs (times, prices, dish names). The invented facts are consistent with each other (for example, the last-order times match the opening hours, and the dishes marked vegan match the vegetarian list).
3. **Key facts.** For each answer I listed the few phrases that must appear for the answer to count as correct. The script checks that each one appears **word for word** inside the answer, so the two can never drift apart.
4. **Script.** `generate_test_cases.py` holds the question/answer list, adds the IDs, checks everything and writes `test_cases.json`, so the file can be regenerated at any time.

Two kinds of cases are included on purpose: normal questions with a clear answer, and one that the restaurant **cannot** answer (SR-029, hotel recommendations). A good model should politely decline instead of inventing hotel names.

---

## Add or change cases

All the data is in the `CASES` list near the top of `generate_test_cases.py`.

**Add a case**

1. Open `generate_test_cases.py` and find the line `CASES = [`.
2. Copy any block (from `{` to `},`) and paste it just before the closing `]` of the list:

   ```python
   {
       "category": "dietary",
       "question": "Do you have dairy-free desserts?",
       "answer": "Yes, our Fresh Fruit Plate is dairy-free. Our Gulab Jamun and Kheer contain milk.",
       "key_facts": ["Fresh Fruit Plate", "Gulab Jamun", "Kheer"],
   },
   ```
3. Fill in the four fields:
   - `category`: one of `hours`, `location`, `reservations`, `dietary`, `menu`, `pricing`, `payment`, `services`, `policies`, `out_of_scope`
   - `question`: ends with `?`
   - `answer`: the exact answer, at most 450 characters
   - `key_facts`: at least one short phrase, each copied word for word from the answer
4. Run `python generate_test_cases.py`. The new case gets the next ID automatically.

**Change a case:** edit its `question`, `answer` or `key_facts` in the list and run the script again.

**Replace the sample facts with real ones:** edit each `answer` (and its `key_facts`) to match Spice Route's real hours, prices, dishes and policies. This is the most important step before the results mean anything.

**Remove a case:** delete its block. IDs are assigned by position, so the cases after it are renumbered.

**What the script checks** (it refuses to write the file and tells you why if anything is wrong):

- between 20 and 100 test cases
- every ID and every question is unique
- no empty `question`, `expected_answer` or `key_facts`
- every question ends with `?`
- every `category` is one of the allowed names
- every answer is at most 450 characters
- every key fact appears word for word in its answer

If you edit `test_cases.json` by hand instead, check it with `python generate_test_cases.py --check`. (Editing the script is better, because the next run of the script would overwrite hand edits.) To write to a different file: `python generate_test_cases.py --out other.json`.

---

## Task 2: run the evaluation

`run_evaluation.py` loads `test_cases.json`, asks the model every question, and saves the raw answers to `raw_results.json`. It has a **config section at the top of the file** (backend, key, model names, settings). Everything there can also be set with environment variables or command-line flags.

### Option A: OpenAI (`gpt-3.5-turbo`)

Nothing to install. Set your key, then run:

```
export OPENAI_API_KEY="sk-..."        # Windows: setx OPENAI_API_KEY "sk-..."  (reopen the terminal)
python run_evaluation.py
```

Optional: `OPENAI_MODEL` (default `gpt-3.5-turbo`) and `OPENAI_BASE_URL` (any OpenAI-compatible server). Never commit your key; use the environment variable.

### Option B: small local model (no key, free)

```
pip install -r requirements.txt
python run_evaluation.py --backend local
```

The first run downloads the model (about 1 GB) and runs on CPU. The default is `Qwen/Qwen2.5-0.5B-Instruct`. Choose another with `--local-model distilgpt2` or by editing `LOCAL_MODEL` in the config section.

> **Why not `distilbert-base-uncased`?** It is a *masked* language model: it fills in blanks and cannot write answers, so the `text-generation` pipeline refuses it. `distilgpt2` is the same family of small model but a generative one; it runs fast, but its answers will be weak.

### Which model is used?

`--backend auto` (the default) uses OpenAI if `OPENAI_API_KEY` is set, otherwise the local model. Force one with `--backend openai` or `--backend local`. `--backend mock` returns canned replies only to test the pipeline offline; its output is labelled `[MOCK]` and is not real model output.

### Useful flags

| Flag | Meaning |
|---|---|
| `--limit 3` | Only the first 3 cases (quick test) |
| `--ids SR-001,SR-010` | Only these cases |
| `--no-info` | Do not give the model `restaurant_info.txt` (it then has to guess) |
| `--out file.json` | Write somewhere else |

### The fact sheet

By default the model is told to answer **only** from `restaurant_info.txt` and to say it is not sure otherwise. This is how a real restaurant chatbot would work. It is hand-written and is not a copy of the expected answers, so the model still has to find and phrase the right facts. Small models that cannot fit the sheet in their context window automatically fall back to a short prompt (a note is printed).

### Output format: `raw_results.json`

```
{
  "generated_at": "2026-11-12T09:01:55+00:00",
  "backend": "openai",
  "model": "gpt-3.5-turbo",
  "temperature": 0.0,
  "used_restaurant_info": true,
  "finished": true,
  "total": 29,
  "errors": 0,
  "results": [
    {
      "id": "SR-001",
      "category": "hours",
      "question": "What are your opening hours?",
      "expected_answer": "...",
      "key_facts": ["..."],
      "model_answer": "...",
      "timestamp": "2026-11-12T09:01:56+00:00",
      "latency_seconds": 0.8,
      "error": null
    }
  ]
}
```

Every result has `id`, `question`, `model_answer` and a UTC `timestamp`. The expected answer and key facts are copied along so Task 3 (scoring) needs only this one file. If one question fails (network error, etc.) its `error` field says why and the run continues. Pressing Ctrl+C saves what is done so far (`"finished": false`). OpenAI rate limits (429) and server errors are retried automatically.

### Testing it

```
python run_evaluation.py --limit 3        # real model, 3 questions
python run_evaluation.py --backend mock   # no model, checks the pipeline
```

---

## Task 3: score the answers

`scoring.py` reads `raw_results.json`, compares every `model_answer` with its `expected_answer`, and writes `scores.csv` and `summary.json`.

```
pip install -r requirements.txt     # pandas + sentence-transformers
python scoring.py
```

The first run downloads the embedding model `all-MiniLM-L6-v2` (about 90 MB).

### The two metrics

| Metric | Column | How it works |
|---|---|---|
| Accuracy | `accuracy` (0 or 1) | **Exact string match.** 1 only if the answer equals the expected answer. Capitals, extra spaces and end punctuation are ignored (`--strict` turns that off). |
| Semantic similarity | `similarity` (0 to 1) | Both texts become sentence embeddings (MiniLM); the score is their **cosine similarity**, so a correct answer in different words still scores high. |

Expect accuracy to be low (often 0%) with a real LLM, because models almost never repeat the exact sentence. That is normal: exact match is the strict test, similarity is the fair one. As a bonus the CSV also has `key_fact_recall` (share of the case's `key_facts` found in the answer).

A failed or empty answer scores 0 on both metrics and is marked `failed`.

### Output

`scores.csv`: `id, category, question, expected_answer, model_answer, accuracy, similarity, key_fact_recall, failed`

`summary.json`: `total_cases`, `accuracy`, `exact_match_count`, `mean_similarity` (plus median, min, max), `mean_key_fact_recall`, `failed_cases`, the model and embedding model used, and a `by_category` breakdown. Task 4's dashboard reads these two files.

### Use it from other code

```python
from scoring import exact_match, embedding_similarity, MiniLMEmbedder
emb = MiniLMEmbedder()
exact_match("We open at noon.", "we open at noon")                      # 1
embedding_similarity("Open from noon", "We open at 12 pm", emb)        # about 0.6 to 0.8
```

### Testing without internet

`python scoring.py --embedder tfidf` uses a simple word-overlap stand-in instead of MiniLM. It only proves the pipeline works; the summary is marked with a warning. Use the real embedder for real scores.

---

## How the next tasks use this file

| Task | Uses |
|---|---|
| 2. Evaluation script (done) | Reads `test_cases.json`, asks the model each `question`, saves its reply |
| 3. Scoring module (done) | Compares each reply with `expected_answer`: accuracy (are the `key_facts` present?) and semantic similarity |
| 4. Streamlit dashboard | Shows per-case results and charts, grouped by `category` |
| 5. Deployment and hand-over | Publishes the dashboard on a free Hugging Face Space |

---

## Known limits

- **The facts are invented.** Treat every number, dish and policy as a placeholder until the restaurant confirms or replaces it.
- **One question, one answer.** Each case is a single question with no follow-ups, in English.
- **Key facts are exact text.** A model that says "half past ten" instead of "10:30 pm" would miss that key fact. The semantic-similarity score added in Task 3 is there to catch such cases.
- **Raw answers are not graded yet.** Task 2 only collects them; scoring is Task 3. Real answers depend on the model, so a rerun with a different model gives different text.
- **29 cases are a starting set**, enough to compare models roughly, not a full guarantee of quality. Add real questions from the restaurant's own guest messages over time.
