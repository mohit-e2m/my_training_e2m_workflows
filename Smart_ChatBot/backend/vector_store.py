"""
Vector database manager using ChromaDB
Handles embedding storage and semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize ChromaDB with persistence"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="e2m_solutions_content",
            metadata={"description": "E2M Solutions website content"}
        )
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded successfully")
    
    def add_documents(self, documents):
        """
        Add documents to vector store
        documents: list of dicts with 'text', 'metadata', and optional 'id'
        """
        if not documents:
            return
        
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        ids = [doc.get('id', f"doc_{i}") for i, doc in enumerate(documents)]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to vector store")
    
    def search(self, query, n_results=3):
        """
        Search for relevant documents
        Returns list of matching documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    def get_collection_count(self):
        """Get number of documents in collection"""
        return self.collection.count()
    
    def clear_collection(self):
        """Clear all documents from collection"""
        self.client.delete_collection(name="e2m_solutions_content")
        self.collection = self.client.get_or_create_collection(
            name="e2m_solutions_content",
            metadata={"description": "E2M Solutions website content"}
        )
        print("Collection cleared")
    
    def add_scraped_content(self, scraped_data):
        """
        Add scraped website content to vector store
        scraped_data: output from scraper.scrape_website()
        """
        documents = []
        
        for page_data in scraped_data:
            for i, chunk in enumerate(page_data['chunks']):
                doc_id = f"{page_data['url']}_chunk_{i}"
                
                documents.append({
                    'id': doc_id,
                    'text': chunk['text'],
                    'metadata': {
                        'url': page_data['url'],
                        'title': page_data['title'],
                        'description': page_data['description'],
                        'chunk_position': chunk['position']
                    }
                })
        
        self.add_documents(documents)
        return len(documents)
