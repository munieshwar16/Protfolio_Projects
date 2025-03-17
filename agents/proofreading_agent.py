from typing import Dict, Any
from .base_agent import BaseAgent

class ProofreadingAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized proofreading agent in a content creation pipeline.
        Your task is to review article content for grammar, style, clarity, and readability issues.
        Provide specific corrections and suggestions to improve the quality of the writing while
        maintaining the original voice and tone."""
        
        super().__init__(name="Proofreading Agent", system_prompt=system_prompt,
                         model_name="google/flan-t5-large")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a proofreading task."""
        content_id = input_data.get("content_id")
        article_content = input_data.get("article_content", "")
        
        print(f"[Proofreading Agent] Reviewing article with ID: {content_id}")
        
        # Prepare the proofreading prompt
        proofreading_prompt = f"""
        Please proofread and edit this article for grammar, style, clarity, and readability:
        
        ARTICLE:
        {article_content}
        
        Review for:
        1. Grammar and spelling errors
        2. Awkward or unclear phrasing
        3. Consistency in tone and style
        4. Appropriate transitions between sections
        5. Overall readability and flow
        
        Provide specific corrections and suggested improvements.
        Format your response with an EDITED ARTICLE section containing the improved text,
        followed by an EDITING NOTES section with explanations of major changes.
        """
        
        # Generate proofreading results using the model
        proofreading_results = self.process_with_model(proofreading_prompt)
        
        # Extract edited article if possible
        edited_article = article_content  # Default to original
        editing_notes = proofreading_results
        
        # Try to extract edited article and notes if the format matches expectations
        if "EDITED ARTICLE" in proofreading_results:
            parts = proofreading_results.split("EDITING NOTES")
            if len(parts) > 1:
                edited_article = parts[0].replace("EDITED ARTICLE", "").strip()
                editing_notes = "EDITING NOTES" + parts[1]
        
        return {
            "content_id": content_id,
            "original_article": article_content,
            "edited_article": edited_article,
            "editing_notes": editing_notes,
            "status": "completed"
        }