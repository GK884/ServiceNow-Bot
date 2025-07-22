import streamlit as st
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")

# UI
st.title("ServiceNow GPT Agent 🔧")
query = st.text_input("Ask your question related to ServiceNow...")

if st.button("Search"):
    if not query:
        st.warning("Please enter a question.")
    else:
        st.info("🔍 Searching on Google...")

        # 1. GOOGLE SEARCH USING SERPER
        search_url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": SERPER_API_KEY}
        payload = {"q": query}
        response = requests.post(search_url, json=payload, headers=headers)
        results = response.json()

        top_links = [result["link"] for result in results.get("organic", [])][:3]

        scraped_texts = []
        for link in top_links:
            # 2. SCRAPE USING BROWSERLESS
            st.info(f"Scraping {link}")
            scrape_response = requests.post(
                "https://chrome.browserless.io/content",
                params={"token": BROWSERLESS_API_KEY},
                json={"url": link}
            )
            if scrape_response.status_code == 200:
                scraped_texts.append(scrape_response.json().get("data", ""))
            else:
                scraped_texts.append("Failed to scrape.")

        full_text = "\n\n".join(scraped_texts)

        # 3. ASK OPENAI TO SUMMARIZE
        st.info("🤖 Summarizing with GPT...")
        openai_response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": "You are a helpful ServiceNow expert."},
        {"role": "user", "content": f"Summarize this content and answer the question: {query}\n\n{full_text}"}
    ]
)

        answer = openai_response.choices[0].message.content
        st.success("✅ Answer:")
        st.write(answer)
 
