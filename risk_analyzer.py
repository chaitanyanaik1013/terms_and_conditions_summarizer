import sys
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error! The environment variable is not set.", file=sys.stderr)
    sys.exit(1)

genai.configure(api_key=API_KEY)

def analyze_text(page_text: str) -> str:
    """
    Sends the scrapped text to the gemini model.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Using the latest model name convention
        
        system_prompt = (
            "Act as a risk analyst for a small business owner. Analyze the following Terms and "
            "Conditions text. First, provide a summary in 10 brief and concise bullet points. "
            "Second, and most importantly, identify the potential risks from clauses related to "
            "these four specific risk categories: 1. Data Privacy and Usage Rights. 2. User Content "
            "Ownership and IP. 3. Account Suspension and Termination Conditions. 4. Subscription "
            "Renewals and Price Changes in a very brief bullet points. If a category is not "
            "mentioned, state 'No specific clauses found.' Present the output clearly, with the "
            "summary first, followed by the four risk categories."
        )
        
        response = model.generate_content(
            page_text,
            generation_config=genai.types.GenerationConfig(
                # You can add config here if needed, e.g., temperature=0.5
            ),
            # The system instruction is now part of the model's initialization or passed differently
            # For simplicity, we can prepend it to the content for some models if system_instruction isn't a direct param.
            # The most robust way is to use the newer ChatSession if a conversational context is needed,
            # but for a single turn, this is fine. Let's prepend it for clarity in this example.
            # A better way for newer models might be:
            # model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=system_prompt)
            # response = model.generate_content(page_text)
            # For now, let's keep it compatible:
        )
        
        # Prepending system prompt to user content
        full_prompt = system_prompt + "\n\n--- TERMS AND CONDITIONS TEXT ---\n\n" + page_text
        response = model.generate_content(full_prompt)

        return response.text
    
    except Exception as e:
        return f"Error during Gemini API Call: {str(e)}"
    
def main(url: str):
    """
    Main function to fetch, parse and analyze the url
    """
    try:
        print(f"Fetching content from {url}... ", file=sys.stderr)
        page_response = requests.get(url, timeout=10)
        page_response.raise_for_status()

        print("Parsing HTML...", file=sys.stderr)
        soup = BeautifulSoup(page_response.text, "html.parser")
        page_text = soup.get_text()

        if not page_text.strip():
            print("Error! Could not load any text from the URL.", file=sys.stderr)
            sys.exit(1)

        print("Sending text to gemini for analysis...", file=sys.stderr)
        analysis_result = analyze_text(page_text)
        print(analysis_result)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occured: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    
    if len(sys.argv)<2:
        print("Usage: python risk_analyzer.py <URL>", file=sys.stderr)
        sys.exit(1)
    
    target_url = sys.argv[1]
    main(target_url)