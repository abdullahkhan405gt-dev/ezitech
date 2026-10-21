# Indus Weaves - Internal Textile Spec Search Tool

A local, free-tier tool that answers questions about fabric specifications (composition, care, origin) with clear source citations, so staff do not have to search PDFs by hand.

**Project progress:** Task 1 of 5 (sample data) is done. Vector store, answer engine, web app and handover docs come in later tasks.

> **The data in this repository is synthetic sample data.** The numbers look realistic but are not lab results and are not real Indus Weaves specifications. Do not use them for real orders or client answers.

---

## Task 1: the sample dataset

`generate_data.py` creates `data/fabric_specs.json`, a list of **27 fabric specs**. This file is the source of truth that the search tool will read in later tasks.

### Quick start (about one minute)

You only need Python 3.8 or newer. There is nothing to install.

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
3. The file `data/fabric_specs.json` is rewritten. The result is identical every time, because the script uses no randomness. After a real change, commit the updated JSON.

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
| `id` | Unique ID. Used later as the citation. |
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
| `text` | One plain-English paragraph combining everything above. **The search tool reads this field.** |

### What the dataset covers

27 fabrics: cotton (10), blend (8), synthetic (4), cellulosic (2), and one each of linen, wool and silk. It includes single-fibre and blended fabrics, woven and knit constructions, different care routines (machine wash, hand wash, dry clean), local and imported yarn, and entries with and without certifications (11 of 27 list one). The variety is deliberate, so the search tool can later be tested on realistic questions such as "which fabrics are dry clean?" (3 entries) or "what is the composition of IW-FAB-005?".

### Built-in checks

Every run verifies, and refuses to save otherwise:

- between 20 and 30 entries
- every ID and every name is unique
- fibre percentages add up to exactly 100
- no required field (`id`, `name`, `category`, `composition`, `care`, `origin`, `source`, `text`) is empty
- each `text` snippet contains the fabric's name and composition

---

## Repository layout

| Path | Purpose |
|---|---|
| `generate_data.py` | Generates and checks the dataset |
| `data/fabric_specs.json` | The generated dataset (committed) |
| `README.md` | This file |
