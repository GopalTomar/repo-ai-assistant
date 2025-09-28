import os
import uuid
from typing import List, Dict, Optional, Tuple
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import OpenAI
import chromadb
from groq import Groq
import tiktoken

class CodeChunker:
    """Advanced code chunking with syntax awareness"""
    
    def __init__(self):
        # Language-specific separators for better code splitting
        self.separators = {
            '.py': ['\nclass ', '\ndef ', '\nasync def ', '\nif __name__', '\n\n', '\n', ' ', ''],
            '.js': ['\nfunction ', '\nclass ', '\nconst ', '\nlet ', '\nvar ', '\nexport ', '\n\n', '\n', ' ', ''],
            '.jsx': ['\nexport default ', '\nexport function ', '\nfunction ', '\nconst ', '\nimport ', '\n\n', '\n', ' ', ''],
            '.ts': ['\ninterface ', '\ntype ', '\nclass ', '\nfunction ', '\nconst ', '\nexport ', '\n\n', '\n', ' ', ''],
            '.tsx': ['\nexport default ', '\ninterface ', '\ntype ', '\nfunction ', '\nconst ', '\n\n', '\n', ' ', ''],
            '.java': ['\npublic class ', '\nprivate class ', '\nprotected class ', '\npublic static ', '\npublic void ', '\nprivate void ', '\n\n', '\n', ' ', ''],
            '.cpp': ['\nclass ', '\nstruct ', '\nnamespace ', '\nvoid ', '\nint ', '\n#include', '\n\n', '\n', ' ', ''],
            '.c': ['\nstruct ', '\nvoid ', '\nint ', '\n#include', '\n#define', '\n\n', '\n', ' ', ''],
            '.go': ['\nfunc ', '\ntype ', '\nvar ', '\nconst ', '\npackage ', '\nimport', '\n\n', '\n', ' ', ''],
            '.rs': ['\nfn ', '\nstruct ', '\nimpl ', '\nenum ', '\ntrait ', '\nuse ', '\n\n', '\n', ' ', ''],
            '.php': ['\nclass ', '\nfunction ', '\npublic function ', '\nprivate function ', '\n<?php', '\n\n', '\n', ' ', ''],
            '.rb': ['\nclass ', '\ndef ', '\nmodule ', '\nrequire', '\n\n', '\n', ' ', ''],
            '.md': ['\n# ', '\n## ', '\n### ', '\n#### ', '\n\n', '\n', ' ', ''],
            '.sql': ['\nCREATE ', '\nSELECT ', '\nINSERT ', '\nUPDATE ', '\nDELETE ', '\nALTER ', '\n\n', '\n', ' ', ''],
            '.html': ['\n<div', '\n<section', '\n<article', '\n<header', '\n<footer', '\n\n', '\n', ' ', ''],
            '.css': ['\n.', '\n#', '\n@media', '\n@import', '\n\n', '\n', ' ', ''],
            '.yaml': ['\n- ', '\n  ', '\n', ' ', ''],
            '.yml': ['\n- ', '\n  ', '\n', ' ', ''],
            '.json': ['\n  "', '\n    "', '\n', ' ', ''],
            'default': ['\n\n', '\n', ' ', '']
        }
    
    def chunk_code(self, files: List[Dict[str, str]], 
                   chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """Split code files into meaningful chunks"""
        documents = []
        
        for file in files:
            separators = self.separators.get(file['extension'], self.separators['default'])
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=separators,
                length_function=len
            )
            
            chunks = splitter.split_text(file['content'])
            
            for i, chunk in enumerate(chunks):
                # Skip very small chunks
                if len(chunk.strip()) < 50:
                    continue
                
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'file_path': file['path'],
                        'file_extension': file['extension'],
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'source': f"{file['path']}#{i}"
                    }
                )
                documents.append(doc)
        
        return documents

class VectorStore:
    """Manages vector database operations with ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        # Try to use Voyage Code embeddings first, fallback to alternatives
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="voyage-code-2",  # Code-aware embeddings as per your requirements
                model_kwargs={'device': 'cpu'}
            )
        except Exception:
            try:
                # Fallback to a more widely available code-aware model
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="microsoft/codebert-base",
                    model_kwargs={'device': 'cpu'}
                )
            except Exception:
                # Final fallback to general purpose model
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document], collection_name: str = None) -> bool:
        """Create and populate vector store"""
        try:
            if collection_name is None:
                collection_name = f"codebase_{uuid.uuid4().hex[:8]}"
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )
            
            # Persist the database
            self.vectorstore.persist()
            return True
            
        except Exception as e:
            st.error(f"Failed to create vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search"""
        if not self.vectorstore:
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            # Return documents with similarity scores
            return [(doc, score) for doc, score in results]
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return []

class RAGPipeline:
    """Complete RAG pipeline for codebase Q&A"""
    
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.chunker = CodeChunker()
        self.vectorstore = VectorStore()
        self.model_name = "llama-3.1-8b-instant"  # As specified in your requirements
    
    def process_codebase(self, files: List[Dict[str, str]]) -> bool:
        """Process codebase files into vector store"""
        with st.spinner("🔄 Chunking code files..."):
            documents = self.chunker.chunk_code(files)
            st.info(f"Created {len(documents)} code chunks")
        
        with st.spinner("🧠 Creating embeddings and vector store..."):
            success = self.vectorstore.create_vectorstore(documents)
        
        if success:
            st.success("✅ Codebase indexed successfully!")
            return True
        return False
    
    def generate_context_prompt(self, query: str, retrieved_docs: List[Tuple]) -> str:
        """Generate augmented prompt with context"""
        context_parts = []
        
        for doc, score in retrieved_docs[:3]:  # Use top 3 results
            context_parts.append(f"""
File: {doc.metadata['file_path']}
Code:
```{doc.metadata['file_extension'][1:]}
{doc.page_content}
```
            """.strip())
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are an expert code analyst. Answer the user's question about the codebase using the provided code snippets as context.

Context from codebase:
{context}

User Question: {query}

Instructions:
1. Answer based primarily on the provided code context
2. If you reference specific code, mention the file name
3. Be concise but comprehensive
4. If the context doesn't contain enough information, say so
5. Provide code examples when relevant

Answer:"""
        
        return prompt
    
    def query_codebase(self, query: str, k: int = 5) -> Dict:
        """Query the codebase and generate response"""
        try:
            # Retrieve relevant documents
            with st.spinner("🔍 Searching codebase..."):
                retrieved_docs = self.vectorstore.similarity_search(query, k=k)
            
            if not retrieved_docs:
                return {
                    'answer': "I couldn't find any relevant code snippets for your query.",
                    'sources': [],
                    'context_used': False
                }
            
            # Generate augmented prompt
            prompt = self.generate_context_prompt(query, retrieved_docs)
            
            # Get response from Groq
            with st.spinner("🤖 Generating answer..."):
                response = self.groq_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful code analyst assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.1
                )
            
            answer = response.choices[0].message.content
            
            # Prepare sources
            sources = []
            for doc, score in retrieved_docs:
                sources.append({
                    'file_path': doc.metadata['file_path'],
                    'content': doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    'similarity_score': score,
                    'chunk_index': doc.metadata.get('chunk_index', 0)
                })
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': True,
                'retrieved_docs_count': len(retrieved_docs)
            }
            
        except Exception as e:
            st.error(f"Query processing failed: {str(e)}")
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'sources': [],
                'context_used': False
            }

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: approximate token count
        return len(text.split()) * 1.3