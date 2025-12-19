"""
Test script for text input functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_text_input():
    """Test the text input endpoint"""
    print("Testing text input functionality...\n")
    
    test_cases = [
        {
            "name": "Probability Problem",
            "text": "What is the probability of rolling a 6 on a fair die?",
            "problem_type": None
        },
        {
            "name": "Probability with Type",
            "text": "A coin is flipped 3 times. What is the probability of getting exactly 2 heads?",
            "problem_type": "probability"
        },
        {
            "name": "Equation Input",
            "text": "Solve the equation: x^2 + 5x + 6 = 0",
            "problem_type": "algebra"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing: {test_case['name']}")
        print(f"   Input: {test_case['text'][:60]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/solve-text",
                json={
                    "text": test_case["text"],
                    "problem_type": test_case["problem_type"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] Status: {response.status_code}")
                print(f"   [OK] Problem Type: {data.get('problem_type', 'N/A')}")
                print(f"   [OK] Has Explanation: {'explanation' in data}")
                print(f"   [OK] Has Steps: {'steps' in data}")
                print(f"   [OK] Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"   [ERROR] Status: {response.status_code}")
                print(f"   [ERROR] Response: {response.text}")
        except Exception as e:
            print(f"   [ERROR] {str(e)}")
        
        print()

if __name__ == "__main__":
    test_text_input()

