import asyncio
import json
import os
from agents.coordinator_agent import CoordinatorAgent
from agents.classification_agent import ContentClassificationAgent
from agents.research_agent import ResearchAgent
from agents.writing_agent import WritingAgent
from agents.fact_check_agent import FactCheckAgent
from agents.proofreading_agent import ProofreadingAgent
from agents.publishing_agent import PublishingAgent

async def run_complete_pipeline():
    # Ensure data directories exist
    os.makedirs("data", exist_ok=True)
    
    print("=== Starting Complete Content Creation Pipeline ===")
    
    # Create coordinator agent
    coordinator = CoordinatorAgent()
    
    # Step 1: Check for updates
    print("\n--- Step 1: Checking for updates ---")
    update_result = await coordinator.process({"command": "check_updates", "force": True})  # Add force=True to reprocess
    
    # Save the update results
    with open("data/update_results.json", "w") as f:
        json.dump(update_result, f, indent=2)
    
    if update_result["status"] == "no_updates":
        print("No new updates found.")
        return
    
    print(f"Found {update_result['updates_found']} updates.")
    
    # For the first content plan, continue the pipeline
    if update_result["content_plans"]:
        # Get the first content plan
        content_plan = update_result["content_plans"][0]
        content_id = content_plan["content_id"]
        
        print(f"\nProcessing content ID: {content_id}")
        print(f"Title: {content_plan['original_update']['title']}")
        
        # Step 2: Content Classification
        print("\n--- Step 2: Content Classification ---")
        classification_agent = ContentClassificationAgent()
        
        classification_result = await classification_agent.process({
            "content_id": content_id,
            "title": content_plan["original_update"]["title"],
            "content_snippet": content_plan["original_update"]["content_snippet"]
        })
        
        # Save classification results
        with open(f"data/classification_{content_id}.json", "w") as f:
            json.dump(classification_result, f, indent=2)
        
        print(f"Classification completed. Content type: {classification_result['content_type']}")
        
        # Step 3: Research phase
        print("\n--- Step 3: Research phase ---")
        research_agent = ResearchAgent()
        
        research_result = await research_agent.process({
            "content_id": content_id,
            "content_plan": content_plan["content_plan"],
            "original_update": content_plan["original_update"],
            "classification": classification_result  # Pass classification to research
        })
        
        # Save research results
        with open(f"data/research_{content_id}.json", "w") as f:
            json.dump(research_result, f, indent=2)
        
        print(f"Research completed and saved.")
        
        # Step 4: Writing phase
        print("\n--- Step 4: Writing phase ---")
        writing_agent = WritingAgent()
        
        writing_result = await writing_agent.process({
            "content_id": content_id,
            "content_plan": content_plan["content_plan"],
            "research_report": research_result["research_report"],
            "classification": classification_result  # Pass classification to writing
        })
        
        # Save the written article
        with open(f"data/article_{content_id}.json", "w") as f:
            json.dump(writing_result, f, indent=2)
        
        # Also save as markdown for easy viewing
        with open(f"data/article_{content_id}.md", "w") as f:
            f.write(writing_result["article_content"])
        
        print(f"Article written and saved.")
        
        # Continue with rest of pipeline (fact-checking, proofreading, publishing)
        # ... (rest of the function remains the same)

if __name__ == "__main__":
    asyncio.run(run_complete_pipeline())    