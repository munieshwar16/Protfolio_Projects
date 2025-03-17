from typing import Dict, Any
import os
import json
from datetime import datetime
from .base_agent import BaseAgent

class PublishingAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized publishing agent in a content creation pipeline.
        Your task is to prepare content for publication by creating appropriate metadata,
        formatting for different platforms, and generating promotion materials."""
        
        super().__init__(name="Publishing Agent", system_prompt=system_prompt)
        
        # Define publication platforms
        self.platforms = ["blog", "medium", "linkedin"]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a publishing task."""
        content_id = input_data.get("content_id")
        article_content = input_data.get("article_content", "")
        # Use edited article if available
        if "edited_article" in input_data and input_data["edited_article"]:
            article_content = input_data["edited_article"]
        
        title = "AI Technology Update"  # Default title
        # Extract title from article if possible
        if article_content.startswith("# "):
            title_line = article_content.split("\n")[0]
            title = title_line.replace("# ", "").strip()
        
        print(f"[Publishing Agent] Preparing article for publication: {title}")
        
        # Generate article metadata
        metadata_prompt = f"""
        Generate appropriate metadata for this article:
        
        TITLE: {title}
        
        ARTICLE SNIPPET:
        {article_content[:500]}...
        
        Please provide:
        1. A list of 5-7 relevant tags/keywords
        2. A short description (150 characters max)
        3. Suggested social media post (280 characters max)
        """
        
        metadata_result = self.process_with_model(metadata_prompt)
        
        # Create publication package
        publication_package = {
            "content_id": content_id,
            "title": title,
            "article_content": article_content,
            "metadata": metadata_result,
            "publication_date": datetime.now().isoformat(),
            "platforms": {}
        }
        
        # Format for different platforms
        for platform in self.platforms:
            if platform == "blog":
                publication_package["platforms"][platform] = {
                    "format": "markdown",
                    "content": article_content
                }
            elif platform == "medium":
                # Medium uses markdown but might need some adjustments
                publication_package["platforms"][platform] = {
                    "format": "markdown",
                    "content": article_content,
                    "import_url": f"https://yourdomain.com/articles/{content_id}"
                }
            elif platform == "linkedin":
                # LinkedIn typically needs a shorter format
                linkedin_prompt = f"""
                Create a shortened version of this article suitable for LinkedIn:
                
                ORIGINAL ARTICLE TITLE: {title}
                
                ORIGINAL ARTICLE:
                {article_content[:1000]}...
                
                Create a 300-500 word professional summary that highlights the key points
                while maintaining a tone appropriate for a professional network.
                """
                
                linkedin_content = self.process_with_model(linkedin_prompt)
                
                publication_package["platforms"][platform] = {
                    "format": "text",
                    "content": linkedin_content
                }
        
        # Save publication package
        publication_dir = os.path.join("data", "publications")
        os.makedirs(publication_dir, exist_ok=True)
        
        file_path = os.path.join(publication_dir, f"publication_{content_id}.json")
        with open(file_path, "w") as f:
            json.dump(publication_package, f, indent=2)
        
        # Also save as formatted files for convenience
        for platform, data in publication_package["platforms"].items():
            platform_dir = os.path.join(publication_dir, platform)
            os.makedirs(platform_dir, exist_ok=True)
            
            if platform == "linkedin":
                filename = f"{content_id}.txt"
            else:
                filename = f"{content_id}.md"
                
            with open(os.path.join(platform_dir, filename), "w") as f:
                f.write(data["content"])
        
        return {
            "content_id": content_id,
            "publication_package": publication_package,
            "files": {
                "json": file_path,
                "platforms": {p: os.path.join(publication_dir, p, f"{content_id}.{'txt' if p == 'linkedin' else 'md'}") 
                             for p in self.platforms}
            },
            "status": "published"
        }