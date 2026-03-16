# Esteira de Otimização de Prompts com LLM
### Pipeline: Pull → Otimizar → Push → Avaliar → Iterar

> **Para quem é este documento?**  
> Times de produto, engenharia e gestão que queiram entender como estruturar o uso de Inteligência Artificial Generativa de forma controlada, mensurável e escalável dentro da empresa.

---

## 1. O Problema que Estamos Resolvendo

Quando uma empresa começa a usar LLMs (modelos de linguagem como ChatGPT, Gemini, Claude), o fluxo típico é:

```
Desenvolvedor escreve um prompt no código
           ↓
"Parece que funcionou bem"
           ↓
Deploy em produção
           ↓
Ninguém sabe se está bom ou ruim
           ↓
Cliente reclama → alguém descobre que estava ruim
```

**O resultado:** prompts perdidos no código, sem histórico, sem métricas, sem controle.

Essa esteira resolve exatamente isso.

---

## 2. Visão Geral da Esteira

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTEIRA DE PROMPTS                           │
│                                                                 │
│  ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌───────────┐  │
│  │  PULL   │ →  │OTIMIZAR  │ →  │  PUSH   │ →  │ AVALIAR   │  │
│  │         │    │          │    │         │    │           │  │
│  │Buscar   │    │Aplicar   │    │Publicar │    │Medir com  │  │
│  │prompt   │    │técnicas  │    │versão   │    │métricas   │  │
│  │do Hub   │    │de PE     │    │nova     │    │automáticas│  │
│  └─────────┘    └──────────┘    └─────────┘    └─────────┬─┘  │
│                                                           │    │
│                    ◄──────── ITERAR ◄─────────────────────┘    │
│                    (repetir até todas as métricas >= 0.9)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Tecnologias Utilizadas e Por Que Elas Importam

### 3.1 LangChain
> **O que é:** Framework Python que padroniza a forma de interagir com diferentes LLMs (OpenAI, Google, Anthropic, etc.).

**Por que importa:**  
Sem LangChain, se você trocar de OpenAI para Gemini, precisa reescrever todo o código. Com LangChain, troca uma linha no `.env`. É a camada de abstração que protege o código de mudanças de provider.

**Analogia:** É como o JDBC para bancos de dados — você escreve o código uma vez e troca o "driver" conforme necessário.

---

### 3.2 LangSmith
> **O que é:** Plataforma de observabilidade, versionamento e avaliação para aplicações LLM. É o "GitHub + Datadog" para prompts.

**Por que importa:**  
Sem LangSmith, prompts vivem dentro do código, sem histórico, sem rastreamento, sem métricas. Com LangSmith você tem:

| Sem LangSmith | Com LangSmith |
|---|---|
| Prompt hardcoded no código | Prompt versionado no Hub |
| "Parece que melhorou" | Score subiu de 0.65 para 0.94 |
| Bug descoberto pelo cliente | Regressão detectada no CI/CD |
| Sem histórico de mudanças | v1, v2, v3 com timestamps |
| Impossível auditar | Trace completo de cada chamada |

**Funcionalidades principais:**
- **Prompt Hub** — repositório central de prompts (como GitHub para código)
- **Tracing** — log de cada chamada ao LLM com inputs, outputs, latência e custo
- **Datasets** — conjuntos de exemplos para avaliação sistemática
- **Experiments** — comparação entre versões de prompts com métricas

---

### 3.3 LLM (Large Language Model)
> **O que é:** Modelo de linguagem treinado em grandes volumes de texto, capaz de gerar, transformar e avaliar texto. Ex: GPT-4, Gemini, Claude.

**Por que importa:**  
É o "motor" da esteira. O mesmo motor que gera as respostas também pode ser usado para avaliar a qualidade das respostas — técnica chamada **LLM-as-Judge**.

---

### 3.4 Prompt Engineering (PE)
> **O que é:** Conjunto de técnicas para escrever instruções que extraem o melhor comportamento possível de um LLM.

**Por que importa:**  
A diferença entre um prompt ruim e um prompt otimizado pode ser a diferença entre 45% e 95% de qualidade — sem trocar o modelo, sem pagar mais.

**Técnicas usadas nesta esteira:**

#### Role Prompting
Definir uma persona detalhada para o modelo assumir.
```
❌ Ruim:   "Você é um assistente."
✅ Bom:    "Você é um Product Manager Sênior com 10 anos de experiência
            em metodologias ágeis (Scrum e Kanban). Sua especialidade é
            transformar relatos de bugs em User Stories acionáveis."
```
**Por que funciona:** O modelo ajusta vocabulário, tom, nível de detalhe e padrões de resposta com base na persona definida.

---

#### Chain of Thought (CoT)
Instruir o modelo a raciocinar passo a passo antes de responder.
```
Antes de escrever a User Story, siga estes passos:
  1. Identifique QUEM é o usuário afetado
  2. Identifique O QUE o usuário precisa fazer
  3. Identifique POR QUE isso é importante
  4. Liste os critérios que provam que o bug foi corrigido
  5. Considere edge cases relevantes
```
**Por que funciona:** Modelos que "pensam em voz alta" cometem menos erros. É equivalente a pedir para um humano mostrar o raciocínio antes de dar a resposta final.

---

#### Few-shot Learning
Fornecer exemplos concretos de entrada/saída dentro do prompt.
```
### Exemplo 1
Relato de Bug: "Botão de login não funciona no mobile."

User Story: Como usuário mobile, eu quero conseguir fazer login
            pelo aplicativo, para que eu possa acessar minha conta
            de qualquer lugar...

Critérios de Aceitação:
- Dado que estou na tela de login mobile, quando toco no botão
  "Entrar", então o sistema processa minha autenticação...
```
**Por que funciona:** Exemplos concretos são mais poderosos que instruções abstratas. O modelo aprende o padrão exato esperado — incluindo formato, nível de detalhe e vocabulário.

---

## 4. O Pipeline em Detalhe

### Etapa 1 — Pull
```python
# Busca o prompt do repositório central
prompt = hub.pull("empresa/bug_to_user_story_v1")
```
**O que acontece:** O script conecta ao LangSmith Hub e baixa o prompt atual para análise local. Permite ver o que está em produção antes de modificar.

---

### Etapa 2 — Otimizar
Edição manual do arquivo YAML com as técnicas de Prompt Engineering:
```yaml
# prompts/bug_to_user_story_v2.yml
system_prompt: |
  Você é um Product Manager Sênior...    ← Role Prompting
  
  Antes de responder, siga estes passos: ← Chain of Thought
  1. Identifique o usuário...
  
  ## Exemplos                             ← Few-shot Learning
  Relato: "..."
  User Story: "..."
```

---

### Etapa 3 — Push
```python
# Publica a versão nova no Hub, tornando pública e versionada
hub.push("empresa/bug_to_user_story_v2", prompt, new_repo_is_public=True)
```
**O que acontece:** A nova versão do prompt vai para o repositório central com metadados (técnicas aplicadas, data, tags). Qualquer sistema que use esse prompt pode atualizar com uma linha.

---

### Etapa 4 — Avaliar (LLM-as-Judge)
> **Termo técnico — LLM-as-Judge:** Uso de um LLM para avaliar automaticamente a qualidade das respostas de outro LLM, com critérios customizados.

```
Dataset (15 exemplos de bugs reais)
              ↓
    Prompt v2 gera User Stories
              ↓
    LLM Avaliador analisa cada resposta
              ↓
    4 métricas calculadas automaticamente:
    
    ┌──────────────────────────────────────────┐
    │ Tone Score              → 0.96 ✓          │
    │ Acceptance Criteria     → 0.90 ✓          │
    │ User Story Format       → 0.97 ✓          │
    │ Completeness Score      → 0.88 ✗          │
    │                                           │
    │ MÉDIA: 0.92  |  STATUS: REPROVADO         │
    │ (todas as 4 devem ser >= 0.9)             │
    └──────────────────────────────────────────┘
```

**As 4 métricas explicadas:**

| Métrica | O que avalia | Por que é importante |
|---|---|---|
| **Tone Score** | Tom profissional e empático com o usuário | User Stories mal escritas criam conflito entre PM e dev |
| **Acceptance Criteria** | Critérios testáveis e bem estruturados (Given-When-Then) | Critérios vagos geram retrabalho e bugs em produção |
| **User Story Format** | Formato ágil correto ("Como... eu quero... para que...") | Padronização facilita estimativas e planejamento de sprint |
| **Completeness Score** | Cobertura completa do bug (contexto, impacto, edge cases) | User Stories incompletas levam a soluções parciais |

---

### Etapa 5 — Iterar
Repetir as etapas 2 → 3 → 4 até **todas** as métricas atingirem >= 0.9.

```
Iteração 1: Tone:0.96 Criteria:0.88 Format:0.97 Completeness:0.72 → ❌ REPROVADO
Iteração 2: Tone:0.96 Criteria:0.90 Format:0.97 Completeness:0.88 → ❌ REPROVADO  
Iteração 3: Tone:0.97 Criteria:0.92 Format:0.98 Completeness:0.91 → ✅ APROVADO
```

---

## 5. Aplicações Práticas na Empresa

### Caso 1 — Automação de Documentação de Bugs
**Situação atual:** PM leva 15-20 minutos para converter cada bug em User Story bem escrita.

**Com a esteira:**
```
Bug criado no Jira/Linear
         ↓
Webhook dispara automaticamente o pipeline
         ↓
LLM gera User Story completa em segundos
         ↓
PM revisa e aprova em 2 minutos
         ↓
User Story vai para o backlog com critérios testáveis
```
**Ganho estimado:** 50 bugs/semana × 15 min = **12,5 horas de trabalho de PM por semana**.

---

### Caso 2 — Controle de Qualidade de IA em Produção
Toda vez que alguém alterar um prompt em produção, o pipeline de avaliação roda automaticamente no CI/CD:

```
git push do novo prompt
         ↓
CI/CD executa: python src/evaluate.py
         ↓
Se todas as métricas >= 0.9 → ✅ Deploy aprovado
Se alguma métrica < 0.9    → ❌ Deploy bloqueado
         ↓
Time recebe relatório com qual métrica falhou e por quê
```
**Benefício:** Regressões de qualidade detectadas antes de chegar ao usuário final.

---

### Caso 3 — A/B Testing de Prompts
Assim como times de produto fazem A/B test de features, times de IA podem comparar versões de prompts com dados reais:

```
Mesmo dataset → Prompt v2 vs Prompt v3 → Comparação automática
```

Decisões baseadas em dados, não em intuição.

---

### Caso 4 — Onboarding de Novos Desenvolvedores
Com prompts versionados no Hub, novos devs não precisam "descobrir" como funciona cada prompt. Eles acessam o LangSmith e veem:
- O prompt atual com metadados
- O histórico de todas as versões
- As métricas de cada versão
- As técnicas aplicadas documentadas

---

## 6. Estrutura do Projeto

```
projeto/
├── .env                          # Credenciais (nunca no git!)
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt original (ruim)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos reais para avaliação
├── src/
│   ├── pull_prompts.py           # Busca prompts do LangSmith Hub
│   ├── push_prompts.py           # Publica prompts otimizados
│   ├── evaluate.py               # Avaliação automática com 4 métricas
│   ├── metrics.py                # Implementação das métricas (LLM-as-Judge)
│   └── utils.py                  # Funções auxiliares
└── tests/
    └── test_prompts.py           # Testes automatizados (pytest)
```

---

## 7. Monitoramento de Custo e Performance

Uma das funcionalidades mais valiosas do LangSmith é a **visibilidade financeira em tempo real** de cada chamada ao LLM. O dashboard de Tracing exibe, por execução:

```
┌──────────────────────────────────────────────────────────────────┐
│ TRACING — desafio-prompt-engineer                                │
├─────────────────┬──────────┬─────────┬────────┬─────────────────┤
│ Nome            │ Latência │ Tokens  │ Custo  │ Status          │
├─────────────────┼──────────┼─────────┼────────┼─────────────────┤
│ RunnableSequence│ 12.69s   │ 4,181   │$0.0014 │ ✅ Sucesso       │
│ ChatGoogleGen.. │  7.63s   │ 2,756   │$0.0008 │ ✅ Sucesso       │
│ ChatGoogleGen.. │  6.21s   │ 2,291   │$0.0006 │ ✅ Sucesso       │
│ ChatGoogleGen.. │ 10.18s   │ 3,298   │$0.0008 │ ✅ Sucesso       │
└─────────────────┴──────────┴─────────┴────────┴─────────────────┘
```

### O que cada coluna significa

| Coluna | O que é | Por que importa |
|---|---|---|
| **Latência** | Tempo de resposta do LLM | Identifica gargalos de performance — prompts muito longos aumentam latência |
| **Tokens** | Quantidade de tokens consumidos (entrada + saída) | Base do cálculo de custo — tokens = "palavras processadas" pelo modelo |
| **Custo** | Valor em dólares daquela chamada específica | Visibilidade financeira por execução |
| **Status** | Sucesso ou erro | Monitoramento de saúde do sistema |

### O que são Tokens?

> **Termo técnico — Token:** Unidade básica que o LLM processa. Aproximadamente 1 token = 0,75 palavras em inglês, ou ~4 caracteres. Um prompt de 1.000 palavras consome cerca de 1.300 tokens.

O custo de cada chamada é calculado assim:
```
Custo = (Tokens de Entrada × Preço/1M) + (Tokens de Saída × Preço/1M)

Exemplo com Gemini 2.5 Flash:
- Entrada: 3.000 tokens × $0,15/1M = $0,00045
- Saída:   1.000 tokens × $0,60/1M = $0,00060
- Total por chamada: ~$0,001
```

### Impacto Financeiro de Prompts Mal Otimizados

Prompts verbosos e sem estrutura consomem mais tokens desnecessariamente:

| Cenário | Tokens/chamada | Custo/chamada | Custo/mês (10k chamadas) |
|---|---|---|---|
| Prompt v1 (ruim, verboso) | ~5.000 | ~$0.003 | **~$30** |
| Prompt v2 (otimizado) | ~3.000 | ~$0.001 | **~$10** |
| **Economia** | **-40%** | **-67%** | **-$20/mês** |

> Em escala real (100k chamadas/mês), a diferença pode ser de **centenas de dólares por mês** apenas com otimização de prompt.

### Alertas e Controle de Gastos

Com o LangSmith + Google AI Studio é possível configurar:

- **Teto de gasto mensal** — bloqueia automaticamente ao atingir o limite (ex: $5/mês)
- **Alertas por projeto** — notificação quando o custo ultrapassa um threshold
- **Dashboard de uso** — gráfico de consumo diário/semanal por modelo

```
Google AI Studio → Projeto → Gasto → Editar gasto máximo
                                            ↓
                              Define limite: US$ 5,00/mês
                                            ↓
                          Sistema bloqueia ao atingir o limite
```

### Visão Estratégica para a Empresa

| Pergunta | Sem LangSmith | Com LangSmith |
|---|---|---|
| Quanto gastamos com IA este mês? | Não sei | $47,32 |
| Qual feature consome mais tokens? | Não sei | Geração de relatórios (60%) |
| O novo prompt é mais barato? | Acho que sim | -34% em tokens |
| Qual chamada demorou mais? | Não sei | Endpoint /summarize (15s avg) |
| Temos chamadas falhando? | Só quando o cliente reclama | 2.3% de erro nas últimas 24h |

---

## 8. Resumo dos Benefícios

| Dimensão | Antes | Depois |
|---|---|---|
| **Versionamento** | Prompt perdido no código | Hub centralizado com histórico |
| **Qualidade** | Subjetiva ("parece bom") | Objetiva (score >= 0.9) |
| **Rastreabilidade** | Impossível auditar | Trace completo de cada chamada |
| **Colaboração** | Cada dev com seu prompt | Time compartilha o mesmo Hub |
| **Deploy** | Manual e arriscado | Automatizado com gate de qualidade |
| **Custo** | Invisível | Monitorado por chamada |
| **Regressão** | Descoberta pelo cliente | Detectada no CI/CD antes do deploy |

---

## 9. Glossário Rápido

| Termo | Definição simples |
|---|---|
| **LLM** | Modelo de IA que processa e gera texto (ex: ChatGPT, Gemini) |
| **Prompt** | Instrução enviada ao LLM para guiar sua resposta |
| **Prompt Engineering** | Arte e ciência de escrever prompts eficazes |
| **LLM-as-Judge** | Usar um LLM para avaliar a qualidade de outro LLM |
| **Few-shot** | Fornecer exemplos no prompt para ensinar o padrão esperado |
| **Chain of Thought** | Instruir o modelo a raciocinar passo a passo |
| **Role Prompting** | Definir uma persona especializada para o modelo assumir |
| **Hub** | Repositório centralizado de prompts (como GitHub) |
| **Tracing** | Log detalhado de cada chamada ao LLM |
| **Dataset** | Conjunto de exemplos usados para avaliação sistemática |
| **CI/CD** | Pipeline automatizado de integração e deploy contínuo |
| **Token** | Unidade de processamento do LLM (~0,75 palavras). Base do cálculo de custo |
| **Tracing** | Log detalhado de cada chamada: input, output, tokens, custo e latência |
| **Latência** | Tempo de resposta de uma chamada ao LLM |
| **Given-When-Then** | Formato estruturado para critérios de aceitação testáveis |

---

*Documento gerado em 15/03/2026 — Esteira de Otimização de Prompts com LangChain + LangSmith*
