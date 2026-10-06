# 🗳️ Election Social Listening 2026

> **Social Listening, Data Analytics e Inteligência Artificial aplicados à análise de conteúdos públicos relacionados ao cenário eleitoral brasileiro de 2026.**

![Election Social Listening 2026](./Imagem%20Dashboard.PNG)

---

## 📊 Sobre o projeto

O **Election Social Listening 2026** é um projeto de Data Analytics desenvolvido para transformar conteúdos públicos relacionados ao cenário eleitoral brasileiro em **dados estruturados, indicadores analíticos e visualizações interativas**.

A solução combina **Engenharia de Dados, Social Listening, Inteligência Artificial, NLP e Business Intelligence** em um pipeline que percorre desde a coleta dos dados até sua disponibilização em um dashboard analítico.

A primeira versão integra:

- coleta automatizada de dados via API;
- tratamento e normalização com Python;
- deduplicação;
- identificação de candidatos;
- resolução contextual de casos ambíguos com IA;
- classificação de sentimento;
- métricas de engajamento;
- análise temporal;
- modelagem dimensional;
- dashboard interativo em Power BI.

> 🚧 **Status atual: V1 — MVP funcional | Em evolução**
>
> Esta é a primeira versão da solução. O projeto continuará recebendo novas fontes, indicadores, análises e funcionalidades.

---

## 🎯 Objetivo

O projeto nasceu a partir de uma pergunta:

> **O que as conversas e conteúdos publicados nas plataformas digitais podem revelar sobre a dinâmica da corrida eleitoral?**

A partir dela, a solução busca explorar questões como:

- Qual é o volume de conteúdos encontrado na amostra?
- Como esse volume evolui ao longo do tempo?
- Quais candidatos são mencionados?
- Qual é o nível de engajamento observado?
- Qual é o sentimento textual associado aos conteúdos?
- Quais assuntos aparecem com maior frequência?
- Existem períodos com aumento relevante de publicações ou interações?
- Quais conteúdos podem estar associados a mudanças observadas nos indicadores?

O objetivo de longo prazo é construir uma arquitetura de **Social Listening modular e reproduzível**, capaz de incorporar novas fontes e novas camadas de inteligência.

> **Importante:** o projeto não tem como objetivo prever resultados eleitorais ou medir intenção de voto.

---

## 📈 V1 em números

A primeira coleta, utilizando dados públicos do YouTube, resultou em:

| Indicador | Resultado |
|---|---:|
| 🎬 Vídeos únicos | **1.399** |
| 👁️ Visualizações | **42.281.469** |
| 👍 Curtidas | **1.468.540** |
| 💬 Comentários | **144.345** |
| ⚡ Interações | **1.612.885** |

Os valores representam exclusivamente a **amostra coletada** e as métricas disponíveis no momento da coleta.

Eles não representam todo o conteúdo existente no YouTube nem devem ser interpretados como indicadores de intenção de voto, aprovação ou apoio político.

---

## 🏗️ Arquitetura da solução

O pipeline atual segue a arquitetura:

```text
                  YouTube Data API
                         │
                         ▼
                       Coleta
                         │
                         ▼
                     Raw Data
                         │
                         ▼
                    Validação
                         │
                         ▼
                   Normalização
                         │
                         ▼
                   Deduplicação
                         │
                         ▼
                 Entity Resolution
                    /           \
                   /             \
      Regras determinísticas     IA Local
                   \             /
                    \           /
                         │
                         ▼
             Classificação de Sentimento
                         │
                         ▼
                Construção de Métricas
                         │
                         ▼
                 Datasets Analíticos
                         │
                         ▼
                     Power BI
                         │
                         ▼
                Dashboard Interativo
```

A arquitetura foi construída de maneira modular para permitir a inclusão futura de **novas plataformas, modelos e camadas analíticas**.

---

## 📡 Fonte de dados — V1

### YouTube

A primeira versão utiliza a **YouTube Data API v3** para recuperar conteúdos públicos relacionados às consultas definidas pelo projeto.

Entre os campos coletados estão:

- ID do vídeo;
- título;
- descrição;
- canal;
- data de publicação;
- visualizações;
- curtidas;
- comentários;
- métricas derivadas de engajamento.

A cobertura está condicionada às consultas, critérios de coleta e limitações da própria API.

---

## ⚙️ Pipeline de dados

Após a coleta, os dados passam por um pipeline de ETL desenvolvido em Python:

```text
Coleta
   ↓
Validação
   ↓
Normalização
   ↓
Deduplicação
   ↓
Identificação de candidatos
   ↓
Classificação contextual
   ↓
Análise de sentimento
   ↓
Construção das métricas
   ↓
Dataset analítico
   ↓
Power BI
```

O processamento inclui tratamento de:

- datas;
- campos textuais;
- identificadores;
- métricas numéricas;
- duplicidades;
- candidatos;
- classificações;
- campos derivados.

---

## 🧠 Identificação de candidatos

A identificação utiliza uma **abordagem híbrida**, combinando regras determinísticas e Inteligência Artificial.

### 1. Regras determinísticas

Quando um candidato pode ser identificado diretamente por nomes ou variações cadastradas, o conteúdo é resolvido sem necessidade de utilizar um modelo de linguagem.

Na primeira execução:

**1.056 conteúdos foram resolvidos deterministicamente.**

### 2. Inteligência Artificial

Conteúdos que permanecem ambíguos são encaminhados para classificação contextual utilizando IA local.

Foram identificados:

**343 casos ambíguos.**

Essa arquitetura permite utilizar processamento determinístico sempre que possível e reservar a IA para situações em que **interpretação contextual** é necessária.

---

## 🤖 Inteligência Artificial

Os modelos são executados localmente utilizando:

- **Ollama**
- **Qwen3 8B**
- **Qwen3 4B Instruct**
- NLP
- Prompt Engineering

O **Qwen3 8B** foi utilizado inicialmente em parte da resolução de ambiguidades.

Posteriormente, o **Qwen3 4B Instruct** foi utilizado para ampliar o processamento e executar etapas de classificação textual e sentimento.

Essa abordagem permite explorar o uso de modelos de linguagem dentro de um pipeline analítico sem depender exclusivamente de processamento externo.

---

## 💬 Análise de sentimento

Os conteúdos são classificados automaticamente em:

```text
POSITIVO
NEUTRO
NEGATIVO
MISTO
INDETERMINADO
```

A classificação considera principalmente:

- candidato identificado;
- título;
- descrição.

Na V1:

**1.399 conteúdos foram processados pelo pipeline de sentimento.**

Tempo médio observado:

**≈ 2,1 segundos por conteúdo**

Erros de execução observados nessa etapa:

**0**

> A conclusão técnica do processamento não representa validação da precisão das classificações.

A validação humano × IA faz parte das próximas etapas do projeto.

---

## 📊 Índice de Sentimento

O dashboard utiliza um indicador experimental de sentimento em escala de **0 a 100**.

A ponderação atual é:

```text
Negativo = 0
Neutro   = 50
Positivo = 100
```

Fórmula conceitual:

```text
          (Positivos × 100) + (Neutros × 50)
Índice = ─────────────────────────────────────
             Positivos + Neutros + Negativos
```

Conteúdos classificados como `MISTO` ou `INDETERMINADO` não participam do cálculo.

O indicador representa uma **síntese matemática das classificações textuais observadas na amostra**.

> O Índice de Sentimento não representa aprovação, popularidade ou intenção de voto.

---

## 🚦 Sentimento predominante

Além do índice numérico, o dashboard apresenta a categoria predominante na distribuição dos conteúdos elegíveis.

A evolução metodológica prevê considerar predominância somente quando uma categoria atingir pelo menos **50% dos conteúdos elegíveis**.

```text
POSITIVO ≥ 50%  → Predominância positiva

NEUTRO ≥ 50%    → Predominância neutra

NEGATIVO ≥ 50%  → Predominância negativa

Nenhuma categoria ≥ 50%
            ↓
     SEM PREDOMINÂNCIA
```

A regra busca evitar que pequenas diferenças entre categorias sejam apresentadas visualmente como uma predominância forte.

---

## 📊 Dashboard

A camada de Business Intelligence foi desenvolvida no **Microsoft Power BI**.

### KPIs

O dashboard acompanha:

- Total de vídeos
- Total de visualizações
- Total de curtidas
- Total de comentários
- Total de engajamento
- Canais únicos
- Taxa de engajamento

### Análises

A V1 disponibiliza:

- Índice de Sentimento
- Sentimento predominante
- Distribuição dos sentimentos
- Evolução diária
- Análise por candidato
- Análise por período
- Indicadores de engajamento

Os principais indicadores respondem dinamicamente aos filtros aplicados pelo usuário.

---

## 📅 Evolução temporal

A solução permite acompanhar a evolução diária das classificações e métricas.

Isso possibilita identificar:

- aumentos no volume de conteúdos;
- alterações na distribuição de sentimentos;
- períodos de maior atividade;
- mudanças nos indicadores;
- pontos que merecem investigação.

Um pico identificado nos dados **não é automaticamente associado a um acontecimento político**.

A interpretação exige investigação dos conteúdos publicados naquele período e contextualização adequada.

---

## 📐 Modelo de dados

A camada analítica utiliza dimensões específicas para controlar filtros e relacionamentos.

### Principais dimensões

```text
Dim_Candidato
Dim_Calendario
```

### Principais tabelas analíticas

```text
powerbi_youtube_posts
powerbi_candidate_summary
powerbi_daily
youtube_sentiment_all
```

A estrutura foi organizada para reduzir relacionamentos diretos desnecessários entre tabelas fato e facilitar a construção das métricas no Power BI.

---

## 🛠️ Stack tecnológica

### Data Engineering

- Python
- Pandas
- APIs
- ETL
- SQL

### Inteligência Artificial

- Ollama
- Qwen3
- NLP
- Prompt Engineering
- Classificação de texto

### Business Intelligence

- Microsoft Power BI
- Power Query
- DAX
- Modelagem dimensional

### Desenvolvimento

- VS Code
- Git
- GitHub

---

## 📁 Estrutura do repositório

```text
Election Social Listening 2026/
│
├── config/
│   └── candidates.json
│
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
│
├── prompts/
│   └── classification_prompt.txt
│
├── sql/
│   ├── metrics.sql
│   └── schema.sql
│
├── src/
│   ├── ai_classifier.py
│   ├── benchmark_4b.py
│   ├── build_powerbi_dataset.py
│   ├── classify.py
│   ├── classify_ambiguous.py
│   ├── classify_sentiment_all.py
│   ├── classify_validation.py
│   ├── collect.py
│   ├── consolidate_youtube.py
│   ├── create_validation_excel.py
│   ├── create_validation_sample.py
│   ├── detect_candidates.py
│   ├── metrics.py
│   ├── normalize.py
│   ├── normalize_final_candidates.py
│   ├── normalize_youtube.py
│   ├── prepare_validation_review.py
│   ├── retry_errors.py
│   └── youtube_collector.py
│
├── Imagem Dashboard.PNG
├── requirements.txt
├── .gitignore
└── README.md
```

Os datasets brutos/processados, credenciais e arquivos de ambiente **não são versionados no repositório público**.

---

## ⚠️ Limitações

Esta primeira versão possui limitações que devem ser consideradas na interpretação dos resultados.

### Cobertura

Os dados representam somente os conteúdos encontrados a partir das consultas e critérios definidos na coleta.

A amostra **não representa todo o conteúdo existente no YouTube**.

### Sentimento

A classificação de sentimento é produzida automaticamente por modelos de linguagem.

A V1 ainda não possui validação humana suficiente para que a classificação seja interpretada como uma medição comprovada de precisão.

### Engajamento

Curtidas, comentários e visualizações representam interações com conteúdos.

**Engajamento não representa apoio político.**

### Menções

Quantidade de conteúdos encontrados sobre determinado candidato não representa intenção de voto.

### Índice de Sentimento

O índice é uma métrica experimental construída especificamente para o projeto.

**Não representa aprovação pública ou intenção de voto.**

---

## 🧭 Princípios de interpretação

Os indicadores devem ser interpretados dentro do contexto e das limitações da amostra.

```text
Menções            ≠ intenção de voto

Engajamento        ≠ apoio político

Visualizações      ≠ aprovação

Sentimento textual ≠ voto

Volume de conteúdo ≠ popularidade eleitoral

Amostra coletada   ≠ população brasileira
```

Sempre que possível, os resultados devem ser acompanhados de:

- período analisado;
- plataforma;
- metodologia;
- cobertura;
- tamanho da amostra;
- limitações.

---

# 🚀 Roadmap

O **Election Social Listening 2026** está em desenvolvimento contínuo.

A V1 estabelece a fundação técnica da solução. As próximas versões avançarão principalmente na capacidade **investigativa, temática e automatizada** do projeto.

## ✅ V1 — MVP funcional

- [x] Estrutura do projeto
- [x] Integração com YouTube Data API
- [x] Coleta automatizada
- [x] Normalização
- [x] Deduplicação
- [x] Entity Resolution
- [x] Resolução de ambiguidades com IA
- [x] Classificação de sentimento
- [x] Dataset analítico
- [x] Modelo dimensional
- [x] KPIs
- [x] Índice de Sentimento
- [x] Sentimento predominante
- [x] Evolução temporal
- [x] Dashboard Power BI

---

## 🚧 Próxima evolução

O foco passa de um dashboard predominantemente descritivo para uma ferramenta cada vez mais **investigativa**.

```text
Evolução temporal
        ↓
Detecção de picos
        ↓
Identificação dos conteúdos relacionados
        ↓
Classificação temática
        ↓
Análise de narrativas
        ↓
Validação humana
```

Planejado:

- [ ] Investigação automática de picos
- [ ] Identificação dos conteúdos associados
- [ ] Refinamento visual do dashboard
- [ ] Classificação temática
- [ ] Identificação de narrativas
- [ ] Validação humano × IA

---

## 🔜 Inteligência temática

Uma das próximas camadas permitirá analisar **sobre o que os conteúdos estão falando**.

Entre os temas previstos:

- economia;
- saúde;
- segurança;
- educação;
- meio ambiente;
- infraestrutura;
- outros assuntos relevantes.

Isso permitirá avançar de:

> **“Quanto conteúdo existe e qual foi sua classificação?”**

para questões como:

> **“O que está sendo discutido, quando houve mudanças e quais conteúdos estão associados a essas mudanças?”**

---

## 🔜 Validação dos modelos

Está prevista uma etapa específica para avaliar formalmente a qualidade das classificações produzidas pela IA.

Planejado:

- [ ] criação de amostra de validação;
- [ ] classificação humana;
- [ ] comparação humano × IA;
- [ ] matriz de confusão;
- [ ] precision;
- [ ] recall;
- [ ] F1-score;
- [ ] análise dos principais tipos de erro.

---

## 🔜 Expansão de fontes

A arquitetura foi pensada para incorporar novas fontes públicas quando houver acesso legítimo e tecnicamente viável.

```text
YouTube        ✅
Reddit         🔜
Web            🔜
Notícias       🔜
Outras APIs    🔜
```

Cada fonte deverá possuir sua própria metodologia e cobertura documentadas.

---

## 🔜 Automação

Outra evolução prevista é tornar o pipeline incremental e automatizado.

```text
Coleta programada
        ↓
Processamento incremental
        ↓
Classificação automática
        ↓
Validação
        ↓
Atualização dos datasets
        ↓
Atualização do dashboard
```

Entre as funcionalidades previstas:

- [ ] coleta incremental;
- [ ] logs de execução;
- [ ] controle de falhas;
- [ ] histórico de processamento;
- [ ] atualização automática;
- [ ] monitoramento da qualidade dos dados.

---

## 👤 Autor

### Henrique Estevão

**Dados & Business Analytics**

Projeto desenvolvido como estudo aplicado da integração entre **dados, estratégia, Inteligência Artificial e Business Intelligence**.

> **Conecto dados, estratégia e negócio para transformar análises em decisões que geram impacto.**

LinkedIn: `linkedin.com/in/henriqueestevao`

---

## 📌 Status do projeto

**Election Social Listening 2026 — V1**

🟢 Pipeline funcional  
🟢 Coleta via API  
🟢 ETL funcional  
🟢 IA integrada  
🟢 Classificação de sentimento  
🟢 Modelo analítico  
🟢 Dashboard Power BI  
🟡 Evolução analítica em andamento  
🟡 Validação humano × IA planejada  
🔵 Inteligência temática planejada  
🔵 Novas fontes planejadas  

---

> **Este repositório representa a primeira versão do Election Social Listening 2026.**
>
> O projeto continuará evoluindo ao longo do ciclo eleitoral, com novas fontes de dados, análises, validações e funcionalidades sendo incorporadas progressivamente.