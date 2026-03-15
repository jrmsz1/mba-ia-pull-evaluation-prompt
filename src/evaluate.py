"""
Script de avaliação usando as 4 métricas específicas para Bug to User Story.
Critério de aprovação: Tone, Acceptance Criteria, User Story Format, Completeness >= 0.9
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, str(Path(__file__).parent))
from utils import check_env_vars, format_score, print_section_header, get_llm as get_configured_llm
from metrics import (
    evaluate_tone_score,
    evaluate_acceptance_criteria_score,
    evaluate_user_story_format_score,
    evaluate_completeness_score
)

load_dotenv()

THRESHOLD = 0.9


def get_llm():
    return get_configured_llm(temperature=0)


def load_dataset_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    examples = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    examples.append(json.loads(line))
        return examples
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def create_evaluation_dataset(client: Client, dataset_name: str, jsonl_path: str) -> str:
    print(f"Verificando dataset: {dataset_name}...")
    examples = load_dataset_from_jsonl(jsonl_path)

    if not examples:
        print("❌ Nenhum exemplo carregado.")
        return dataset_name

    print(f"   ✔ {len(examples)} exemplos carregados de {jsonl_path}")

    try:
        existing = None
        for ds in client.list_datasets(dataset_name=dataset_name):
            if ds.name == dataset_name:
                existing = ds
                break

        if existing:
            print(f"   ✔ Dataset '{dataset_name}' já existe, reutilizando.")
        else:
            dataset = client.create_dataset(dataset_name=dataset_name)
            for ex in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=ex["inputs"],
                    outputs=ex["outputs"]
                )
            print(f"   ✔ Dataset criado com {len(examples)} exemplos.")
    except Exception as e:
        print(f"   ⚠️  Erro ao criar dataset: {e}")

    return dataset_name


def pull_prompt(prompt_name: str) -> ChatPromptTemplate:
    print(f"   Carregando prompt do LangSmith: {prompt_name}")
    try:
        prompt = hub.pull(prompt_name)
        print("   ✔ Prompt carregado com sucesso.")
        return prompt
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ Não foi possível carregar o prompt '{prompt_name}'")
        print(f"{'='*60}")
        print("Verifique se você já fez push:")
        print("  python src/push_prompts.py")
        print(f"{'='*60}\n")
        raise


def evaluate_example(prompt_template, example, llm) -> Dict[str, Any]:
    try:
        inputs = example.inputs if hasattr(example, 'inputs') else {}
        outputs = example.outputs if hasattr(example, 'outputs') else {}

        chain = prompt_template | llm
        response = chain.invoke(inputs)
        user_story = response.content

        bug_report = inputs.get("bug_report", inputs.get("question", ""))
        reference = outputs.get("reference", "") if isinstance(outputs, dict) else ""

        return {
            "bug_report": bug_report,
            "user_story": user_story,
            "reference": reference
        }
    except Exception as e:
        print(f"      ⚠️  Erro no exemplo: {e}")
        return {"bug_report": "", "user_story": "", "reference": ""}


def evaluate_prompt(prompt_name: str, dataset_name: str, client: Client) -> Dict[str, float]:
    print(f"\n🔍 Avaliando: {prompt_name}")

    try:
        prompt_template = pull_prompt(prompt_name)
        examples = list(client.list_examples(dataset_name=dataset_name))
        print(f"   Dataset: {len(examples)} exemplos (avaliando primeiros 10)")

        llm = get_llm()

        tone_scores = []
        criteria_scores = []
        format_scores = []
        completeness_scores = []

        print("   Avaliando exemplos...")

        for i, example in enumerate(examples[:10], 1):
            result = evaluate_example(prompt_template, example, llm)

            if not result["user_story"]:
                continue

            bug = result["bug_report"]
            story = result["user_story"]
            ref = result["reference"]

            tone = evaluate_tone_score(bug, story, ref)
            criteria = evaluate_acceptance_criteria_score(bug, story, ref)
            fmt = evaluate_user_story_format_score(bug, story, ref)
            completeness = evaluate_completeness_score(bug, story, ref)

            tone_scores.append(tone["score"])
            criteria_scores.append(criteria["score"])
            format_scores.append(fmt["score"])
            completeness_scores.append(completeness["score"])

            print(
                f"      [{i}/10] "
                f"Tone:{tone['score']:.2f} "
                f"Criteria:{criteria['score']:.2f} "
                f"Format:{fmt['score']:.2f} "
                f"Completeness:{completeness['score']:.2f}"
            )

        def avg(lst): return round(sum(lst) / len(lst), 4) if lst else 0.0

        return {
            "tone_score": avg(tone_scores),
            "acceptance_criteria_score": avg(criteria_scores),
            "user_story_format_score": avg(format_scores),
            "completeness_score": avg(completeness_scores),
        }

    except Exception as e:
        print(f"   ❌ Erro na avaliação: {e}")
        return {
            "tone_score": 0.0,
            "acceptance_criteria_score": 0.0,
            "user_story_format_score": 0.0,
            "completeness_score": 0.0,
        }


def display_results(prompt_name: str, scores: Dict[str, float]) -> bool:
    print("\n" + "=" * 50)
    print(f"Prompt: {prompt_name}")
    print("=" * 50)

    labels = {
        "tone_score": "Tone Score",
        "acceptance_criteria_score": "Acceptance Criteria Score",
        "user_story_format_score": "User Story Format Score",
        "completeness_score": "Completeness Score",
    }

    all_passed = True
    for key, label in labels.items():
        score = scores[key]
        passed = score >= THRESHOLD
        if not passed:
            all_passed = False
        print(f"  - {label}: {format_score(score, THRESHOLD)}")

    average = round(sum(scores.values()) / len(scores), 4)
    print("\n" + "-" * 50)
    print(f"📊 MÉDIA: {average:.4f}")
    print("-" * 50)

    if all_passed and average >= THRESHOLD:
        print(f"\n✅ STATUS: APROVADO — todas as métricas >= {THRESHOLD}")
    else:
        print(f"\n❌ STATUS: REPROVADO")
        failing = [labels[k] for k, v in scores.items() if v < THRESHOLD]
        for f in failing:
            print(f"   ⚠️  {f} abaixo de {THRESHOLD}")

    return all_passed and average >= THRESHOLD


def main():
    print_section_header("AVALIAÇÃO DE PROMPTS — Bug to User Story")

    provider = os.getenv("LLM_PROVIDER", "google")
    llm_model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    eval_model = os.getenv("EVAL_MODEL", "gemini-2.5-flash")

    print(f"Provider: {provider}")
    print(f"Modelo: {llm_model}")
    print(f"Modelo Avaliação: {eval_model}\n")

    required_vars = ["LANGSMITH_API_KEY", "GOOGLE_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    langsmith_username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not langsmith_username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return 1

    jsonl_path = "datasets/bug_to_user_story.jsonl"
    if not Path(jsonl_path).exists():
        print(f"❌ Dataset não encontrado: {jsonl_path}")
        return 1

    client = Client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "desafio-prompt-engineer")
    dataset_name = f"{project_name}-eval"

    create_evaluation_dataset(client, dataset_name, jsonl_path)

    prompt_name = f"{langsmith_username}/bug_to_user_story_v2"
    prompts_to_evaluate = [prompt_name]

    all_passed = True
    results_summary = []

    for name in prompts_to_evaluate:
        try:
            scores = evaluate_prompt(name, dataset_name, client)
            passed = display_results(name, scores)
            all_passed = all_passed and passed
            results_summary.append({"prompt": name, "scores": scores, "passed": passed})
        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{name}': {e}")
            all_passed = False

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50)
    aprovados = sum(1 for r in results_summary if r["passed"])
    print(f"Avaliados: {len(results_summary)} | Aprovados: {aprovados} | Reprovados: {len(results_summary) - aprovados}")

    if all_passed:
        print(f"\n✅ Todos os prompts aprovados com média >= {THRESHOLD}!")
        print(f"\nConfira: https://smith.langchain.com/projects/{project_name}")
        return 0
    else:
        print(f"\n⚠️  Refatore o prompt e rode novamente:")
        print("  1. Edite: prompts/bug_to_user_story_v2.yml")
        print("  2. Push:  python src/push_prompts.py")
        print("  3. Avalie: python src/evaluate.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())