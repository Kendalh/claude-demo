#!/usr/bin/env python3
import anthropic
import os
import httpx

def read_api_key(file_path="ANTHROPIC_KEY"):
    with open(file_path, 'r') as f:
        return f.read().strip()

def simple_conversation():
    api_key = read_api_key()
    cert_path = os.path.join(os.path.dirname(__file__), "nscacert_combined.pem")
    
    # Create custom httpx client with SSL certificate and proper headers
    http_client = httpx.Client(
        verify=cert_path,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    client = anthropic.Anthropic(
        api_key=api_key,
        http_client=http_client
    )
    
    message = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Hello! Can you tell me a fun fact about Python programming?"}
        ]
    )
    
    print("User: Hello! Can you tell me a fun fact about Python programming?")
    print(f"Claude: {message.content[0].text}")

if __name__ == "__main__":
    simple_conversation()