import streamlit as st
from google import genai
from tavily import TavilyClient

# 1. Page Config
st.set_page_config(page_title="AI Search Engine", page_icon="🔍")
st.title("🔍 My AI Search Engine")

# 2. Sidebar Keys
st.sidebar.header("🔑 API Keys")
gemini_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
tavily_key = st.sidebar.text_input("Enter Tavily API Key:", type="password")

# 3. Input Search Bar
query = st.text_input("What would you like to search?")

# 4. Search Execution
if st.button("Search Web"):
    if not gemini_key or not tavily_key:
        st.error("Please enter BOTH keys in the sidebar on the left!")
    elif not query:
        st.warning("Please type a search query!")
    else:
        with st.spinner("Searching the live web..."):
            try:
                # Get web results
                tavily = TavilyClient(api_key=tavily_key)
                search_result = tavily.search(query=query, max_results=3)

                context = ""
                for result in search_result.get("results", []):
                    context += f"Source: {result['title']}\nSnippet: {result['content']}\n\n"

                # Pass to Gemini
                client = genai.Client(api_key=gemini_key)
                prompt = f"Query: {query}\n\nContext:\n{context}\n\nSummarize a direct answer based on the web context."

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

                st.subheader("💡 Answer:")
                st.write(response.text)

                with st.expander("🔗 View Sources"):
                    for result in search_result.get("results", []):
                        st.markdown(f"- [{result['title']}]({result['url']})")

            except Exception as e:
                st.error(f"Error: {e}")
