import random
import streamlit as st
from google import genai
from tavily import TavilyClient

# Set page config
st.set_page_config(page_title="Orbit Ai", page_icon="🔍")

# Dynamic, friendly greetings list
greetings = [
    "Hey there! 👋 How was your day today?",
    "Welcome back! 😊 How are you doing today?",
    "Hello! 🌟 Hope you're having an awesome day! What are we exploring?",
    "Hey! 👋 Ready to discover something new today?"
]

# Randomly select a greeting on refresh
if "selected_greeting" not in st.session_state:
    st.session_state.selected_greeting = random.choice(greetings)

st.title("🔍 Orbit Ai")
st.markdown(f"### {st.session_state.selected_greeting}")

# Fetch API keys directly from Streamlit Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
tavily_api_key = st.secrets.get("TAVILY_API_KEY")

# Interactive suggestion chips
st.write("💡 **Popular topics to search:**")
col1, col2 = st.columns(2)

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

def set_query(text):
    st.session_state.search_query = text

with col1:
    if st.button("🚀 Latest tech & AI news"):
        set_query("Latest tech & AI news")
with col2:
    if st.button("🎬 Trending movies & shows"):
        set_query("Trending movies & shows")

# Search form (triggers on Enter key or button click)
with st.form(key="search_form"):
    query = st.text_input(
        "Ask anything or search the web:", 
        value=st.session_state.search_query
    )
    submit_button = st.form_submit_button("Search Web")

if submit_button and query:
    if not gemini_api_key or not tavily_api_key:
        st.error("API keys are missing from Streamlit Secrets!")
    else:
        with st.spinner("Searching the web..."):
            try:
                # 1. Fast web search limited to 3 top results
                tavily = TavilyClient(api_key=tavily_api_key)
                search_result = tavily.search(query=query, search_depth="fast", max_results=3)
                
                # 2. Gemini client setup with custom persona
                gemini_client = genai.Client(api_key=gemini_api_key)
                
                prompt = f"""
                You are Nova Search, a friendly and intelligent AI search assistant created by Saahas.
                
                CRITICAL INSTRUCTION: If the user asks who created you, who made you, or who built this app, you MUST respond clearly that you were created and built by Saahas.
                
                Based on these web search results:
                {search_result}
                
                Answer the user's question clearly, warmly, and concisely: {query}
                """
                
                st.subheader("Answer:")
                
                # Stream the response word-by-word for maximum speed
                def stream_response():
                    response = gemini_client.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                st.write_stream(stream_response)
                
                # 3. Follow-up suggestions
                st.divider()
                st.subheader("💡 Related Search Ideas:")
                
                suggestion_prompt = f"""
                Based on the user query: "{query}"
                Provide 2 brief alternative topics or related follow-up questions they might want to search next.
                Format them as bullet points with emojis.
                """
                
                suggestions = gemini_client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=suggestion_prompt
                )
                st.write(suggestions.text)
                
            except Exception as e:
                st.error(f"Error: {e}")
