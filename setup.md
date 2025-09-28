# Talk to Your Codebase - Setup Instructions

A powerful RAG-powered tool to chat with any GitHub repository using Groq's Llama-3.1-8b model, ChromaDB, and Voyage Code embeddings.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git installed on your system
- Groq API key (free from https://console.groq.com/)

### 1. Clone or Download the Project
```bash
mkdir codebase_chat
cd codebase_chat
# Copy all the provided files into this directory
```

### 2. Create Virtual Environment
```bash
python -m venv codebase_rag
source codebase_rag/bin/activate  # On Windows: codebase_rag\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
codebase_chat/
├── app.py              # Main Streamlit application
├── rag_pipeline.py     # RAG pipeline implementation
├── utils.py           # Utility functions
├── requirements.txt   # Python dependencies
├── .env              # Environment variables
├── chroma_db/        # ChromaDB storage (auto-created)
└── setup.md          # This file
```

## 🛠️ How It Works

### 1. Repository Loading
- Clone any public GitHub repository
- Extract and filter code files (supports 20+ file types)
- Generate repository statistics and visualizations

### 2. Code Processing
- **AST-based Chunking**: Intelligently splits code using Abstract Syntax Tree analysis
- **Voyage Code Embeddings**: Uses code-aware embeddings for better semantic understanding
- **ChromaDB Storage**: Efficient vector storage and similarity search

### 3. Question Answering
- **Groq Llama-3.1-8b**: Ultra-fast inference with the specified model
- **Context-Aware**: Retrieves relevant code snippets for each query
- **Source Attribution**: Shows exactly which files and code sections were used

## 🎯 Features

### Core Functionality
- ✅ Load any public GitHub repository
- ✅ Intelligent code chunking with syntax awareness
- ✅ Real-time chat interface with conversation history
- ✅ Source code attribution and similarity scores
- ✅ Repository statistics and visualizations

### Advanced Features
- ✅ Multi-language support (Python, JavaScript, Java, C++, etc.)
- ✅ Code-aware embeddings for better relevance
- ✅ Responsive and modern UI design
- ✅ Example queries to get started quickly
- ✅ Conversation persistence during session

### UI Components
- 🎨 Modern gradient design
- 📊 Interactive charts and metrics
- 💬 Chat interface with timestamps
- 🔍 Expandable source code viewers
- 📱 Responsive layout

## 🔧 Configuration Options

### Model Settings (in rag_pipeline.py)
```python
# Change embedding model
self.embeddings = HuggingFaceEmbeddings(
    model_name="voyage-code-2",  # As per your requirements
    model_kwargs={'device': 'cpu'}
)

# Change LLM model
self.model_name = "llama-3.1-8b-instant"  # Groq model
```

### Chunking Parameters
```python
# Adjust chunk sizes in rag_pipeline.py
chunk_size = 1000      # Characters per chunk
chunk_overlap = 200    # Overlap between chunks
k = 5                  # Number of chunks to retrieve
```

## 📝 Usage Examples

### Sample Queries You Can Try
1. **Architecture Understanding**
   - "How is this application structured?"
   - "What design patterns are used here?"

2. **Function Discovery**
   - "Where is user authentication handled?"
   - "How does the database connection work?"

3. **Code Analysis**
   - "Explain the main algorithm in this codebase"
   - "How does error handling work?"

4. **Security & Best Practices**
   - "Are there any potential security issues?"
   - "How is input validation implemented?"

## 🐛 Troubleshooting

### Common Issues

1. **"Groq API Key Missing" Error**
   - Ensure `.env` file exists with correct API key
   - Verify the API key is valid at https://console.groq.com/

2. **Repository Cloning Fails**
   - Check if the repository URL is public
   - Ensure you have internet connection
   - Verify Git is installed on your system

3. **Out of Memory Errors**
   - Try with smaller repositories first
   - Reduce chunk_size in rag_pipeline.py
   - Close other applications to free up RAM

4. **Slow Performance**
   - Check your internet connection
   - Try reducing the number of retrieved chunks (k parameter)
   - Consider using FAISS instead of ChromaDB for larger repos

### Performance Tips
- Start with smaller repositories (< 100 files) to test
- Use repositories with familiar code structure
- Clear chat history regularly for better performance

## 🔄 Updates and Enhancements

### Potential Improvements
- [ ] Support for private repositories (with GitHub tokens)
- [ ] Code modification suggestions
- [ ] Multi-repository comparison
- [ ] Export conversation history
- [ ] Custom embedding models
- [ ] Real-time collaboration features

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure your Groq API key has sufficient quota
4. Try with a different, smaller repository first

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ The Streamlit app loads without errors
- ✅ You can successfully load a GitHub repository
- ✅ The repository statistics appear correctly
- ✅ You get relevant answers to your code questions
- ✅ Source code snippets are displayed with proper attribution

Enjoy exploring codebases with AI! 🚀