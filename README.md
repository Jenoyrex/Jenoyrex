<p align="center">
  <img src="./assets/night.gif" width="100%" alt="Pixel-art night landscape: dark mountains, a moon, scattered stars and slowly drifting clouds" />
</p>

# Jenoy Rex

3rd-year Data Science Engineering student. Most of what I build is backend and infrastructure
work (APIs, job queues, CI, authentication, encryption), and I use it for LLM evaluation and
ML experiments.

<sub>[linkedin](https://www.linkedin.com/in/jenoy-rex-0173111b6/) · [email](mailto:jenoyrex95@gmail.com) · [github](https://github.com/Jenoyrex)</sub>

```python
class JenoyRex:
    role = "3rd-year Data Science Engineering student"

    focus = {
        "backend systems":    "FastAPI services, job queues, CI, auth",
        "LLM evaluation":     "tracing, relevance evaluators, offline benchmarks",
        "ML experimentation": "seeded environments, preregistered metrics",
        "security":           "client-side encryption, least-privilege GitHub Apps",
    }
```

## selected work

### 01 / Vigil

<sub>llm observability · evaluation</sub>

LLM tracing and evaluation platform. A Python SDK sends spans to a FastAPI ingestion API backed by
ClickHouse; a Postgres-backed worker scores sampled LLM spans with TF-IDF and embedding-based
relevance evaluators, benchmarked offline on WikiQA with a held-out test split.

`python · fastapi · clickhouse · postgresql · next.js`

[repository](https://github.com/Jenoyrex/vigil) · [live demo](https://vigiljr.netlify.app)

### 02 / VaultDrop

<sub>security · full stack</sub>

File vault with client-side AES-GCM encryption via the Web Crypto API. The server stores ciphertext
and wrapped keys, never usable key material.

`typescript · next.js · express · prisma · postgresql`

[repository](https://github.com/Jenoyrex/VaultDrop) · [live demo](https://vaultdrop95.netlify.app)

### 03 / ADPO

<sub>ci analytics · statistics</sub>

GitHub App that syncs GitHub Actions run history and runs six statistical analyzers over it
(regressions, slow jobs and steps, retry waste, dependency-install overhead). No LLM in the analysis.

`python · fastapi · postgresql · react`

[repository](https://github.com/Jenoyrex/ADPO) · [live demo](https://adpo-gilt.vercel.app)

### 04 / multi-agent-cooperation

<sub>llm research · college group project</sub>

Research harness for LLM-vs-LLM negotiation experiments with seeded environments and preregistered
welfare and fairness metrics. In progress; no experimental results yet.

`python · anthropic api · openai api · sqlite`

[repository](https://github.com/Jenoyrex/multi-agent-cooperation)

## stack

```text
languages    python · typescript · sql
backend      fastapi · sqlalchemy · alembic · express · prisma
data         postgresql · clickhouse · sqlite
frontend     next.js · react
ml / llm     scikit-learn · fastembed · anthropic api · openai api
tooling      docker · github actions · pytest · vitest
```

## activity

<img src="./assets/activity.svg" width="100%" alt="Contribution calendar, October 2025 to October 2026: 251 contributions" />

<sub>github achievements · [pull shark ×2](https://github.com/Jenoyrex?tab=achievements)</sub>

<br />

<sub>banner: a pixel-art night scene with its clouds set drifting by [`scripts/build_banner.py`](./scripts/build_banner.py) · activity: a snapshot of public GitHub data from [`scripts/generate_stats.py`](./scripts/generate_stats.py)</sub>
