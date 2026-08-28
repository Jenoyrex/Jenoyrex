### Jenoy REX

Full-stack engineer who builds, tests, secures, and deploys production systems — not just tutorials.

I work across the stack: React/Next.js and TypeScript on the frontend, Express/FastAPI on the backend, PostgreSQL for data, and I take projects from a design decision through to a live, monitored deployment. Security and testing aren't an afterthought — both projects below ship with real threat models, automated test suites, and CI pipelines.

---

### Flagship projects

**[VaultDrop](https://github.com/Jenoyrex/VaultDrop)** — a zero-knowledge encrypted file vault. File contents, names, and encryption keys are encrypted client-side with AES-256-GCM before anything reaches the server, which only ever stores ciphertext. Deployed live across four independent providers (Netlify, Render, Neon, Backblaze B2), with Argon2id auth, rate limiting, CSP-hardened headers, and CI running typecheck/test/build on every push.
[Live demo](https://vaultdrop95.netlify.app/) · Next.js · Express · Prisma · PostgreSQL

**[ADPO](https://github.com/Jenoyrex/ADPO)** — deterministic CI intelligence for GitHub Actions. Connects to a repository via a GitHub App, syncs its workflow run history, and runs six statistics-based analyzers (no LLM involved) to surface concrete, evidence-backed CI problems — slow jobs, dependency-install bottlenecks, flaky retries, missed parallelization — each finding citing the actual run IDs and numbers behind it. Three independently-deployed packages (a pure-Python analysis engine, a FastAPI backend, a React dashboard), 206 automated tests, GitHub App auth with encrypted-at-rest tokens.
[Live demo](https://adpo-gilt.vercel.app) · FastAPI · React · PostgreSQL · GitHub Apps

---

### Technical focus

**Full-stack:** React, Next.js, TypeScript, Tailwind CSS
**Backend:** Express, FastAPI, Prisma, PostgreSQL
**Security:** client-side encryption, authentication/authorization, GitHub App integrations
**Delivery:** automated testing, GitHub Actions CI/CD, production deployment

---

### Currently building

Expanding VaultDrop's automated security test coverage and adding file-sharing between users (see its [roadmap](https://github.com/Jenoyrex/VaultDrop#roadmap--phase-2)).
