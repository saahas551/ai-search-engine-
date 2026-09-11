 import streamlit as st
from google import genai
from tavily import TavilyClient

# Set page config
st.set_page_config(page_title="My AI Search Engine", page_icon="🔍")

# Page title
st.title("🔍 My AI Search Engine")

# Fetch API keys directly from Streamlit Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
tavily_api_key = st.secrets.get("TAVILY_API_KEY")

# Input field for search query
query = st.text_input("What would you like to search?")

if st.button("Search Web"):
    if not query:
        st.warning("Please enter a search topic.")
    elif not gemini_api_key or not tavily_api_key:
        st.error("API keys are missing from Streamlit Secrets!")
    else:
        with st.spinner("Searching the web and generating answer..."):
            try:
                # Initialize clients using stored secrets
                tavily = TavilyClient(api_key=tavily_api_key)
                search_result = tavily.search(query=query, search_depth="basic")
                
                gemini_client = genai.Client(api_key=gemini_api_key)
                
                prompt = f"""
                You are a helpful search assistant. Based on these search results:
                {search_result}
                
                Answer the user's question clearly: {query}
                """
                
                response = gemini_client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
                
                st.subheader("Answer:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")
