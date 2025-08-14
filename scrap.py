from bs4 import BeautifulSoup
import requests
from google import genai
from google.genai import types

link = input()

url = f"{link}"
page_response = requests.get(url)

soup = BeautifulSoup(page_response.text, "html.parser")
page_text = soup.get_text()

#Sending the file to the google gemini api

client = genai.Client(api_key="AIzaSyBG0i4nXf09Yu-e9eEs2mMX1ilwf5gdBsM")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="Act as a risk analyst for a small " \
        "business owner. Analyze the following Terms and " \
        "Conditions text. First, provide a summary in 10 " \
        "brief and concise bullet points. Second, and most importantly, " \
        "identify the potential risks from clauses related to " \
        "these four specific risk categories: 1. Data Privacy "
        "and Usage Rights. 2. User Content Ownership and IP. " \
        "3. Account Suspension and Termination Conditions. " \
        "4. Subscription Renewals and Price Changes in a very brief bullet points. If a " \
        "category is not mentioned, state 'No specific clauses " \
        "found.' Present the output clearly, with the summary " \
        "first, followed by the four risk categories."),
    contents=page_text
)
print(response.text)