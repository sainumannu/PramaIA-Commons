"""
Event Logger Processor - Sistema di logging e audit trail
Processore per registrazione eventi di workflow e monitoraggio operazioni.
"""

import logging
import json
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class EventLoggerProcessor(BaseNodeProcessor):
    """
    Processore reale per logging eventi e audit trail.
    
    Registra tutte le operazioni di workflow per monitoraggio e debug.
    """
    
    def __init__(self):
        self.log_file = "workflow_events.log"
        self.audit_db = "workflow_audit.db"
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Registra evento di workflow nel sistema di logging.
        """
        logger.info(f"📋 Event Logger Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        node_config = getattr(node, 'config', {})
        
        # Prepara evento da loggare
        event = self._prepare_event_data(input_data, context, node_config)
        
        # Log in file
        if node_config.get('log_to_file', True):
            await self._log_to_file(event)
        
        # Log in database per audit
        if node_config.get('log_to_db', True):
            await self._log_to_database(event)
        
        # Log applicativo
        log_level = node_config.get('log_level', 'info')
        self._log_to_application(event, log_level)
        
        # Statistiche logging
        logging_stats = {
            "event_logged": True,
            "timestamp": event["timestamp"],
            "event_id": event["event_id"],
            "logged_to": []
        }
        
        if node_config.get('log_to_file', True):
            logging_stats["logged_to"].append("file")
        if node_config.get('log_to_db', True):
            logging_stats["logged_to"].append("database")
        
        result = {
            "event": event,
            "logging_stats": logging_stats,
            "status": "logged"
        }
        
        logger.info(f"  ✅ Evento loggato: {event['event_id']}")
        return result
    
    def _prepare_event_data(self, input_data: Dict[str, Any], context: ExecutionContext, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara i dati dell'evento per il logging."""
        
        # Genera ID evento univoco
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Estrai informazioni workflow
        workflow_info = {
            "workflow_id": context.workflow.workflow_id,
            "workflow_name": context.workflow.name,
            "execution_id": context.execution_id,
            "node_id": context.current_node_id if hasattr(context, 'current_node_id') else None
        }
        
        # Estrai dati rilevanti dall'input (filtrati per sicurezza)
        safe_input_data = self._sanitize_for_logging(input_data)
        
        # Informazioni di sistema
        system_info = {
            "user_id": getattr(context, 'user_id', 'system'),
            "source_ip": getattr(context, 'source_ip', 'localhost'),
            "user_agent": getattr(context, 'user_agent', 'PramaIA-Workflow')
        }
        
        # Determina livello evento e categoria
        event_level = config.get('event_level', 'info')
        event_category = config.get('event_category', self._infer_category(input_data))
        
        return {
            "event_id": event_id,
            "timestamp": timestamp,
            "level": event_level,
            "category": event_category,
            "workflow_info": workflow_info,
            "system_info": system_info,
            "data": safe_input_data,
            "metadata": {
                "processor": "EventLoggerProcessor",
                "version": "1.0.0"
            }
        }
    
    def _sanitize_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rimuove dati sensibili dal logging."""
        sanitized = {}
        
        # Campi sicuri da loggare
        safe_fields = [
            'document_id', 'operation', 'status', 'processing_stats',
            'chunk_count', 'file_size', 'event_type', 'timestamp',
            'metadata_fields', 'search_query', 'results_count'
        ]
        
        for field in safe_fields:
            if field in data:
                sanitized[field] = data[field]
        
        # Aggiungi contatori senza contenuto sensibile
        if 'text' in data:
            sanitized['text_length'] = len(data['text'])
        if 'chunks' in data:
            sanitized['chunks_count'] = len(data['chunks'])
        if 'results' in data:
            sanitized['results_count'] = len(data['results'])
        
        return sanitized
    
    def _infer_category(self, data: Dict[str, Any]) -> str:
        """Inferisce la categoria dell'evento dai dati."""
        if 'operation' in data:
            operation = data['operation']
            if operation in ['index', 'search', 'update', 'delete']:
                return 'vector_store'
            elif operation in ['create', 'read', 'update', 'delete']:
                return 'crud'
        
        if 'document_id' in data:
            return 'document_processing'
        
        if 'event_type' in data:
            return 'system_event'
        
        return 'workflow'
    
    async def _log_to_file(self, event: Dict[str, Any]):
        """Scrive evento nel file di log."""
        try:
            log_entry = json.dumps(event, ensure_ascii=False, separators=(',', ':'))
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
                
        except Exception as e:
            logger.error(f"❌ Errore logging su file: {e}")
    
    async def _log_to_database(self, event: Dict[str, Any]):
        """Salva evento nel database di audit."""
        try:
            # Inizializza database se non existe
            await self._ensure_audit_db()
            
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO workflow_events (
                    event_id, timestamp, level, category,
                    workflow_id, execution_id, user_id,
                    event_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event['event_id'],
                event['timestamp'],
                event['level'],
                event['category'],
                event['workflow_info']['workflow_id'],
                event['workflow_info']['execution_id'],
                event['system_info']['user_id'],
                json.dumps(event['data'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Errore logging su database: {e}")
    
    async def _ensure_audit_db(self):
        """Assicura che il database di audit esista."""
        try:
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    timestamp TEXT,
                    level TEXT,
                    category TEXT,
                    workflow_id TEXT,
                    execution_id TEXT,
                    user_id TEXT,
                    event_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crea indici per performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_id ON workflow_events(workflow_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON workflow_events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON workflow_events(category)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione audit database: {e}")
    
    def _log_to_application(self, event: Dict[str, Any], level: str):
        """Log nell'application logger."""
        message = f"[{event['category']}] {event['workflow_info']['workflow_name']} - {event['event_id']}"
        
        if level == 'debug':
            logger.debug(message)
        elif level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        valid_levels = ['debug', 'info', 'warning', 'error']
        level = config.get('log_level', 'info')
        
        if level not in valid_levels:
            return False
        
        return True