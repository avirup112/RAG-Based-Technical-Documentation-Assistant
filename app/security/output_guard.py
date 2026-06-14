from app.core.llm import get_judge_llm
from loguru import logger


def check_output_safety(output: str) -> bool:
    """
    Uses an LLM-as-a-judge to validate that the output doesn't contain toxic content,
    forbidden leaks, or malicious advice.
    Returns True if safe, False otherwise.
    """
    # Quick heuristic check first to save LLM calls
    forbidden_terms = [
        "AGENT_SECRET_KEY",
        "JWT_SECRET_KEY",
        "TAVILY_API_KEY",
        "MONGODB_URI",
    ]
    for term in forbidden_terms:
        if term in output:
            logger.warning("Output guard triggered by keyword leak.")
            return False

    try:
        llm = get_judge_llm(temperature=0.0)

        prompt = f"""
        You are an output safety guard for a technical documentation assistant.
        Analyze the following response that the assistant is about to send to the user.
        Determine if the response violates any safety policies:
        1. Contains highly toxic, offensive, or harmful language.
        2. Leaks internal system configuration (like API keys or internal database paths).
        3. Instructs the user to run destructive commands (like 'rm -rf /' without proper context).

        Response:
        "{output}"

        Is this response completely safe to display to the user? Answer ONLY 'yes' or 'no'.
        """

        res = llm.invoke(prompt)
        score = res.content.strip().lower()

        if "no" in score:
            logger.warning("Output guard triggered by LLM analysis.")
            return False

        return True
    except Exception as e:
        logger.error(f"Error during LLM output guard check: {e}")
        return True
