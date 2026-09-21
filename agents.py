"""
Agents Module
Contains the two AI agents:
  1. DocumentationGeneratorAgent — generates documentation from code.
  2. DocumentationReviewerAgent — reviews the generated documentation.
"""

from llm_client import call_llm, is_demo_mode
from code_analyzer import analyze_code, format_analysis_summary


# ─────────────────────────────────────────────────────
# Agent 1 — Documentation Generator
# ─────────────────────────────────────────────────────

class DocumentationGeneratorAgent:
    """
    Agent that analyzes source code and generates technical documentation.

    Workflow:
        1. Receives source code + language + style preference.
        2. Runs code analysis to extract structure.
        3. Sends a prompt to the LLM to generate documentation.
        4. Returns the generated documentation.
    """

    def __init__(self):
        self.name = "Documentation Generator Agent"

    def generate(self, code: str, language: str, style: str, review_feedback: str = "") -> str:
        """
        Generate documentation for the given source code.

        Args:
            code: The source code to document.
            language: Programming language.
            style: Documentation style (Markdown, Google Style, Javadoc, JSDoc).
            review_feedback: Optional feedback from the reviewer for improvement.

        Returns:
            Generated documentation as a Markdown string.
        """
        # Step 1: Analyze the code
        analysis = analyze_code(code, language)

        # Step 2: Build the prompt
        prompt = self._build_prompt(code, analysis, style, review_feedback)

        # Step 3: Call the LLM
        documentation = call_llm(prompt)

        return documentation

    def _build_prompt(self, code: str, analysis: dict, style: str, feedback: str) -> str:
        """Build the LLM prompt for documentation generation."""
        lang = analysis.get("language", "Unknown")
        funcs = analysis.get("functions", [])
        classes = analysis.get("classes", [])

        # Build structural context
        structure = ""
        if funcs:
            structure += "Functions found:\n"
            for f in funcs:
                params = ", ".join(f["params"]) if f["params"] else "none"
                structure += f"  - {f['name']}({params})"
                if f.get("docstring"):
                    structure += f" — existing docstring: \"{f['docstring'][:100]}\""
                structure += "\n"

        if classes:
            structure += "Classes found:\n"
            for c in classes:
                structure += f"  - {c['name']}"
                if c.get("methods"):
                    structure += f" with methods: {', '.join(c['methods'])}"
                structure += "\n"

        feedback_section = ""
        if feedback:
            feedback_section = (
                f"\n\nIMPORTANT — A reviewer found these issues in a previous version. "
                f"Please fix them:\n{feedback}\n"
            )

        prompt = f"""You are a technical documentation writer.

Generate clear, well-structured documentation for the following {lang} code.

**Documentation Style:** {style}

**Code Analysis:**
{structure if structure else "No specific structure extracted — analyze the code directly."}

**Source Code:**
```{lang.lower()}
{code}
```
{feedback_section}

**Instructions:**
1. Write an Overview section describing what the code does.
2. Document every function with: description, parameters, return values.
3. Document every class with: description, attributes, methods.
4. Explain any important logic or algorithms.
5. Include a usage example.
6. Use {style} formatting.
7. Be accurate — only document what the code actually does.
8. Output ONLY the documentation in Markdown format.
"""
        return prompt


# ─────────────────────────────────────────────────────
# Agent 2 — Documentation Reviewer
# ─────────────────────────────────────────────────────

class DocumentationReviewerAgent:
    """
    Agent that reviews generated documentation for completeness and accuracy.

    Workflow:
        1. Receives original code + generated documentation.
        2. Checks if all functions/classes are documented.
        3. Checks if parameters and return values are mentioned.
        4. Returns a review verdict.
    """

    def __init__(self):
        self.name = "Documentation Reviewer Agent"

    def review(self, code: str, documentation: str, language: str) -> dict:
        """
        Review the generated documentation.

        Args:
            code: The original source code.
            documentation: The generated documentation.
            language: Programming language.

        Returns:
            Dictionary with 'verdict', 'issues', and 'is_acceptable'.
        """
        # Step 1: Analyze the code
        analysis = analyze_code(code, language)

        # Step 2: Build the review prompt
        prompt = self._build_prompt(code, documentation, analysis)

        # Step 3: Call the LLM
        review_text = call_llm(prompt)

        # Step 4: Determine if documentation is acceptable
        is_acceptable = self._check_acceptable(review_text)

        return {
            "review": review_text,
            "is_acceptable": is_acceptable,
        }

    def _build_prompt(self, code: str, documentation: str, analysis: dict) -> str:
        """Build the LLM prompt for documentation review."""
        lang = analysis.get("language", "Unknown")
        funcs = analysis.get("functions", [])
        classes = analysis.get("classes", [])

        func_names = [f["name"] for f in funcs]
        class_names = [c["name"] for c in classes]

        prompt = f"""You are a documentation reviewer.

Review the following documentation generated for {lang} code.

**Functions in the code:** {', '.join(func_names) if func_names else 'None detected'}
**Classes in the code:** {', '.join(class_names) if class_names else 'None detected'}

**Original Code:**
```{lang.lower()}
{code}
```

**Generated Documentation:**
{documentation}

**Review Checklist:**
1. Are ALL functions documented? List any missing ones.
2. Are parameters described for each function?
3. Are return values explained?
4. Does the documentation accurately match the code?
5. Is anything important missing?

**Instructions:**
- If the documentation is complete, say "✅ Documentation is complete and accurate."
- If there are issues, list them clearly so the generator can fix them.
- Be concise. Output your review in Markdown format.
"""
        return prompt

    def _check_acceptable(self, review_text: str) -> bool:
        """Simple heuristic to check if the review is positive."""
        positive_signals = ["complete", "accurate", "✅", "no issues", "looks good", "well-documented"]
        negative_signals = ["missing", "not documented", "incorrect", "lacks", "❌", "issue"]

        text_lower = review_text.lower()
        positive_count = sum(1 for s in positive_signals if s in text_lower)
        negative_count = sum(1 for s in negative_signals if s in text_lower)

        return positive_count >= negative_count


# ─────────────────────────────────────────────────────
# Agentic Workflow
# ─────────────────────────────────────────────────────

def run_agentic_workflow(code: str, language: str, style: str) -> dict:
    """
    Run the full agentic documentation workflow:

        Code → Analysis → Generator Agent → Reviewer Agent → (Optional Improvement) → Final Output

    Args:
        code: Source code to document.
        language: Programming language.
        style: Documentation style.

    Returns:
        Dictionary with 'analysis', 'documentation', 'review', and 'mode'.
    """
    # Validate input
    if not code or not code.strip():
        return {
            "analysis": "⚠️ No code provided.",
            "documentation": "⚠️ Please paste or upload source code to generate documentation.",
            "review": "",
            "mode": "error",
        }

    # Step 1: Analyze code
    analysis = analyze_code(code, language)
    analysis_summary = format_analysis_summary(analysis)

    # Step 2: Generator Agent — first pass
    generator = DocumentationGeneratorAgent()
    documentation = generator.generate(code, language, style)

    # Step 3: Reviewer Agent
    reviewer = DocumentationReviewerAgent()
    review_result = reviewer.review(code, documentation, language)

    # Step 4: If reviewer found issues, run ONE improvement iteration
    if not review_result["is_acceptable"]:
        documentation = generator.generate(
            code, language, style,
            review_feedback=review_result["review"]
        )
        # Review again after improvement
        review_result = reviewer.review(code, documentation, language)
        review_result["review"] += "\n\n> 🔄 *Documentation was improved based on reviewer feedback (1 iteration).*"

    # Determine mode
    mode = "demo" if is_demo_mode() else "ai"

    return {
        "analysis": analysis_summary,
        "documentation": documentation,
        "review": review_result["review"],
        "mode": mode,
    }
