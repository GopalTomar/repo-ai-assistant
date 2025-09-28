# Configuration settings for the Codebase Chat application

# Model Configuration
GROQ_MODEL_NAME = "llama-3.1-8b-instant"  # As specified in requirements
EMBEDDING_MODEL_NAME = "voyage-code-2"     # Code-aware embeddings
ALTERNATIVE_EMBEDDING = "all-MiniLM-L6-v2"  # Fallback if voyage-code-2 unavailable

# RAG Pipeline Settings
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_RETRIEVAL_K = 5
MAX_TOKENS = 2000
TEMPERATURE = 0.1

# File Processing Settings
SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', 
    '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.scala',
    '.kt', '.swift', '.r', '.sql', '.md', '.txt', '.yml', '.yaml',
    '.json', '.xml', '.html', '.css', '.sh', '.dockerfile'
}

IGNORE_DIRECTORIES = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next',
    'target', 'bin', 'obj', '.idea', '.vscode', '.vs',
    'coverage', '.nyc_output', 'logs', 'temp', 'tmp'
}

IGNORE_FILES = {
    '.gitignore', '.env', '.env.local', '.DS_Store',
    'package-lock.json', 'yarn.lock', 'poetry.lock',
    '.gitattributes', 'LICENSE', 'license.txt'
}

# File Size Limits
MAX_FILE_SIZE_BYTES = 500_000  # 500KB max per file
MAX_TOTAL_FILES = 500          # Maximum files to process

# UI Configuration
APP_TITLE = "Talk to Your Codebase"
APP_ICON = "💬"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Vector Database Settings
VECTOR_DB_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME_PREFIX = "codebase"

# Language-specific chunking separators
LANGUAGE_SEPARATORS = {
    '.py': ['\nclass ', '\ndef ', '\nasync def ', '\n\n', '\n', ' ', ''],
    '.js': ['\nfunction ', '\nclass ', '\nconst ', '\nlet ', '\nvar ', '\n\n', '\n', ' ', ''],
    '.jsx': ['\nexport function ', '\nexport default ', '\nfunction ', '\nconst ', '\n\n', '\n', ' ', ''],
    '.ts': ['\ninterface ', '\ntype ', '\nclass ', '\nfunction ', '\nconst ', '\n\n', '\n', ' ', ''],
    '.tsx': ['\nexport function ', '\nexport default ', '\ninterface ', '\ntype ', '\n\n', '\n', ' ', ''],
    '.java': ['\npublic class ', '\nprivate class ', '\nprotected class ', '\npublic static ', '\npublic void ', '\n\n', '\n', ' ', ''],
    '.cpp': ['\nclass ', '\nstruct ', '\nnamespace ', '\nvoid ', '\nint ', '\n\n', '\n', ' ', ''],
    '.c': ['\nstruct ', '\nvoid ', '\nint ', '\n\n', '\n', ' ', ''],
    '.go': ['\nfunc ', '\ntype ', '\nvar ', '\nconst ', '\n\n', '\n', ' ', ''],
    '.rs': ['\nfn ', '\nstruct ', '\nimpl ', '\nenum ', '\ntrait ', '\n\n', '\n', ' ', ''],
    '.php': ['\nclass ', '\nfunction ', '\npublic function ', '\nprivate function ', '\n\n', '\n', ' ', ''],
    '.rb': ['\nclass ', '\ndef ', '\nmodule ', '\n\n', '\n', ' ', ''],
    '.md': ['\n# ', '\n## ', '\n### ', '\n\n', '\n', ' ', ''],
    '.sql': ['\nCREATE ', '\nSELECT ', '\nINSERT ', '\nUPDATE ', '\nDELETE ', '\n\n', '\n', ' ', ''],
    'default': ['\n\n', '\n', ' ', '']
}

# Example queries for different types of repositories
EXAMPLE_QUERIES_BY_TYPE = {
    'web_app': [
        "How is user authentication handled?",
        "What are the main API endpoints?",
        "How is database connection managed?",
        "What security measures are implemented?",
        "How is error handling done?",
        "What is the project structure?",
        "How are environment variables used?",
        "What testing framework is used?"
    ],
    'data_science': [
        "What machine learning models are used?",
        "How is data preprocessing handled?",
        "What are the main features in the dataset?",
        "How is model evaluation performed?",
        "What visualization libraries are used?",
        "How is the data pipeline structured?",
        "What preprocessing steps are applied?",
        "How are hyperparameters tuned?"
    ],
    'mobile_app': [
        "How is navigation implemented?",
        "What UI components are used?",
        "How is state management handled?",
        "What API calls are made?",
        "How is local storage used?",
        "What third-party libraries are integrated?",
        "How are push notifications handled?",
        "What is the app architecture?"
    ],
    'general': [
        "What is the main purpose of this codebase?",
        "How is the project structured?",
        "What are the key dependencies?",
        "How do I run this project?",
        "What are the main functions/classes?",
        "Are there any configuration files?",
        "How is testing implemented?",
        "What documentation is available?"
    ]
}

# Performance Settings
ENABLE_CACHING = True
CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_CHAT_HISTORY = 50     # Maximum chat messages to keep

# Development/Debug Settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"
SHOW_SIMILARITY_SCORES = True
SHOW_CHUNK_METADATA = True

# Streamlit Specific Settings
STREAMLIT_CONFIG = {
    'theme.primaryColor': '#667eea',
    'theme.backgroundColor': '#ffffff',
    'theme.secondaryBackgroundColor': '#f0f2f6',
    'theme.textColor': '#262730'
}

# Color Scheme for UI
COLOR_SCHEME = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545',
    'info': '#17a2b8'
}