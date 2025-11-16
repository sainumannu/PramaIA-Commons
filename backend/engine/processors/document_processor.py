"""
Document Processor - Elaborazione avanzata documenti
Processore per chunking, arricchimento metadati e preparazione all'indicizzazione.
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class DocumentProcessorProcessor(BaseNodeProcessor):
    """
    Processore reale per elaborazione avanzata documenti.
    
    Combina testo, metadati e analisi per preparare il documento
    per indicizzazione e archiviazione.
    """
    
    def __init__(self):
        self.chunk_size = 512  # Dimensione chunk default
        self.chunk_overlap = 50  # Overlap tra chunk
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Elabora il documento completo creando chunks e struttura finale.
        """
        logger.info(f"📝 Document Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai componenti documento
        text_content = input_data.get("text", "")
        metadata = input_data.get("processed_metadata", input_data.get("metadata", {}))
        file_path = input_data.get("file_path", "")
        
        # Configurazione da nodo
        node_config = getattr(node, 'config', {})
        chunk_size = node_config.get('chunk_size', self.chunk_size)
        chunk_overlap = node_config.get('chunk_overlap', self.chunk_overlap)
        
        # Genera ID documento univoco
        document_id = self._generate_document_id(text_content, file_path)
        
        # Suddividi testo in chunks
        text_chunks = self._create_text_chunks(text_content, chunk_size, chunk_overlap)
        
        # Arricchisci ogni chunk con metadati
        enriched_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "chunk_size": len(chunk_text),
                "document_id": document_id
            })
            
            enriched_chunks.append({
                "chunk_id": f"{document_id}_chunk_{i}",
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        # Preparazione documento strutturato
        processed_document = {
            "document_id": document_id,
            "original_text": text_content,
            "chunks": enriched_chunks,
            "metadata": metadata,
            "processing_info": {
                "chunk_count": len(text_chunks),
                "total_length": len(text_content),
                "processing_timestamp": datetime.now().isoformat(),
                "chunk_strategy": {
                    "size": chunk_size,
                    "overlap": chunk_overlap,
                    "method": "sliding_window"
                }
            }
        }
        
        # Statistiche processing
        processing_stats = {
            "chunks_created": len(text_chunks),
            "avg_chunk_size": sum(len(chunk["text"]) for chunk in enriched_chunks) / len(enriched_chunks) if enriched_chunks else 0,
            "metadata_fields": len(metadata),
            "processing_success": True
        }
        
        result = {
            "processed_document": processed_document,
            "document_id": document_id,
            "chunks": enriched_chunks,
            "processing_stats": processing_stats,
            "ready_for_storage": True
        }
        
        logger.info(f"  ✅ Documento processato: {len(text_chunks)} chunks, ID: {document_id[:8]}...")
        return result
    
    def _generate_document_id(self, content: str, file_path: str) -> str:
        """Genera ID univoco per il documento."""
        # Combina hash contenuto + timestamp + path per unicità
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        path_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"doc_{timestamp}_{content_hash[:8]}_{path_hash[:8]}"
    
    def _create_text_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Suddivide il testo in chunks con overlap."""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calcola fine chunk
            end = min(start + chunk_size, text_length)
            
            # Se non è l'ultimo chunk, cerca un punto di separazione naturale
            if end < text_length:
                # Cerca l'ultimo spazio, punto o newline prima del limite
                for separator in ['\n\n', '. ', '! ', '? ', '\n', ' ']:
                    last_sep = text.rfind(separator, start, end)
                    if last_sep > start + chunk_size // 2:  # Almeno metà chunk
                        end = last_sep + len(separator)
                        break
            
            # Estrai chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Calcola prossimo inizio con overlap
            if end >= text_length:
                break
                
            start = max(end - overlap, start + 1)
        
        return chunks
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        chunk_size = config.get('chunk_size', 512)
        chunk_overlap = config.get('chunk_overlap', 50)
        
        if not isinstance(chunk_size, int) or chunk_size < 100:
            return False
        if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
            return False
        if chunk_overlap >= chunk_size:
            return False
            
        return True