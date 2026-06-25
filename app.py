import streamlit as st
import os
from dotenv import load_dotenv

# Import your existing logic
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# Page Configuration
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🤖",
    layout="wide"
)

load_dotenv()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Inputs ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.info("Upload a video/audio source or provide a YouTube link to get started.")
    
    source_input = st.text_input("YouTube URL or Local File Path", placeholder="https://youtube.com/...")
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    
    process_button = st.button("🚀 Process Media", use_container_width=True)
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# --- Main Logic Flow ---
st.title("🎥 AI Video Assistant")
st.caption("Transcribe, Summarize, and Chat with your Meetings/Videos")

if process_button:
    if not source_input:
        st.error("Please provide a valid source (URL or File Path).")
    else:
        try:
            with st.status("🛠️ Working on your request...", expanded=True) as status:
                st.write("📥 Processing input...")
                chunks = process_input(source_input)
                
                st.write("✍️ Transcribing audio (this might take a while)...")
                transcript = transcribe_all(chunks, language)
                
                st.write("📝 Generating summary and insights...")
                title = generate_title(transcript)
                summary = summarize(transcript)
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)
                
                st.write("🧠 Building RAG Engine...")
                rag_chain = build_rag_chain(transcript)
                
                st.session_state.processed_data = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain": rag_chain,
                }
                status.update(label="✅ Processing Complete!", state="complete", expanded=False)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Display Results ---
if st.session_state.processed_data:
    data = st.session_state.processed_data
    
    st.divider()
    st.header(f"📌 {data['title']}")
    
    # Create Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🔍 Key Insights", "📜 Full Transcript", "💬 Chat with Video"])
    
    with tab1:
        st.subheader("Summary")
        st.write(data['summary'])
        
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Action Items")
            st.markdown(data['action_items'])
        with col2:
            st.subheader("🔑 Key Decisions")
            st.markdown(data['key_decisions'])
            
        st.divider()
        st.subheader("❓ Open Questions")
        st.markdown(data['open_questions'])
        
    with tab3:
        st.subheader("Raw Transcription")
        st.text_area("Transcript Content", data['transcript'], height=400)
        
    with tab4:
        st.subheader("Chat with your Meeting")
        
        # Display chat messages from history on app rerun
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask something about the video..."):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.spinner("Thinking..."):
                # Get response from RAG engine
                response = ask_question(data['rag_chain'], prompt)
                
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    # Empty state
    st.info("👈 Enter a source in the sidebar and click 'Process Media' to start.")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📝 Smart Summary")
        st.write("Get a concise summary of long videos in seconds.")
    with col2:
        st.markdown("### 🎯 Key Insights")
        st.write("Automatically extract action items and decisions.")
    with col3:
        st.markdown("### 💬 Interactive Chat")
        st.write("Ask specific questions about the content using RAG.")