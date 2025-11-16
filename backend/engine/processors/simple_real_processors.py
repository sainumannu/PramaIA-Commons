"""
Processori Reali Semplificati - Versione senza dipendenze complesse

Implementazioni funzionali dei processori senza ChromaDB e SentenceTransformers
per evitare problemi di compatibilità. Mantiene la funzionalità core.
"""

import logging
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# PDF processing semplificato
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 non disponibile")

# Text processing
import re
import sqlite3

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class SimpleEventInputProcessor(BaseNodeProcessor):
    """Processore semplificato per eventi di input."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"🎯 Real Event Input Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        result = {
            "event_data": {
                "event_type": input_data.get("event_type", "document"),
                "timestamp": datetime.now().isoformat(),
                "execution_id": context.execution_id
            },
            "payload": input_data.get("payload", {}),
            "file_path": input_data.get("file_path")
        }
        
        logger.info(f"  ✅ Event processed: {result['event_data']['event_type']}")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True


class SimpleFileParsingProcessor(BaseNodeProcessor):
    """Processore semplificato per parsing PDF."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"📄 Real File Parsing Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        file_path = input_data.get("file_path")
        
        if not file_path or not Path(file_path).exists():
            logger.warning(f"File non trovato: {file_path}")
            return {
                "text": "File non disponibile per estrazione",
                "metadata": {"error": "file_not_found"},
                "extraction_status": "failed"
            }
        
        if PDF_AVAILABLE and file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\\n"
                    
                    metadata = {
                        "pages": len(pdf_reader.pages),
                        "title": str(pdf_reader.metadata.get("/Title", "")) if pdf_reader.metadata else "",
                        "author": str(pdf_reader.metadata.get("/Author", "")) if pdf_reader.metadata else ""
                    }
                    
                    result = {
                        "text": text.strip(),
                        "metadata": metadata,
                        "extraction_status": "success",
                        "file_path": file_path
                    }
                    
                    logger.info(f"  ✅ PDF estratto: {len(text)} caratteri")
                    return result
                    
            except Exception as e:
                logger.error(f"Errore estrazione PDF: {e}")
        
        # Fallback per testo semplice
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
                result = {
                    "text": text,
                    "metadata": {"file_type": "text"},
                    "extraction_status": "success",
                    "file_path": file_path
                }
                
                logger.info(f"  ✅ File testo estratto: {len(text)} caratteri")
                return result
                
        except Exception as e:
            logger.error(f"Errore lettura file: {e}")
            return {
                "text": "",
                "metadata": {"error": str(e)},
                "extraction_status": "failed"
            }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True


class SimpleMetadataManagerProcessor(BaseNodeProcessor):
    """Processore semplificato per metadati."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"📊 Real Metadata Manager Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai metadati esistenti
        metadata = input_data.get("metadata", {})
        text = input_data.get("text", "")
        
        # Arricchisci metadati
        enriched_metadata = metadata.copy()
        enriched_metadata.update({
            "processed_at": datetime.now().isoformat(),
            "text_length": len(text),
            "word_count": len(text.split()) if text else 0,
            "content_hash": hashlib.md5(text.encode('utf-8')).hexdigest() if text else "",
            "processor_version": "simplified_1.0"
        })
        
        result = {
            "processed_metadata": enriched_metadata,
            "metadata_status": "processed"
        }
        
        logger.info(f"  ✅ Metadati processati: {len(enriched_metadata)} campi")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True


class SimpleDocumentProcessorProcessor(BaseNodeProcessor):
    """Processore semplificato per documenti."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"📝 Real Document Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        text = input_data.get("text", "")
        metadata = input_data.get("processed_metadata", input_data.get("metadata", {}))
        
        # Crea chunks semplici
        chunk_size = 500
        chunks = []
        
        if text:
            words = text.split()
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                chunks.append({
                    "chunk_id": f"chunk_{i}",
                    "text": chunk_text,
                    "metadata": metadata
                })
        
        # Genera document ID
        document_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        result = {
            "document_id": document_id,
            "processed_document": {
                "document_id": document_id,
                "original_text": text,
                "chunks": chunks,
                "metadata": metadata
            },
            "chunks": chunks,
            "processing_stats": {
                "chunks_created": len(chunks),
                "total_length": len(text)
            }
        }
        
        logger.info(f"  ✅ Documento processato: {len(chunks)} chunks")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True


class SimpleVectorStoreOperationsProcessor(BaseNodeProcessor):
    """Processore semplificato per vector store (mock)."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"🔍 Real Vector Store Processor (Simplified): '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Simula operazioni vector store senza ChromaDB
        operation = getattr(node, 'config', {}).get('operation', 'index')
        document_id = input_data.get("document_id", "unknown")
        
        logger.warning("⚠️ Vector Store semplificato - ChromaDB non disponibile")
        
        if operation == 'index':
            chunks = input_data.get("chunks", [])
            result = {
                "status": "simulated_success",
                "operation": "index",
                "document_id": document_id,
                "indexed_count": len(chunks),
                "message": "Indicizzazione simulata (Vector store non disponibile)"
            }
        elif operation == 'search':
            query = input_data.get("query", "")
            result = {
                "status": "simulated_success",
                "operation": "search",
                "query": query,
                "results": [],
                "message": "Ricerca simulata (Vector store non disponibile)"
            }
        else:
            result = {
                "status": "simulated_success",
                "operation": operation,
                "message": f"Operazione {operation} simulata"
            }
        
        logger.info(f"  ✅ Vector store operation '{operation}' simulata")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True


class SimpleEventLoggerProcessor(BaseNodeProcessor):
    """Processore semplificato per logging."""
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        logger.info(f"📋 Real Event Logger Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Logga evento
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "workflow_id": context.workflow.workflow_id,
            "execution_id": context.execution_id,
            "data_summary": {
                "keys": list(input_data.keys()),
                "data_types": {k: type(v).__name__ for k, v in input_data.items()}
            }
        }
        
        # Log in file semplice
        log_file = "workflow_events_simple.log"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\\n')
        except Exception as e:
            logger.warning(f"Errore scrittura log: {e}")
        
        result = {
            "event": event,
            "logging_stats": {
                "event_logged": True,
                "event_id": event_id,
                "timestamp": timestamp
            },
            "status": "logged"
        }
        
        logger.info(f"  ✅ Evento loggato: {event_id}")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True