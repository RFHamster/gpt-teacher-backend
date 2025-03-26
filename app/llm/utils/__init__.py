import json

from transformers import PreTrainedTokenizerBase


def count_tokens(text: str, tokenizer: PreTrainedTokenizerBase) -> int:
    """Contar o número de tokens em um texto usando o tokenizer fornecido."""
    return len(tokenizer.encode(text))


def treat_llm_output(text: str) -> str:
    """Removes trailing whitespaces, and other special chars from the LLM
    output."""

    if isinstance(text, str):
        treated_text = '' + text

        treated_text = treated_text.strip()
        treated_text = treated_text.strip(r'```json')
        treated_text = treated_text.strip(r'```')
        treated_text = treated_text.strip()

        return treated_text

    if isinstance(text, dict):
        return json.dumps(text)
