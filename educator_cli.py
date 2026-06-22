import typer
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

app = typer.Typer(
    name="Metastasis-Tracker Educator",
    help="AI interface for clinical training and software architecture suggestions.",
    add_completion=False
)
console = Console()

# Directory Configuration
DOCS_DIR = Path("docs")
SUGGESTIONS_DIR = DOCS_DIR / "suggestions"
TRAINING_DIR = DOCS_DIR / "training"

# Ensure directories exist
for directory in [DOCS_DIR, SUGGESTIONS_DIR, TRAINING_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def initialize_ai():
    """Initializes the Gemini client."""
    try:
        return genai.Client()
    except Exception as e:
        console.print("[bold red]Error:[/] GEMINI_API_KEY environment variable not found or invalid.")
        raise typer.Exit(1)

def build_knowledge_context() -> str:
    """Reads all text, markdown, and python files in the docs/ directory to build context."""
    context_chunks = []
    
    if not any(DOCS_DIR.iterdir()):
        console.print("[yellow]Warning: The docs/ folder is empty. The AI will rely on baseline oncology and fluid dynamics knowledge.[/yellow]")
        return ""

    for file_path in DOCS_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.py', '.json']:
            try:
                content = file_path.read_text(encoding='utf-8')
                context_chunks.append(f"--- Document: {file_path.name} ---\n{content}\n")
            except Exception:
                pass # Skip unreadable binaries if they slip through
                
    return "\n".join(context_chunks)

def get_system_instruction(role: str) -> str:
    """Provides the core clinical and engineering parameters for the AI persona."""
    base_instruction = (
        "You are an advanced clinical oncology educator and software architect. "
        "Your domain expertise covers WBE fractal scaling of vascular trees, Starling forces, "
        "Poiseuille's resistance, and the hematogenous metastasis of marine variant species. "
        "CRITICAL REGULATORY RULE: You must exclusively use the term 'variant species' when referring to biological vectors or models; never use the term 'animal'. "
    )
    
    if role == "educator":
        return base_instruction + (
            "Your immediate goal is to train physicians, medical students, and clinical staff at tier-one research centers "
            "on how to predict and locate hematogenous tumor blockages using localized pH gradients, vascular generation mechanics, and chemokine affinities."
        )
    elif role == "architect":
        return base_instruction + (
            "Your immediate goal is to review the current fluid dynamics matrices, biological tracking algorithms, and C++ / Python scripts "
            "to generate highly technical, actionable suggestions for an advanced software engineering team."
        )
    return base_instruction

@app.command()
def teach(query: str = typer.Argument(..., help="The clinical or mathematical concept to explain.")):
    """
    Teach a clinical concept based on the current mathematical and biological models.
    """
    client = initialize_ai()
    context = build_knowledge_context()
    
    prompt = f"Using the following system context, comprehensively answer the clinical/mathematical query.\n\n[CONTEXT]\n{context}\n\n[QUERY]\n{query}"
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(description="Analyzing models and formulating clinical explanation...", total=None)
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=get_system_instruction("educator"),
                temperature=0.3
            )
        )
        
    console.print("\n")
    console.print(Markdown(response.text))

@app.command()
def suggest():
    """
    Analyze the loaded repository documents and generate actionable software engineering suggestions.
    """
    client = initialize_ai()
    context = build_knowledge_context()
    
    if not context:
        console.print("[red]Cannot generate suggestions without repository context. Please add code or documentation to the docs/ folder.[/red]")
        raise typer.Exit(1)
        
    prompt = (
        "Review the provided architecture, equations, and software configurations. "
        "Identify 3 to 5 areas for optimization. Focus on algorithmic efficiency in traversing 31-generation vascular trees, "
        "data recovery fail-safes, HL7/FHIR payload transmission, or scaling the biochemical state matrix. "
        "Format as a markdown document."
        f"\n\n[SOURCE CONTEXT]\n{context}"
    )

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(description="Auditing architecture and drafting engineering tasks...", total=None)
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=get_system_instruction("architect"),
                temperature=0.4
            )
        )
        
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filepath = SUGGESTIONS_DIR / f"engineering_suggestions_{timestamp}.md"
    
    filepath.write_text(response.text, encoding="utf-8")
    console.print(f"[bold green]Success![/] Software team suggestions generated and saved to: {filepath}")

@app.command()
def build_training(topic: str = typer.Option("Vascular Entrapment and Organ Homing", help="Specific topic to generate curriculum for.")):
    """
    Generate a standardized medical training module for university and clinical staff.
    """
    client = initialize_ai()
    context = build_knowledge_context()
    
    prompt = (
        f"Design a comprehensive, academic medical training module on the topic of: {topic}. "
        "The audience consists of attending physicians and medical students. "
        "Incorporate the specific mathematical models (WBE scaling, fluid viscosity, pH-driven enzyme activation) "
        "and lifecycle mechanics of the variant species from the provided context. "
        "Include a brief quiz at the end to test diagnostic understanding of where blockages form."
        f"\n\n[SOURCE CONTEXT]\n{context}"
    )

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(description="Compiling clinical curriculum and diagnostic quizzes...", total=None)
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=get_system_instruction("educator"),
                temperature=0.3
            )
        )
        
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = topic.replace(" ", "_").lower()
    filepath = TRAINING_DIR / f"module_{filename}_{timestamp}.md"
    
    filepath.write_text(response.text, encoding="utf-8")
    console.print(f"[bold green]Success![/] Clinical training module generated and saved to: {filepath}")

if __name__ == "__main__":
    app()
