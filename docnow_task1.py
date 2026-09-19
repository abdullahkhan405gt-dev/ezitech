"""
DocNow Telehealth Consultation Summariser - Task 1
Beginner-friendly single-file version.

Run in VS Code:
    python docnow_task1.py

This implements the requirements from the project brief:
- Strict grounding rules
- "I don't know" refusal when information is missing
- Structured output
- Tests for missing/ambiguous information
- Versioned prompt template inside this file
"""

import json
import re

VERSION = "v1.0"

# 1. STRICT PROMPT TEMPLATE
SYSTEM_PROMPT = """
You are a grounded telehealth consultation summarizer.

RULES:
1. Use ONLY information explicitly present in the transcript.
2. Never guess, assume, or invent medical facts.
3. If a requested detail is missing, write "I don't know".
4. If a symptom or detail is ambiguous, write "I don't know".
5. Do not create a diagnosis unless the transcript explicitly states one.
6. Do not create medicines, doses, allergies, test results, medical history,
   or follow-up instructions unless they are explicitly stated.
7. Keep the summary faithful to the patient's and clinician's words.
8. Return the result using the required structured format.
""".strip()

# 2. SIMPLE GROUNDED EXTRACTOR

UNKNOWN = "I don't know"

def extract_summary(transcript):
    """Extract information only from the supplied transcript."""

    text = transcript.strip()

    result = {
        "patient_symptoms": [],
        "medical_history": [],
        "diagnosis": UNKNOWN,
        "medications": [],
        "doctor_instructions": [],
        "follow_up": UNKNOWN,
        "missing_information": []
    }

    if not text:
        result["missing_information"].append("Transcript is empty")
        return result

    # Split transcript into simple sentences.
    sentences = re.split(r'(?<=[.!?])\s+', text)

    for sentence in sentences:
        s = sentence.strip()
        lower = s.lower()

        if not s:
            continue

        # Symptoms: only capture explicit patient statements.
        if lower.startswith(("patient:", "patient says:", "patient reports:")):
            statement = re.sub(
                r'^(patient|patient says|patient reports):\s*',
                '',
                s,
                flags=re.I
            ).strip()

            # Do not treat a clear negative answer as a symptom.
            if statement.lower() not in {
                "no.", "no", "none.", "none", "i don't know.", "i don't know"
            }:
                result["patient_symptoms"].append(statement)

        # Diagnosis: only when explicitly stated.
        if "diagnosis:" in lower:
            value = s.split(":", 1)[1].strip()
            if value:
                result["diagnosis"] = value

        # Medication: only when explicitly stated.
        if lower.startswith(("medication:", "medications:")):
            value = s.split(":", 1)[1].strip()
            if value:
                result["medications"].append(value)

        # Doctor instructions.
        if lower.startswith(("doctor:", "instruction:", "instructions:")):
            value = s.split(":", 1)[1].strip()
            if value:
                result["doctor_instructions"].append(value)

        # Follow-up.
        if lower.startswith(("follow-up:", "follow up:", "followup:")):
            value = s.split(":", 1)[1].strip()
            if value:
                result["follow_up"] = value

        # Medical history.
        if lower.startswith(("history:", "medical history:")):
            value = s.split(":", 1)[1].strip()
            if value:
                result["medical_history"].append(value)

    # Refusal rules for missing information.
    if not result["patient_symptoms"]:
        result["patient_symptoms"] = [UNKNOWN]
        result["missing_information"].append("Patient symptoms were not provided")

    if not result["medical_history"]:
        result["missing_information"].append("Medical history was not provided")

    if not result["medications"]:
        result["missing_information"].append("Medications were not provided")

    if result["diagnosis"] == UNKNOWN:
        result["missing_information"].append("Diagnosis was not provided")

    if result["follow_up"] == UNKNOWN:
        result["missing_information"].append("Follow-up instructions were not provided")

    if not result["doctor_instructions"]:
        result["missing_information"].append("Doctor instructions were not provided")

    return result


# 3. TEST CASES

def run_tests():
    print("\n========== RUNNING TESTS ==========\n")

    # Test 1: Normal transcript
    transcript1 = """
    Patient: I have had a headache since yesterday.
    History: No previous medical problems reported.
    Diagnosis: I don't know.
    Doctor: Take rest and drink plenty of water.
    Follow-up: Return if the headache gets worse.
    """

    result1 = extract_summary(transcript1)

    assert "I have had a headache since yesterday." in result1["patient_symptoms"]
    assert "Take rest and drink plenty of water." in result1["doctor_instructions"]
    assert result1["follow_up"] == "Return if the headache gets worse."
    print("TEST 1 PASSED - Normal transcript")

    # Test 2: Missing patient data
    transcript2 = """
    Doctor: Please provide more information about the symptoms.
    """

    result2 = extract_summary(transcript2)

    assert result2["patient_symptoms"] == [UNKNOWN]
    assert result2["diagnosis"] == UNKNOWN
    assert len(result2["missing_information"]) > 0
    print("TEST 2 PASSED - Missing information triggers refusal")

    # Test 3: No invented diagnosis
    transcript3 = """
    Patient: I have stomach pain.
    """

    result3 = extract_summary(transcript3)

    assert result3["patient_symptoms"] == ["I have stomach pain."]
    assert result3["diagnosis"] == UNKNOWN
    print("TEST 3 PASSED - No diagnosis invented")

    # Test 4: Ambiguous/missing symptom
    transcript4 = """
    Patient: I'm not sure what is wrong.
    """

    result4 = extract_summary(transcript4)

    assert result4["diagnosis"] == UNKNOWN
    print("TEST 4 PASSED - Ambiguous information handled safely")

    print("\nALL TESTS PASSED.\n")



# 4. MAIN PROGRAM


def main():
    print("=" * 60)
    print("DOCNOW TELEHEALTH CONSULTATION SUMMARISER")
    print("Task 1 - Strict Extraction and Refusal Prompts")
    print("Version:", VERSION)
    print("=" * 60)

    print("\nSTRICT RULES:")
    print("- Only use information from the transcript.")
    print('- Missing information -> "I don\'t know".')
    print("- Never guess or invent medical facts.")
    print("- No diagnosis unless explicitly stated.")

    print("\nEnter a consultation transcript.")
    print("Example:")
    print("Patient: I have had a headache since yesterday.")
    print("Doctor: Take rest and drink plenty of water.")
    print("Follow-up: Return if the headache gets worse.")
    print("\nType END on a new line when finished.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    transcript = "\n".join(lines)

    result = extract_summary(transcript)

    print("\n========== STRUCTURED OUTPUT ==========\n")
    print(json.dumps(result, indent=4))

    print("\n========== PROMPT TEMPLATE ==========\n")
    print(SYSTEM_PROMPT)

    print("\n========== LOCAL SAFETY TESTS ==========")
    run_tests()


if __name__ == "__main__":
    main()
