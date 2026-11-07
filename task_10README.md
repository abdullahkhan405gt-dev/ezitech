---
title: Indus Weaves Spec Search
emoji: 🧵
colorFrom: indigo
colorTo: blue
sdk: streamlit
python_version: "3.11"
app_file: app.py
pinned: false
---

# Indus Weaves Spec Search

An internal web tool for Indus Weaves staff. Type a question about a fabric ("How do I wash the linen blend?") and get a short answer **with the fabric spec entry it came from** (for example `Source: IW-FAB-015`). If the specs do not contain the answer, it says **"I don't know"** instead of guessing.

| | |
|---|---|
| **Live app** | _Paste your Hugging Face Space link here after deploying (see [Put it online](#put-it-online-free))_ |
| **Demo video** | [`docs/demo.mp4`](docs/demo.mp4) (about 30 seconds: 3 questions plus one "not in the data" case) |
| **Code** | `ezitech.py` (all the logic, one file), `app.py` (starts the web page), `generate_data.py` (makes the data) |

> **The data in this repository is synthetic sample data.** The 27 fabrics look realistic but are not real Indus Weaves specifications. Replace them with real specs before anyone relies on an answer (see [Update the data](#update-the-data)).

---

## Contents

1. [Demo](#demo)
2. [Using the app](#using-the-app)
3. [Run it on your computer](#run-it-on-your-computer)
4. [Update the data](#update-the-data)
5. [Put it online (free)](#put-it-online-free)
6. [How it works](#how-it-works)
7. [Known limitations](#known-limitations)
8. [Troubleshooting](#troubleshooting)
9. [Tests](#tests)
10. [Optional: use a free LLM](#optional-use-a-free-llm)
11. [Repository layout](#repository-layout)

---

## Demo

Three different questions, each answered with its source. The video [`docs/demo.mp4`](docs/demo.mp4) shows the same thing live.

| 1. A care question | 2. A composition question | 3. A certification question |
|---|---|---|
| ![care](docs/01-care-question.png) | ![composition](docs/02-composition-question.png) | ![certification](docs/03-certification-question.png) |
| "How do I wash the linen blend?" gives the care steps, **Source: IW-FAB-015** | "What is the composition of silk twill?" gives "100% Silk", **Source: IW-FAB-023** | "Does the merino wool twill have a certification?" gives "Responsible Wool Standard (RWS)", **Source: IW-FAB-022** |

And a question that is not in the data ("What is the capital of France?"): the tool says it does not know and shows no source.

![not in the data](docs/04-not-in-the-data.png)

The "Show the spec text this answer is based on" box under each answer shows the exact spec text and a match score, so staff can check the answer themselves. (The demo was recorded on sample data in a build environment; the match scores on your machine will differ, see [Known limitations](#known-limitations), point 4.)

---

## Using the app

1. Open the live link (or run it on your computer, below).
2. Type a question and press **Ask** (or press Enter). Or click one of the four examples.
3. Read the answer in the green box. The line under it, **Source**, is the spec entry (ID and fabric name) the answer came from.
4. Open **Show the spec text this answer is based on** to see the original text.

**What it can answer:** composition, weight and width, construction and finish, care instructions, origin, and certifications of the fabrics in the data.

**Questions that work well:**

- "How do I wash the cotton-linen blend?"
- "What is the composition of silk twill?"
- "Where is the organic cotton sateen made?"
- "Which fabric is dry clean only?"
- "Can I use fabric softener on stretch denim?"

**Tips:** name the fabric when you can. Ask one thing at a time. A yellow box saying **"I don't know"** means nothing in the specs matched well enough: try rewording, or the information is not in the data.

---

## Run it on your computer

You need **Python 3.10 or newer** (3.11 or 3.12 recommended) and an internet connection for the first start (it downloads a free 90 MB language model once; no account or API key).

**1. Open a terminal in this folder and create a private environment:**

| | Windows | Mac / Linux |
|---|---|---|
| Create it | `python -m venv .venv` | `python3 -m venv .venv` |
| Turn it on | `.venv\Scripts\activate` | `source .venv/bin/activate` |

**2. Install the libraries** (a few minutes; PyTorch is a large download):

```
pip install -r requirements.txt
```

**3. Start the web page:**

```
streamlit run app.py
```

Your browser opens at `http://localhost:8501`. **The first start takes about a minute** (it loads the model and builds the search database `chroma_db/` if it is missing). Stop it with Ctrl+C. (`python ezitech.py web` does the same.)

Command-line use, without the web page:

```
python ezitech.py ask "How do I wash the linen blend?"        # answer + source
python ezitech.py ask "Where is the silk twill made?" -v      # also show the spec text and scores
python ezitech.py search "dry clean" -n 5 --category wool     # raw closest spec text
```

In Python code, the main function is:

```python
from ezitech import answer_question
r = answer_question("How do I wash the linen blend?")
r["answer"]    # the answer text
r["sources"]   # ['IW-FAB-015']
```

---

## Update the data

All answers come from **`data/fabric_specs.json`**, which is generated by **`generate_data.py`**. To change what the tool knows, edit the fabric list in `generate_data.py`, regenerate the JSON, and rebuild the search database.

### Add a fabric

1. Open `generate_data.py` and find the list called `FABRICS`.
2. Copy any block and paste it at the end of the list (before the closing `]`). Edit the values:

   ```python
   {
       "name": "Cotton Voile 60",
       "breakdown": [("Cotton", 100)],            # fibre and percent; percentages must add up to 100
       "weight_gsm": 70, "width_cm": 145,
       "construction": "Plain weave, fine yarn",
       "finish": "Soft finish",
       "care": [WASH_COLD, NO_BLEACH, LINE_DRY, IRON_LOW],   # ready-made lines, or your own text in quotes
       "origin": "Faisalabad, Pakistan",
       "certifications": ["OEKO-TEX Standard 100"],          # or [] for none
       "notes": "Light and breathable; creases easily.",     # or "" for none
   },
   ```

   The ready-made care lines are `WASH_COLD`, `WASH_WARM`, `WASH_GENTLE`, `HAND_COLD`, `NO_BLEACH`, `TUMBLE_LOW`, `NO_TUMBLE`, `LINE_DRY`, `DRY_FLAT`, `IRON_LOW`, `IRON_MED`, `IRON_HIGH`, `NO_IRON`, `NO_SOFTENER`, `DRY_CLEAN`. You can also type any text, for example `"Wash separately for the first three washes"`.
3. IDs (`IW-FAB-028`, ...) are assigned automatically, in order.

### Change or remove a fabric

Edit the values in its block, or delete the block. **Note:** IDs are assigned by position, so removing a fabric from the middle renumbers the ones after it. Add new fabrics at the end, and avoid deleting if other documents refer to the IDs.

### Regenerate and rebuild

```
python generate_data.py          # checks the data and rewrites data/fabric_specs.json
python ezitech.py build          # rebuilds the search database in chroma_db/
```

`generate_data.py` refuses to save, and tells you why, if something is wrong: percentages not adding up to 100, a missing field, a duplicate ID or name, or more than 500 fabrics (change `MAX_ENTRIES` near the top of the file if you ever need more).

The web page also notices changed data on its own: when it starts, it compares the data with what is stored in `chroma_db/` and rebuilds if they differ. So after regenerating the JSON, restarting `streamlit run app.py` is enough.

### Update the live app

Upload the new `data/fabric_specs.json` (and `generate_data.py`) to your Hugging Face Space (Files > Upload, or `git push`). The Space restarts and rebuilds the database by itself in about a minute.

### Using your own spec documents

The tool reads only the JSON in the format above (see one entry in `data/fabric_specs.json`). To load real specs from another source (a spreadsheet or PDFs), convert them to the same fields. Each entry needs: `id`, `name`, `category`, `composition`, `weight_gsm`, `width_cm`, `construction`, `finish`, `care` (a list), `origin`, `certifications` (a list), `notes`, `source`. The easiest path is to paste them into the `FABRICS` list as shown above.

---

## Put it online (free)

[Hugging Face Spaces](https://huggingface.co) is the recommended free host: its free CPU machine has 16 GB of memory, enough for the language model. (Render's free plan has 512 MB, which is too small.)

1. Create a free account at huggingface.co.
2. Click **New** > **Space**. Name it (for example `indus-weaves-spec-search`), choose **Streamlit** as the SDK, **CPU basic (free)**, **Public**.
3. Put these files in the Space:

   | File | Why |
   |---|---|
   | `app.py` | The page |
   | `ezitech.py` | All the logic |
   | `requirements.txt` | Libraries (installed automatically) |
   | `data/fabric_specs.json` | The spec data |
   | `.streamlit/config.toml` | Page settings |
   | `README.md` | Its first lines (between `---`) tell Hugging Face how to run the app |

   You do **not** need to upload `chroma_db/`: the app builds it on the first start.

   With git (use your Hugging Face username; when asked for a password, paste an access token with **write** permission from huggingface.co/settings/tokens):

   ```
   git clone https://huggingface.co/spaces/YOUR-USERNAME/indus-weaves-spec-search
   cd indus-weaves-spec-search
   # copy the files from the table above into this folder, then:
   git add .
   git commit -m "Indus Weaves spec search"
   git push
   ```

   Or use **Files** > **Add file** > **Upload files** on the Space page (drag in the `.streamlit` and `data` folders whole).
4. Watch the **Logs** tab. The build takes about 5 to 10 minutes. When the status says **Running**, open the Space URL.
5. **First-time check:** ask the three example questions from the [Demo](#demo) and confirm the sources match. Then paste the link at the top of this README.

Good to know:

- Free Spaces **go to sleep** when nobody uses them, and wake on the next visit (about a minute). Open the link before a meeting.
- Anyone with the link can use the page (there is no login). It holds only the data you upload.
- Files written on a free Space are not kept across restarts. That is fine: the database is rebuilt from the JSON each time.

---

## How it works

```
data/fabric_specs.json -> 3 chunks per fabric -> local embedding model -> ChromaDB (chroma_db/)
                                                                              |
 your question -> same model -> closest chunks -> confidence check -> answer + source IDs -> web page
```

1. **Chunks.** Each fabric is split into three short chunks (overview, care, origin and certifications). Every chunk starts with the fabric name and ID, so it can be cited on its own.
2. **Search by meaning.** A free language model (`all-MiniLM-L6-v2`, runs on your computer, no API key) turns each chunk and each question into numbers. ChromaDB, saved in `chroma_db/`, finds the chunks closest in meaning to the question. This is why "how do I wash denim?" finds care text even though the words differ.
3. **Confidence check.** If nothing matches well enough (the score is below `MIN_SCORE`, default 0.30), the answer is "I don't know".
4. **Answer with sources.** The default answer is built directly from the matching spec text, so it never says something the specs do not say. The **source IDs always come from the matched spec entries**, never from a language model.

The database in `chroma_db/` is persistent (ChromaDB `PersistentClient`), so it survives restarts. Every build re-opens it from disk to prove it was saved and appends a record to `results/vector_store_log.txt`. These two folders are committed to the repository on purpose.

---

## Known limitations

Please read these before relying on the tool.

1. **The data is sample data.** Answers are only as good as the specs loaded. Do not use them for real orders or client answers until real specs replace the samples.
2. **It cannot tell if a question is really answerable.** By default it returns the closest spec text when the match is good enough. "What is the price of Cotton Poplin?" may return Cotton Poplin spec text (which has no price). Only the optional LLM mode can say "I don't know" in that case.
3. **The "I don't know" cut-off is an estimate.** The default `MIN_SCORE` of 0.30 is a reasonable guess for the model, not a measured value. Run `python ezitech.py calibrate` once; it suggests a better value. Too high: good questions get "I don't know". Too low: nonsense questions get an answer.
4. **Real-model results were not verified by the author.** The build environment could not download the language model, so the tests and the demo were run with a stand-in for the search step (same code, different embedding step). Run `python ezitech.py test` once on your computer (expect `17/17` then `22/22`) and do the first-time check after deploying. Match scores you see will differ from the screenshots.
5. **It answers about specific fabrics, not whole-catalogue questions.** "Which fabric is dry clean only?" returns the closest few entries; it does **not** list all matches, count, sort or compare ("how many cotton fabrics?", "which is the heaviest?").
6. **Keyword rules decide what kind of text to show** (care, origin, specification). Unusual wording can pick the wrong kind. English only.
7. **Exact codes and numbers are weak spots** for search by meaning (for example a certificate number or an exact gsm value).
8. **Small data.** It was built and checked with 27 fabrics. Much larger data (hundreds of fabrics, long documents) needs re-testing.
9. **Free hosting limits.** Spaces sleep when idle, restart slowly, and are public by link. For private use, run it inside your company network or use a private (paid) Space.
10. **LLM mode is lightly tested.** It was tested only against a fake local server, not a real Ollama or hosted model. Small models can ignore instructions; the tool rejects answers that cite a missing or unknown source, but cannot detect a wrong summary.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Red box "Could not load the embedding model" | The first start needs internet to download the model (about 90 MB). Connect and reload. Some company networks block `huggingface.co` |
| `streamlit: command not found` | Turn on your environment (step 1 of Run it) and run `pip install -r requirements.txt` |
| `pip install` fails | Check `python --version` is 3.10 or newer |
| Page shows "Running..." for a long time | Normal on the first start (model download and building the database). Wait about a minute |
| `No vector store at ...` | Run `python ezitech.py build` first |
| `data/fabric_specs.json not found` | Run `python generate_data.py` |
| Good questions return "I don't know" | Lower `MIN_SCORE`: run `python ezitech.py calibrate` and follow its suggestion (for example `MIN_SCORE=0.25`) |
| Nonsense questions return spec text | Raise `MIN_SCORE`, or use the optional LLM mode |
| Port already in use | Close the other copy, or use `streamlit run app.py --server.port 8502` |
| Answers look odd after editing the data | Run `python generate_data.py`, then `python ezitech.py build`, and restart the page |
| Space build fails on `torch` | Make sure `requirements.txt` still has the `--extra-index-url` line at the top |
| `'python' is not recognized` (Windows) | Try `py` instead of `python`, or reinstall Python with "Add to PATH" ticked |

---

## Tests

```
python ezitech.py test
```

It builds a throw-away database in a temporary folder (your real `chroma_db/` is untouched) and runs two suites:

- **17 checks on the search database:** chunking, saving to disk and re-opening, no duplicates after a rebuild, category filter, six sample questions, a clear error when the database is missing.
- **22 checks on the answer engine:** source IDs, the "I don't know" fallbacks, the citation guard for LLM answers, a fake LLM server, and six real questions (for example "How do I wash the linen blend?" must cite `IW-FAB-015`).

Expect `17/17 checks passed.` then `22/22 checks passed.` If the language model cannot be downloaded, the real-search checks are skipped and the exit code is 2.

The sample questions in the tests refer to the **sample fabrics** (for example `IW-FAB-015`). After you replace the sample data with real specs, those sample-question checks will fail by design; the other checks still apply.

---

## Optional: use a free LLM

By default no LLM is needed. If you want answers written in natural sentences, any OpenAI-compatible endpoint works. The easiest free option is [Ollama](https://ollama.com) on your own computer:

```
ollama pull llama3.2
python ezitech.py ask "How do I wash the linen blend?" --mode llm
```

| Variable | Default | Meaning |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Endpoint |
| `LLM_MODEL` | `llama3.2` | Model name |
| `LLM_API_KEY` | empty | Key, if the provider needs one |
| `MIN_SCORE` | `0.30` | Confidence cut-off |

Safety rules: if the LLM cites a source that was not retrieved, or none, its answer is thrown away and the spec text is shown instead (with a note). If it says "I don't know", that is respected. If it cannot be reached, the spec text is shown with a note. On the web page, LLM mode switches on automatically when `LLM_BASE_URL` is set (on a Space, set it as a **secret**; a local Ollama cannot be reached from a Hugging Face server).

---

## Repository layout

| Path | Purpose |
|---|---|
| `ezitech.py` | **All the code in one file:** load and chunk the data, embed, save to ChromaDB, search, `answer_question()` with source IDs, the web page, and the built-in tests |
| `app.py` | Starts the web page (`streamlit run app.py`) |
| `generate_data.py` | Creates and checks `data/fabric_specs.json` (edit the `FABRICS` list to change the data) |
| `data/fabric_specs.json` | The spec data the tool reads |
| `chroma_db/` | The saved (persistent) search database. Built by `python ezitech.py`; commit it |
| `results/vector_store_log.txt` | Log of each database build, with proof it was saved and re-read from disk. Commit it |
| `docs/` | Demo video (`demo.mp4`) and screenshots |
| `.streamlit/config.toml` | Page settings (no usage tracking, clean toolbar) |
| `requirements.txt` | Libraries to install |
| `README.md` | This file (its first lines also configure Hugging Face) |
<img width="1000" height="1100" alt="03-certification-question" src="https://github.com/user-attachments/assets/3a893783-2ba4-4b90-9aa7-69b7ecdb8356" />
<img width="1000" height="1100" alt="02-composition-question" src="https://github.com/user-attachments/assets/7963ae1d-08ae-497b-98e6-479f22d8804a" />
<img width="1000" height="1100" alt="003-certification-question" src="https://github.com/user-attachments/assets/942c7420-50e8-4f60-abc4-19069f20028a" />
