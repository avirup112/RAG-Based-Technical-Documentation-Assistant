from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from loguru import logger

# Initialize engines once at module level
try:
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
except Exception as e:
    logger.error(
        f"Failed to initialize Presidio engines: {e}. Make sure python -m spacy download en_core_web_lg is installed."
    )
    analyzer = None
    anonymizer = None


def redact_pii(text: str) -> str:
    """
    Advanced PII detection and redaction using Microsoft Presidio.
    Detects entities like EMAIL_ADDRESS, PHONE_NUMBER, PERSON, LOCATION, US_SSN, CREDIT_CARD.
    """
    if not text or not isinstance(text, str):
        return text or ""
    if not analyzer or not anonymizer:
        logger.warning("Presidio is not initialized, falling back to original text.")
        return text

    try:
        # Analyze the text for PII entities
        results = analyzer.analyze(text=text, entities=[], language="en")

        # Anonymize the findings
        anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)

        return anonymized_result.text
    except Exception as e:
        logger.error(f"Error during PII redaction: {e}")
        return text
