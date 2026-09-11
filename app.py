import random
import streamlit as st
from google import genai
from tavily import TavilyClient

# Browser tab title & icon
st.set_page_config(page_title="Orbit AI", page_icon="🌐", layout="centered")

# --- CUSTOM CSS: Colors, Typography & Animations ---
st.markdown("""
<style>
    /* Dark Slate Theme Background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Bold Title Styling with Gradient */
    h1 {
        background: linear-gradient(135deg, #7928CA 0%, #FF0080 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 3rem !important;
        letter-spacing: -1px;
    }

    /* Subheadings Bolder */
    h2, h3, .stMarkdown h3 {
        color: #58a6ff !important;
        font-weight: 700 !important;
    }

    /* Custom Form & Input Box styling */
    div[data-baseweb="input"] {
        border-radius: 12px !important;
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        transition: all 0.3s ease;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #58a6ff !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
    }
    
    /* Styling Buttons with Hover Animations */
    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(90deg, #1f6feb 0%, #238636 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        width: 100%;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(31, 111, 235, 0.4) !important;
    }

    /* Custom Glowing Pulse Animation for Searches */
    @keyframes orbit-pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(88, 166, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
    }
    .search-loader {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        margin: 15px 0;
        background: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    .pulse-circle {
        width: 20px;
        height: 20px;
        background-color: #58a6ff;
        border-radius: 50%;
        margin-right: 15px;
        animation: orbit-pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Dynamic greetings
greetings = [
    "Hey there! 👋 How was your day today?",
    "Welcome back! 😊 How are you doing today?",
    "Hello! 🌟 Hope you're having an awesome day! What are we exploring?",
    "Hey! 👋 Ready to discover something new today?"
]

if "selected_greeting" not in st.session_state:
    st.session_state.selected_greeting = random.choice(greetings)

# Main Heading on Page
st.title("🌐 Orbit AI")
st.markdown(f"### {st.session_state.selected_greeting}")

# Fetch API keys
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
tavily_api_key = st.secrets.get("TAVILY_API_KEY")

# Suggestion buttons
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

# Search form
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
        # Custom Animated Loading Indicator
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
            <div class="search-loader">
                <div class="pulse-circle"></div>
                <span style="font-weight: 600; font-size: 1.1rem; color: #58a6ff;">Orbiting the web for answers...</span>
            </div>
        """, unsafe_allow_html=True)

        try:
            # 1. Tavily Search
            tavily = TavilyClient(api_key=tavily_api_key)
            search_result = tavily.search(query=query, search_depth="fast", max_results=3)
            
            # 2. Gemini Setup with updated prompt name
            gemini_client = genai.Client(api_key=gemini_api_key)
            
            prompt = f"""
            You are Orbit AI, a friendly and intelligent AI search assistant created by Saahas.
            
            CRITICAL INSTRUCTION: If the user asks who created you, who made you, or who built this app, you MUST respond clearly that you were created and built by Saahas.
            
            Based on these web search results:
            {search_result}
            
            Answer the user's question clearly, warmly, and concisely: {query}
            """
            
            # Clear loading animation before streaming text
            loading_placeholder.empty()
            
            st.subheader("Answer:")
            
            def stream_response():
                response = gemini_client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            st.write_stream(stream_response)
            
            # 3. Follow-up ideas
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
            loading_placeholder.empty()
            st.error(f"Error: {e}")
