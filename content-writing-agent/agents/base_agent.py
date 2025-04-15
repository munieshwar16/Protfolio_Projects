from typing import Dict, Any, List
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAgent:
    def __init__(self, name: str, system_prompt: str, model_name: str = "Mistral-7B-Instruct-v0.2"):
        """
        Initialize a base agent with a Hugging Face model.
        
        Args:
            name: The name of the agent
            system_prompt: Instructions for the agent
            model_name: Hugging Face model identifier
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model_name
        
        # Get API token from environment
        self.api_token = os.environ.get("HUGGINGFACE_API_KEY")
        
        if not self.api_token:
            print("WARNING: No Hugging Face API token found. Using fallback responses.")
            
    def process_with_model(self, prompt: str) -> str:
        """Process a prompt with the Hugging Face API using Llama 3."""
        if not self.api_token:
            return self._fallback_response(prompt)
            
        print(f"[{self.name}] Sending request to Hugging Face API for Llama 3")
        
        # Combine system prompt with the input prompt
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        # Prepare the API request - use Llama 3 model
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            # Make the API request
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", str(result[0]))
            return str(result)
        except Exception as e:
            print(f"[{self.name}] Error using Hugging Face API: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when the API is unavailable."""
        print(f"[{self.name}] Using fallback response method...")
        
        # Get the first 100 words of the prompt to understand the context
        prompt_preview = " ".join(prompt.split()[:100])
        
        # Simple rule-based response based on agent type
        if "research" in self.name.lower():
            return f"""
Key Facts and Findings:
- This is a fallback research response
- The topic appears to be about {prompt_preview.split()[:5]}
- Multiple sources were consulted

Background and Context:
- This technology is part of recent developments
- Several organizations are involved in this space

Expert Opinions:
- Experts generally view this development as significant
- There are differing perspectives on implementation

Statistics and Data:
- Limited quantitative data is available
- Early metrics suggest promising results

Potential Implications:
- This could affect the industry in several ways
- Users may see new capabilities in related applications
"""
        elif "writ" in self.name.lower():
            return f"""
                        # Breaking News: Important Development in AI Technology

                        ## Introduction
                        A significant development has recently emerged in the AI landscape, drawing attention from industry experts and users alike. This article explores the key aspects of this development and what it means for the future.

                        ## Key Features
                        The technology represents an important step forward in how AI systems can be implemented and utilized. While still in its early stages, the technology shows promising capabilities that could transform several industries.

                        ## Expert Analysis
                        Industry experts have weighed in on this development, with many noting its potential significance. "This could represent a shift in how we approach certain AI problems," noted one researcher familiar with the technology.

                        ## Implications
                        For users and businesses, this development may lead to more powerful and accessible AI tools. The technology's ability to handle complex tasks offers new possibilities for innovation.

                        ## Conclusion
                        As this technology continues to evolve, we'll be monitoring its progress and impact. The coming months will likely reveal more about its practical applications and long-term significance.
                        """
        else:
            return f"This is a fallback response from {self.name} regarding: {prompt_preview}..."
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return response - to be implemented by child classes."""
        raise NotImplementedError