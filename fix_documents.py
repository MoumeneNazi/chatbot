#!/usr/bin/env python3
import requests
import sys
import os
import json

def fix_document_paths(base_url, token):
    """Call the API to fix document paths"""
    url = f"{base_url}/api/therapist/fix-document-paths"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"Success: {result['message']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            try:
                detail = e.response.json().get('detail', 'No detail provided')
                print(f"Detail: {detail}")
            except:
                print(f"Response text: {e.response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_documents.py <base_url> <auth_token>")
        print("Example: python fix_documents.py http://localhost:8000 eyJhbGciOiJIUzI1NiIs...")
        sys.exit(1)
    
    base_url = sys.argv[1]
    token = sys.argv[2]
    
    success = fix_document_paths(base_url, token)
    sys.exit(0 if success else 1) 