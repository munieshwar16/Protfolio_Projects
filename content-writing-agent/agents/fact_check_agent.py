from typing import Dict, Any, List
from .base_agent import BaseAgent

class FactCheckAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized fact-checking agent in a content creation pipeline.
        Your task is to review article content against research materials, identify any inaccuracies,
        and ensure all claims are properly supported by evidence. Provide specific corrections
        and suggestions to improve factual accuracy."""
        
        super().__init__(name="Fact Check Agent", system_prompt=system_prompt, 
                         model_name="google/flan-t5-large")  # Using a larger model for better analysis
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a fact-checking task."""
        content_id = input_data.get("content_id")
        article_content = input_data.get("article_content", "")
        research_report = input_data.get("research_report", "")
        
        print(f"[Fact Check Agent] Reviewing article with ID: {content_id}")
        
        # Prepare the fact-checking prompt
        fact_check_prompt = f"""
        Please fact-check this article against the research report.
        
        ARTICLE:
        {article_content}
        
        RESEARCH REPORT:
        {research_report}
        
        Review the article for:
        1. Any factual inaccuracies or claims not supported by the research
        2. Misleading statements or exaggerations
        3. Missing important context or qualifications
        4. Incorrect attribution of opinions or statements
        
        Provide specific corrections and suggested improvements to ensure accuracy.
        Format your response as a list of findings, each with a correction or suggestion.
        """
        
        # Generate fact-checking report using the model
        fact_check_report = self.process_with_model(fact_check_prompt)
        
        # Check if there are significant issues
        if "no significant issues" in fact_check_report.lower() or "no factual inaccuracies" in fact_check_report.lower():
            status = "passed"
        else:
            status = "needs_revision"
        
        return {
            "content_id": content_id,
            "fact_check_report": fact_check_report,
            "status": status
        }