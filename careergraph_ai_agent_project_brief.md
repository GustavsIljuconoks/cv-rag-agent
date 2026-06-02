# AI Agent Project Brief: CareerGraph — AI Job Search Analyst

## 1. Project Summary

Build **CareerGraph**, an AI-powered job-search analyst that helps a developer find, rank, analyze, and apply to relevant job opportunities.

This is not a generic chatbot. The goal is to build a practical RAG + workflow system that:

- collects job listings from job APIs,
- stores and searches job posts semantically,
- compares job requirements against a candidate profile/CV,
- ranks jobs using both deterministic scoring and AI explanation,
- detects missing skills,
- generates honest application material grounded in the user's real experience,
- tracks applications and learning priorities.

The project should demonstrate applied AI engineering, not only prompt usage.

The system should use:

- **LangGraph** for workflow orchestration,
- **Hugging Face Sentence Transformers** for embeddings and reranking,
- **Qdrant** as the vector database,
- **FastAPI** as the backend API,
- **PostgreSQL** for structured relational data,
- **Next.js or React** for the frontend,
- **Adzuna API** as the first job data source,
- optional later support for SerpApi, JSearch, or other job APIs.

---

## 2. Main Goal

The final app should answer questions like:

- "Which AI-related jobs match me best this week?"
- "Which roles are realistic for my current skill level?"
- "What skills am I missing most often?"
- "Compare this job with my CV."
- "Generate a short, honest cover letter for this role."
- "Which jobs mention Laravel, Python, React, Docker, AI, or automation?"
- "What should I learn next based on the jobs I am saving?"
- "Show me remote Europe jobs where I match at least 70% of requirements."

The system must always be honest. It must not invent experience, skills, projects, years of experience, education, or achievements.

---

## 3. Core Product Idea

CareerGraph has three main knowledge areas:

### 3.1 Candidate Knowledge

This includes:

- CV text,
- personal summary,
- skills,
- projects,
- work experience,
- education,
- preferred roles,
- preferred locations,
- preferred technologies,
- salary expectations,
- application history,
- notes from interviews or applications.

This data is used to ground answers about the candidate.

### 3.2 Job Knowledge

This includes:

- job title,
- company,
- location,
- remote/hybrid/on-site status,
- salary if available,
- job description,
- required skills,
- nice-to-have skills,
- seniority level,
- source URL,
- date posted,
- source platform.

This data is used for semantic search and ranking.

### 3.3 Application Knowledge

This includes:

- saved jobs,
- application status,
- cover letters,
- notes,
- deadlines,
- interview feedback,
- rejected/accepted/ignored outcomes.

This data helps the system learn which roles are worth applying to.

---

## 4. MVP Scope

Build the MVP in small steps. Do not overbuild the first version.

### MVP 1: Basic Job Matching

Required features:

1. User can create/edit a candidate profile.
2. User can upload or paste CV text.
3. Backend can fetch jobs from Adzuna API.
4. Jobs are stored in PostgreSQL.
5. Job descriptions are embedded using Hugging Face Sentence Transformers.
6. Job vectors are stored in Qdrant.
7. User can run a job-matching query.
8. System returns top matching jobs.
9. Each result includes:
   - match score,
   - matched skills,
   - missing skills,
   - short explanation,
   - recommendation: apply / maybe / skip.
10. UI displays results clearly.

### MVP 2: LangGraph Workflow

Add LangGraph to manage a multi-step workflow:

1. classify user intent,
2. load candidate profile,
3. retrieve relevant jobs,
4. retrieve relevant candidate context,
5. score job fit,
6. generate explanation,
7. detect missing skills,
8. save result.

### MVP 3: Application Assistant

Add:

1. cover letter draft generation,
2. CV bullet suggestions,
3. application tracker,
4. saved jobs,
5. weekly job summary.

### MVP 4: Evaluation

Add:

1. test job posts,
2. expected ranking examples,
3. retrieval quality checks,
4. hallucination checks,
5. latency/cost tracking,
6. small evaluation dashboard.

---

## 5. Non-Goals for the First Version

Do not implement these in the first MVP:

- scraping LinkedIn or Indeed directly,
- complex multi-user authentication,
- local LLM hosting,
- payment system,
- browser extension,
- advanced analytics dashboard,
- automatic job application submission,
- fully autonomous job applying,
- fine-tuning custom models.

These can be added later.

---

## 6. Recommended Tech Stack

### Backend

Use:

- Python
- FastAPI
- Pydantic
- SQLAlchemy or SQLModel
- PostgreSQL
- Qdrant
- LangGraph
- Sentence Transformers

### Frontend

Use:

- Next.js or React
- TypeScript
- Tailwind CSS
- simple dashboard UI

### AI / RAG

Use:

- Hugging Face Sentence Transformers for embeddings,
- optional cross-encoder reranker later,
- Qdrant for vector search,
- LangGraph for workflow orchestration,
- an LLM provider for answer generation.

The first version can use any available chat model through an API. Do not make LLM hosting the main challenge at the beginning.

### Background Jobs

Later add:

- Celery + Redis,
- or RQ,
- or APScheduler for simple scheduled fetching.

---

## 7. Suggested Folder Structure

```txt
careergraph/
  backend/
    app/
      main.py
      config.py

      api/
        routes/
          jobs.py
          profile.py
          matching.py
          applications.py

      db/
        session.py
        models.py
        migrations/

      services/
        adzuna_client.py
        job_normalizer.py
        cv_parser.py
        embedding_service.py
        qdrant_service.py
        scoring_service.py
        skill_extractor.py
        cover_letter_service.py

      graphs/
        job_ingestion_graph.py
        job_matching_graph.py
        application_assistant_graph.py

      prompts/
        job_fit_prompt.md
        cover_letter_prompt.md
        skill_gap_prompt.md
        truthfulness_rules.md

      evals/
        test_cases.yaml
        run_evals.py

    tests/
      test_scoring.py
      test_skill_extraction.py
      test_matching_graph.py

  frontend/
    app/
      page.tsx
      jobs/
      profile/
      applications/
    components/
      JobCard.tsx
      MatchScore.tsx
      MissingSkills.tsx
      SourceBadge.tsx

  docker-compose.yml
  README.md
  .env.example
```

---

## 8. Data Model

Use PostgreSQL for structured data.

### users

```txt
id
name
email
created_at
```

### candidate_profiles

```txt
id
user_id
summary
preferred_roles
preferred_locations
preferred_remote_type
preferred_technologies
salary_expectation_min
salary_expectation_max
created_at
updated_at
```

### candidate_experiences

```txt
id
candidate_profile_id
title
company
description
start_date
end_date
```

### candidate_projects

```txt
id
candidate_profile_id
name
description
technologies
url
```

### candidate_skills

```txt
id
candidate_profile_id
skill_name
category
confidence_level
evidence
```

### jobs

```txt
id
source
external_id
title
company
location
remote_type
salary_min
salary_max
description
url
posted_at
created_at
updated_at
```

### job_skills

```txt
id
job_id
skill_name
importance
source_text
```

### job_matches

```txt
id
job_id
candidate_profile_id
match_score
semantic_score
skill_score
seniority_score
location_score
salary_score
interest_score
matched_skills
missing_skills
explanation
recommendation
created_at
```

### applications

```txt
id
job_id
candidate_profile_id
status
notes
cover_letter
applied_at
created_at
updated_at
```

---

## 9. Vector Database Design

Use Qdrant collections.

### Collection: candidate_profile_chunks

Store chunks from:

- CV,
- profile summary,
- projects,
- work experience,
- education,
- skills,
- application notes.

Payload metadata:

```json
{
  "type": "candidate_profile",
  "section": "project | experience | skill | education | note",
  "source_id": "database_id",
  "candidate_profile_id": "uuid",
  "text": "original text"
}
```

### Collection: job_description_chunks

Store chunks from job posts.

Payload metadata:

```json
{
  "type": "job",
  "job_id": "uuid",
  "title": "Backend Developer",
  "company": "Company Name",
  "location": "Remote Europe",
  "source": "Adzuna",
  "url": "https://...",
  "posted_at": "date",
  "text": "original chunk"
}
```

### Search Strategy

Start with dense vector search.

Later add hybrid retrieval:

- dense semantic search for meaning,
- sparse/keyword search for exact terms like:
  - Laravel,
  - React,
  - Docker,
  - Python,
  - LangGraph,
  - LLM,
  - PostgreSQL,
  - Qdrant,
  - n8n,
  - EU,
  - remote.

---

## 10. Embedding and Reranking

Start with:

```txt
sentence-transformers/all-MiniLM-L6-v2
```

Later test:

```txt
sentence-transformers/all-mpnet-base-v2
```

Reranking can be added later using a cross-encoder model.

Suggested retrieval pipeline:

```txt
query
↓
embed query
↓
retrieve top 30 jobs from Qdrant
↓
rerank top 30
↓
keep top 10
↓
score with deterministic scoring
↓
generate explanation
```

---

## 11. LangGraph Workflows

Use LangGraph for clear graph-based workflows.

### 11.1 Job Ingestion Graph

Purpose: fetch and store jobs.

```txt
START
↓
fetch_jobs_from_adzuna
↓
normalize_jobs
↓
deduplicate_jobs
↓
extract_skills
↓
store_jobs_in_postgres
↓
chunk_job_descriptions
↓
embed_chunks
↓
store_vectors_in_qdrant
↓
END
```

### 11.2 Job Matching Graph

Purpose: match jobs against candidate profile.

```txt
START
↓
load_candidate_profile
↓
retrieve_candidate_context
↓
retrieve_relevant_jobs
↓
rerank_jobs
↓
calculate_deterministic_scores
↓
generate_fit_explanations
↓
detect_missing_skills
↓
save_job_matches
↓
END
```

### 11.3 User Query Graph

Purpose: route user queries.

```txt
START
↓
classify_intent
├── find_jobs → job_matching_graph
├── analyze_job → single_job_analysis
├── skill_gaps → skill_gap_analysis
├── cover_letter → cover_letter_graph
├── application_status → application_tracker
└── fallback → clarification_or_general_answer
```

### 11.4 Cover Letter Graph

Purpose: generate honest application material.

```txt
START
↓
select_job
↓
retrieve_job_context
↓
retrieve_candidate_context
↓
analyze_fit
↓
draft_cover_letter
↓
truthfulness_check
↓
improve_draft
↓
return_final_draft
↓
END
```

---

## 12. Ranking Logic

Do not let the LLM invent the score.

Use deterministic scoring first. Then let the LLM explain the score.

Suggested formula:

```txt
final_score =
  0.35 * semantic_similarity
+ 0.25 * required_skill_match
+ 0.15 * seniority_match
+ 0.10 * location_match
+ 0.10 * salary_match
+ 0.05 * user_interest_match
```

Convert to 0–100.

### Score Meaning

```txt
85–100: Strong match. Apply.
70–84: Good match. Apply if interested.
55–69: Possible match. Needs tailoring or learning.
40–54: Weak match. Save only if very interesting.
0–39: Skip.
```

### Recommendation Labels

Use:

```txt
apply
maybe
skip
learn_first
```

---

## 13. Skill Extraction

Extract skills from job posts and candidate profile.

Start with simple rule-based extraction using a skills dictionary.

Example skill categories:

```txt
Programming languages:
Python, JavaScript, TypeScript, PHP, Go, C#, SQL

Frontend:
React, Next.js, Vue, Svelte, Tailwind CSS

Backend:
FastAPI, Laravel, Node.js, ASP.NET, Django

AI:
RAG, LangChain, LangGraph, LLMs, embeddings, vector databases, Hugging Face

Infrastructure:
Docker, VPS, PostgreSQL, MySQL, Redis, CI/CD, GitHub Actions

Tools:
Git, GitHub, GitLab, Slack, n8n, Zapier
```

Later improve with LLM-based extraction.

---

## 14. Truthfulness Rules

Very important.

The application assistant must never invent experience.

### Allowed

The system may say:

```txt
I have experience with full-stack development, deployment, APIs, and automation, and I am building AI/RAG workflow projects.
```

Only if those facts are present in the candidate profile.

### Not Allowed

The system must not say:

```txt
I have 3 years of production machine learning experience.
```

Unless this is explicitly present in the candidate profile.

### Cover Letter Rules

Every claim in a cover letter must be grounded in candidate context.

If the system is unsure, it must choose a weaker but honest phrasing.

Use language like:

```txt
I am currently developing practical skills in...
I have hands-on project experience with...
My background in web development helps me understand...
```

Avoid exaggerated claims.

---

## 15. API Endpoints

### Profile

```txt
POST /profile
GET /profile
PUT /profile
POST /profile/cv
GET /profile/skills
```

### Jobs

```txt
POST /jobs/fetch
GET /jobs
GET /jobs/{job_id}
POST /jobs/{job_id}/save
```

### Matching

```txt
POST /matching/run
GET /matching/results
GET /matching/results/{job_id}
```

### Applications

```txt
POST /applications
GET /applications
PUT /applications/{application_id}
```

### Cover Letters

```txt
POST /cover-letter/{job_id}
```

### Evaluation

```txt
POST /evals/run
GET /evals/results
```

---

## 16. Frontend Pages

### Dashboard

Shows:

- number of new jobs,
- top 5 matches,
- most common missing skills,
- saved jobs,
- application status.

### Profile Page

Allows user to edit:

- CV,
- skills,
- projects,
- preferred roles,
- preferred locations.

### Jobs Page

Shows job cards with:

- title,
- company,
- location,
- salary,
- match score,
- matched skills,
- missing skills,
- apply/maybe/skip label.

### Job Detail Page

Shows:

- full job description,
- fit explanation,
- retrieved candidate evidence,
- missing skills,
- suggested CV bullets,
- cover letter draft.

### Applications Page

Shows:

- saved,
- applied,
- interviewing,
- rejected,
- offer,
- archived.

---

## 17. Output Format for Job Matches

Each job match should return:

```json
{
  "job_id": "uuid",
  "title": "AI Automation Developer",
  "company": "Example Company",
  "location": "Remote Europe",
  "url": "https://...",
  "match_score": 83,
  "recommendation": "apply",
  "matched_skills": ["React", "Docker", "API integration", "automation"],
  "missing_skills": ["LangGraph production experience", "advanced Python"],
  "explanation": "This role is a strong match because it combines workflow automation, API integrations, and AI tooling. Your full-stack and deployment background is relevant. The main gap is deeper production experience with LangGraph.",
  "suggested_action": "Apply. Emphasize web development, automation, deployment, and your CareerGraph/RAG project."
}
```

---

## 18. Prompt Templates

### Job Fit Explanation Prompt

```txt
You are an honest AI job-search analyst.

You receive:
1. Candidate profile context.
2. Job description context.
3. Deterministic scoring details.

Your task:
- explain why this job is or is not a good match,
- mention matched skills,
- mention missing skills,
- recommend apply/maybe/skip,
- do not invent experience,
- use only candidate facts present in the profile context.

Return concise, practical advice.
```

### Cover Letter Prompt

```txt
You are helping write a short, honest cover letter.

Rules:
- Use only facts from candidate context.
- Do not invent years of experience.
- Do not invent previous employers.
- Do not invent production ML experience.
- Connect candidate experience to the job requirements.
- Keep the tone professional and direct.
- Max length: 250 words.

Inputs:
- candidate context
- job description
- match explanation
- missing skills

Output:
- cover letter draft
- list of claims used
- warning if any claim is weak or unsupported
```

### Skill Gap Prompt

```txt
You are analyzing skill gaps.

Inputs:
- candidate skills
- job requirements
- saved job history

Return:
- repeated missing skills,
- importance level,
- suggested learning priority,
- small project ideas to prove those skills.
```

---

## 19. Evaluation Plan

Build simple evaluation from the beginning.

### Test Cases

Create 20–50 test cases.

Each test case should include:

```yaml
question: "Which jobs match a junior full-stack developer interested in AI automation?"
expected_relevant_skills:
  - React
  - APIs
  - Docker
  - Python
  - AI automation
must_not_claim:
  - "5 years ML experience"
  - "senior AI engineer"
expected_behavior:
  - rank junior/mid roles higher than senior ML scientist roles
  - show missing skills clearly
```

### Metrics

Track:

- retrieval precision,
- skill extraction quality,
- ranking quality,
- hallucinated experience claims,
- latency,
- number of jobs analyzed,
- top-k relevance,
- cover letter truthfulness.

### Hallucination Check

Every generated application text should be checked against candidate profile context.

If a claim is unsupported, mark it.

---

## 20. Environment Variables

Create `.env.example`:

```txt
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/careergraph
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
LLM_PROVIDER=
LLM_API_KEY=
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 21. Docker Compose

Use Docker Compose for local development.

Services:

```txt
backend
frontend
postgres
qdrant
redis optional
```

The first version can skip Redis if background jobs are not yet implemented.

---

## 22. Development Milestones

### Milestone 1: Project Setup

- Create repo structure.
- Add Docker Compose.
- Add FastAPI backend.
- Add PostgreSQL.
- Add Qdrant.
- Add basic frontend.

Acceptance:

- `docker compose up` starts the stack.
- Backend health endpoint works.
- Frontend loads.

### Milestone 2: Candidate Profile

- Create profile form.
- Store CV/profile in PostgreSQL.
- Chunk and embed candidate profile.
- Store candidate vectors in Qdrant.

Acceptance:

- User can save profile.
- Candidate chunks appear in Qdrant.

### Milestone 3: Job Ingestion

- Connect to Adzuna API.
- Fetch jobs by keyword/location.
- Normalize job data.
- Store jobs in PostgreSQL.
- Chunk and embed job descriptions.
- Store job vectors in Qdrant.

Acceptance:

- User can fetch jobs.
- Jobs are stored.
- Job vectors are searchable.

### Milestone 4: Basic Matching

- Retrieve relevant jobs.
- Compute deterministic match scores.
- Show top matches in UI.

Acceptance:

- User can see ranked jobs with scores.

### Milestone 5: LangGraph Matching

- Implement job matching workflow with LangGraph.
- Add fit explanation.
- Add missing skills.

Acceptance:

- Matching runs as a graph.
- Output includes explanation and missing skills.

### Milestone 6: Application Assistant

- Generate cover letter draft.
- Add truthfulness check.
- Save application status.

Acceptance:

- Cover letter uses only candidate facts.
- Unsupported claims are flagged.

### Milestone 7: Evaluation

- Add test cases.
- Run evaluations.
- Show results.

Acceptance:

- Evaluation script checks ranking and hallucination behavior.

---

## 23. Coding Rules for the AI Agent

When implementing this project:

1. Work in small commits.
2. Build one feature at a time.
3. Do not create large unfinished abstractions.
4. Prefer readable code over clever code.
5. Write tests for scoring and parsing logic.
6. Do not hard-code secrets.
7. Use `.env.example`.
8. Keep prompts in separate markdown files.
9. Keep graph nodes small and testable.
10. Log important steps in job ingestion and matching.
11. Do not invent candidate facts in generated text.
12. Use deterministic scoring for match score.
13. Use LLM only for explanation and drafting.
14. Store original source text for traceability.
15. Always show the source job URL in the UI.
16. Do not scrape websites that disallow scraping.
17. Use public APIs first.

---

## 24. First Implementation Tasks for the AI Agent

Start with these tasks in order:

### Task 1

Create project structure:

```txt
backend/
frontend/
docker-compose.yml
.env.example
README.md
```

### Task 2

Create Docker Compose with:

```txt
postgres
qdrant
backend
frontend
```

### Task 3

Create FastAPI backend with:

```txt
GET /health
```

### Task 4

Create PostgreSQL models:

```txt
candidate_profiles
jobs
job_matches
applications
```

### Task 5

Create Adzuna client:

```txt
search_jobs(keyword, location, country)
```

### Task 6

Create embedding service using Sentence Transformers.

### Task 7

Create Qdrant service:

```txt
create_collection
upsert_chunks
search_similar
```

### Task 8

Create basic job ingestion pipeline.

### Task 9

Create basic matching service with deterministic score.

### Task 10

Create first LangGraph job matching graph.

---

## 25. Recommended README Sections

The README should include:

```txt
1. What this project does
2. Why it exists
3. Tech stack
4. Architecture diagram
5. RAG pipeline
6. LangGraph workflows
7. Data model
8. Local setup
9. Environment variables
10. API examples
11. Evaluation strategy
12. Limitations
13. Future improvements
```

---

## 26. Important Design Philosophy

The project should show that AI engineering is more than calling an LLM.

The key engineering ideas are:

- structured job data,
- semantic retrieval,
- vector search,
- deterministic scoring,
- graph-based workflows,
- grounded explanations,
- truthfulness checks,
- evaluation,
- clear UI,
- useful business workflow.

The strongest portfolio story is:

> "I built an AI job-search analyst that uses job APIs, RAG, vector search, Hugging Face embeddings, and LangGraph workflows to rank job opportunities against a candidate profile, explain skill gaps, and generate honest application material."

---

## 27. Architectural Improvements

The following improvements should be added incrementally. They make the system easier to debug, evaluate, and extend without expanding the first MVP unnecessarily.

### 27.1 Separate Retrieval, Ranking, and Generation

Treat these as distinct stages:

```txt
retrieve candidate-relevant job chunks from Qdrant
->
aggregate chunk-level results into job-level candidates
->
calculate deterministic job scores
->
rank jobs
->
generate explanations only for the top results
```

Qdrant retrieval finds potentially relevant jobs. The deterministic scoring service decides the match score and recommendation. The LLM explains the result but must not change the score.

### 27.2 Store Raw Source Data and Ingestion Runs

Keep the original Adzuna payload for traceability and debugging.

Add:

```txt
job_source_payloads
  id
  job_id
  source
  external_id
  raw_payload
  payload_hash
  fetched_at

ingestion_runs
  id
  source
  query
  location
  status
  fetched_count
  inserted_count
  updated_count
  skipped_count
  error_count
  started_at
  completed_at
```

Use a unique constraint on:

```txt
(source, external_id)
```

The ingestion pipeline should support pagination, retries, logging, deduplication, and freshness filters.

### 27.3 Track Candidate Document Versions

Do not store only the current CV text. Keep candidate document versions so matches and generated text can be traced back to the profile context used at the time.

Add:

```txt
candidate_documents
  id
  candidate_profile_id
  document_type
  original_text
  content_hash
  version
  created_at
```

Store the candidate profile version or document version on each saved match and generated cover letter.

### 27.4 Track Vector Index State

PostgreSQL should remain the source of truth. Qdrant stores a searchable representation of that data.

Add:

```txt
vector_index_records
  id
  entity_type
  entity_id
  qdrant_collection
  qdrant_point_id
  content_hash
  embedding_model
  indexed_at
```

This allows the system to:

- detect stale vectors,
- re-index records when text changes,
- migrate embedding models,
- repair Qdrant from PostgreSQL,
- avoid embedding unchanged content.

### 27.5 Define Missing-Data Scoring Rules

Job listings often omit salary, seniority, or remote status. Missing values must not accidentally reduce a match score.

For every scoring factor, define:

```txt
known match
known mismatch
unknown value
```

Use a neutral score or redistribute weights when data is unknown. Store a scoring version with each match:

```txt
job_matches.scoring_version
```

This keeps rankings reproducible when the formula changes.

### 27.6 Normalize Skills

Use canonical skill names and aliases.

Examples:

```txt
Postgres -> PostgreSQL
React.js -> React
NodeJS -> Node.js
LLM -> LLMs
CI CD -> CI/CD
```

Store:

```txt
canonical_skill_name
matched_alias
category
importance
source_text
extraction_method
```

Distinguish between:

```txt
required
preferred
inferred
```

Start with a rule-based dictionary. Add LLM extraction later only as a structured, reviewable enrichment step.

### 27.7 Add Claim-Level Grounding for Generated Text

Prompt instructions alone are not enough to guarantee truthful cover letters.

Generated application material should return:

```json
{
  "draft": "cover letter text",
  "claims": [
    {
      "claim": "I have built API integrations.",
      "candidate_evidence_ids": ["candidate_chunk_uuid"],
      "support_status": "supported"
    }
  ],
  "warnings": []
}
```

The truthfulness check should flag or weaken unsupported claims before returning the final draft.

### 27.8 Keep LangGraph Nodes Thin

LangGraph nodes should orchestrate tested services rather than contain large blocks of business logic.

Examples:

```txt
fetch_jobs_node -> adzuna_client + ingestion_service
score_jobs_node -> scoring_service
embed_chunks_node -> embedding_service + qdrant_service
draft_cover_letter_node -> cover_letter_service
```

This makes each service testable outside the graph and avoids coupling workflow orchestration to implementation details.

### 27.9 Improve Evaluation Metrics

Add measurable checks for:

```txt
precision@k
recall@k
nDCG@k
skill extraction precision
skill extraction recall
unsupported claim rate
duplicate ingestion rate
vector index synchronization failures
latency per graph node
```

Use fixed candidate profiles and labeled job fixtures before relying on live API results.

### 27.10 Recommended Thin Vertical Slice

Before building the full assistant, complete one end-to-end path:

```txt
create candidate profile
->
save CV text
->
fetch and normalize jobs
->
embed and index jobs
->
retrieve relevant jobs
->
calculate deterministic scores
->
show ranked jobs with evidence and source URLs
```

After this works reliably, add LangGraph orchestration, explanation generation, cover letters, application tracking, and scheduled summaries.

---

## 28. Useful Official References

Use these as technical references while building:

- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph GitHub: https://github.com/langchain-ai/langgraph
- LangGraph agentic RAG guide: https://docs.langchain.com/oss/python/langgraph/agentic-rag
- Hugging Face Sentence Transformers: https://huggingface.co/sentence-transformers
- Sentence Transformers docs: https://sbert.net/
- Qdrant LangChain integration: https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant
- Qdrant LangChain docs: https://qdrant.tech/documentation/frameworks/langchain/
- Adzuna developer API: https://developer.adzuna.com/
- Adzuna search endpoint: https://developer.adzuna.com/docs/search
- LangSmith RAG evaluation tutorial: https://docs.langchain.com/langsmith/evaluate-rag-tutorial
- Ragas docs: https://docs.ragas.io/
