# Indus Weaves - Internal Textile Spec Search Tool

A local, free-tier tool that answers questions about fabric specifications (composition, care, origin) with clear source citations, so staff do not have to search PDFs by hand.

**Project progress:** Tasks 1 to 3 of 5 are done: sample data (Task 1), the local vector store (Task 2) and the answer engine that cites sources (Task 3). The web app and handover docs come in later tasks.

> **The data in this repository is synthetic sample data.** The numbers look realistic but are not lab results and are not real Indus Weaves specifications. Do not use them for real orders or client answers.

---

## Contents

1. [Task 1: the sample dataset](#task-1-the-sample-dataset) (needs only Python)
2. [Task 2: the local vector store](#task-2-the-local-vector-store-search-backend) (free, local, no API key)
3. [Task 3: the answer engine](#task-3-the-answer-engine-answers-with-sources) (no extra installs; optional free LLM)
4. [Repository layout](#repository-layout)

---

# Task 1: the sample dataset

`generate_data.py` creates `data/fabric_specs.json`, a list of **27 fabric specs**. This file is the source of truth that the search tool reads.

### Quick start (about one minute)

You only need Python 3.8 or newer. There is nothing to install for this task.

```
python generate_data.py
```

On Mac or Linux, use `python3` instead of `python`.

You should see:

```
Saved 27 fabric specs to .../data/fabric_specs.json

ID          Name                              Composition
IW-FAB-001  Cotton Poplin 120                 100% Cotton
IW-FAB-002  Organic Cotton Sateen             100% Cotton
...
All checks passed. (Synthetic sample data - not real specifications.)
```

### How to regenerate the data

1. Open a terminal in this folder.
2. Run `python generate_data.py`.
3. The file `data/fabric_specs.json` is rewritten. The result is identical every time, because the script uses no randomness. After a real change, commit the updated JSON, then rebuild the vector store (Task 2).

Optional: `python generate_data.py --out other/path.json` writes to a different file.

### How to add or change a fabric

1. Open `generate_data.py` and find the `FABRICS` list.
2. Copy one block, paste it at the end of the list, and edit the values.
3. Run `python generate_data.py` again. IDs are assigned automatically (`IW-FAB-001`, `IW-FAB-002`, ...).

The script refuses to save the file, and tells you why, if the data fails any check below.

### What one entry looks like

```json
{
  "id": "IW-FAB-003",
  "name": "Poly-Cotton Drill 65/35",
  "category": "blend",
  "composition": "65% Polyester, 35% Cotton",
  "composition_breakdown": [
    { "fibre": "Polyester", "percent": 65 },
    { "fibre": "Cotton", "percent": 35 }
  ],
  "weight_gsm": 245,
  "width_cm": 150,
  "construction": "2/1 twill (drill)",
  "finish": "Easy-care resin finish",
  "care": ["Machine wash warm (40°C max)", "Do not bleach", "Tumble dry low", "Iron medium heat"],
  "origin": "Faisalabad, Pakistan",
  "certifications": [],
  "notes": "Common choice for workwear and uniforms.",
  "source": "Sample spec sheet IW-FAB-003",
  "text": "Poly-Cotton Drill 65/35 (IW-FAB-003). Composition: 65% Polyester, 35% Cotton. Weight 245 gsm, width 150 cm. Construction: 2/1 twill (drill). Finish: Easy-care resin finish. Care: Machine wash warm (40°C max); Do not bleach; Tumble dry low; Iron medium heat. Origin: Faisalabad, Pakistan. Certifications: none listed. Note: Common choice for workwear and uniforms."
}
```

| Field | Meaning |
|---|---|
| `id` | Unique ID. Used as the citation. |
| `name` | Fabric name |
| `category` | `cotton`, `linen`, `cellulosic`, `synthetic`, `wool`, `silk`, or `blend` (set automatically) |
| `composition` | Fibre content as text, e.g. `100% Cotton` |
| `composition_breakdown` | The same content as numbers, for filtering |
| `weight_gsm`, `width_cm` | Weight (grams per square metre) and width |
| `construction`, `finish` | How the fabric is made and treated |
| `care` | List of care instructions |
| `origin` | Where it is woven (and where the yarn comes from, if imported) |
| `certifications` | Sample certification labels (empty list if none) |
| `notes` | Extra practical notes (may be empty) |
| `source` | Name of the sample spec sheet, used for citations |
| `text` | One plain-English paragraph combining everything above, handy for display. (The vector store builds its chunks from the individual fields instead, see Task 2.) |

### What the dataset covers

27 fabrics: cotton (10), blend (8), synthetic (4), cellulosic (2), and one each of linen, wool and silk. It includes single-fibre and blended fabrics, woven and knit constructions, different care routines (machine wash, hand wash, dry clean), local and imported yarn, and entries with and without certifications (11 of 27 list one).

### Built-in checks

Every run verifies, and refuses to save otherwise:

- between 20 and 30 entries
- every ID and every name is unique
- fibre percentages add up to exactly 100
- no required field (`id`, `name`, `category`, `composition`, `care`, `origin`, `source`, `text`) is empty
- each `text` snippet contains the fabric's name and composition

---

# Task 2: the local vector store (search backend)

A vector store lets you search by **meaning**, not just exact words. A question such as "how do I wash denim?" finds the right care instructions even if those exact words are not in the text.

| Term | Plain meaning |
|---|---|
| **Chunk** | A small piece of text. Each fabric is split into 3 chunks (overview, care, origin) so a care question finds a *care* chunk. |
| **Embedding** | A list of 384 numbers that captures the meaning of a chunk. Similar meanings give similar numbers. |
| **Vector store** | A database that saves chunks with their embeddings and finds the closest ones to a question. Here: ChromaDB, saved in the `chroma_db/` folder. |

Everything is **free and local**: the embedding model (`all-MiniLM-L6-v2`, via the `sentence-transformers` library) runs on your own computer. No API key, no paid service, and no data leaves your machine after the one-time model download.

## Setup (about 10 minutes the first time)

**1. You need Python 3.10 or newer** (3.11 or 3.12 recommended). Check with `python --version`.

**2. Open a terminal in this folder and create a private environment** (keeps the install tidy):

| | Windows | Mac / Linux |
|---|---|---|
| Create it | `python -m venv .venv` | `python3 -m venv .venv` |
| Turn it on | `.venv\Scripts\activate` | `source .venv/bin/activate` |

**3. Install the libraries:**

```
pip install -r requirements.txt
```

This installs ChromaDB, sentence-transformers and PyTorch (the engine behind the model). PyTorch is a big download. On Windows and Mac it is a few hundred MB. On Linux the default can be several GB because it includes GPU libraries. To keep it small on Linux, install the CPU-only build first:

```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

**4. Make sure the data exists.** The file `data/fabric_specs.json` is already in the repository. If it is missing, run `python generate_data.py`.

## Build the store and ask a question

```
python vector_store.py
```

This one command loads the JSON, splits it into chunks, embeds them, saves them to `chroma_db/`, and then answers a demo question. **The first run downloads the model once (about 90 MB, needs internet, about a minute).** After that it works offline.

You should see this layout (the exact fabrics and scores will differ; the demo question should return care chunks of cotton fabrics):

```
Loaded 27 fabric specs, splitting into 81 chunks.
Loading embedding model 'all-MiniLM-L6-v2' (local, no API key)...
Saved 81 chunks from 27 fabrics to .../chroma_db (collection 'fabric_specs').

Persisted on disk: .../chroma_db  (about 1100 KB)
  <folder-id>/data_level0.bin  (...)
  chroma.sqlite3  (...)
Verified: re-opened the saved database with a new connection -> 81 chunks, model 'all-MiniLM-L6-v2'.
Build log added to results/vector_store_log.txt. Commit chroma_db/ and results/ to the repository.

Question: "What is the care instruction for cotton?"

1. [IW-FAB-0xx | care]  <name of a cotton fabric>   (match 0.xx)
   <name> (IW-FAB-0xx) care instructions: Machine wash cold (30°C max); Do not bleach; ...
2. ...
3. ...
```

Each result shows a **citation** in brackets, `[fabric ID | section]`, the fabric name, a **match score** (1.0 = identical meaning, higher is closer) and the exact chunk text.

### Where the database is saved, and how to prove it

The database is **persistent**: `vector_store.py` uses `chromadb.PersistentClient` (function `persistent_client`), which writes everything to files in the `chroma_db/` folder, collection name `fabric_specs`. Nothing is kept only in memory, so you can close the program, come back tomorrow, and search without rebuilding.

Every build checks this itself. It opens the saved folder with a brand-new connection, reads the data back, prints the files it found, and **adds a record to `results/vector_store_log.txt`** (time, model, number of chunks, file sizes). The test (`python vector_store.py test`) also checks that a fresh connection can read the saved database.

**Before you submit, commit both folders** so the database and its proof are in the repository:

```
python vector_store.py
git add chroma_db results
git commit -m "Task 2: persisted ChromaDB vector store and build log"
```

`chroma_db/` is only about 1 MB. It is not ignored by `.gitignore` on purpose.

### Ask your own questions

```
python vector_store.py search "Which fabric is dry clean only?"
python vector_store.py search "Can I tumble dry stretch denim?" -n 5
python vector_store.py search "how to wash it" --category silk
```

| Option | Meaning |
|---|---|
| `-n 5` | Number of results (default 3) |
| `--category wool` | Only search one category: `cotton`, `linen`, `cellulosic`, `synthetic`, `wool`, `silk`, `blend` |
| `--db-dir PATH` | Use a different database folder (put it before `build` or `search`) |

### Rebuild after changing the data

```
python generate_data.py
python vector_store.py build
```

Building again replaces the old store, so nothing is duplicated.

## Run the tests

```
python vector_store.py test
```

It builds a throw-away store in a temporary folder (your real `chroma_db/` is untouched) and runs 17 checks:

| Group | What it checks |
|---|---|
| Chunking | Every fabric gives 3 chunks; IDs are unique; chunks are short enough for the model; each chunk starts with the fabric name and ID |
| Persistence | The database is saved to disk and can be re-opened by a fresh connection; building twice does not duplicate chunks |
| Filtering | `--category wool` returns only wool chunks |
| Search | 6 sample questions each return the correct chunk in the top results, for example "What is the care instruction for cotton?" must return a *care* chunk of a cotton fabric in the top 3 |
| Errors | Searching before building gives a clear message |

The last line should read `17/17 checks passed.` For each question the test also prints the top results so you can see what came back.

## How it works

```
data/fabric_specs.json  ->  3 chunks per fabric  ->  embeddings (local model)  ->  ChromaDB (chroma_db/)
                                                                                         |
          your question  ->  embedding (same model)  ->  closest chunks  ->  results with citations
```

**Chunking.** A whole spec is only about 50 words (41 to 60), so it would fit the model in one piece, and no chunk is longer than 235 characters. It is still split into three focused chunks, so a question about *care* matches a care chunk rather than a long paragraph where care is a small part:

| Chunk | Contains |
|---|---|
| `overview` | Name, ID, category, composition, weight, width, construction, finish |
| `care` | Care instructions, plus the practical notes (shrinkage, softener warnings) |
| `origin` | Where it is made and certifications |

Every chunk starts with the fabric name and ID, so it makes sense on its own and can be cited as `[IW-FAB-006 | care]`. Each chunk is also stored with metadata (fabric ID, name, category, section, source), which is what makes category filtering and citations possible. The chunks are rebuilt from the structured fields, so editing a fabric in `generate_data.py` is all that is needed.

**Design choices**

| Choice | Why |
|---|---|
| ChromaDB (not FAISS) | Saves to disk and supports metadata filters out of the box, with very little code |
| `all-MiniLM-L6-v2` | Small (about 90 MB), fast on an ordinary laptop CPU, no GPU or key needed. Another sentence-transformers model can be tried with the `EMBEDDING_MODEL` environment variable, then rebuild |
| Cosine similarity, normalised vectors | The standard way to compare sentence embeddings |
| Model name saved inside the database | Searching with a different model than the one used to build gives a clear error instead of wrong results |

## Known limits

- **It always returns the closest chunks, even when nothing is relevant.** Ask about something not in the data and you still get results, with low match scores. Task 3 (the answer engine) needs to use the scores to say "not found" instead of guessing.
- Only 27 sample fabrics, written for this project. Results on real, longer, messier spec documents will differ and would need re-testing.
- The test questions were written for this dataset. Passing them shows the pipeline works; it is not a general accuracy guarantee.
- Meaning-based search can miss exact codes or numbers (for example a specific certificate number). Task 3 may combine it with plain keyword matching.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Could not load the embedding model` | The first run needs internet to download the model (about 90 MB). Connect and try again. Some company or school networks block `huggingface.co` |
| `sentence-transformers is not installed` | Turn on your environment (step 2) and run `pip install -r requirements.txt` |
| `pip install` fails or `No matching distribution` | Check `python --version` is 3.10 or newer |
| `No vector store at ...` | Run `python vector_store.py build` first |
| `The store was built with '...' but you are searching with '...'` | You changed `EMBEDDING_MODEL`. Rebuild with `python vector_store.py build` |
| `data/fabric_specs.json not found` | Run `python generate_data.py` |
| `'python' is not recognized` (Windows) | Try `py` instead of `python`, or reinstall Python with "Add to PATH" ticked |
| Results look odd after editing data | Rebuild: `python vector_store.py build` |

---

# Task 3: the answer engine (answers with sources)

`answer_engine.py` takes a question, searches the vector store, and returns a short answer that **names the fabric spec entry it used**.

```
How do I wash the linen blend?
-> Cotton-Linen Blend 55/45 [IW-FAB-015] - care: Machine wash cold (30°C max); Do not bleach; Line dry in shade; Iron high heat. Notes: Creases less than pure linen.
   Source: IW-FAB-015
```

## Run it

You need the Task 2 setup done first, and the database must exist (`python vector_store.py`). Nothing else to install.

```
python answer_engine.py                                   # runs a few demo questions
python answer_engine.py ask "How do I wash the linen blend?"
python answer_engine.py ask "Where is the silk twill made?" -v     # -v shows the retrieved chunks and scores
python answer_engine.py ask "Who is the president of France?"      # -> "I don't know..."
python answer_engine.py test                              # 22 checks
python answer_engine.py calibrate                         # helps pick the confidence cut-off
```

## How it works

1. **Retrieve** the top 3 chunks for the question (`retrieve`).
2. **Check confidence.** If there are no chunks, or the best match score is below `MIN_SCORE` (default 0.30), the answer is `I don't know. I couldn't find this in the Indus Weaves fabric specs.`
3. **Build the prompt** from a simple template that contains the chunks (`PROMPT_TEMPLATE`).
4. **Answer** in one of two modes:
   - `template` (default): the answer is built directly from the retrieved spec text. Free, offline, no setup.
   - `llm`: the prompt is sent to a free LLM and its reply is used.
5. **Sources** are taken from the metadata of the retrieved chunks (`extract_source_ids`), never from the LLM. The final line is always `Source: IW-FAB-xxx`.

Care questions are matched to *care* chunks, origin questions to *origin* chunks, using simple keyword rules, so the answer is not padded with unrelated sections.

### Using a free LLM (optional)

Any OpenAI-compatible endpoint works. The easiest free option is [Ollama](https://ollama.com) on your own computer:

```
ollama pull llama3.2
python answer_engine.py ask "How do I wash the linen blend?" --mode llm
```

Other free tiers can be used with environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Endpoint (Ollama) |
| `LLM_MODEL` | `llama3.2` | Model name |
| `LLM_API_KEY` | empty | Key, if the provider needs one |
| `MIN_SCORE` | `0.30` | Confidence cut-off |

Safety rules in `llm` mode: if the LLM cites an ID that was not retrieved, or cites none, its answer is thrown away and the template answer is shown with a note. If the LLM says "I don't know", that is respected. If the LLM cannot be reached, the template answer is shown with a note.

### Set the confidence cut-off (do this once)

The default 0.30 is a reasonable guess for `all-MiniLM-L6-v2`, not a measured value. Run:

```
python answer_engine.py calibrate
```

It prints the best score for questions that are in the data and questions that are not, and suggests a cut-off. If it differs from 0.30, set `MIN_SCORE` (for example `MIN_SCORE=0.35 python answer_engine.py ...`).

## Tests

`python answer_engine.py test` runs 22 checks: 16 logic checks (retrieval size, source extraction, the prompt contains the chunks, "I don't know" fallbacks, citation guard, LLM errors, a fake LLM server) and 6 real searches, for example "How do I wash the linen blend?" must answer with `IW-FAB-015`. Expect `22/22 checks passed.` If the model cannot load, only the 16 logic checks run and the exit code is 2.

## Known limits

- **Template mode cannot tell whether the question is really answerable.** It returns the closest spec text if the score is high enough. A question like "What is the price of Cotton Poplin?" may return Cotton Poplin spec text, which has no price. Only `llm` mode can say "I don't know" for that.
- The cut-off needs calibrating (see above). Results with the real embedding model were not verified by the author of this code in an offline sandbox; run the tests and `calibrate` on your machine.
- `llm` mode was tested against a fake local server, not a real Ollama or hosted model. Small local models can ignore instructions; the citation guard catches missing or invented IDs but not a wrong summary.
- Question types (care, origin) are detected by keywords and can miss unusual wording.
- Answers come from sample data, not real specifications.

## Troubleshooting (Task 3)

| Problem | Fix |
|---|---|
| `No vector store at ...` | Run `python vector_store.py` first |
| Note says `The LLM was not available` | Start Ollama (`ollama serve`) and pull the model, or use `--mode template` |
| Good questions return "I don't know" | Lower `MIN_SCORE` (run `calibrate`) |
| Nonsense questions return spec text | Raise `MIN_SCORE`, or use `--mode llm` |

---

# Repository layout

| Path | Purpose |
|---|---|
| `generate_data.py` | Task 1: generates and checks the dataset |
| `data/fabric_specs.json` | Task 1: the generated dataset (committed) |
| `vector_store.py` | Task 2: load, chunk, embed, store, search, and the built-in test (`python vector_store.py test`, 17 checks). One file, all the code |
| `requirements.txt` | Task 2: libraries to install |
| `chroma_db/` | Task 2: the saved (persistent) vector database, created by `python vector_store.py`. Commit it |
| `results/vector_store_log.txt` | Task 2: log of each build, with proof the database was saved and re-read from disk. Commit it |
| `answer_engine.py` | Task 3: retrieve, confidence check, prompt template, answer with source IDs, and its built-in test (`python answer_engine.py test`, 22 checks). One file |
| `README.md` | This file |
