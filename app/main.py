import uuid
import tempfile
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver

from app.graph import graph

app = FastAPI(title="Adaptive Onboarding Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

checkpointer = MemorySaver()

# -----------------------------
# Payload Builder
# (inline from your export_ui_payload logic)
# -----------------------------

REQUIRED_KEYS = ["candidate_name", "skill_gap_analysis_data", "mermaid_code", "final_roadmap"]

def build_ui_payload(state: dict) -> dict:
    ui_data = {}
    for key in REQUIRED_KEYS:
        val = state.get(key)
        if val is None:
            continue
        if hasattr(val, "model_dump"):
            ui_data[key] = val.model_dump()
        else:
            ui_data[key] = val
    return ui_data


# -----------------------------
# POST /analyze
# Accepts: resume PDF (file upload) + job description (form field)
# Returns: UI payload JSON
# -----------------------------

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Job description text"),
    candidate_name: str = Form(default="Candidate"),
):
    # 1. Save uploaded PDF to a temp file
    tmp_path = None
    try:
        suffix = Path(resume.filename).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name

        # 2. Build initial graph state
        initial_input = {
            "candidate_name": candidate_name,
            "resume_text": None,
            "job_description": job_description,
            "file_path": tmp_path,          # local temp path for PyMuPDF
            "resume_data": None,
            "extraction_error": None,
            "JobDescriptionExtract_data": None,
            "skill_gap_analysis_data": None,
            "messages": [],
            "mermaid_code": None,
            "final_roadmap": None,
        }

        # 3. Run the graph
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        final_state = graph.invoke(initial_input, config=config)

        # 4. Check for extraction errors
        if final_state.get("extraction_error"):
            raise HTTPException(
                status_code=422,
                detail=f"Extraction failed: {final_state['extraction_error']}"
            )

        # 5. Build and return UI payload
        return build_ui_payload(final_state)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 6. Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# -----------------------------
# GET /health
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "Adaptive Onboarding Engine"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)