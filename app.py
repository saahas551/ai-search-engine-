import streamlit as st
from google import genai
from tavily import TavilyClient

# Set page config
st.set_page_config(page_title="My AI Search Engine", page_icon="🔍")

# Page title & Greeting
st.title("🔍 My AI Search Engine")
st.markdown("### Hey there! 👋 How can I help you today?")

# Fetch API keys directly from Streamlit Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
tavily_api_key = st.secrets.get("TAVILY_API_KEY")

# Starter search suggestions
st.write("💡 **Try searching for:**")
col1, col2, col3 = st.columns(3)

# Session state to handle suggestion button clicks
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

def set_query(text):
    st.session_state.search_query = text

with col1:
    if st.button("🚀 Latest AI breakthroughs"):
        set_query("Latest AI breakthroughs")
with col2:
    if st.button("🎬 Movies releasing this week"):
        set_query("Movies releasing this week")
with col3:
    if st.button("🍎 Simple healthy dinner ideas"):
        set_query("Simple healthy dinner ideas")

# Form for query input (triggers on Enter or Button click)
with st.form(key="search_form"):
    query = st.text_input(
        "What would you like to search?", 
        value=st.session_state.search_query,
        key="query_input"
    )
    submit_button = st.form_submit_button("Search Web")

if submit_button and query:
    if not gemini_api_key or not tavily_api_key:
        st.error("API keys are missing from Streamlit Secrets!")
    else:
        with st.spinner("Searching the web..."):
            try:
                # 1. Fetch search results from Tavily
                tavily = TavilyClient(api_key=tavily_api_key)
                search_result = tavily.search(query=query, search_depth="fast", max_results=3)
                
                # 2. Setup Gemini client
                gemini_client = genai.Client(api_key=gemini_api_key)
                
                prompt = f"""
                You are a helpful search assistant. Based on these search results:
                {search_result}
                
                Answer the user's question clearly and concisely: {query}
                """
                
                st.subheader("Answer:")
                
                # Helper function to stream text word-by-word
                def stream_response():
                    response = gemini_client.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                # 3. Stream main response
                st.write_stream(stream_response)
                
                # 4. Generate related search alternatives/follow-up ideas
                st.divider()
                st.subheader("💡 Related Search Ideas & Alternatives:")
                
                suggestion_prompt = f"""
                Based on the user's query: "{query}"
                Provide 3 brief alternative topics or related questions they might want to search next.
                Format them as bullet points with relevant emojis.
                """
                
                suggestions = gemini_client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=suggestion_prompt
                )
                st.write(suggestions.text)
                
            except Exception as e:
                st.error(f"Error: {e}")
