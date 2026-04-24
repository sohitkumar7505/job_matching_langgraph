# 🚀 Smart Job Matching & Application Decision Engine (LangGraph)

## 📌 Overview

This project is an **advanced LangGraph-based system** that automates job matching and application preparation.

It takes a **candidate profile** and multiple **job listings**, evaluates their compatibility, routes them through different processing pipelines, and produces a **final application strategy** with human approval.

---

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install groq langgraph pydantic python-dotenv langchain-groq langchain-core
   ```

2. **Set up environment variables:**
   - Create a `.env` file in the root directory
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```

3. **Run the system:**
   ```bash
   python main.py
   ```

---

## 🎮 Interactive Human Review

When you run the system, it will:

1. **Analyze Jobs** - Score each job 1-10 based on candidate fit
2. **Route Processing** - Send jobs through pipelines:
   - HIGH (8-10) → Full analysis + tailored resume + cover letter
   - MEDIUM (5-7) → Quick summary + skill matching
   - LOW (1-4) → Skipped
3. **Pause for Review** - Display processed jobs with full details
4. **Get Your Decision** - Choose from:
   - `approve` - Approve all jobs
   - `approve 1,2,3` - Approve specific jobs
   - `reject` - Reject all
   - `review 1` - View detailed info for a job
   - `revise 1,2` - Mark jobs for revision
5. **Generate Strategy** - Show final recommendations with stats
6. **Streamed LLM Text Output** - View cover letters, summaries, and analysis as they generate in real time

## 🎯 Key Features

* ✅ **Multi-job processing** (3–5 jobs at once)
* ✅ **LLM-based scoring system** (1–10 scale)
* ✅ **Conditional routing** (HIGH / MEDIUM / LOW)
* ✅ **Subgraph pipelines**

  * Full Pipeline (for HIGH matches)
  * Quick Pipeline (for MEDIUM matches)
* ✅ **Quality loop with retry mechanism**
* ✅ **Human-in-the-loop (HitL)** with pause & resume
* ✅ **State persistence using MemorySaver**
* ✅ **Final structured output (Pydantic model)**

---

## 🧠 System Architecture

```
START
  ↓
[intake] → Load candidate & jobs
  ↓
[scorer] → Score each job (1–10)
  ↓
[router] → Categorize jobs

  ├── HIGH → full_pipeline (subgraph)
  ├── MEDIUM → quick_pipeline (subgraph)
  └── LOW → skip_log

  ↓
[aggregate]
  ↓
[human_review] (PAUSE here)
  ↓
[strategy]
  ↓
END
```

---

## ⚙️ Tech Stack

* **Python**
* **LangGraph**
* **LangChain**
* **Pydantic**
* **OpenAI / Groq (optional for LLM)**
* **dotenv**

---

## 📁 Project Structure

```
job-matching-engine/
│
├── main.py
├── state.py
├── models.py
│
├── nodes/
│   ├── intake.py
│   ├── scorer.py
│   ├── router.py
│   ├── aggregate.py
│   ├── human_review.py
│   ├── strategy.py
│   └── skip_log.py
│
├── subgraphs/
│   ├── full_pipeline.py
│   └── quick_pipeline.py
│
├── data/
│   ├── candidate.json
│   └── jobs.json
│
└── requirements.txt
```

---

## 🧩 Core Concepts

### 🔹 State-Driven Architecture

The entire system is built around a **shared state (`GraphState`)**.

* All nodes **read → modify → return** the state
* Jobs are stored as a list of `JobState`

---

### 🔹 Conditional Routing

Jobs are categorized based on score:

| Score | Category | Pipeline       |
| ----- | -------- | -------------- |
| 8–10  | HIGH     | Full Pipeline  |
| 5–7   | MEDIUM   | Quick Pipeline |
| 1–4   | LOW      | Skip           |

---

### 🔹 Subgraphs

#### 🟢 Full Pipeline (HIGH)

```
analyze_jd → tailor_resume → cover_letter → quality_check
```

* Includes **retry loop** if quality < 7

#### 🟡 Quick Pipeline (MEDIUM)

```
extract → match → summary
```

---

### 🔹 Human-in-the-Loop (HitL)

* Execution **pauses before `human_review`**
* User can:

  * ✅ Approve jobs
  * ❌ Reject jobs
  * 🔁 Request revision

---

### 🔹 Persistence

* Uses `MemorySaver`
* Enables:

  * Pause execution
  * Resume later from checkpoint

---

## 🚀 Installation

```bash
pip install langgraph langchain openai pydantic python-dotenv
```

---

## ▶️ How to Run

```bash
python main.py
```

### Flow:

1. Graph starts execution
2. Pauses at human review
3. User provides input
4. Graph resumes
5. Final output generated

---

## 📊 Sample Input

### Candidate

* Python Developer (3 yrs)
* Skills: Python, FastAPI, Docker, LangChain

### Jobs

1. AI Agent Developer → HIGH
2. Data Scientist → LOW
3. Full Stack Developer → MEDIUM
4. AI Platform Engineer → HIGH

---

## 📌 Expected Output

```json
{
  "candidate_name": "Ravi Kumar",
  "total_jobs_analyzed": 4,
  "approved_jobs": [...],
  "skipped_jobs": [...],
  "recommended_apply_order": [...]
}
```

---

## 🔥 Advanced Features Implemented

* ✔ Nested subgraphs
* ✔ Conditional edges
* ✔ Loop inside graph (quality retry)
* ✔ Interrupt-based execution
* ✔ Resume capability
* ✔ Multi-job orchestration

---

## 🧠 Learning Outcomes

* Understanding **LangGraph workflows**
* Designing **stateful AI systems**
* Implementing **human-in-the-loop pipelines**
* Building **modular, scalable architectures**

---

## 🚀 Future Improvements

* 🔹 Integrate real LLM APIs (OpenAI / Groq)
* 🔹 Add streaming outputs
* 🔹 Graph visualization (Mermaid)
* 🔹 Parallel execution with Send API
* 🔹 File export (resume + cover letters)

---

## 👥 Team Roles

* **Member 1:** Intake, Scoring, Router, State & Models
* **Member 2:** Full Pipeline + Quick Pipeline
* **Member 3:** Orchestration, Human Review, Strategy, Persistence

---

## 🏆 Conclusion

This project demonstrates how to build a **production-level AI workflow system** using LangGraph with:

* Dynamic decision-making
* Human oversight
* Scalable architecture

---

## 📌 Author

**Sohit Kumar**
AI/ML Enthusiast | Full Stack Developer

---
