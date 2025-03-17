from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import os

# Import your agents
from agents.coordinator_agent import CoordinatorAgent
from agents.classification_agent import ContentClassificationAgent
from agents.research_agent import ResearchAgent
from agents.writing_agent import WritingAgent
from agents.fact_check_agent import FactCheckAgent
from agents.proofreading_agent import ProofreadingAgent
from agents.publishing_agent import PublishingAgent
from services.minio_storage_service import MinioStorageService

# Create FastAPI app
app = FastAPI(title="AI Content Creation Pipeline")

# Setup static files and templates
templates = Jinja2Templates(directory="templates")

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize the coordinator
coordinator = CoordinatorAgent()

# Define request and response models
class CheckUpdatesRequest(BaseModel):
    force: bool = False

class ContentRequest(BaseModel):
    content_id: str
    
class PipelineStatusResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Background task to run the full content pipeline
async def run_content_pipeline(content_id: str):
    try:
        # Get the content plan
        with open(f"data/content_plans/{content_id}.json", "r") as f:
            content_plan = json.load(f)
        
        # Step 1: Classification
        classification_agent = ContentClassificationAgent()
        classification_result = await classification_agent.process({
            "content_id": content_id,
            "title": content_plan["original_update"]["title"],
            "content_snippet": content_plan["original_update"]["content_snippet"]
        })
        
        # Save classification results
        with open(f"data/classification_{content_id}.json", "w") as f:
            json.dump(classification_result, f, indent=2)
        
        # Step 2: Research
        research_agent = ResearchAgent()
        research_result = await research_agent.process({
            "content_id": content_id,
            "content_plan": content_plan["content_plan"],
            "original_update": content_plan["original_update"],
            "classification": classification_result
        })
        
        # Save research results
        with open(f"data/research_{content_id}.json", "w") as f:
            json.dump(research_result, f, indent=2)
        
        # Step 3: Writing
        writing_agent = WritingAgent()
        writing_result = await writing_agent.process({
            "content_id": content_id,
            "content_plan": content_plan["content_plan"],
            "research_report": research_result["research_report"],
            "classification": classification_result
        })
        
        # Save writing results
        with open(f"data/article_{content_id}.json", "w") as f:
            json.dump(writing_result, f, indent=2)
        
        # Save as markdown for easy viewing
        with open(f"data/article_{content_id}.md", "w") as f:
            f.write(writing_result["article_content"])
        
        # Step 4: Fact Checking
        fact_check_agent = FactCheckAgent()
        fact_check_result = await fact_check_agent.process({
            "content_id": content_id,
            "article_content": writing_result["article_content"],
            "research_report": research_result["research_report"]
        })
        
        # Save fact check results
        with open(f"data/fact_check_{content_id}.json", "w") as f:
            json.dump(fact_check_result, f, indent=2)
        
        # Step 5: Proofreading
        proofreading_agent = ProofreadingAgent()
        proofreading_result = await proofreading_agent.process({
            "content_id": content_id,
            "article_content": writing_result["article_content"]
        })
        
        # Save proofreading results
        with open(f"data/proofread_{content_id}.json", "w") as f:
            json.dump(proofreading_result, f, indent=2)
        
        # Save edited article
        with open(f"data/edited_article_{content_id}.md", "w") as f:
            f.write(proofreading_result["edited_article"])
        
        # Step 6: Publishing
        publishing_agent = PublishingAgent()
        publishing_result = await publishing_agent.process({
            "content_id": content_id,
            "article_content": proofreading_result["edited_article"]
        })
        
        # Save publishing results
        with open(f"data/publishing_{content_id}.json", "w") as f:
            json.dump(publishing_result, f, indent=2)
        
        # Update pipeline status
        with open(f"data/status_{content_id}.json", "w") as f:
            status = {
                "content_id": content_id,
                "status": "completed",
                "stages": {
                    "classification": "completed",
                    "research": "completed",
                    "writing": "completed",
                    "fact_check": "completed",
                    "proofreading": "completed",
                    "publishing": "completed"
                }
            }
            json.dump(status, f, indent=2)
        
    except Exception as e:
        # On error, save the error status
        with open(f"data/status_{content_id}.json", "w") as f:
            status = {
                "content_id": content_id,
                "status": "error",
                "error": str(e)
            }
            json.dump(status, f, indent=2)
        
        print(f"Error in content pipeline for {content_id}: {e}")

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check-updates", response_model=PipelineStatusResponse)
async def check_updates(request: CheckUpdatesRequest):
    try:
        # Create content plans directory if it doesn't exist
        os.makedirs("data/content_plans", exist_ok=True)
        
        # Check for updates
        result = await coordinator.process({"command": "check_updates", "force": request.force})
        
        if result["status"] == "no_updates":
            return PipelineStatusResponse(
                status="success",
                message="No new updates found",
                details={"updates_found": 0}
            )
        
        # Save content plans
        for plan in result["content_plans"]:
            with open(f"data/content_plans/{plan['content_id']}.json", "w") as f:
                json.dump(plan, f, indent=2)
        
        return PipelineStatusResponse(
            status="success",
            message=f"Found {result['updates_found']} updates",
            details={
                "updates_found": result["updates_found"],
                "content_ids": [plan["content_id"] for plan in result["content_plans"]]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-content/{content_id}", response_model=PipelineStatusResponse)
async def process_content(content_id: str, background_tasks: BackgroundTasks):
    try:
        # Check if content plan exists
        if not os.path.exists(f"data/content_plans/{content_id}.json"):
            raise HTTPException(status_code=404, detail=f"Content ID {content_id} not found")
        
        # Create status file
        with open(f"data/status_{content_id}.json", "w") as f:
            status = {
                "content_id": content_id,
                "status": "processing",
                "stages": {
                    "classification": "pending",
                    "research": "pending",
                    "writing": "pending",
                    "fact_check": "pending",
                    "proofreading": "pending",
                    "publishing": "pending"
                }
            }
            json.dump(status, f, indent=2)
        
        # Start processing in background
        background_tasks.add_task(run_content_pipeline, content_id)
        
        return PipelineStatusResponse(
            status="processing",
            message=f"Started content pipeline for ID: {content_id}",
            details={"content_id": content_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{content_id}", response_model=PipelineStatusResponse)
async def get_status(content_id: str):
    try:
        # Check if status file exists
        if not os.path.exists(f"data/status_{content_id}.json"):
            return PipelineStatusResponse(
                status="unknown",
                message=f"No status information for content ID: {content_id}",
                details={"content_id": content_id}
            )
        
        # Read status file
        with open(f"data/status_{content_id}.json", "r") as f:
            status = json.load(f)
        
        return PipelineStatusResponse(
            status=status["status"],
            message=f"Pipeline status for content ID: {content_id}",
            details=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content/{content_id}", response_class=HTMLResponse)
async def view_content(request: Request, content_id: str):
    try:
        # Check if the article exists
        article_path = f"data/edited_article_{content_id}.md"
        if not os.path.exists(article_path):
            article_path = f"data/article_{content_id}.md"
            if not os.path.exists(article_path):
                raise HTTPException(status_code=404, detail=f"No article found for content ID: {content_id}")
        
        # Read the article
        with open(article_path, "r") as f:
            article_content = f.read()
        
        # Get status
        status = {"status": "unknown"}
        if os.path.exists(f"data/status_{content_id}.json"):
            with open(f"data/status_{content_id}.json", "r") as f:
                status = json.load(f)
        
        # Get content plan
        content_plan = {}
        if os.path.exists(f"data/content_plans/{content_id}.json"):
            with open(f"data/content_plans/{content_id}.json", "r") as f:
                content_plan = json.load(f)
        
        return templates.TemplateResponse(
            "view_article.html", 
            {
                "request": request, 
                "content_id": content_id,
                "article_content": article_content,
                "status": status,
                "content_plan": content_plan
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-content")
async def list_content():
    try:
        # Get all content plans
        content_plans = []
        if os.path.exists("data/content_plans"):
            for filename in os.listdir("data/content_plans"):
                if filename.endswith(".json"):
                    content_id = filename.replace(".json", "")
                    
                    # Get plan info
                    with open(f"data/content_plans/{filename}", "r") as f:
                        plan = json.load(f)
                    
                    # Get status info
                    status = {"status": "unknown"}
                    if os.path.exists(f"data/status_{content_id}.json"):
                        with open(f"data/status_{content_id}.json", "r") as f:
                            status = json.load(f)
                    
                    content_plans.append({
                        "content_id": content_id,
                        "title": plan["original_update"]["title"],
                        "status": status["status"],
                        "created": plan.get("timestamp", "unknown")
                    })
        
        return {"content_plans": content_plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
import os

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/content_plans", exist_ok=True)
os.makedirs("data/research", exist_ok=True)
os.makedirs("data/articles", exist_ok=True)
os.makedirs("data/status", exist_ok=True) 