from bs4 import BeautifulSoup
import requests

link = input()

url = f"{link}"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
page_text = soup.get_text()

with open("tnc.txt", "w") as file:
    file.write(page_text)