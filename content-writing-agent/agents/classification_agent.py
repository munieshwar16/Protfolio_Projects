from typing import Dict, Any, List
from .base_agent import BaseAgent

class ContentClassificationAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized content classification agent in a content creation pipeline.
        Your task is to analyze news articles and determine their type and subject matter to ensure
        appropriate content creation strategies are used."""
        
        super().__init__(name="Content Classification Agent", system_prompt=system_prompt)
        
        # Define possible content types
        self.content_types = [
            "product_launch",      # New AI product or service announcement
            "research_paper",      # Academic or scientific research about AI
            "legal_case",          # Legal news, lawsuits, regulations related to AI
            "business_news",       # Business developments, mergers, investments in AI companies
            "technical_update",    # Technical advancements or improvements in AI
            "opinion_piece",       # Commentary or analysis about AI trends
            "event_announcement",  # Conferences, webinars, competitions related to AI
            "tutorial_guide",      # How-to content or educational material about AI
            "other"                # Miscellaneous AI news
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process article data to classify its type."""
        content_id = input_data.get("content_id")
        title = input_data.get("title", "")
        content_snippet = input_data.get("content_snippet", "")
        
        print(f"[Classification Agent] Analyzing: {title}")
        
        # Prepare classification prompt
        classification_prompt = f"""
        Please analyze this news article and classify it according to its type:
        
        TITLE: {title}
        
        CONTENT SNIPPET: 
        {content_snippet[:1000]}...
        
        Classify this article into ONE of the following categories:
        - product_launch: New AI product or service announcement
        - research_paper: Academic or scientific research about AI
        - legal_case: Legal news, lawsuits, regulations related to AI
        - business_news: Business developments, mergers, investments in AI companies
        - technical_update: Technical advancements or improvements in AI
        - opinion_piece: Commentary or analysis about AI trends
        - event_announcement: Conferences, webinars, competitions related to AI
        - tutorial_guide: How-to content or educational material about AI
        - other: Miscellaneous AI news
        
        Also identify:
        1. Key entities (people, companies, technologies) mentioned
        2. Main subject matter or focus of the article
        3. Target audience
        
        Format your response as:
        CONTENT_TYPE: [one type from the list]
        KEY_ENTITIES: [comma-separated list]
        SUBJECT_MATTER: [brief description]
        TARGET_AUDIENCE: [brief description]
        REASONING: [explain your classification]
        """
        
        # Use the model to classify content
        classification_result = self.process_with_model(classification_prompt)
        print(f"Classification complete for: {title}")
        
        # Parse the classification results
        # Default values
        content_type = "other"
        key_entities = []
        subject_matter = "AI technology"
        target_audience = "AI professionals and enthusiasts"
        reasoning = ""
        
        # Extract information from the model's response
        for line in classification_result.split('\n'):
            line = line.strip()
            if line.startswith("CONTENT_TYPE:"):
                content_type = line.replace("CONTENT_TYPE:", "").strip().lower()
                # Validate against known types
                if content_type not in self.content_types:
                    content_type = "other"
            elif line.startswith("KEY_ENTITIES:"):
                entities_str = line.replace("KEY_ENTITIES:", "").strip()
                key_entities = [e.strip() for e in entities_str.split(',') if e.strip()]
            elif line.startswith("SUBJECT_MATTER:"):
                subject_matter = line.replace("SUBJECT_MATTER:", "").strip()
            elif line.startswith("TARGET_AUDIENCE:"):
                target_audience = line.replace("TARGET_AUDIENCE:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
        
        # Compile results
        result = {
            "content_id": content_id,
            "title": title,
            "content_type": content_type,
            "key_entities": key_entities,
            "subject_matter": subject_matter,
            "target_audience": target_audience,
            "reasoning": reasoning,
            "classification_result": classification_result
        }
        
        return result