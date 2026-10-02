# Jenoy Rex

3rd-year Data Science Engineering student. Most of what I've built so far is backend and
infrastructure work (APIs, databases, CI, authentication, encryption), and I'm building on
that toward LLM evaluation and ML experimentation.

## Featured work

**[Vigil](https://github.com/Jenoyrex/vigil)**: LLM tracing and evaluation platform. A Python SDK
sends spans to a FastAPI ingestion API backed by ClickHouse; a Postgres-backed worker scores sampled
LLM spans with TF-IDF and embedding-based relevance evaluators. Next.js dashboard.
[Live demo](https://vigiljr.netlify.app)

**[VaultDrop](https://github.com/Jenoyrex/VaultDrop)**: File vault with client-side AES-GCM
encryption via the Web Crypto API. The server stores ciphertext and wrapped keys, never usable key
material. Next.js, Express, Prisma, PostgreSQL. [Live demo](https://vaultdrop95.netlify.app)

**[ADPO](https://github.com/Jenoyrex/ADPO)**: GitHub App that syncs GitHub Actions run history and
runs six statistical analyzers over it (regressions, slow jobs and steps, retry waste,
dependency-install overhead). No LLM in the analysis. FastAPI, PostgreSQL, React.
[Live demo](https://adpo-gilt.vercel.app)

**[multi-agent-cooperation](https://github.com/Jenoyrex/multi-agent-cooperation)**: College group
project. Research harness for LLM-vs-LLM negotiation experiments with seeded environments and
preregistered welfare and fairness metrics. In progress; no experimental results yet.

## Currently working on

- Vigil's evaluation pipeline: relevance evaluators (TF-IDF baseline and a local embedding model)
  run by a background worker over sampled LLM spans
- The preregistered negotiation experiments in multi-agent-cooperation

## Technical focus

- **Languages:** Python, TypeScript, SQL
- **Backend and data:** FastAPI, SQLAlchemy/Alembic, Express, Prisma, PostgreSQL, ClickHouse
- **Frontend:** Next.js, React
- **ML / LLM:** scikit-learn, fastembed, Anthropic and OpenAI APIs
- **Tooling:** Docker, GitHub Actions, pytest, Vitest

## Contact

[LinkedIn](https://www.linkedin.com/in/jenoy-rex-0173111b6/) · [jenoyrex95@gmail.com](mailto:jenoyrex95@gmail.com)
