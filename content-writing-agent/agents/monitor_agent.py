import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random
import asyncio
import json
import os
from typing import Dict, Any, List
from .base_agent import BaseAgent

class WebMonitorAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a specialized web monitoring agent. 
        Your task is to analyze content from tech news sources and identify new AI tool releases
        and significant AI news."""
        
        super().__init__(name="Web Monitor Agent", system_prompt=system_prompt)
        
        # Sources to monitor - RSS feeds of popular AI and tech websites
        self.sources = [
            {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
            {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
            {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"}
        ]
        
        # Keep track of articles we've already processed
        self.processed_urls_file = "data/processed_urls.json"
        self.processed_urls = self._load_processed_urls()
        
    def _load_processed_urls(self):
        """Load the set of processed URLs from file."""
        if os.path.exists(self.processed_urls_file):
            try:
                with open(self.processed_urls_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"Error loading processed URLs: {e}")
        return set()
    
    def _save_processed_urls(self):
        """Save the set of processed URLs to file."""
        try:
            os.makedirs(os.path.dirname(self.processed_urls_file), exist_ok=True)
            with open(self.processed_urls_file, 'w') as f:
                json.dump(list(self.processed_urls), f)
        except Exception as e:
            print(f"Error saving processed URLs: {e}")
    
    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check sources for new AI updates."""
        new_updates = []
        
        for source in self.sources:
            try:
                print(f"Checking source: {source['name']}")
                # Parse the RSS feed
                feed = feedparser.parse(source["url"])
                
                # Get articles from the last 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for entry in feed.entries[:3]:  # Limit to 3 entries per source for testing
                    # Get publication date
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                    else:
                        # If no date, assume it's recent
                        pub_date = datetime.now()
                    
                    # Skip if we've already processed it
                    if entry.link in self.processed_urls:
                        continue
                    
                    print(f"  Found potential article: {entry.title}")
                    
                    # Get article content
                    article_content = self._fetch_article_content(entry.link)
                    
                    # Simple AI-related keyword check instead of using model
                    ai_keywords = ["ai", "artificial intelligence", "machine learning", "neural network", 
                                   "deep learning", "llm", "large language model", "chatgpt", "gpt", 
                                   "claude", "gemini", "openai", "anthropic"]
                    
                    title_lower = entry.title.lower()
                    content_lower = article_content.lower()
                    
                    # Check if any AI keywords are in the title or content
                    is_ai_related = any(keyword in title_lower or keyword in content_lower 
                                        for keyword in ai_keywords)
                    
                    if is_ai_related:
                        print(f"  ✓ Article is relevant: {entry.title}")
                        new_updates.append({
                            "title": entry.title,
                            "url": entry.link,
                            "source": source["name"],
                            "published_date": pub_date.isoformat(),
                            "content_snippet": article_content[:1000],
                            "analysis": f"This article about '{entry.title}' contains AI-related content and appears to be significant news about AI technology or applications."
                        })
                        
                        # Mark as processed
                        self.processed_urls.add(entry.link)
                    else:
                        print(f"  ✗ Article not relevant: {entry.title}")
                
                # Be nice to the servers - add a small delay between sources
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error processing source {source['name']}: {e}")
        
        # Save the updated processed URLs
        self._save_processed_urls()
        
        return new_updates
    
    def _fetch_article_content(self, url: str) -> str:
        """Fetch and extract the main content of an article."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
            
            return content
        except Exception as e:
            print(f"Error fetching article content: {e}")
            return ""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring request - usually just triggers a check."""
        command = input_data.get("command", "check")
        
        if command == "check":
            updates = await self.check_for_updates()
            return {
                "updates_found": len(updates),
                "updates": updates
            }
        
        return {"error": "Unknown command"}