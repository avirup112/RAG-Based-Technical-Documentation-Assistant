from app.graph.workflow import decide_to_generate


def test_decide_to_generate_has_docs():
    state = {"relevant_docs": [{"content": "test"}]}
    assert decide_to_generate(state) == "generate"


def test_decide_to_generate_no_docs_retry():
    state = {"relevant_docs": [], "retries": 0}
    assert decide_to_generate(state) == "rewrite"


def test_decide_to_generate_max_retries():
    state = {"relevant_docs": [], "retries": 2}
    assert decide_to_generate(state) == "web_search"
