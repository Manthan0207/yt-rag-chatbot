# backend/test_models.py

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings

HF_TOKEN = os.getenv("HF_TOKEN")



print("=== Testing LLM ===")

# Option 1: Use Qwen (works perfectly with text-generation)
print("Testing Qwen (recommended for streaming)...")
try:
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        max_new_tokens=100,
        temperature=0.3,
        streaming=True,
    )
    
    # Test basic invoke
    print("Basic invoke:")
    res = llm.invoke("say hello in one sentence")
    print("Response:", res)
    print("Type:", type(res))
    
    # Test streaming
    print("\nStreaming:")
    chunks = []
    for chunk in llm.stream("say hello in one sentence"):
        print("chunk:", repr(chunk))
        chunks.append(chunk)
    print("Total chunks:", len(chunks))
    
except Exception as e:
    print(f"Qwen error: {e}")

# Option 2: Mistral with conversational task (no streaming)
print("\n\nTesting Mistral with conversational task...")
try:
    llm_mistral = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        huggingfacehub_api_token=HF_TOKEN,
        task="conversational",
        max_new_tokens=100,
        temperature=0.3,
    )
    
    # Test basic invoke
    print("Basic invoke:")
    res = llm_mistral.invoke("say hello in one sentence")
    print("Response:", res)
    print("Type:", type(res))
    
    # Note: Mistral conversational task may not support streaming
    print("\nStreaming may not work with conversational task")
    
except Exception as e:
    print(f"Mistral error: {e}")

# Option 3: Phi-3 (works with text-generation and streaming)
print("\n\nTesting Phi-3...")
try:
    llm_phi = HuggingFaceEndpoint(
        repo_id="microsoft/Phi-3-mini-4k-instruct",
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        max_new_tokens=100,
        temperature=0.3,
        streaming=True,
    )
    
    print("Basic invoke:")
    res = llm_phi.invoke("say hello in one sentence")
    print("Response:", res)
    print("Type:", type(res))
    
    print("\nStreaming:")
    chunks = []
    for chunk in llm_phi.stream("say hello in one sentence"):
        print("chunk:", repr(chunk))
        chunks.append(chunk)
    print("Total chunks:", len(chunks))
    
except Exception as e:
    print(f"Phi-3 error: {e}")

print("\n=== Testing Embeddings ===")
try:
    embeddings = HuggingFaceEndpointEmbeddings(
        model="BAAI/bge-large-en-v1.5",
        huggingfacehub_api_token=HF_TOKEN,
    )
    
    vec = embeddings.embed_query("hello world")
    print("Embedding dimension:", len(vec))
    print("First 5 values:", vec[:5])
    
except Exception as e:
    print(f"Embeddings error: {e}")
    
    
    
    
    
print("\n=== Streaming Test ===")

try:
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        max_new_tokens=100,
        temperature=0.3,
        streaming=True,
    )

    print("Streaming response:")
    full_response = ""

    for i, chunk in enumerate(llm.stream("Explain recursion in one short paragraph.")):
        print(f"Chunk {i}: {repr(chunk)}")
        full_response += chunk

    print("\nFinal response:")
    print(full_response)

except Exception as e:
    print("Streaming failed!")
    print(type(e).__name__)
    print(e)