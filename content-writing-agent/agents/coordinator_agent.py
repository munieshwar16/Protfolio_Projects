import asyncio
import uuid
import os
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .monitor_agent import WebMonitorAgent
from .classification_agent import ContentClassificationAgent


class CoordinatorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a coordinator agent that manages a content creation pipeline. 
        Your job is to analyze new AI updates, assign tasks to specialized agents, and 
        ensure that high-quality content is created and published efficiently."""
        
        super().__init__(name="Coordinator Agent", system_prompt=system_prompt)
        
        # Initialize the web monitor agent
        self.monitor_agent = WebMonitorAgent()
        
        # Initialize the classification agent
        self.classification_agent = ContentClassificationAgent()
        
        # Initialize a task queue file path
        self.task_queue_file = "data/task_queue.json"
        
        # Load existing task queue if it exists
        self.task_queue = self._load_task_queue()
    
    def _load_task_queue(self):
        """Load the task queue from file."""
        if os.path.exists(self.task_queue_file):
            try:
                with open(self.task_queue_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading task queue: {e}")
        return []
    
    def _save_task_queue(self):
        """Save the task queue to file."""
        try:
            os.makedirs(os.path.dirname(self.task_queue_file), exist_ok=True)
            with open(self.task_queue_file, 'w') as f:
                json.dump(self.task_queue, f, indent=2)
        except Exception as e:
            print(f"Error saving task queue: {e}")
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check for new AI updates using the monitor agent."""
        return await self.monitor_agent.process({"command": "check"})
    
    async def create_content_plan(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Create a content plan for a specific update."""
        # Generate a unique ID for this content item
        content_id = str(uuid.uuid4())
        
        # Extract core info from the update
        title = update["title"]
        url = update["url"]
        content_snippet = update["content_snippet"]
        
        # Create a plan (simple version without using LLM)
        content_plan = f"""
        Content Plan for: {title}
        
        Headline: {title}
        
        Subtopics to cover:
        1. Overview of the announcement/development
        2. Technical details and capabilities
        3. Industry impact and significance
        4. Expert opinions and analysis
        5. Future implications
        
        Multimedia elements:
        - Feature image related to {title.split()[0:3]}
        - Infographic showing key points
        - Related technology comparison if applicable
        
        Target audience:
        - Primary: Tech professionals and AI enthusiasts
        - Secondary: Business decision-makers interested in AI implementation
        
        Key points to emphasize:
        - What makes this development unique or noteworthy
        - How it compares to existing technologies
        - Practical applications and use cases
        - Future development roadmap
        """
        
        return {
            "content_id": content_id,
            "original_update": update,
            "content_plan": content_plan,
            "status": "plan_created",
            "tasks": [
                {"task_type": "research", "status": "pending"},
                {"task_type": "outline", "status": "pending"},
                {"task_type": "write", "status": "pending"},
                {"task_type": "fact_check", "status": "pending"},
                {"task_type": "proofread", "status": "pending"},
                {"task_type": "publish", "status": "pending"}
            ]
        }
    
    async def process_new_updates(self) -> Dict[str, Any]:
        """Process any new updates and create content plans."""
        # Check for updates
        update_result = await self.check_for_updates()
        
        # If no updates, return early
        if update_result["updates_found"] == 0:
            return {"status": "no_updates", "message": "No new updates found"}
        
        # Create content plans for each update
        content_plans = []
        for update in update_result["updates"]:
            plan = await self.create_content_plan(update)
            content_plans.append(plan)
            
            # Add to task queue
            self.task_queue.append(plan)
        
        # Save the updated task queue
        self._save_task_queue()
        
        return {
            "status": "updates_processed",
            "updates_found": update_result["updates_found"],
            "content_plans": content_plans
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process coordinator commands."""
        command = input_data.get("command", "")
        
        if command == "check_updates":
            return await self.process_new_updates()
        elif command == "get_queue":
            return {"task_queue": self.task_queue}
        else:
            return {"error": f"Unknown command: {command}"}