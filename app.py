"""
Intelligent Code Documentation Generator
Main Gradio Application
"""

import gradio as gr
import tempfile
import os
from agents import run_agentic_workflow
from llm_client import is_demo_mode


# ─────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────

def read_uploaded_file(file) -> str:
    """Read content from an uploaded file."""
    if file is None:
        return ""
    try:
        # Gradio 6 gives the file path as a string
        filepath = file if isinstance(file, str) else file.name
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"


def save_documentation(documentation: str) -> str:
    """Save documentation to a temporary .md file for download."""
    if not documentation or documentation.startswith("⚠️"):
        return None
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="documentation_",
        delete=False, encoding="utf-8"
    )
    tmp.write(documentation)
    tmp.close()
    return tmp.name


def generate_docs(code_text, uploaded_file, language, style):
    """
    Main handler: process input and run the agentic workflow.
    """
    # Get code from textbox or uploaded file
    code = code_text.strip() if code_text else ""

    if uploaded_file is not None and not code:
        code = read_uploaded_file(uploaded_file)

    if not code:
        return (
            "⚠️ Please paste code or upload a file.",
            "⚠️ No code provided.",
            "",
            None,
        )

    # Run the agentic workflow
    result = run_agentic_workflow(code, language, style)

    # Prepare download file
    download_path = save_documentation(result["documentation"])

    # Mode banner
    mode_banner = ""
    if result["mode"] == "demo":
        mode_banner = "\n\n> ⚠️ **Demo Mode** — No AI API key configured. Output is simulated.\n"

    return (
        result["analysis"] + mode_banner,
        result["documentation"],
        result["review"],
        download_path,
    )


# ─────────────────────────────────────────────────────
# Gradio Interface
# ─────────────────────────────────────────────────────

def create_app():
    """Build and return the Gradio app."""

    mode_text = "🟡 Demo Mode (no API key)" if is_demo_mode() else "🟢 AI Mode (API key loaded)"

    with gr.Blocks() as app:

        # ── Header ──
        gr.Markdown(
            f"""
            <div style="text-align:center; padding:20px 0 10px 0;">
                <h1 style="font-size:2em; margin-bottom:5px;">🤖 Intelligent Code Documentation Generator</h1>
                <p style="font-size:1.1em; color:#666;">
                    Generate clear technical documentation from source code using AI agents.
                </p>
                <p>
                    <span style="display:inline-block; padding:4px 14px; border-radius:20px; font-size:0.9em; font-weight:600;
                    {'background:#fff3cd; color:#856404;' if is_demo_mode() else 'background:#d4edda; color:#155724;'}">
                    {mode_text}</span>
                </p>
            </div>
            """
        )

        with gr.Row():
            # ── Left Column: Input ──
            with gr.Column(scale=1):
                gr.Markdown("### 📥 Input")

                code_input = gr.Textbox(
                    label="Paste Source Code",
                    placeholder="Paste your code here...",
                    lines=15,
                    max_lines=40,
                )

                file_input = gr.File(
                    label="Or Upload a Source Code File",
                    file_types=[".py", ".java", ".cpp", ".c", ".js", ".ts", ".h", ".hpp", ".txt"],
                )

                with gr.Row():
                    lang_dropdown = gr.Dropdown(
                        choices=["Auto Detect", "Python", "Java", "C++", "JavaScript"],
                        value="Auto Detect",
                        label="Programming Language",
                    )
                    style_dropdown = gr.Dropdown(
                        choices=["Markdown", "Google Style", "Javadoc", "JSDoc"],
                        value="Markdown",
                        label="Documentation Style",
                    )

                generate_btn = gr.Button(
                    "🚀 Generate Documentation",
                    variant="primary",
                    size="lg",
                )

                gr.Markdown(
                    """
                    ---
                    #### 🔄 Agentic Workflow
                    ```
                    User Code
                      ↓
                    Code Analysis
                      ↓
                    📝 Generator Agent
                      ↓
                    🔍 Reviewer Agent
                      ↓
                    ✅ Final Documentation
                    ```
                    """
                )

            # ── Right Column: Output ──
            with gr.Column(scale=2):
                gr.Markdown("### 📤 Output")

                with gr.Accordion("📊 Code Analysis", open=True):
                    analysis_output = gr.Markdown(
                        value="*Code analysis will appear here after generation.*"
                    )

                with gr.Accordion("📄 Generated Documentation", open=True):
                    docs_output = gr.Markdown(
                        value="*Generated documentation will appear here.*"
                    )

                with gr.Accordion("🤖 AI Review", open=True):
                    review_output = gr.Markdown(
                        value="*Reviewer feedback will appear here.*"
                    )

                with gr.Accordion("⬇️ Download", open=True):
                    download_output = gr.File(
                        label="Download Documentation (.md)",
                    )

        # ── Wire up the button ──
        generate_btn.click(
            fn=generate_docs,
            inputs=[code_input, file_input, lang_dropdown, style_dropdown],
            outputs=[analysis_output, docs_output, review_output, download_output],
        )

    return app


# ─────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        css="footer { display: none !important; } .settings-button { display: none !important; }"
    )
