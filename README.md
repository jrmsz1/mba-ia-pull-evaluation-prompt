# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

---

## Técnicas Aplicadas (Fase 2)

Foram aplicadas **3 técnicas** de Prompt Engineering na otimização do prompt `bug_to_user_story_v2`:

### 1. Role Prompting
**O que é:** Definir uma persona especializada e detalhada para o modelo assumir antes de responder.

**Por que foi escolhida:** Sem uma persona definida, o modelo responde de forma genérica. Ao definir um "Product Manager Sênior com 10 anos de experiência em metodologias ágeis", o modelo adota o vocabulário, o tom profissional e o nível de detalhe esperado de um PM real — melhorando diretamente o Tone Score e o User Story Format Score.

**Como foi aplicada:**
```
Você é um Product Manager Sênior com mais de 10 anos de experiência
em metodologias ágeis (Scrum e Kanban). Sua especialidade é transformar
relatos de bugs de usuários em User Stories claras, acionáveis e bem
estruturadas para o time de desenvolvimento.
```

---

### 2. Chain of Thought (CoT)
**O que é:** Instruir o modelo a raciocinar passo a passo antes de produzir a resposta final.

**Por que foi escolhida:** Bugs muitas vezes contêm informações implícitas (quem é afetado, qual o impacto, quais os edge cases). Sem o CoT, o modelo "pula" para a resposta sem considerar todos os aspectos — resultando em User Stories incompletas. Com CoT, o Completeness Score melhorou significativamente.

**Como foi aplicada:**
```
Antes de escrever a User Story, siga internamente estes passos:
1. Identifique QUEM é o usuário afetado (persona)
2. Identifique O QUE o usuário precisa fazer (funcionalidade esperada)
3. Identifique POR QUE isso é importante (valor de negócio real)
4. Liste os critérios que provam que o bug foi corrigido (testáveis)
5. Considere edge cases e cenários alternativos relevantes
```

---

### 3. Few-shot Learning
**O que é:** Fornecer exemplos concretos de entrada/saída dentro do próprio prompt.

**Por que foi escolhida:** É a técnica mais eficaz para padronizar o formato de saída. Os exemplos ensinam ao modelo exatamente o padrão esperado — incluindo o formato Given-When-Then nos critérios, o nível de detalhe e quando incluir Notas Técnicas. Melhora diretamente o Acceptance Criteria Score e User Story Format Score.

**Como foi aplicada:** 2 exemplos completos no system prompt, cada um com Relato de Bug → User Story → Critérios de Aceitação (Given-When-Then) → Notas Técnicas.

```
### Exemplo 1
Relato de Bug: "Quando clico em 'Esqueci minha senha', recebo uma
mensagem de erro genérica e nunca chega o email de recuperação."

User Story: Como usuário cadastrado que perdeu acesso à conta, eu quero
recuperar minha senha através do email, para que eu possa voltar a usar
a plataforma sem precisar criar uma nova conta.

Critérios de Aceitação:
- [ ] Dado que estou na tela de login, quando clico em "Esqueci minha
      senha", então o sistema exibe um formulário solicitando meu email
...
```

---

## Resultados Finais

### Github
🔗 **Link público:** https://github.com/jrmsz1/mba-ia-pull-evaluation-prompt

### Dashboard LangSmith
🔗 **Link público:** https://smith.langchain.com/o/d344b043-76f1-4948-9014-24fe3aea121a/projects/p/42be6e56-12db-419b-b5c0-b60a1b80d86a

🔗 **Prompt publicado:** https://smith.langchain.com/prompts/bug_to_user_story_v2?organizationId=d344b043-76f1-4948-9014-24fe3aea121a

---

### Avaliação Final — Prompt v2 (APROVADO ✅)

```
==================================================
Prompt: jrmsz1/bug_to_user_story_v2
==================================================
  - Tone Score:                0.98 ✓
  - Acceptance Criteria Score: 0.97 ✓
  - User Story Format Score:   0.98 ✓
  - Completeness Score:        0.95 ✓
--------------------------------------------------
📊 MÉDIA: 0.9704
--------------------------------------------------
✅ STATUS: APROVADO — todas as métricas >= 0.9
```

---

### Tabela Comparativa: v1 vs v2

| Métrica | Prompt v1 (original) | Prompt v2 (otimizado) | Melhoria |
|---|---|---|---|
| Tone Score | ~0.45 | **0.98** | +117% |
| Acceptance Criteria | ~0.48 | **0.97** | +102% |
| User Story Format | ~0.50 | **0.98** | +96% |
| Completeness Score | ~0.46 | **0.95** | +106% |
| **MÉDIA** | **~0.47** | **0.97** | **+106%** |

---

### Jornada de Iterações

| Iteração | Tone | Criteria | Format | Completeness | Média | Status |
|---|---|---|---|---|---|---|
| v2 — iter 1 | 0.96 | 0.90 | 0.97 | 0.88 | 0.93 | ❌ Reprovado |
| v2 — iter 2 | 0.96 | 0.90 | 0.97 | 0.88 | 0.93 | ❌ Reprovado |
| v2 — iter 3 | 0.98 | 0.97 | 0.98 | 0.95 | **0.97** | ✅ Aprovado |

**Principais ajustes entre iterações:**
- Adicionado formato obrigatório **Given-When-Then** nos critérios de aceitação
- Atualizado os exemplos Few-shot para usar Given-When-Then (consistência com as regras)
- Adicionada seção **"Completude Obrigatória"** exigindo contexto técnico e impacto no usuário

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com) com API Key
- API Key do [Google AI Studio](https://aistudio.google.com/app/apikey) (Gemini) **ou** [OpenAI](https://platform.openai.com/api-keys)
- Handle público criado no LangSmith (necessário para push de prompts)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/mba-ia-pull-evaluation-prompt
cd mba-ia-pull-evaluation-prompt

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### Configuração do `.env`

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

```env
# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_sua_key_aqui
LANGSMITH_PROJECT=desafio-prompt-engineer

# Seu handle público do LangSmith Hub
USERNAME_LANGSMITH_HUB=seu_handle_aqui

# Google Gemini (recomendado)
GOOGLE_API_KEY=AIza_sua_key_aqui

# Configuração do LLM
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
```

> **Nota:** Para descobrir seu `USERNAME_LANGSMITH_HUB`, publique qualquer prompt no LangSmith e clique no ícone de cadeado — ele solicitará a criação do seu handle público.

---

### Ordem de Execução

#### Fase 1 — Pull dos prompts ruins

```bash
python src/pull_prompts.py
```
Baixa o prompt original `leonanluppi/bug_to_user_story_v1` e salva em `prompts/raw_prompts.yml`.

#### Fase 2 — Otimizar o prompt

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas de Prompt Engineering.

#### Fase 3 — Push do prompt otimizado

```bash
python src/push_prompts.py
```
Publica o prompt otimizado como `{seu_handle}/bug_to_user_story_v2` no LangSmith Hub (público).

#### Fase 4 — Avaliação

```bash
python src/evaluate.py
```
Avalia o prompt contra o dataset de 15 bugs usando as 4 métricas específicas. Critério de aprovação: **todas as métricas >= 0.9**.

#### Fase 5 — Testes automatizados

```bash
pytest tests/test_prompts.py -v
```
Valida a estrutura do prompt v2 com 6 testes automatizados.

---

### Resultado esperado após aprovação

```
==================================================
Prompt: seu_handle/bug_to_user_story_v2
==================================================
  - Tone Score:                0.98 ✓
  - Acceptance Criteria Score: 0.97 ✓
  - User Story Format Score:   0.98 ✓
  - Completeness Score:        0.95 ✓
--------------------------------------------------
📊 MÉDIA: 0.9704
--------------------------------------------------
✅ STATUS: APROVADO — todas as métricas >= 0.9
```

---

## Estrutura do Projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml    # Prompt original (baixa qualidade)
│   ├── bug_to_user_story_v2.yml    # Prompt otimizado (aprovado)
│   └── raw_prompts.yml             # Output do pull_prompts.py
│
├── datasets/
│   └── bug_to_user_story.jsonl     # 15 exemplos de bugs para avaliação
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith Hub
│   ├── push_prompts.py       # Push ao LangSmith Hub
│   ├── evaluate.py           # Avaliação automática com 4 métricas
│   ├── metrics.py            # Implementação LLM-as-Judge
│   └── utils.py              # Funções auxiliares
│
└── tests/
    └── test_prompts.py       # 6 testes de validação (pytest)
```

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.9+ | Linguagem principal |
| LangChain | latest | Framework LLM |
| LangSmith | latest | Observabilidade e avaliação |
| Google Gemini | gemini-2.5-flash | LLM principal e avaliador |
| pytest | 8.x | Testes automatizados |
| PyYAML | latest | Leitura/escrita de prompts |
