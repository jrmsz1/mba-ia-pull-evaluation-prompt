"""
Script para fazer pull de prompts do LangSmith Prompt Hub.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub

sys.path.insert(0, str(Path(__file__).parent))
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    print_section_header("Pull de Prompts do LangSmith")

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull de: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print("✅ Prompt recebido com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao fazer pull: {e}")
        return False

    messages = []
    for msg in prompt.messages:
        class_name = msg.__class__.__name__.lower()
        if "system" in class_name:
            role = "system"
        elif "human" in class_name:
            role = "human"
        else:
            role = "assistant"
        messages.append({
            "role": role,
            "content": msg.prompt.template
        })

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt original (baixa qualidade) - extraído do LangSmith",
            "source": prompt_name,
            "messages": messages,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"]
        }
    }

    output_path = "prompts/raw_prompts.yml"
    if save_yaml(prompt_data, output_path):
        print(f"✅ Prompt salvo em: {output_path}")
    else:
        print("❌ Erro ao salvar arquivo.")
        return False

    print("\nConteúdo extraído:")
    for msg in messages:
        print(f"\n[{msg['role'].upper()}]")
        content = msg['content']
        print(content[:400] + "..." if len(content) > 400 else content)

    return True


def main():
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())