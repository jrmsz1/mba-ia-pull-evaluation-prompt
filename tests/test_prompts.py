"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils import validate_prompt_structure

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    data = load_prompts(PROMPT_FILE)
    return data[PROMPT_KEY]


class TestPrompts:

    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        assert "você é" in system_prompt or "voce e" in system_prompt or "you are" in system_prompt, \
            "Prompt não define uma persona com 'Você é...'"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_markdown = "markdown" in system_prompt
        has_user_story_format = "como" in system_prompt and "eu quero" in system_prompt
        has_format_keyword = "formato" in system_prompt or "format" in system_prompt
        assert has_markdown or has_user_story_format or has_format_keyword, \
            "Prompt não menciona formato Markdown ou estrutura de User Story"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_exemplo = "exemplo" in system_prompt or "example" in system_prompt
        has_relato = "relato de bug" in system_prompt
        assert has_exemplo and has_relato, \
            "Prompt não contém exemplos Few-shot (deve ter 'Exemplo' e 'Relato de Bug')"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não há [TODO] no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        assert "[TODO]" not in system_prompt, "system_prompt contém [TODO] não resolvido"
        assert "[TODO]" not in user_prompt, "user_prompt contém [TODO] não resolvido"

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, \
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])