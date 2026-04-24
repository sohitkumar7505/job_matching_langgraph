import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import sys

load_dotenv()

def get_groq_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment. Please add it to your .env file.")
    return ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0.1
    )

# Global LLM instance for reuse
llm = get_groq_llm()

def stream_llm_response(prompt, show_prefix=None):
    """Stream LLM response with real-time output.
    
    Args:
        prompt: The prompt to send to LLM
        show_prefix: Optional prefix to show before streaming (e.g., "🤖 AI: ")
        
    Returns:
        Full response content as string
    """
    if show_prefix:
        print(show_prefix, end="", flush=True)
    
    full_response = ""
    
    # Stream the response
    for chunk in llm.stream([HumanMessage(content=prompt)]):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
    
    print()  # New line after streaming
    return full_response

def get_llm_response(prompt):
    """Get LLM response without streaming (for structured data like JSON)."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()