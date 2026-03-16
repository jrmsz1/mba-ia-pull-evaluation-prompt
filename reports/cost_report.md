# Relatório de Custos — Prompt v1 vs v2
**Gerado em:** 16/03/2026 09:26  
**Projeto:** desafio-prompt-engineer  
**Modelo:** Gemini 2.5 Flash  

---

## O que este relatório mostra?

Este documento compara o **custo real** de usar um prompt ruim (v1) versus
um prompt otimizado (v2) para converter relatos de bugs em User Stories.

> 💡 **Para quem não é técnico:**
> Um *prompt* é a instrução que enviamos para a Inteligência Artificial.
> Um prompt mal escrito gera respostas ruins, que precisam ser corrigidas
> manualmente por uma pessoa — isso custa tempo e dinheiro.
> Um prompt bem escrito gera respostas prontas para usar.

O custo total tem **duas partes** que precisam ser consideradas juntas:

```
  Custo Total = Custo da API (pagar pela IA) + Custo Humano (tempo corrigindo)
               ─────────────────────────     ──────────────────────────────────
               Visível na fatura              Invisível — mas é o maior custo!
```

> ⚠️  A maioria das empresas só olha o custo da API e ignora o custo humano.
> Este relatório mostra o **custo real completo**.

---

## Resumo Executivo

### O que mudou do v1 para o v2?

| | Prompt v1 (original) | Prompt v2 (otimizado) |
|---|---|---|
| **Qualidade das respostas** | 47% ❌ | 97% ✅ |
| **User Stories que precisam correção** | 70% | 10% |
| **Tempo de revisão por US** | 15 min (reescrever) | 3 min (só aprovar) |
| **Horas do PM por mês** (100 bugs) | 18h corrigindo | 0.5h revisando |
| **Custo de API por requisição** | $0.00024 | $0.0010 |
| **Custo humano por requisição** | $3.71 (R$21.18) | $0.106 (R$0.61) |
| **CUSTO TOTAL por requisição** | **$3.72** | **$0.107** |

> ✅ **Resultado: o Prompt v2 é 97% mais barato no custo total**,
> mesmo custando mais caro na API — porque elimina quase todo o retrabalho humano.

---

## Por que o Retrabalho Humano é o Maior Custo?

> 💡 **Analogia para entender:**
> Imagine que você contrata um assistente para redigir documentos.
> Se os documentos saem ruins, seu gerente (que ganha mais) precisa
> reescrever tudo do zero — 15 minutos por documento.
> Com um briefing claro, o assistente entrega certo na primeira vez
> e o gerente só lê e aprova — 3 minutos.
> O custo do assistente subiu um pouco, mas o custo total caiu muito.

### Como calculamos o custo humano

| Parâmetro | Valor | Explicação |
|---|---|---|
| Salário PM Sênior | R$ 12.000/mês | Média de mercado Brasil 2026 |
| Custo real para empresa | R$ 20.400/mês | Salário + ~70% encargos (FGTS, INSS, férias, 13º) |
| Custo por hora | R$121.00/hora | R$20.400 ÷ 168 horas úteis/mês |
| Custo por minuto | R$2.02/minuto | Base para calcular o retrabalho |

### Cálculo do retrabalho com Prompt v1

```
  Situação: 70% das User Stories geradas precisavam de correção manual
  Tempo médio de correção: 15 minutos (reescrever do zero)

  Fórmula:
  70% de chance × 15 minutos × R$2.02/min = R$21.18 por User Story

  Em 100 bugs/mês:
  70 correções × 15 min = 1.050 minutos = 17,5 horas desperdiçadas
  Custo: 17,5h × R$121.00/hora = R$2,117.50/mês
```

### Cálculo do retrabalho com Prompt v2

```
  Situação: apenas 10% das User Stories precisam de ajuste fino
  Tempo médio de revisão: 3 minutos (ler, aprovar ou ajustar detalhe)

  Fórmula:
  10% de chance × 3 minutos × R$2.02/min = R$0.61 por User Story

  Em 100 bugs/mês:
  10 revisões × 3 min = 30 minutos totais
  Custo: 0,5h × R$121.00/hora = R$60.50/mês
```

**Economia de retrabalho em 100 bugs/mês:**
R$2,117.50 - R$60.50 = **R$2,057.00/mês** economizados

---

## Custo Detalhado por Requisição

> 💡 **O que é uma requisição?** É cada vez que a IA converte um bug em User Story.

| Tipo de Custo | Prompt v1 | Prompt v2 | Economia | Obs |
|---|---|---|---|---|
| 🤖 API (custo da IA) | $0.00024 | $0.0010 | $0.00078 a mais | v2 maior por ser mais completo |
| 👤 Humano (tempo do PM) | $3.71 | $0.106 | **$3.61** | Principal fonte de economia |
| 💰 **TOTAL** | **$3.72** | **$0.107** | **$3.61 (97%)** | **Economia real** |

```
  Visualizando o custo por requisição:

  v1: [  $0.00024 IA] + [     $3.71 pessoa] = $3.72 total
  v2: [   $0.0010 IA] + [    $0.106 pessoa] = $0.107 total
                                              economia = $3.61 (97%)
```

---

## Projeções de Custo por Volume Mensal

> 💡 Escolha o volume que mais se aproxima da sua realidade.

### 🤖 Custo de API (somente a IA)

| Bugs/mês | Custo v1 | Custo v2 | Diferença |
|---|---|---|---|
|        100 |     $0.024 |     $0.102 | +$0.078 (v2 maior) |
|         1k |     $0.240 |      $1.02 | +$0.780 (v2 maior) |
|        10k |      $2.40 |     $10.20 | +$7.80 (v2 maior) |
|       100k |     $24.00 |    $102.00 | +$78.00 (v2 maior) |
|         1M |    $240.00 |  $1,020.00 | +$780.00 (v2 maior) |

### 👤 Custo Humano de Retrabalho

| Bugs/mês | Custo Humano v1 | Custo Humano v2 | Economia | Horas economizadas |
|---|---|---|---|---|
|        100 |         $371.49 |          $10.61 | **$360.88** | 17.0h |
|         1k |       $3,714.91 |         $106.14 | **$3,608.77** | 170.0h |
|        10k |      $37,149.12 |       $1,061.40 | **$36,087.72** | 1700.0h |
|       100k |     $371,491.23 |      $10,614.04 | **$360,877.19** | 17000.0h |
|         1M |   $3,714,912.28 |     $106,140.35 | **$3,608,771.93** | 170000.0h |

### 💰 Custo TOTAL — O número que realmente importa

| Bugs/mês | Total v1 | Total v2 | Economia/mês | Economia/ano |
|---|---|---|---|---|
|        100 |    $371.52 |     $10.72 | **$360.80** | **$4,329.59** |
|         1k |  $3,715.15 |    $107.16 | **$3,607.99** | **$43,295.90** |
|        10k | $37,151.52 |  $1,071.60 | **$36,079.92** | **$432,959.03** |
|       100k | $371,515.23 | $10,716.04 | **$360,799.19** | **$4,329,590.32** |
|         1M | $3,715,152.28 | $107,160.35 | **$3,607,991.93** | **$43,295,903.16** |

---

## ROI da Otimização — Vale o Investimento?

> 💡 **O que é ROI?** É o retorno sobre o que foi investido.
> Se você gasta R$985 para melhorar algo e economiza R$2.040/mês,
> você recupera o investimento em menos de 15 dias.

### Investimento para otimizar o prompt

| Item | Custo |
|---|---|
| Tempo do engenheiro/PM (8 horas) | R$ 968,00 |
| Custo de API nos testes e iterações | R$ 17,00 (~$3) |
| **Total investido** | **R$ 985,00** |

### Payback e ROI por cenário

| Cenário | Bugs/mês | Economia/mês | Payback | Ganho líquido em 12 meses |
|---|---|---|---|---|
| 🟢 Pequena empresa | 50 | R$1,028.28/mês | **29 dias** | R$11,354.33 (1153% ROI) |
| 🟡 Empresa média | 200 | R$4,113.11/mês | **7 dias** | R$48,372.33 (4911% ROI) |
| 🔵 Grande empresa | 1k | R$20,565.55/mês | **1 dias** | R$245,801.65 (24954% ROI) |
| 🔴 Enterprise | 10k | R$205,655.54/mês | **0 dias** | R$2,466,881.48 (250445% ROI) |

> 💡 **Como ler:** Uma empresa média com 200 bugs/mês recupera o
> investimento de R$985 em menos de 7 dias
> e lucra no restante do ano.

---

## Comparativo por Modelo de IA

> 💡 Esta tabela mostra quanto custaria o Prompt v2 em diferentes modelos.
> O custo humano é o mesmo para todos — só muda o custo da API.

| Modelo | API/req | Total/req (c/ humano) | 1k bugs/mês | Qualidade |
|---|---|---|---|---|
| Gemini 2.5 Flash ✅ atual | $0.0010 | $0.107 | $107.16 | ⭐⭐⭐⭐⭐ Excelente |
| Gemini 2.0 Flash | $0.00068 | $0.107 | $106.82 | ⭐⭐⭐⭐ Muito boa |
| Gemini 1.5 Flash | $0.00051 | $0.107 | $106.65 | ⭐⭐⭐ Boa |
| GPT-4o Mini | $0.0010 | $0.107 | $107.16 | ⭐⭐⭐⭐ Muito boa |
| GPT-4o | $0.017 | $0.123 | $123.14 | ⭐⭐⭐⭐⭐ Excelente |

---

## Conclusão

### O erro mais comum das empresas

```
  ❌ Visão incompleta (só custo de API):
     Prompt v1: $0.00024/req  →  Prompt v2: $0.0010/req
     Conclusão ERRADA: 'v2 é mais caro, vou continuar com o v1'

  ✅ Visão completa (API + retrabalho humano):
     Prompt v1: $0.00024 (IA) + $3.71 (pessoa) = $3.72/req
     Prompt v2: $0.0010 (IA) + $0.106 (pessoa) = $0.107/req
     Conclusão CORRETA: 'v2 economiza 97% no custo total'
```

### Em uma frase

> O Prompt v2 custa **$0.00078 a mais por requisição na API**,
> mas economiza **$3.61 por requisição em tempo humano**,
> resultando em uma economia líquida de **$3.61 por User Story** —
> com qualidade **106% superior**.

---

*Gerado em 16/03/2026 09:26 — `src/cost_report.py` — Projeto: `desafio-prompt-engineer`*  
*Premissas: salário PM R$12.000/mês · câmbio R$5,70/USD · 70% retrabalho v1 · 10% retrabalho v2*