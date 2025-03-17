from typing import Dict, Any
from .base_agent import BaseAgent

class WritingAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized writing agent in a content creation pipeline.
        Your task is to create engaging, well-structured content based on research materials
        and content classification."""
        
        super().__init__(name="Writing Agent", system_prompt=system_prompt)
    
    def get_template_for_content_type(self, content_type: str) -> str:
        """Return a prompt template appropriate for the content type."""
        templates = {
            "product_launch": """
            Write an article about a new AI product or service launch with these sections:
            1. Introduction to the new product/service
            2. Key features and capabilities
            3. How it compares to existing solutions
            4. Target markets and use cases
            5. Expert opinions on its potential impact
            6. Availability and pricing details (if available)
            7. Conclusion with future outlook
            """,
            
            "research_paper": """
            Write an article summarizing AI research findings with these sections:
            1. Overview of the research and its significance
            2. Key findings and methodology
            3. Technical innovations presented
            4. Potential applications of the research
            5. Expert perspectives on the research
            6. Limitations and future work
            7. Conclusion on the research's impact on the field
            """,
            
            "legal_case": """
            Write an article about a legal development in AI with these sections:
            1. Summary of the legal case or development
            2. Background on the parties involved
            3. Key legal issues or questions at stake
            4. Potential precedents or implications for AI
            5. Expert legal opinions
            6. Timeline of next steps in the case
            7. Broader impact on AI regulation and industry
            """,
            
            "business_news": """
            Write an article about a business development in AI with these sections:
            1. Overview of the business announcement
            2. Key details about the companies involved
            3. Financial or strategic implications
            4. Market analysis and competitive context
            5. Expert opinions on the business move
            6. Future outlook for the companies involved
            7. Broader impact on the AI industry
            """,
            
            "technical_update": """
            Write an article about a technical advancement in AI with these sections:
            1. Introduction to the technical update or improvement
            2. Technical details and advancements
            3. Performance improvements or new capabilities
            4. Development process and challenges overcome
            5. Potential applications and use cases
            6. Expert technical perspectives
            7. Future development roadmap
            """,
            
            "opinion_piece": """
            Write an analytical article about AI trends with these sections:
            1. Introduction to the key opinion or analysis
            2. Context and background of the topic
            3. Main arguments or insights
            4. Supporting evidence or examples
            5. Counter-perspectives or considerations
            6. Implications for stakeholders
            7. Conclusion with forward-looking thoughts
            """,
            
            "event_announcement": """
            Write an article about an AI-related event with these sections:
            1. Introduction to the event and its significance
            2. Key details (time, location, format)
            3. Notable speakers or participants
            4. Main themes or topics to be covered
            5. Target audience and benefits of attending
            6. How to participate or register
            7. Context of the event within the broader AI landscape
            """,
            
            "tutorial_guide": """
            Write an informative article about using AI with these sections:
            1. Introduction to the AI technique or tool
            2. Why this approach is useful or important
            3. Step-by-step guidance or explanation
            4. Best practices and recommendations
            5. Common challenges and solutions
            6. Examples or use cases
            7. Resources for further learning
            """
        }
        
        # Return the appropriate template or a default one if type not found
        return templates.get(content_type, """
        Write an informative article about this AI-related topic with these sections:
        1. Introduction to the topic
        2. Key information and details
        3. Context and significance
        4. Relevant stakeholders and perspectives
        5. Implications and impact
        6. Future outlook
        7. Conclusion
        """)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a writing task."""
        content_id = input_data.get("content_id")
        content_plan = input_data.get("content_plan", {})
        research_report = input_data.get("research_report", "")
        classification = input_data.get("classification", {})
        
        # Extract content type and other classification info
        content_type = "other"
        key_entities = []
        subject_matter = ""
        target_audience = ""
        
        if classification:
            content_type = classification.get("content_type", "other")
            key_entities = classification.get("key_entities", [])
            subject_matter = classification.get("subject_matter", "")
            target_audience = classification.get("target_audience", "")
        
        print(f"[Writing Agent] Creating {content_type} article with ID: {content_id}")
        
        # Get the appropriate template for this content type
        template = self.get_template_for_content_type(content_type)
        
        # Prepare writing prompt
        writing_prompt = f"""
        Write an engaging article based on this research and classification:
        
        CONTENT TYPE: {content_type}
        
        SUBJECT MATTER: {subject_matter}
        
        KEY ENTITIES: {', '.join(key_entities)}
        
        TARGET AUDIENCE: {target_audience}
        
        CONTENT PLAN:
        {content_plan}
        
        RESEARCH REPORT:
        {research_report}
        
        ARTICLE STRUCTURE:
        {template}
        
        Create a well-structured article that:
        1. Has an appropriate headline for this type of content
        2. Accurately represents the subject matter and entities involved
        3. Uses language and style appropriate for the target audience
        4. Follows the structure provided for this content type
        5. Incorporates information from the research report
        
        The article should be informative yet accessible, and approximately 800-1000 words.
        
        IMPORTANT: Start your response with the title preceded by "# " for markdown formatting.
        """
        
        # Generate article using the model
        full_response = self.process_with_model(writing_prompt)
        
        # Clean up the article content
        article_content = full_response
        
        # Remove prompt remnants if they appear in the output
        prompt_markers = [
            "Here's an engaging article based on the research",
            "I'll create an engaging article",
            "CONTENT TYPE:",
            "SUBJECT MATTER:",
            "KEY ENTITIES:"
        ]
        
        # Check if any prompt markers are at the beginning of the response
        for marker in prompt_markers:
            if article_content.startswith(marker):
                # Find where the actual article content starts
                header_index = article_content.find("#")
                if header_index > 0:
                    article_content = article_content[header_index:]
                break
        
        # Ensure article starts with a heading
        if not article_content.startswith("#"):
            # Try to extract title from content
            if "Title:" in article_content:
                title = article_content.split("Title:")[1].split("\n")[0].strip()
                article_content = f"# {title}\n\n" + article_content
        
        return {
            "content_id": content_id,
            "article_content": article_content,
            "content_type": content_type,
            "status": "completed"
        }