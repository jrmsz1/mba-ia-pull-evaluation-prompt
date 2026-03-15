"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    errors = []

    if not prompt_data.get("system_prompt", "").strip():
        errors.append("system_prompt está vazio ou ausente")

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("user_prompt está vazio ou ausente")

    if "[TODO]" in prompt_data.get("system_prompt", ""):
        errors.append("system_prompt ainda contém [TODO]")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    print(f"\nFazendo push de: {prompt_name}")

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return False

    try:
        system_prompt = prompt_data["system_prompt"]
        user_prompt = prompt_data["user_prompt"]

        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(user_prompt),
        ])

        hub.push(
            prompt_name,
            chat_prompt,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
        )

        print(f"✅ Push realizado com sucesso: {prompt_name}")
        print(f"   🔗 https://smith.langchain.com/prompts/{prompt_name.split('/')[-1]}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        return False


def main():
    print_section_header("Push de Prompts Otimizados para o LangSmith")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    langsmith_username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not langsmith_username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        print("   Adicione: LANGSMITH_USERNAME=seu_usuario_langsmith")
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"
    data = load_yaml(yaml_path)

    if not data:
        print(f"❌ Não foi possível carregar: {yaml_path}")
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)

    if not prompt_data:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        return 1

    prompt_name = f"{langsmith_username}/{prompt_key}"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print("\n✅ Push concluído!")
        print("\nPróximos passos:")
        print("  1. Verifique em: https://smith.langchain.com/prompts")
        print("  2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        print("\n❌ Push falhou. Corrija os erros acima e tente novamente.")
        return 1


if __name__ == "__main__":
    sys.exit(main())