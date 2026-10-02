
# DocNow Telehealth Structured Transcript Validator

## Description

This project validates telehealth consultation transcripts before
summarization.

It extracts patient metadata and doctor/patient dialogue, converts the
information into structured JSON, and uses Pydantic to validate the data.

Invalid transcripts are rejected with clear error messages.

## Features

- Extracts patient ID
- Extracts patient name
- Extracts date of birth
- Extracts consultation date
- Extracts doctor and patient dialogue
- Validates dates using Pydantic
- Detects missing required fields
- Detects empty dialogue
- Stops summarization when validation fails
- Outputs validated JSON

## Project Structure

text
docnow-telehealth-validator/
│
├── src/
│   └── validator.py
│
├── README.md
│
└── requirements.txt

## Installation

Open the project folder in VS Code.

Install Pydantic:


pip install -r requirements.txt


## Run

From the project root folder:


python src\validator.py
 

## Test Cases

The program tests four transcripts:

1. Good Transcript

   * Should pass validation.

2. Bad Date

   * Contains an invalid date.
   * Should be rejected.

3. Missing Field

   * Missing consultation date.
   * Should be rejected.

4. Broken Dialogue

   * Contains an empty Doctor dialogue.
   * Should be rejected.

## Expected Result

text
Good transcript: PASS
Bad date rejection: PASS
Missing field rejection: PASS
Broken dialogue rejection: PASS


## Technologies

* Python
* Pydantic
* JSON


