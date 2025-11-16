"""
Event Input Processor - Gestione eventi di input
Processore per gestire input di eventi dal sistema di trigger.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class EventInputProcessor(BaseNodeProcessor):
    """
    Processore reale per gestire input di eventi dal sistema di trigger.
    
    Estrae e valida i dati dell'evento iniziale del workflow.
    """
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Processa l'evento di input e prepara i dati per il workflow.
        """
        logger.info(f"🎯 Event Input Processor: '{node.name}'")
        
        # Ottieni i dati dell'evento dal contesto
        input_data = context.get_input_for_node(node.node_id)
        
        # Configurazioni nodo
        config = getattr(node, 'config', {})
        
        # Estrai informazioni evento
        event_type = input_data.get("event_type", "document")
        payload = input_data.get("payload", {})
        file_path = input_data.get("file_path")
        
        # Validazione dati evento
        if not payload and not file_path:
            logger.warning("Evento senza payload e senza file_path")
            
        # Prepara risultato
        result = {
            "event_data": {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "execution_id": context.execution_id,
                "source": input_data.get("source", "unknown")
            },
            "payload": payload,
            "file_path": file_path,
            "metadata": input_data.get("metadata", {}),
            "processing_status": "event_received"
        }
        
        # Aggiungi informazioni configurazione
        if config:
            result["node_config"] = config
            
        logger.info(f"  ✅ Evento processato: {event_type}")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        # EventInput ha configurazione minima
        return True