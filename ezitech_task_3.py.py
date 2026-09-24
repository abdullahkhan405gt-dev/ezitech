import json
from datetime import date
from pydantic import BaseModel, ValidationError


class PatientMetadata(BaseModel):
    patient_id: str
    patient_name: str
    date_of_birth: date
    consultation_date: date


class DialogueBlock(BaseModel):
    speaker: str
    text: str


class TelehealthRecord(BaseModel):
    patient: PatientMetadata
    dialogue: list[DialogueBlock]


GOOD_TRANSCRIPT = """
Patient ID: P001
Patient Name: Ali Khan
Date of Birth: 1998-05-12
Consultation Date: 2026-09-20

Doctor: Hello Ali, what brings you in today?
Patient: I have had a headache since yesterday.
Doctor: Do you have a fever?
Patient: No, I do not have a fever.
Doctor: Please take rest and drink plenty of water.
"""

BAD_DATE_TRANSCRIPT = """
Patient ID: P002
Patient Name: Ahmed
Date of Birth: 1995-20-50
Consultation Date: 2026-09-20

Doctor: What is your problem?
Patient: I have a headache.
"""

MISSING_FIELD_TRANSCRIPT = """
Patient ID: P003
Patient Name: Sara
Date of Birth: 2000-04-10

Doctor: What brings you here?
Patient: I have a cough.
"""

BROKEN_DIALOGUE_TRANSCRIPT = """
Patient ID: P004
Patient Name: Hamza
Date of Birth: 1999-03-15
Consultation Date: 2026-09-20

Doctor:
Patient: I have stomach pain.
Doctor: How long have you had it?
"""


def extract_transcript(raw_text):
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    patient_id = None
    patient_name = None
    date_of_birth = None
    consultation_date = None
    dialogue = []

    for line in lines:
        if line.startswith("Patient ID:"):
            patient_id = line.replace("Patient ID:", "").strip()

        elif line.startswith("Patient Name:"):
            patient_name = line.replace("Patient Name:", "").strip()

        elif line.startswith("Date of Birth:"):
            date_of_birth = line.replace("Date of Birth:", "").strip()

        elif line.startswith("Consultation Date:"):
            consultation_date = line.replace("Consultation Date:", "").strip()

        elif line.startswith("Doctor:"):
            text = line.replace("Doctor:", "").strip()

            if not text:
                raise ValueError("Doctor dialogue is empty.")

            dialogue.append({
                "speaker": "Doctor",
                "text": text
            })

        elif line.startswith("Patient:"):
            text = line.replace("Patient:", "").strip()

            if not text:
                raise ValueError("Patient dialogue is empty.")

            dialogue.append({
                "speaker": "Patient",
                "text": text
            })

    missing = []

    if patient_id is None:
        missing.append("patient_id")
    if patient_name is None:
        missing.append("patient_name")
    if date_of_birth is None:
        missing.append("date_of_birth")
    if consultation_date is None:
        missing.append("consultation_date")
    if not dialogue:
        missing.append("dialogue")

    if missing:
        raise ValueError(
            "Missing required fields: " + ", ".join(missing)
        )

    return {
        "patient": {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "date_of_birth": date_of_birth,
            "consultation_date": consultation_date
        },
        "dialogue": dialogue
    }


def process_transcript(name, raw_text):
    print("\n" + "=" * 60)
    print("TEST:", name)
    print("=" * 60)

    try:
        data = extract_transcript(raw_text)
        record = TelehealthRecord.model_validate(data)

        print("STATUS: VALID")
        print("\nValidated JSON:")
        print(json.dumps(record.model_dump(mode="json"), indent=4))
        print("\nSummarisation can continue.")

        return True

    except ValidationError as error:
        print("STATUS: INVALID")
        print("\nValidation error:")
        print(error)
        print("\nSummarisation STOPPED.")
        return False

    except ValueError as error:
        print("STATUS: INVALID")
        print("\nError:")
        print(error)
        print("\nSummarisation STOPPED.")
        return False


def main():
    print("=" * 60)
    print("DOCNOW TELEHEALTH - TASK 2")
    print("Structured Transcript Validator")
    print("=" * 60)

    results = []

    results.append(process_transcript("Good Transcript", GOOD_TRANSCRIPT))
    results.append(process_transcript("Bad Date", BAD_DATE_TRANSCRIPT))
    results.append(process_transcript("Missing Field", MISSING_FIELD_TRANSCRIPT))
    results.append(process_transcript("Broken Dialogue", BROKEN_DIALOGUE_TRANSCRIPT))

    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)

    print("Good transcript:", "PASS" if results[0] else "FAIL")
    print("Bad date rejection:", "PASS" if not results[1] else "FAIL")
    print("Missing field rejection:", "PASS" if not results[2] else "FAIL")
    print("Broken dialogue rejection:", "PASS" if not results[3] else "FAIL")

    print("\nTask 2 validation test completed.")


if __name__ == "__main__":
    main()
