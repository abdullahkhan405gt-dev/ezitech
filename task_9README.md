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

# Indus Weaves - Internal Textile Spec Search Tool

A local, free-tier tool that answers questions about fabric specifications (composition, care, origin) with clear source citations, so staff do not have to search PDFs by hand.

**Project progress:** Tasks 1 to 4 of 5 are done: sample data (Task 1), the local vector store (Task 2), the answer engine that cites sources (Task 3) and the web page (Task 4). The handover docs come in the last task.

**Live app:** _paste the Hugging Face Space link here after deploying (see Task 4)_

> **The data in this repository is synthetic sample data.** The numbers look realistic but are not lab results and are not real Indus Weaves specifications. Do not use them for real orders or client answers.

---

## Contents

1. [Task 1: the sample dataset](#task-1-the-sample-dataset) (needs only Python)
2. [Task 2: the local vector store](#task-2-the-local-vector-store-search-backend) (free, local, no API key)
3. [Task 3: the answer engine](#task-3-the-answer-engine-answers-with-sources) (no extra installs; optional free LLM)
4. [Task 4: the web app and deployment](#task-4-the-web-app-and-deployment) (Streamlit, free hosting)
5. [Repository layout](#repository-layout)

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
| **Vector store** | A
