# 🤖 Intelligent Code Documentation Generator

An AI-powered tool that automatically generates clear, structured technical documentation from source code using an **agentic AI workflow**.

## 📋 Problem Statement

Writing and maintaining code documentation is a time-consuming, tedious task that developers often skip. Poorly documented code leads to difficulty in understanding, maintaining, and collaborating on software projects. An intelligent system that can automatically generate accurate documentation would save significant development time and improve code quality.

## 🎯 Objective

To build an AI-powered application that:
- Analyzes source code structure (functions, classes, parameters).
- Generates comprehensive technical documentation using AI agents.
- Reviews the documentation for completeness and accuracy.
- Provides a user-friendly web interface for the entire workflow.

## ✨ Features

- **Multi-language support** — Python, Java, C++, JavaScript
- **Automatic language detection** from code patterns
- **Python AST analysis** — deep structure extraction for Python code
- **Agentic AI workflow** — two cooperating AI agents
- **Documentation review** — automated quality checking
- **Self-improvement** — generator improves docs based on reviewer feedback
- **Multiple documentation styles** — Markdown, Google Style, Javadoc, JSDoc
- **Download output** — export documentation as `.md` file
- **Demo Mode** — works without an API key for demonstration

## 🛠️ Technology Used

| Technology | Purpose |
|-----------|---------|
| Python 3.10+ | Core programming language |
| Gradio | Web-based GUI framework |
| Google Gemini API | LLM for AI-powered generation |
| Python AST | Code structure analysis |
| python-dotenv | Environment variable management |

## 🔄 Agentic AI Workflow

```
User Code
   ↓
Code Analyzer (AST / Regex)
   ↓
┌─────────────────────────────────┐
│  Agent 1: Documentation Generator │
│  Generates structured docs       │
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────┐
│  Agent 2: Documentation Reviewer │
│  Checks completeness & accuracy  │
└─────────────┬───────────────────┘
              ↓
        Issues found?
       /            \
     Yes             No
      ↓               ↓
  Generator          Final
  improves           Output
  docs (1x)            ↓
      ↓           Display &
  Re-review        Download
```

### Agent 1 — Documentation Generator
- Receives source code, language, and style preference
- Uses code analysis results for context
- Sends a structured prompt to the LLM
- Generates complete documentation

### Agent 2 — Documentation Reviewer
- Receives the original code + generated documentation
- Checks if all functions and classes are documented
- Verifies parameters and return values are described
- Returns a review verdict with specific issues

### Why is this Agentic AI?
This project demonstrates **agentic AI** because:
1. **Multiple autonomous agents** work together toward a shared goal
2. Agents have **distinct roles** (generator vs. reviewer)
3. There is an **iterative feedback loop** — the reviewer's feedback improves the output
4. The system makes **autonomous decisions** about when documentation needs improvement

## 📦 Installation

```bash
# 1. Clone or navigate to the project
cd "Intelligent-Code-Documentation-Generator"

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set up your API key
copy .env.example .env
# Edit .env and add your Google Gemini API key
# Get a free key from: https://aistudio.google.com/app/apikey
```

## 🚀 How to Run

```bash
python app.py
```

The application will start and show a URL (usually `http://127.0.0.1:7860`). Open it in your browser.

> **Note:** The app works in **Demo Mode** without an API key. To use real AI, add your Gemini API key to a `.env` file.

## 📝 Example

**Input code:**
```python
def add(a, b):
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y
```

**Generated documentation:**
```markdown
# Module Documentation

## Functions

### add(a, b)
Adds two values and returns their sum.

**Parameters:**
- `a`: First value
- `b`: Second value

**Returns:** The sum of `a` and `b`.

### multiply(x, y)
Multiply two numbers.

**Parameters:**
- `x`: First number
- `y`: Second number

**Returns:** The product of `x` and `y`.
```

## 🔮 Future Scope

- Support for more languages (Go, Rust, TypeScript)
- Integration with GitHub repositories
- Batch documentation for entire projects
- Support for additional LLM providers (OpenAI, Anthropic)
- Documentation versioning and diff comparison
- CI/CD integration for automated documentation updates

## 📁 Project Structure

```
project/
├── app.py              # Gradio GUI and main entry point
├── agents.py           # AI agents (Generator + Reviewer)
├── code_analyzer.py    # Code analysis (AST + regex)
├── llm_client.py       # LLM API client with demo mode
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

*Built as a mini-project for demonstrating Agentic AI in B.Tech CSE.*
