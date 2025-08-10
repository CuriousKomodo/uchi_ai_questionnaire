import os
from typing import List, Dict, Any, Optional

from openai import AzureOpenAI
from dotenv import load_dotenv

from utils import retry


# Load environment variables
load_dotenv()

class AzureClient:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        # Model deployments
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
        
        if not all([self.endpoint, self.api_key]):
            raise ValueError("Missing required environment variables: AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key
        )

    @retry(ExceptionToCheck=Exception, tries=3, delay=30, backoff=2)
    def get_embeddings(self, texts: List[str]) -> List[list[float]]:
        """
        Get embeddings for a list of texts using Azure OpenAI.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_deployment
            )
            
            results = []
            for item in response.data:
                results.append(item.embedding)
            
            return results
            
        except Exception as e:
            print(f"Error getting embeddings: {str(e)}")
            raise

    @retry(ExceptionToCheck=Exception, tries=3, delay=30, backoff=2)
    def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get chat completion from Azure OpenAI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Controls diversity via nucleus sampling
            frequency_penalty: Reduces repetition of token sequences
            presence_penalty: Encourages model to talk about new topics
            
        Returns:
            Dictionary containing completion and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            print(f"Error getting chat completion: {str(e)}")
            raise

def main():
    # Example usage
    client = AzureClient()
    
    # Test embeddings
    print("\nTesting Embeddings:")
    print("------------------")
    texts = [
        "This is the first test phrase",
        "Here's another example text",
        "And a third one for testing"
    ]
    
    try:
        embeddings = client.get_embeddings(texts)
        for item in embeddings:
            print(item)
    except Exception as e:
        print(f"Error in embeddings test: {str(e)}")
    
    # Test chat completion
    print("\nTesting Chat Completion:")
    print("----------------------")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    try:
        chat_result = client.get_chat_completion(messages)
        print(f"\nResponse: {chat_result['content']}")
        print(f"Role: {chat_result['role']}")
        print(f"Finish reason: {chat_result['finish_reason']}")
        print("\nUsage:")
        print(f"Prompt tokens: {chat_result['usage']['prompt_tokens']}")
        print(f"Completion tokens: {chat_result['usage']['completion_tokens']}")
        print(f"Total tokens: {chat_result['usage']['total_tokens']}")
    except Exception as e:
        print(f"Error in chat completion test: {str(e)}")


if __name__ == "__main__":
    main()