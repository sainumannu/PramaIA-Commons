"""
Vector Store Processor - Operazioni ChromaDB 
Processore per gestione embedding, indicizzazione e ricerca nel vector database.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# ChromaDB e embedding - Import diretti senza fallback
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class VectorStoreOperationsProcessor(BaseNodeProcessor):
    """
    Processore reale per operazioni ChromaDB vector store.
    
    Gestisce embedding, indicizzazione e ricerca nel vector database.
    """
    
    def __init__(self):
        self.chroma_client = None
        self.collection_name = "prama_documents"
        
        # Inizializza modello embedding
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Modello embedding caricato: all-MiniLM-L6-v2")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Esegue operazioni vector store basate sulla configurazione nodo.
        """
        logger.info(f"🔍 Vector Store Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        node_config = getattr(node, 'config', {})
        
        # Determina operazione
        operation = node_config.get('operation', 'index')  # index, search, update, delete
        
        # Inizializza client ChromaDB se necessario
        if not self.chroma_client:
            await self._initialize_chroma_client()
        
        # Esegui operazione specifica
        if operation == 'index':
            result = await self._index_document(input_data, node_config)
        elif operation == 'search':
            result = await self._search_documents(input_data, node_config)
        elif operation == 'update':
            result = await self._update_document(input_data, node_config)
        elif operation == 'delete':
            result = await self._delete_document(input_data, node_config)
        else:
            raise ValueError(f"Operazione vector store non supportata: {operation}")
        
        logger.info(f"  ✅ Operazione '{operation}' completata")
        return result
    
    async def _initialize_chroma_client(self):
        """Inizializza client ChromaDB."""
        try:
            # Configurazione ChromaDB (nuova API v1.3+)
            persist_dir = Path(__file__).parent.parent / "chromadb_data"
            persist_dir.mkdir(exist_ok=True)
            
            # Nuova sintassi per ChromaDB 1.3+
            self.chroma_client = chromadb.PersistentClient(path=str(persist_dir))
            
            # Ottieni o crea collection
            try:
                self.collection = self.chroma_client.get_collection(self.collection_name)
                logger.info(f"📚 Collection esistente caricata: {self.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(self.collection_name)
                logger.info(f"📚 Nuova collection creata: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione ChromaDB: {e}")
            raise
    
    async def _index_document(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Indicizza documento nel vector store."""
        chunks = input_data.get("chunks", [])
        document_id = input_data.get("document_id")
        
        if not chunks:
            return {"status": "no_chunks", "indexed_count": 0}
        
        # Prepara dati per ChromaDB
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["chunk_id"] for chunk in chunks]
        
        # Genera embeddings
        logger.info(f"  🔄 Generando embeddings per {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Indicizza in ChromaDB
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            indexed_count = len(chunks)
            logger.info(f"  ✅ Indicizzati {indexed_count} chunks")
            
            return {
                "status": "success",
                "operation": "index",
                "document_id": document_id,
                "indexed_count": indexed_count,
                "chunk_ids": ids
            }
            
        except Exception as e:
            logger.error(f"❌ Errore indicizzazione: {e}")
            return {
                "status": "error",
                "operation": "index",
                "error": str(e),
                "indexed_count": 0
            }
    
    async def _search_documents(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Cerca documenti nel vector store."""
        query_text = input_data.get("query", input_data.get("search_query", ""))
        limit = config.get("limit", 10)
        
        if not query_text:
            return {"status": "no_query", "results": []}
        
        try:
            # Genera embedding per query
            query_embedding = self.embedding_model.encode([query_text]).tolist()
            
            # Cerca in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=limit
            )
            
            # Formatta risultati
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    search_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i],
                        "id": results['ids'][0][i]
                    })
            
            logger.info(f"  🔍 Trovati {len(search_results)} risultati")
            
            return {
                "status": "success",
                "operation": "search",
                "query": query_text,
                "results": search_results,
                "total_found": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Errore ricerca: {e}")
            return {
                "status": "error",
                "operation": "search",
                "query": query_text,
                "error": str(e),
                "results": []
            }
    
    async def _update_document(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Aggiorna documento nel vector store."""
        # Per semplicità, implementiamo update come delete + add
        delete_result = await self._delete_document(input_data, config)
        if delete_result["status"] == "success":
            return await self._index_document(input_data, config)
        return delete_result
    
    async def _delete_document(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina documento dal vector store."""
        document_id = input_data.get("document_id")
        chunk_ids = input_data.get("chunk_ids", [])
        
        if not document_id and not chunk_ids:
            return {"status": "no_identifiers", "deleted_count": 0}
        
        try:
            # Se abbiamo chunk_ids specifici, usa quelli
            if chunk_ids:
                ids_to_delete = chunk_ids
            else:
                # Altrimenti cerca tutti i chunk del documento
                search_results = self.collection.get(
                    where={"document_id": document_id}
                )
                ids_to_delete = search_results['ids'] if search_results['ids'] else []
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                deleted_count = len(ids_to_delete)
                logger.info(f"  🗑️ Eliminati {deleted_count} chunks")
            else:
                deleted_count = 0
                logger.info("  ℹ️ Nessun chunk da eliminare trovato")
            
            return {
                "status": "success",
                "operation": "delete",
                "document_id": document_id,
                "deleted_count": deleted_count,
                "deleted_ids": ids_to_delete
            }
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione: {e}")
            return {
                "status": "error",
                "operation": "delete",
                "document_id": document_id,
                "error": str(e),
                "deleted_count": 0
            }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        operation = config.get('operation', 'index')
        valid_operations = ['index', 'search', 'update', 'delete']
        
        if operation not in valid_operations:
            return False
        
        # Validazioni specifiche per operazione
        if operation == 'search':
            limit = config.get('limit', 10)
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                return False
        
        return True