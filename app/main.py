import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.utils.ui_payload_constructor import UIPayload
from app.graph import graph
from app.utils.cloudinary_utils import get_resume_url
 
 
app = FastAPI(title="Adaptive Onboarding Engine")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
@app.post("/analyze")
async def analyze(
    user_id: str = Form(..., description="User ID — used to fetch resume from Cloudinary"),
    job_description: str = Form(..., description="Job description text"),
):
    # 1. Fetch PDF URL from Cloudinary using user_id
    try:
        pdf_url = get_resume_url(user_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
 
    # 2. Build graph state
    initial_input = {
        "candidate_name": None,
        "resume_text": None,
        "file_path": pdf_url,
        "job_description": job_description,
        "resume_data": None,
        "extraction_error": None,
        "JobDescriptionExtract_data": None,
        "skill_gap_analysis_data": None,
        "messages": [],
        "mermaid_code": None,
        "final_roadmap": None,
    }
 
    # 3. Run graph — use user_id as thread_id for checkpointer
    config = {"configurable": {"thread_id": user_id}}
 
    try:
        final_state = graph.invoke(initial_input, config=config)
 
        if final_state.get("extraction_error"):
            raise HTTPException(
                status_code=422,
                detail=f"Extraction failed: {final_state['extraction_error']}"
            )
 
        payload = UIPayload.from_state(final_state)
        return payload.to_dict()
 
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.get("/health")
def health():
    return {"status": "ok", "service": "Adaptive Onboarding Engine"}
 
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)