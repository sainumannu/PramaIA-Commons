"""
Stub Processors

Processori stub per nodi non ancora implementati.
Permettono l'esecuzione dei workflow passando i dati attraverso senza modificarli.
"""

import logging
from typing import Dict, Any

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext

logger = logging.getLogger(__name__)


class StubProcessor(BaseNodeProcessor):
    """
    Processore stub generico che passa i dati attraverso senza modificarli.
    
    Utile per nodi non ancora implementati o per testing.
    """
    
    def __init__(self, node_type_name: str = "stub"):
        self.node_type_name = node_type_name
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Esegue il nodo stub passando i dati attraverso.
        """
        logger.warning(f"⚠️ Usando processore STUB per nodo '{node.name}' (tipo: {self.node_type_name})")
        
        # Ottieni i dati di input
        input_data = context.get_input_for_node(node.node_id)
        
        logger.info(f"  Input keys: {list(input_data.keys())}")
        
        # Passa i dati attraverso senza modificarli
        # Se c'è un solo valore, restituiscilo direttamente
        if len(input_data) == 1:
            result = next(iter(input_data.values()))
            logger.info(f"  Output: singolo valore passthrough")
            return result
        
        # Altrimenti restituisci tutto l'input come output
        logger.info(f"  Output: tutti gli input come dict")
        return input_data
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Stub accetta qualsiasi configurazione."""
        return True


class EventInputProcessor(StubProcessor):
    """Processore per nodi di input eventi."""
    
    def __init__(self):
        super().__init__("event_input_node")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Restituisce i dati di input del workflow (l'evento)."""
        logger.info(f"📨 Event Input Node: '{node.name}'")
        
        # Restituisci tutti i dati di input del workflow
        input_data = context.input_data
        logger.info(f"  Event data keys: {list(input_data.keys())}")
        
        return input_data


class FileParsingProcessor(StubProcessor):
    """Processore stub per parsing file."""
    
    def __init__(self):
        super().__init__("file_parsing")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Simula il parsing di un file PDF."""
        logger.warning(f"⚠️ File Parsing STUB per '{node.name}' - simulazione")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Simula estrazione testo e metadati
        return {
            "text": "Contenuto simulato del PDF",
            "metadata": {
                "pages": 10,
                "author": "Sistema",
                "title": "Documento di test"
            },
            "file_path": input_data.get("file_path", "unknown")
        }


class MetadataManagerProcessor(StubProcessor):
    """Processore stub per gestione metadati."""
    
    def __init__(self):
        super().__init__("metadata_manager")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Passa i metadati attraverso."""
        logger.warning(f"⚠️ Metadata Manager STUB per '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai metadati se presenti
        metadata = input_data.get("metadata", {})
        
        return {
            "processed_metadata": metadata,
            "metadata_status": "processed_stub"
        }


class DocumentProcessorProcessor(StubProcessor):
    """Processore stub per processing documenti."""
    
    def __init__(self):
        super().__init__("document_processor")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Processa il testo del documento."""
        logger.warning(f"⚠️ Document Processor STUB per '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai testo
        text = input_data.get("text", "")
        
        return {
            "processed_text": text,
            "processing_status": "processed_stub",
            "chunks": [text]  # Simula chunking
        }


class VectorStoreOperationsProcessor(StubProcessor):
    """Processore stub per operazioni VectorStore."""
    
    def __init__(self):
        super().__init__("vector_store_operations")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Simula aggiunta al vector store."""
        logger.warning(f"⚠️ VectorStore Operations STUB per '{node.name}'")
        logger.info(f"  ℹ️ In un'implementazione reale, questo nodo chiamerebbe il VectorstoreService")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Simula successo
        return {
            "result": "success_stub",
            "vector_store_status": "added_stub",
            "document_id": "stub_doc_id_12345",
            "message": "Documento aggiunto al vectorstore (SIMULATO)"
        }


class EventLoggerProcessor(StubProcessor):
    """Processore stub per logging eventi."""
    
    def __init__(self):
        super().__init__("event_logger")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """Logga l'evento."""
        logger.info(f"📝 Event Logger: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        logger.info(f"  Event logged: {list(input_data.keys())}")
        
        return {
            "logged": True,
            "log_status": "success",
            "timestamp": context.started_at.isoformat()
        }
