import os
import json
import io
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MinioStorageService:
    """Service for storing and retrieving content and assets using MinIO."""
    
    def __init__(self):
        """Initialize the storage service with MinIO client."""
        # Get configuration from environment variables or use defaults
        self.minio_endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        self.minio_secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
        self.use_ssl = os.environ.get("MINIO_USE_SSL", "False").lower() == "true"
        
        print(f"Connecting to MinIO at {self.minio_endpoint}")
        
        # Initialize MinIO client
        self.client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=self.use_ssl
        )
        
        # Define bucket names
        self.content_bucket = "ai-content"
        self.assets_bucket = "ai-assets"
        
        # Ensure buckets exist
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist."""
        for bucket in [self.content_bucket, self.assets_bucket]:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    print(f"Created bucket: {bucket}")
                else:
                    print(f"Bucket already exists: {bucket}")
            except S3Error as e:
                print(f"Error checking/creating bucket {bucket}: {e}")
    
    def store_content_plan(self, content_id: str, content_plan: dict):
        """Store a content plan in the content bucket."""
        try:
            # Add timestamp
            if "timestamp" not in content_plan:
                content_plan["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(content_plan).encode('utf-8')
            json_stream = io.BytesIO(json_data)
            
            # Store in MinIO
            object_name = f"plans/{content_id}.json"
            self.client.put_object(
                self.content_bucket,
                object_name,
                json_stream,
                len(json_data),
                'application/json'
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing content plan: {e}")
            return False, str(e)
    
    def get_content_plan(self, content_id: str):
        """Retrieve a content plan from the content bucket."""
        try:
            object_name = f"plans/{content_id}.json"
            response = self.client.get_object(self.content_bucket, object_name)
            
            # Read and parse JSON
            content_data = response.read().decode('utf-8')
            return json.loads(content_data)
        except Exception as e:
            print(f"Error retrieving content plan: {e}")
            return None
    
    def store_article(self, content_id: str, article_data: dict):
        """Store a finished article in the content bucket."""
        try:
            # Add timestamp if not present
            if "timestamp" not in article_data:
                article_data["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(article_data).encode('utf-8')
            json_stream = io.BytesIO(json_data)
            
            # Store in MinIO
            object_name = f"articles/{content_id}.json"
            self.client.put_object(
                self.content_bucket,
                object_name,
                json_stream,
                len(json_data),
                'application/json'
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing article: {e}")
            return False, str(e)
    
    def store_markdown_article(self, content_id: str, markdown_content: str):
        """Store a markdown article in the content bucket."""
        try:
            # Convert to bytes
            content_bytes = markdown_content.encode('utf-8')
            content_stream = io.BytesIO(content_bytes)
            
            # Store in MinIO
            object_name = f"articles/{content_id}.md"
            self.client.put_object(
                self.content_bucket,
                object_name,
                content_stream,
                len(content_bytes),
                'text/markdown'
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing markdown article: {e}")
            return False, str(e)
    
    def get_article(self, content_id: str, format="json"):
        """Retrieve an article from the content bucket."""
        try:
            if format == "json":
                object_name = f"articles/{content_id}.json"
                response = self.client.get_object(self.content_bucket, object_name)
                content_data = response.read().decode('utf-8')
                return json.loads(content_data)
            else:
                object_name = f"articles/{content_id}.md"
                response = self.client.get_object(self.content_bucket, object_name)
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error retrieving article: {e}")
            return None
    
    def store_research(self, content_id: str, research_data: dict):
        """Store research results in the content bucket."""
        try:
            # Add timestamp if not present
            if "timestamp" not in research_data:
                research_data["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(research_data).encode('utf-8')
            json_stream = io.BytesIO(json_data)
            
            # Store in MinIO
            object_name = f"research/{content_id}.json"
            self.client.put_object(
                self.content_bucket,
                object_name,
                json_stream,
                len(json_data),
                'application/json'
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing research: {e}")
            return False, str(e)
    
    def get_research(self, content_id: str):
        """Retrieve research results from the content bucket."""
        try:
            object_name = f"research/{content_id}.json"
            response = self.client.get_object(self.content_bucket, object_name)
            
            # Read and parse JSON
            content_data = response.read().decode('utf-8')
            return json.loads(content_data)
        except Exception as e:
            print(f"Error retrieving research: {e}")
            return None
    
    def store_asset(self, content_id: str, asset_name: str, asset_data, content_type: str):
        """Store a multimedia asset in the assets bucket."""
        try:
            # Prepare asset data
            if isinstance(asset_data, str):
                asset_bytes = asset_data.encode('utf-8')
            elif isinstance(asset_data, bytes):
                asset_bytes = asset_data
            else:
                raise ValueError("asset_data must be string or bytes")
            
            asset_stream = io.BytesIO(asset_bytes)
            
            # Store in MinIO
            object_name = f"{content_id}/{asset_name}"
            self.client.put_object(
                self.assets_bucket,
                object_name,
                asset_stream,
                len(asset_bytes),
                content_type
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing asset: {e}")
            return False, str(e)
    
    def get_asset(self, content_id: str, asset_name: str):
        """Retrieve an asset from the assets bucket."""
        try:
            object_name = f"{content_id}/{asset_name}"
            response = self.client.get_object(self.assets_bucket, object_name)
            
            return response.read()
        except Exception as e:
            print(f"Error retrieving asset: {e}")
            return None
    
    def list_content(self):
        """List all content in the content bucket."""
        try:
            # Get all content plans
            plans = []
            for obj in self.client.list_objects(self.content_bucket, prefix="plans/"):
                content_id = obj.object_name.replace("plans/", "").replace(".json", "")
                plans.append({
                    "content_id": content_id,
                    "type": "plan",
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat()
                })
            
            # Get all articles
            articles = []
            for obj in self.client.list_objects(self.content_bucket, prefix="articles/"):
                if obj.object_name.endswith(".json"):
                    content_id = obj.object_name.replace("articles/", "").replace(".json", "")
                    articles.append({
                        "content_id": content_id,
                        "type": "article",
                        "size": obj.size,
                        "last_modified": obj.last_modified.isoformat()
                    })
            
            return {
                "plans": plans,
                "articles": articles
            }
        except Exception as e:
            print(f"Error listing content: {e}")
            return {"plans": [], "articles": []}
    
    def store_pipeline_status(self, content_id: str, status_data: dict):
        """Store pipeline status in the content bucket."""
        try:
            # Add timestamp if not present
            if "timestamp" not in status_data:
                status_data["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(status_data).encode('utf-8')
            json_stream = io.BytesIO(json_data)
            
            # Store in MinIO
            object_name = f"status/{content_id}.json"
            self.client.put_object(
                self.content_bucket,
                object_name,
                json_stream,
                len(json_data),
                'application/json'
            )
            
            return True, object_name
        except Exception as e:
            print(f"Error storing pipeline status: {e}")
            return False, str(e)
    
    def get_pipeline_status(self, content_id: str):
        """Retrieve pipeline status from the content bucket."""
        try:
            object_name = f"status/{content_id}.json"
            response = self.client.get_object(self.content_bucket, object_name)
            
            # Read and parse JSON
            content_data = response.read().decode('utf-8')
            return json.loads(content_data)
        except Exception as e:
            print(f"Error retrieving pipeline status: {e}")
            return None


