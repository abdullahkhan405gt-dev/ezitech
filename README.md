DocNow Telehealth Consultation Summariser

This project is a beginner-friendly Python tool that summarizes telehealth consultation transcripts while avoiding invented medical information.

What it does:

Extracts patient symptoms and consultation details.
Uses “I don't know” when information is missing or unclear.
Does not invent diagnoses, medicines, or medical facts.
Produces structured JSON output.
Includes automated tests for missing and ambiguous information.
Provides strict grounding and refusal rules.# ezitech
onsite Ai internship 

FOR EZITECH TASK_3

# DocNow Telehealth – Task 2

## Description

A Python program that converts raw telehealth transcripts into structured JSON and validates the data using Pydantic.

## Features

* Extracts patient metadata.
* Extracts doctor/patient dialogue.
* Validates dates and required fields.
* Produces structured JSON.
* Rejects invalid transcripts.
* Stops summarisation when validation fails.

## Technologies

* Python
* Pydantic
* JSON
* VS Code

## How to Run

Install Pydantic:

```bash
pip install pydantic
```

Run the program:

```bash
python ezitech.py
```

## Tests

The program tests:

* Valid transcript 
* Invalid date 
* Missing field 
* Broken dialogue 

All validation tests pass.

## Project Structure

```text
telehealth-task2/
├── ezitech.py
└── README.md
```

## Author

Muhammad Abdullah Khan
