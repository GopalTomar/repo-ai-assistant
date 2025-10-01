import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from utils import CodebaseManager, format_code_snippet, extract_repo_name, safe_markdown
from rag_pipeline import RAGPipeline

# Page configuration
st.set_page_config(
    page_title="Talk to Your Codebase",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .source-container {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .answer-container {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .repo-stats {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'codebase_manager' not in st.session_state:
        st.session_state.codebase_manager = CodebaseManager()
    
    if 'rag_pipeline' not in st.session_state:
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            st.session_state.rag_pipeline = RAGPipeline(groq_api_key)
        else:
            st.session_state.rag_pipeline = None
    
    if 'repo_loaded' not in st.session_state:
        st.session_state.repo_loaded = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'repo_stats' not in st.session_state:
        st.session_state.repo_stats = None
    
    if 'current_repo' not in st.session_state:
        st.session_state.current_repo = None

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>💬 Talk to Your Codebase</h1>
        <p>Upload any GitHub repository and chat with your code using advanced RAG technology</p>
        <p><strong>Powered by:</strong> Groq Llama-3.1-8b • ChromaDB • Code Embeddings</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with repository information and statistics"""
    with st.sidebar:
        st.markdown("### 🔧 Repository Manager")
        
        # API Key status
        if st.session_state.rag_pipeline:
            st.success("✅ Groq API Key Loaded")
        else:
            st.error("❌ Groq API Key Missing")
            st.info("Please add your Groq API key to the .env file")
        
        st.markdown("---")
        
        # Repository input
        repo_url = st.text_input(
            "🌐 GitHub Repository URL",
            placeholder="https://github.com/user/repo",
            help="Enter a public GitHub repository URL"
        )
        
        load_repo = st.button("📥 Load Repository", type="primary", use_container_width=True)
        
        if load_repo and repo_url:
            if not st.session_state.codebase_manager.is_valid_github_url(repo_url):
                st.error("❌ Please enter a valid GitHub URL")
            else:
                load_repository(repo_url)
        
        st.markdown("---")
        
        # Repository Statistics
        if st.session_state.repo_loaded and st.session_state.repo_stats:
            display_repository_stats()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        st.markdown("**Search Parameters**")
        k_docs = st.slider("Number of code chunks to retrieve", 3, 10, 5)
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.session_state.repo_loaded:
            if st.button("🔄 Reset Repository", use_container_width=True):
                reset_session()
                st.rerun()

def load_repository(repo_url: str):
    """Load and process repository with comprehensive error handling"""
    repo_name = extract_repo_name(repo_url)
    st.session_state.current_repo = repo_name
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Clone repository
        status_text.text(f"🔄 Step 1/3: Cloning {repo_name}...")
        progress_bar.progress(10)
        
        with st.spinner(f"Cloning {repo_name}..."):
            repo_path = st.session_state.codebase_manager.clone_repository(repo_url)
        
        if not repo_path:
            st.error("❌ Failed to clone repository")
            st.error("**Troubleshooting Steps:**")
            st.error("1. Verify the repository URL is correct")
            st.error("2. Ensure the repository is public (not private)")
            st.error("3. Check your internet connectivity")
            st.error("4. Try a different repository")
            st.info("**Test with:** https://github.com/streamlit/streamlit-example")
            progress_bar.empty()
            status_text.empty()
            return
        
        progress_bar.progress(35)
        
        # Step 2: Analyze code files
        status_text.text("📂 Step 2/3: Analyzing code files...")
        progress_bar.progress(40)
        
        with st.spinner("Analyzing code files..."):
            files = st.session_state.codebase_manager.get_code_files(repo_path)
        
        if not files:
            st.error("❌ No code files found in the repository")
            st.warning("**This could mean:**")
            st.warning("1. The repository contains only binary files or images")
            st.warning("2. All files have unsupported extensions")
            st.warning("3. The repository is empty or very minimal")
            st.info("**Supported file types:** .py, .js, .jsx, .ts, .tsx, .java, .cpp, .go, .rs, etc.")
            st.info("**Try a code-heavy repository like:** https://github.com/pallets/flask")
            progress_bar.empty()
            status_text.empty()
            return
        
        # Generate repository statistics
        st.session_state.repo_stats = st.session_state.codebase_manager.get_repo_stats(files)
        progress_bar.progress(65)
        
        st.success(f"✅ Found {len(files)} code files with {st.session_state.repo_stats['total_lines']:,} lines of code")
        
        # Step 3: Process with RAG pipeline
        status_text.text("🧠 Step 3/3: Creating embeddings and indexing code...")
        progress_bar.progress(70)
        
        if not st.session_state.rag_pipeline:
            st.error("❌ RAG pipeline not initialized")
            st.error("Please check your GROQ_API_KEY in environment variables")
            progress_bar.empty()
            status_text.empty()
            return
        
        with st.spinner("Creating embeddings and vector database..."):
            success = st.session_state.rag_pipeline.process_codebase(files)
        
        if success:
            st.session_state.repo_loaded = True
            progress_bar.progress(100)
            st.success(f"🎉 Successfully loaded {repo_name}!")
            st.balloons()
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            st.rerun()
        else:
            st.error("❌ Failed to process repository")
            st.error("The RAG pipeline encountered an error during processing")
            progress_bar.empty()
            status_text.empty()
            
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        
        # Show detailed error information
        import traceback
        with st.expander("🔍 View detailed error information"):
            st.code(traceback.format_exc())
        
        st.info("Please try again or contact support if the issue persists")
        
    finally:
        progress_bar.empty()
        status_text.empty()

def display_repository_stats():
    """Display repository statistics in sidebar"""
    stats = st.session_state.repo_stats
    
    st.markdown("### 📊 Repository Stats")
    
    # Basic metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Files", stats['total_files'])
    with col2:
        st.metric("Lines", f"{stats['total_lines']:,}")
    
    # File type distribution
    if stats['extensions']:
        st.markdown("**File Types**")
        ext_data = []
        for ext, info in stats['extensions'].items():
            ext_data.append({'Extension': ext or 'No ext', 'Files': info['count'], 'Lines': info['lines']})
        
        df = pd.DataFrame(ext_data).sort_values('Files', ascending=False).head(8)
        
        # Create a simple bar chart
        fig = px.bar(df, x='Files', y='Extension', orientation='h',
                    color='Lines', color_continuous_scale='Viridis')
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

def display_chat_interface():
    """Display the main chat interface"""
    if not st.session_state.repo_loaded:
        st.info("👆 Please load a repository from the sidebar to start chatting!")
        return
    
    st.markdown(f"### 💬 Chat with **{st.session_state.current_repo}**")
    
    # Display chat history
    for i, chat in enumerate(st.session_state.chat_history):
        display_chat_message(chat, i)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_query = st.text_input(
                "Ask a question about the codebase:",
                placeholder="e.g., Where is the database connection logic? How does authentication work?",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send 🚀", use_container_width=True, type="primary")
        
        if submitted and user_query.strip():
            process_query(user_query.strip())

def process_query(query: str):
    """Process user query and generate response"""
    # Add user message to chat history
    user_message = {
        'type': 'user',
        'content': query,
        'timestamp': datetime.now()
    }
    st.session_state.chat_history.append(user_message)
    
    # Generate response
    response = st.session_state.rag_pipeline.query_codebase(query)
    
    # Add assistant response to chat history
    assistant_message = {
        'type': 'assistant',
        'content': response['answer'],
        'sources': response['sources'],
        'timestamp': datetime.now(),
        'context_used': response['context_used']
    }
    st.session_state.chat_history.append(assistant_message)
    
    # Rerun to display new messages
    st.rerun()

def display_chat_message(chat: dict, index: int):
    """Display individual chat message"""
    if chat['type'] == 'user':
        with st.container():
            st.markdown(f"""
            <div class="chat-message">
                <strong>🧑‍💻 You ({chat['timestamp'].strftime('%H:%M')})</strong><br>
                {safe_markdown(chat['content'])}
            </div>
            """, unsafe_allow_html=True)
    
    else:  # assistant
        with st.container():
            st.markdown(f"""
            <div class="answer-container">
                <strong>🤖 Assistant ({chat['timestamp'].strftime('%H:%M')})</strong>
            """, unsafe_allow_html=True)
            
            # Display answer
            st.markdown(chat['content'])
            
            # Display sources if available
            if chat.get('sources') and chat['context_used']:
                with st.expander(f"📁 View Sources ({len(chat['sources'])} files)", expanded=False):
                    for i, source in enumerate(chat['sources'][:3]):  # Show top 3 sources
                        st.markdown(f"""
                        <div class="source-container">
                            <strong>📄 {source['file_path']}</strong> 
                            <small>(Similarity: {source['similarity_score']:.3f})</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display code snippet
                        code_preview = source['content'][:300] + "..." if len(source['content']) > 300 else source['content']
                        file_ext = source['file_path'].split('.')[-1] if '.' in source['file_path'] else 'text'
                        st.code(code_preview, language=file_ext)
            
            st.markdown("</div>", unsafe_allow_html=True)

def display_example_queries():
    """Display example queries for inspiration"""
    if st.session_state.repo_loaded:
        st.markdown("### 💡 Example Questions")
        
        examples = [
            "🔍 Where is the main application logic?",
            "🗄️ How is the database connection handled?",
            "🔐 How does authentication work?",
            "📡 What are the main API endpoints?",
            "🧪 How are tests structured?",
            "📦 What dependencies does this project use?",
            "🐛 Are there any error handling patterns?",
            "📊 How is data validation implemented?"
        ]
        
        cols = st.columns(4)
        for i, example in enumerate(examples):
            with cols[i % 4]:
                if st.button(example, key=f"example_{i}", use_container_width=True):
                    # Remove emoji and process as query
                    query = example.split(' ', 1)[1]
                    process_query(query)

def reset_session():
    """Reset session state"""
    if st.session_state.codebase_manager:
        st.session_state.codebase_manager.cleanup()
    
    st.session_state.repo_loaded = False
    st.session_state.chat_history = []
    st.session_state.repo_stats = None
    st.session_state.current_repo = None

def display_welcome_screen():
    """Display welcome screen when no repository is loaded"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h2>🚀 Welcome to CodebaseChat!</h2>
        <p style="font-size: 1.2em; color: #666; margin: 2rem 0;">
            Transform any GitHub repository into an interactive Q&A experience using advanced AI.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h4>🧠 Smart Code Analysis</h4>
            <p>Advanced AST-based chunking for precise code understanding and context-aware responses.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h4>⚡ Lightning Fast</h4>
            <p>Powered by Groq's Llama-3.1-8b-instant for ultra-fast response times.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h4>🎯 Code-Aware Search</h4>
            <p>Specialized embeddings for superior code similarity matching.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample queries
    st.markdown("### 🎯 What You Can Ask")
    
    sample_queries = [
        "**Architecture Questions**: 'How is this application structured?', 'What design patterns are used?'",
        "**Function Discovery**: 'Where is user authentication handled?', 'How does data validation work?'",
        "**Code Understanding**: 'Explain this algorithm', 'How does this API endpoint work?'",
        "**Best Practices**: 'Are there any security concerns?', 'How is error handling implemented?'",
        "**Dependencies**: 'What libraries are being used?', 'How are external services integrated?'"
    ]
    
    for query in sample_queries:
        st.markdown(f"• {query}")

def main():
    """Main application function"""
    # Initialize session state
    init_session_state()
    
    # Display header
    display_header()
    
    # Check if Groq API key is available
    if not st.session_state.rag_pipeline:
        st.error("🚫 **Groq API Key Missing!**")
        st.info("""
        Please add your Groq API key to the `.env` file:
        
        ```
        GROQ_API_KEY=your_api_key_here
        ```
        
        You can get a free API key from: https://console.groq.com/
        """)
        st.stop()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    if st.session_state.repo_loaded:
        # Create tabs for better organization
        tab1, tab2 = st.tabs(["💬 Chat", "📊 Repository Overview"])
        
        with tab1:
            display_chat_interface()
            display_example_queries()
        
        with tab2:
            display_repository_overview()
    else:
        display_welcome_screen()

def display_repository_overview():
    """Display detailed repository overview"""
    if not st.session_state.repo_stats:
        st.info("No repository loaded yet.")
        return
    
    stats = st.session_state.repo_stats
    
    # Overview metrics
    st.markdown("### 📈 Repository Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📁 Total Files",
            value=stats['total_files']
        )
    
    with col2:
        st.metric(
            label="📝 Lines of Code",
            value=f"{stats['total_lines']:,}"
        )
    
    with col3:
        avg_lines = stats['total_lines'] // stats['total_files'] if stats['total_files'] > 0 else 0
        st.metric(
            label="📊 Avg Lines/File",
            value=avg_lines
        )
    
    with col4:
        st.metric(
            label="📚 File Types",
            value=len(stats['extensions'])
        )
    
    # File type analysis
    if stats['extensions']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Files by Type")
            ext_data = []
            for ext, info in stats['extensions'].items():
                ext_data.append({
                    'Extension': ext if ext else 'No extension', 
                    'Count': info['count'],
                    'Lines': info['lines']
                })
            
            df = pd.DataFrame(ext_data).sort_values('Count', ascending=False)
            
            # Pie chart for file distribution
            fig = px.pie(df.head(8), values='Count', names='Extension', 
                        title="File Type Distribution")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Lines of Code by Type")
            
            # Bar chart for lines of code
            fig = px.bar(df.head(8), x='Extension', y='Lines',
                        title="Lines of Code by File Type",
                        color='Lines', color_continuous_scale='viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("#### 📋 Detailed Breakdown")
        st.dataframe(
            df.style.format({'Lines': '{:,}'}),
            use_container_width=True
        )

# Footer
def display_footer():
    """Display footer information"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with Streamlit • Powered by Groq Llama-3.1-8b • ChromaDB • Code Embeddings</p>
        <p><small>⚠️ This tool analyzes public repositories. Ensure you have permission to analyze private code.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    display_footer()
