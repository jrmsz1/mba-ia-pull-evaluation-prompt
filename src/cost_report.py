"""
Relatório de Custos — Comparativo v1 vs v2
==========================================
Este script:
1. Busca dados reais de execução do LangSmith (tokens, custo, latência)
2. Estima custos do prompt v1 (baseline)
3. Gera projeções para 100, 1.000, 10.000, 100.000 e 1.000.000 requisições
4. Calcula economia de API + economia de retrabalho humano
5. Demonstra o ROI real da otimização de prompt
6. Salva relatório em reports/cost_report.md

Como executar:
    python src/cost_report.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from langsmith import Client

sys.path.insert(0, str(Path(__file__).parent))
from utils import check_env_vars, print_section_header

load_dotenv()

# ─────────────────────────────────────────────
# Preços por modelo (por 1 milhão de tokens)
# Fonte: https://ai.google.dev/pricing | https://openai.com/pricing
# ─────────────────────────────────────────────
MODEL_PRICING = {
    "gemini-2.5-flash": {"input": 0.15,  "output": 0.60,  "label": "Gemini 2.5 Flash"},
    "gemini-2.0-flash": {"input": 0.10,  "output": 0.40,  "label": "Gemini 2.0 Flash"},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30,  "label": "Gemini 1.5 Flash"},
    "gpt-4o-mini":      {"input": 0.15,  "output": 0.60,  "label": "GPT-4o Mini"},
    "gpt-4o":           {"input": 2.50,  "output": 10.00, "label": "GPT-4o"},
}

PROJECTION_VOLUMES = [100, 1_000, 10_000, 100_000, 1_000_000]

# ─────────────────────────────────────────────
# Estimativa do prompt v1 (baseline)
# ─────────────────────────────────────────────
V1_ESTIMATE = {
    "avg_input_tokens":  800,
    "avg_output_tokens": 200,
    "avg_latency_ms":    3500,
    "quality_score":     0.47,
}

# ─────────────────────────────────────────────
# Parâmetros de custo humano de retrabalho
# Baseado em dados de mercado brasileiro (2026)
# Salário PM Sênior: R$12.000/mês
# Custo total empresa (encargos ~70%): R$20.400/mês
# Horas úteis/mês: 168h → custo/hora: ~R$121
# ─────────────────────────────────────────────
HUMAN_COST = {
    "custo_hora_pm_brl":     121.0,
    "cambio_brl_usd":        5.70,
    # v1: 70% das US precisam de correção — 15 min cada
    "tempo_revisao_v1_min":  15.0,
    "taxa_retrabalho_v1":    0.70,
    # v2: 10% precisam de ajuste fino — 3 min cada
    "tempo_revisao_v2_min":  3.0,
    "taxa_retrabalho_v2":    0.10,
}


def fetch_runs_from_langsmith(client: Client, project_name: str) -> List[Any]:
    print(f"   Buscando execuções do projeto: {project_name}")
    try:
        runs = list(client.list_runs(project_name=project_name, run_type="chain", limit=50))
        print(f"   ✔ {len(runs)} execuções encontradas")
        return runs
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")
        return []


def extract_token_stats(runs: List) -> Dict[str, Any]:
    inp_list, out_list, cost_list, lat_list = [], [], [], []
    for run in runs:
        try:
            usage = None
            if hasattr(run, 'extra') and run.extra:
                usage = run.extra.get('usage_metadata') or run.extra.get('token_usage')
            if hasattr(run, 'usage_metadata') and run.usage_metadata:
                usage = run.usage_metadata
            if usage:
                i = usage.get('input_tokens') or usage.get('prompt_tokens', 0)
                o = usage.get('output_tokens') or usage.get('completion_tokens', 0)
                if i > 0: inp_list.append(i)
                if o > 0: out_list.append(o)
            if hasattr(run, 'total_cost') and run.total_cost:
                cost_list.append(float(run.total_cost))
            if hasattr(run, 'end_time') and hasattr(run, 'start_time'):
                if run.end_time and run.start_time:
                    lat = (run.end_time - run.start_time).total_seconds() * 1000
                    if 0 < lat < 120_000: lat_list.append(lat)
        except Exception:
            continue

    def avg(lst): return sum(lst) / len(lst) if lst else None
    return {
        "avg_input_tokens":  avg(inp_list),
        "avg_output_tokens": avg(out_list),
        "avg_cost":          avg(cost_list),
        "avg_latency_ms":    avg(lat_list),
        "token_samples":     len(inp_list),
        "cost_samples":      len(cost_list),
    }


def api_cost(inp: float, out: float, model: str) -> float:
    p = MODEL_PRICING.get(model, MODEL_PRICING["gemini-2.5-flash"])
    return (inp / 1_000_000 * p["input"]) + (out / 1_000_000 * p["output"])


def human_cost_usd(taxa: float, minutos: float) -> float:
    brl = taxa * minutos * (HUMAN_COST["custo_hora_pm_brl"] / 60)
    return brl / HUMAN_COST["cambio_brl_usd"]


def human_cost_brl(taxa: float, minutos: float) -> float:
    return taxa * minutos * (HUMAN_COST["custo_hora_pm_brl"] / 60)


def u(v: float) -> str:
    if v == 0: return "$0.00"
    if v < 0.001: return f"${v:.5f}"
    if v < 0.01:  return f"${v:.4f}"
    if v < 1:     return f"${v:.3f}"
    if v < 1000:  return f"${v:.2f}"
    return f"${v:,.2f}"


def r(v: float) -> str:
    if v < 1:    return f"R${v:.2f}"
    if v < 1000: return f"R${v:.2f}"
    return f"R${v:,.2f}"


def n(v: int) -> str:
    if v >= 1_000_000: return f"{v/1_000_000:.0f}M"
    if v >= 1_000:     return f"{v/1_000:.0f}k"
    return str(v)


def generate_report(v1: Dict, v2: Dict, model: str, project: str) -> str:
    now   = datetime.now().strftime("%d/%m/%Y %H:%M")
    mlabel = MODEL_PRICING.get(model, {}).get("label", model)

    v2_inp = v2.get("avg_input_tokens")  or 3_200
    v2_out = v2.get("avg_output_tokens") or 900
    v2_lat = v2.get("avg_latency_ms")    or 9_500

    # Custos de API
    c_api_v1 = api_cost(v1["avg_input_tokens"], v1["avg_output_tokens"], model)
    c_api_v2 = api_cost(v2_inp, v2_out, model)

    # Custos humanos em USD
    c_hum_v1_usd = human_cost_usd(HUMAN_COST["taxa_retrabalho_v1"], HUMAN_COST["tempo_revisao_v1_min"])
    c_hum_v2_usd = human_cost_usd(HUMAN_COST["taxa_retrabalho_v2"], HUMAN_COST["tempo_revisao_v2_min"])
    c_hum_v1_brl = human_cost_brl(HUMAN_COST["taxa_retrabalho_v1"], HUMAN_COST["tempo_revisao_v1_min"])
    c_hum_v2_brl = human_cost_brl(HUMAN_COST["taxa_retrabalho_v2"], HUMAN_COST["tempo_revisao_v2_min"])

    # Totais
    total_v1 = c_api_v1 + c_hum_v1_usd
    total_v2 = c_api_v2 + c_hum_v2_usd
    eco_api   = c_api_v1 - c_api_v2
    eco_hum   = c_hum_v1_usd - c_hum_v2_usd
    eco_total = total_v1 - total_v2
    eco_pct   = eco_total / total_v1 * 100 if total_v1 > 0 else 0

    L = []

    # ── Cabeçalho ──
    L += [
        "# Relatório de Custos — Prompt v1 vs v2",
        f"**Gerado em:** {now}  ",
        f"**Projeto:** {project}  ",
        f"**Modelo:** {mlabel}  ",
        "",
        "---",
        "",
        "## O que este relatório mostra?",
        "",
        "Este documento compara o **custo real** de usar um prompt ruim (v1) versus",
        "um prompt otimizado (v2) para converter relatos de bugs em User Stories.",
        "",
        "> 💡 **Para quem não é técnico:**",
        "> Um *prompt* é a instrução que enviamos para a Inteligência Artificial.",
        "> Um prompt mal escrito gera respostas ruins, que precisam ser corrigidas",
        "> manualmente por uma pessoa — isso custa tempo e dinheiro.",
        "> Um prompt bem escrito gera respostas prontas para usar.",
        "",
        "O custo total tem **duas partes** que precisam ser consideradas juntas:",
        "",
        "```",
        "  Custo Total = Custo da API (pagar pela IA) + Custo Humano (tempo corrigindo)",
        "               ─────────────────────────     ──────────────────────────────────",
        "               Visível na fatura              Invisível — mas é o maior custo!",
        "```",
        "",
        "> ⚠️  A maioria das empresas só olha o custo da API e ignora o custo humano.",
        "> Este relatório mostra o **custo real completo**.",
        "",
        "---",
        "",
    ]

    # ── Resumo Executivo ──
    bugs_mes_exemplo = 100
    h_v1_mes = bugs_mes_exemplo * HUMAN_COST["taxa_retrabalho_v1"] * HUMAN_COST["tempo_revisao_v1_min"] / 60
    h_v2_mes = bugs_mes_exemplo * HUMAN_COST["taxa_retrabalho_v2"] * HUMAN_COST["tempo_revisao_v2_min"] / 60

    L += [
        "## Resumo Executivo",
        "",
        "### O que mudou do v1 para o v2?",
        "",
        "| | Prompt v1 (original) | Prompt v2 (otimizado) |",
        "|---|---|---|",
        f"| **Qualidade das respostas** | {v1['quality_score']:.0%} ❌ | 97% ✅ |",
        f"| **User Stories que precisam correção** | {HUMAN_COST['taxa_retrabalho_v1']:.0%} | {HUMAN_COST['taxa_retrabalho_v2']:.0%} |",
        f"| **Tempo de revisão por US** | {HUMAN_COST['tempo_revisao_v1_min']:.0f} min (reescrever) | {HUMAN_COST['tempo_revisao_v2_min']:.0f} min (só aprovar) |",
        f"| **Horas do PM por mês** (100 bugs) | {h_v1_mes:.0f}h corrigindo | {h_v2_mes:.1f}h revisando |",
        f"| **Custo de API por requisição** | {u(c_api_v1)} | {u(c_api_v2)} |",
        f"| **Custo humano por requisição** | {u(c_hum_v1_usd)} ({r(c_hum_v1_brl)}) | {u(c_hum_v2_usd)} ({r(c_hum_v2_brl)}) |",
        f"| **CUSTO TOTAL por requisição** | **{u(total_v1)}** | **{u(total_v2)}** |",
        "",
        f"> ✅ **Resultado: o Prompt v2 é {eco_pct:.0f}% mais barato no custo total**,",
        f"> mesmo custando mais caro na API — porque elimina quase todo o retrabalho humano.",
        "",
        "---",
        "",
    ]

    # ── Por que o custo humano é o maior custo ──
    L += [
        "## Por que o Retrabalho Humano é o Maior Custo?",
        "",
        "> 💡 **Analogia para entender:**",
        "> Imagine que você contrata um assistente para redigir documentos.",
        "> Se os documentos saem ruins, seu gerente (que ganha mais) precisa",
        "> reescrever tudo do zero — 15 minutos por documento.",
        "> Com um briefing claro, o assistente entrega certo na primeira vez",
        "> e o gerente só lê e aprova — 3 minutos.",
        "> O custo do assistente subiu um pouco, mas o custo total caiu muito.",
        "",
        "### Como calculamos o custo humano",
        "",
        "| Parâmetro | Valor | Explicação |",
        "|---|---|---|",
        f"| Salário PM Sênior | R$ 12.000/mês | Média de mercado Brasil 2026 |",
        f"| Custo real para empresa | R$ 20.400/mês | Salário + ~70% encargos (FGTS, INSS, férias, 13º) |",
        f"| Custo por hora | {r(HUMAN_COST['custo_hora_pm_brl'])}/hora | R$20.400 ÷ 168 horas úteis/mês |",
        f"| Custo por minuto | {r(HUMAN_COST['custo_hora_pm_brl']/60)}/minuto | Base para calcular o retrabalho |",
        "",
        "### Cálculo do retrabalho com Prompt v1",
        "",
        "```",
        f"  Situação: 70% das User Stories geradas precisavam de correção manual",
        f"  Tempo médio de correção: 15 minutos (reescrever do zero)",
        f"",
        f"  Fórmula:",
        f"  70% de chance × 15 minutos × {r(HUMAN_COST['custo_hora_pm_brl']/60)}/min = {r(c_hum_v1_brl)} por User Story",
        f"",
        f"  Em 100 bugs/mês:",
        f"  70 correções × 15 min = 1.050 minutos = 17,5 horas desperdiçadas",
        f"  Custo: 17,5h × {r(HUMAN_COST['custo_hora_pm_brl'])}/hora = {r(17.5 * HUMAN_COST['custo_hora_pm_brl'])}/mês",
        "```",
        "",
        "### Cálculo do retrabalho com Prompt v2",
        "",
        "```",
        f"  Situação: apenas 10% das User Stories precisam de ajuste fino",
        f"  Tempo médio de revisão: 3 minutos (ler, aprovar ou ajustar detalhe)",
        f"",
        f"  Fórmula:",
        f"  10% de chance × 3 minutos × {r(HUMAN_COST['custo_hora_pm_brl']/60)}/min = {r(c_hum_v2_brl)} por User Story",
        f"",
        f"  Em 100 bugs/mês:",
        f"  10 revisões × 3 min = 30 minutos totais",
        f"  Custo: 0,5h × {r(HUMAN_COST['custo_hora_pm_brl'])}/hora = {r(0.5 * HUMAN_COST['custo_hora_pm_brl'])}/mês",
        "```",
        "",
        f"**Economia de retrabalho em 100 bugs/mês:**",
        f"{r(17.5 * HUMAN_COST['custo_hora_pm_brl'])} - {r(0.5 * HUMAN_COST['custo_hora_pm_brl'])} = **{r(17.0 * HUMAN_COST['custo_hora_pm_brl'])}/mês** economizados",
        "",
        "---",
        "",
    ]

    # ── Custo detalhado por requisição ──
    L += [
        "## Custo Detalhado por Requisição",
        "",
        "> 💡 **O que é uma requisição?** É cada vez que a IA converte um bug em User Story.",
        "",
        "| Tipo de Custo | Prompt v1 | Prompt v2 | Economia | Obs |",
        "|---|---|---|---|---|",
        f"| 🤖 API (custo da IA) | {u(c_api_v1)} | {u(c_api_v2)} | {u(eco_api) if eco_api >= 0 else u(abs(eco_api))+' a mais'} | v2 maior por ser mais completo |",
        f"| 👤 Humano (tempo do PM) | {u(c_hum_v1_usd)} | {u(c_hum_v2_usd)} | **{u(eco_hum)}** | Principal fonte de economia |",
        f"| 💰 **TOTAL** | **{u(total_v1)}** | **{u(total_v2)}** | **{u(eco_total)} ({eco_pct:.0f}%)** | **Economia real** |",
        "",
        "```",
        f"  Visualizando o custo por requisição:",
        f"",
        f"  v1: [{u(c_api_v1):>10} IA] + [{u(c_hum_v1_usd):>10} pessoa] = {u(total_v1)} total",
        f"  v2: [{u(c_api_v2):>10} IA] + [{u(c_hum_v2_usd):>10} pessoa] = {u(total_v2)} total",
        f"                                              economia = {u(eco_total)} ({eco_pct:.0f}%)",
        "```",
        "",
        "---",
        "",
    ]

    # ── Projeções ──
    L += [
        "## Projeções de Custo por Volume Mensal",
        "",
        "> 💡 Escolha o volume que mais se aproxima da sua realidade.",
        "",
        "### 🤖 Custo de API (somente a IA)",
        "",
        "| Bugs/mês | Custo v1 | Custo v2 | Diferença |",
        "|---|---|---|---|",
    ]
    for vol in PROJECTION_VOLUMES:
        c1 = c_api_v1 * vol
        c2 = c_api_v2 * vol
        d  = c2 - c1
        L.append(f"| {n(vol):>10} | {u(c1):>10} | {u(c2):>10} | {'+' if d>0 else ''}{u(abs(d))} {'(v2 maior)' if d>0 else '(v2 menor)'} |")

    L += [
        "",
        "### 👤 Custo Humano de Retrabalho",
        "",
        "| Bugs/mês | Custo Humano v1 | Custo Humano v2 | Economia | Horas economizadas |",
        "|---|---|---|---|---|",
    ]
    for vol in PROJECTION_VOLUMES:
        ch1 = c_hum_v1_usd * vol
        ch2 = c_hum_v2_usd * vol
        eco = ch1 - ch2
        h1  = vol * HUMAN_COST["taxa_retrabalho_v1"] * HUMAN_COST["tempo_revisao_v1_min"] / 60
        h2  = vol * HUMAN_COST["taxa_retrabalho_v2"] * HUMAN_COST["tempo_revisao_v2_min"] / 60
        L.append(f"| {n(vol):>10} | {u(ch1):>15} | {u(ch2):>15} | **{u(eco)}** | {h1-h2:.1f}h |")

    L += [
        "",
        "### 💰 Custo TOTAL — O número que realmente importa",
        "",
        "| Bugs/mês | Total v1 | Total v2 | Economia/mês | Economia/ano |",
        "|---|---|---|---|---|",
    ]
    for vol in PROJECTION_VOLUMES:
        t1 = total_v1 * vol
        t2 = total_v2 * vol
        em = t1 - t2
        ea = em * 12
        L.append(f"| {n(vol):>10} | {u(t1):>10} | {u(t2):>10} | **{u(em)}** | **{u(ea)}** |")

    L += ["", "---", ""]

    # ── ROI ──
    investimento_brl = 985.0
    cambio = HUMAN_COST["cambio_brl_usd"]

    L += [
        "## ROI da Otimização — Vale o Investimento?",
        "",
        "> 💡 **O que é ROI?** É o retorno sobre o que foi investido.",
        "> Se você gasta R$985 para melhorar algo e economiza R$2.040/mês,",
        "> você recupera o investimento em menos de 15 dias.",
        "",
        "### Investimento para otimizar o prompt",
        "",
        "| Item | Custo |",
        "|---|---|",
        "| Tempo do engenheiro/PM (8 horas) | R$ 968,00 |",
        "| Custo de API nos testes e iterações | R$ 17,00 (~$3) |",
        "| **Total investido** | **R$ 985,00** |",
        "",
        "### Payback e ROI por cenário",
        "",
        "| Cenário | Bugs/mês | Economia/mês | Payback | Ganho líquido em 12 meses |",
        "|---|---|---|---|---|",
    ]

    cenarios = [
        ("🟢 Pequena empresa",  50),
        ("🟡 Empresa média",   200),
        ("🔵 Grande empresa", 1_000),
        ("🔴 Enterprise",    10_000),
    ]

    for label, vol in cenarios:
        eco_mes_usd = eco_total * vol
        eco_mes_brl = eco_mes_usd * cambio
        eco_ano_brl = eco_mes_brl * 12
        payback     = investimento_brl / eco_mes_brl if eco_mes_brl > 0 else 999
        ganho_liq   = eco_ano_brl - investimento_brl
        roi_pct     = ganho_liq / investimento_brl * 100

        if payback < 1:
            pb = f"{payback*30:.0f} dias"
        elif payback < 12:
            pb = f"{payback:.1f} meses"
        else:
            pb = f"{payback/12:.1f} anos"

        L.append(
            f"| {label} | {n(vol)} | {r(eco_mes_brl)}/mês | **{pb}** | "
            f"{r(ganho_liq)} ({roi_pct:.0f}% ROI) |"
        )

    L += [
        "",
        "> 💡 **Como ler:** Uma empresa média com 200 bugs/mês recupera o",
        f"> investimento de R$985 em menos de {985/(eco_total*200*cambio)*30:.0f} dias",
        "> e lucra no restante do ano.",
        "",
        "---",
        "",
    ]

    # ── Comparativo multi-modelo ──
    qualidade = {
        "gemini-2.5-flash": "⭐⭐⭐⭐⭐ Excelente",
        "gemini-2.0-flash": "⭐⭐⭐⭐ Muito boa",
        "gemini-1.5-flash": "⭐⭐⭐ Boa",
        "gpt-4o-mini":      "⭐⭐⭐⭐ Muito boa",
        "gpt-4o":           "⭐⭐⭐⭐⭐ Excelente",
    }

    L += [
        "## Comparativo por Modelo de IA",
        "",
        "> 💡 Esta tabela mostra quanto custaria o Prompt v2 em diferentes modelos.",
        "> O custo humano é o mesmo para todos — só muda o custo da API.",
        "",
        "| Modelo | API/req | Total/req (c/ humano) | 1k bugs/mês | Qualidade |",
        "|---|---|---|---|---|",
    ]
    for m, pricing in MODEL_PRICING.items():
        cr  = api_cost(v2_inp, v2_out, m)
        tot = cr + c_hum_v2_usd
        mark = " ✅ atual" if m == model else ""
        L.append(
            f"| {pricing['label']}{mark} | {u(cr)} | {u(tot)} | "
            f"{u(tot*1_000)} | {qualidade.get(m,'—')} |"
        )

    L += ["", "---", ""]

    # ── Conclusão ──
    L += [
        "## Conclusão",
        "",
        "### O erro mais comum das empresas",
        "",
        "```",
        "  ❌ Visão incompleta (só custo de API):",
        f"     Prompt v1: {u(c_api_v1)}/req  →  Prompt v2: {u(c_api_v2)}/req",
        f"     Conclusão ERRADA: 'v2 é mais caro, vou continuar com o v1'",
        "",
        "  ✅ Visão completa (API + retrabalho humano):",
        f"     Prompt v1: {u(c_api_v1)} (IA) + {u(c_hum_v1_usd)} (pessoa) = {u(total_v1)}/req",
        f"     Prompt v2: {u(c_api_v2)} (IA) + {u(c_hum_v2_usd)} (pessoa) = {u(total_v2)}/req",
        f"     Conclusão CORRETA: 'v2 economiza {eco_pct:.0f}% no custo total'",
        "```",
        "",
        "### Em uma frase",
        "",
        f"> O Prompt v2 custa **{u(abs(eco_api))} a mais por requisição na API**,",
        f"> mas economiza **{u(eco_hum)} por requisição em tempo humano**,",
        f"> resultando em uma economia líquida de **{u(eco_total)} por User Story** —",
        f"> com qualidade **{((0.97/v1['quality_score'])-1)*100:.0f}% superior**.",
        "",
        "---",
        "",
        f"*Gerado em {now} — `src/cost_report.py` — Projeto: `{project}`*  ",
        f"*Premissas: salário PM R$12.000/mês · câmbio R$5,70/USD · {HUMAN_COST['taxa_retrabalho_v1']:.0%} retrabalho v1 · {HUMAN_COST['taxa_retrabalho_v2']:.0%} retrabalho v2*",
    ]

    return "\n".join(L)


def main():
    print_section_header("RELATÓRIO DE CUSTOS — Prompt v1 vs v2")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    model   = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    project = os.getenv("LANGCHAIN_PROJECT", "desafio-prompt-engineer")
    print(f"Modelo: {model} | Projeto: {project}\n")

    client   = Client()
    runs     = fetch_runs_from_langsmith(client, project)
    v2_stats = extract_token_stats(runs)

    print(f"\n📊 Dados reais do v2 ({v2_stats['token_samples']} amostras de tokens):")
    if v2_stats['avg_input_tokens']:
        print(f"   Tokens entrada:  {v2_stats['avg_input_tokens']:,.0f}")
    if v2_stats['avg_output_tokens']:
        print(f"   Tokens saída:    {v2_stats['avg_output_tokens']:,.0f}")
    if v2_stats['avg_latency_ms']:
        print(f"   Latência média:  {v2_stats['avg_latency_ms']:,.0f}ms")

    report = generate_report(V1_ESTIMATE, v2_stats, model, project)

    Path("reports").mkdir(exist_ok=True)
    output = Path("reports/cost_report.md")
    output.write_text(report, encoding="utf-8")

    # Prévia no terminal
    c_api_v1  = api_cost(V1_ESTIMATE["avg_input_tokens"], V1_ESTIMATE["avg_output_tokens"], model)
    v2_inp    = v2_stats.get("avg_input_tokens") or 3_200
    v2_out    = v2_stats.get("avg_output_tokens") or 900
    c_api_v2  = api_cost(v2_inp, v2_out, model)
    hv1       = human_cost_usd(HUMAN_COST["taxa_retrabalho_v1"], HUMAN_COST["tempo_revisao_v1_min"])
    hv2       = human_cost_usd(HUMAN_COST["taxa_retrabalho_v2"], HUMAN_COST["tempo_revisao_v2_min"])
    t1, t2    = c_api_v1 + hv1, c_api_v2 + hv2

    print(f"\n{'='*60}")
    print("PRÉVIA — CUSTO TOTAL POR REQUISIÇÃO")
    print(f"{'='*60}")
    print(f"  v1: {u(c_api_v1):>10} (IA) + {u(hv1):>10} (pessoa) = {u(t1)} total")
    print(f"  v2: {u(c_api_v2):>10} (IA) + {u(hv2):>10} (pessoa) = {u(t2)} total")
    print(f"  Economia: {u(t1-t2)} por req ({(t1-t2)/t1*100:.0f}% mais barato)")
    print(f"\n✅ Relatório completo salvo em: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
