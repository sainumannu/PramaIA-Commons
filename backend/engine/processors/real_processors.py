"""
Real Processors - Implementazioni complete per sostituire i processori stub

Questo modulo contiene le implementazioni reali dei processori di workflow,
con funzionalità complete per elaborazione documenti, gestione metadati,
operazioni vector store e logging.
"""

import logging
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# PDF processing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2/pdfplumber non disponibili. Installare con: pip install PyPDF2 pdfplumber")

# Text processing
import re
from io import BytesIO

# Imports PramaIA
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
        
        # Estrai informazioni evento
        event_data = {
            "event_type": input_data.get("event_type", "unknown"),
            "event_source": input_data.get("event_source", "system"),
            "timestamp": input_data.get("timestamp", datetime.now().isoformat()),
            "workflow_id": context.workflow.workflow_id,
            "execution_id": context.execution_id,
            "user_id": getattr(context, 'user_id', None)
        }
        
        # Payload specifico dell'evento
        payload = input_data.get("payload", {})
        
        # Log evento ricevuto
        logger.info(f"  📨 Evento ricevuto: {event_data['event_type']}")
        logger.info(f"  🔗 Execution ID: {context.execution_id}")
        logger.info(f"  📦 Payload keys: {list(payload.keys())}")
        
        # Preparazione output completo
        result = {
            "event_data": event_data,
            "payload": payload,
            "raw_input": input_data
        }
        
        # Se c'è un file path nel payload, aggiungilo come output separato
        if "file_path" in payload:
            result["file_path"] = payload["file_path"]
            
        # Se ci sono metadati, estraili
        if "metadata" in payload:
            result["metadata"] = payload["metadata"]
            
        logger.info(f"  ✅ Event processing completato")
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del nodo."""
        # EventInput non richiede configurazioni speciali
        return True


class FileParsingProcessor(BaseNodeProcessor):
    """
    Processore reale per estrazione testo da file PDF.
    
    Utilizza PyPDF2 e pdfplumber per estrazione testo robusta.
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        if not PDF_AVAILABLE:
            logger.error("❌ Librerie PDF non disponibili!")
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Estrae testo e metadati da file PDF.
        """
        logger.info(f"📄 File Parsing Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        file_path = input_data.get("file_path")
        
        if not file_path:
            raise ValueError("File path non trovato nell'input")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
            
        if not PDF_AVAILABLE:
            raise ImportError("Librerie PDF non disponibili")
        
        # Determina formato file
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Formato file non supportato: {file_ext}")
        
        # Estrazione con metodi multipli per robustezza
        result = await self._extract_pdf_content(file_path)
        
        # Aggiungi metadati file
        file_stats = os.stat(file_path)
        result.update({
            "file_path": file_path,
            "file_size": file_stats.st_size,
            "file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "extraction_method": "PyPDF2+pdfplumber",
            "processing_timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"  ✅ Estrazione completata: {len(result.get('text', ''))} caratteri")
        return result
    
    async def _extract_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Estrae contenuto PDF usando metodi multipli."""
        
        text_content = ""
        metadata = {}
        pages_info = []
        
        try:
            # Metodo 1: PyPDF2 per metadati e testo di base
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Metadati documento
                if pdf_reader.metadata:
                    metadata.update({
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "producer": pdf_reader.metadata.get("/Producer", ""),
                        "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                        "modification_date": str(pdf_reader.metadata.get("/ModDate", ""))
                    })
                
                # Informazioni pagine
                num_pages = len(pdf_reader.pages)
                metadata["pages"] = num_pages
                
                # Estrazione testo con PyPDF2
                pypdf2_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        pypdf2_text += page_text + "\\n"
                        pages_info.append({
                            "page_number": page_num + 1,
                            "text_length": len(page_text),
                            "extraction_method": "PyPDF2"
                        })
                    except Exception as e:
                        logger.warning(f"Errore estrazione pagina {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Errore con PyPDF2: {e}")
            pypdf2_text = ""
        
        try:
            # Metodo 2: pdfplumber per testo più accurato
            with pdfplumber.open(file_path) as pdf:
                pdfplumber_text = ""
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            pdfplumber_text += page_text + "\\n"
                            
                            # Aggiorna info pagina se pdfplumber ha più testo
                            if page_num < len(pages_info):
                                if len(page_text) > pages_info[page_num]["text_length"]:
                                    pages_info[page_num].update({
                                        "text_length": len(page_text),
                                        "extraction_method": "pdfplumber"
                                    })
                    except Exception as e:
                        logger.warning(f"Errore pdfplumber pagina {page_num + 1}: {e}")
                        
        except Exception as e:
            logger.warning(f"Errore con pdfplumber: {e}")
            pdfplumber_text = ""
        
        # Scegli il testo migliore (più lungo)
        if len(pdfplumber_text) > len(pypdf2_text):
            text_content = pdfplumber_text
            extraction_method = "pdfplumber"
        else:
            text_content = pypdf2_text
            extraction_method = "PyPDF2"
        
        # Pulizia e normalizzazione testo
        text_content = self._clean_text(text_content)
        
        return {
            "text": text_content,
            "metadata": metadata,
            "pages_info": pages_info,
            "extraction_method": extraction_method,
            "text_length": len(text_content)
        }
    
    def _clean_text(self, text: str) -> str:
        """Pulisce e normalizza il testo estratto."""
        if not text:
            return ""
        
        # Rimuovi caratteri di controllo eccessivi
        text = re.sub(r'\\n{3,}', '\\n\\n', text)
        text = re.sub(r'\\s{3,}', ' ', text)
        
        # Normalizza spazi
        text = re.sub(r'[ \\t]+', ' ', text)
        
        # Rimuovi righe vuote eccessive
        lines = text.split('\\n')
        cleaned_lines = []
        empty_line_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                empty_line_count += 1
                if empty_line_count <= 2:  # Max 2 righe vuote consecutive
                    cleaned_lines.append(line)
            else:
                empty_line_count = 0
                cleaned_lines.append(line)
        
        return '\\n'.join(cleaned_lines).strip()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        # Verifica che le librerie PDF siano disponibili
        return PDF_AVAILABLE


class MetadataManagerProcessor(BaseNodeProcessor):
    """
    Processore reale per gestione e validazione metadati documenti.
    
    Normalizza, valida e arricchisce i metadati estratti dai documenti.
    """
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Gestisce e normalizza i metadati del documento.
        """
        logger.info(f"📊 Metadata Manager Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai metadati da diverse fonti
        file_metadata = input_data.get("metadata", {})
        file_path = input_data.get("file_path", "")
        text_content = input_data.get("text", "")
        
        # Normalizza metadati
        normalized_metadata = self._normalize_metadata(file_metadata)
        
        # Arricchisci con analisi contenuto
        content_analysis = self._analyze_content(text_content)
        normalized_metadata.update(content_analysis)
        
        # Aggiungi metadati file system
        if file_path and os.path.exists(file_path):
            fs_metadata = self._extract_filesystem_metadata(file_path)
            normalized_metadata.update(fs_metadata)
        
        # Genera hash del contenuto per deduplicazione
        content_hash = self._generate_content_hash(text_content)
        normalized_metadata["content_hash"] = content_hash
        
        # Timestamp processing
        normalized_metadata["processed_at"] = datetime.now().isoformat()
        normalized_metadata["processor_version"] = "1.0.0"
        
        result = {
            "processed_metadata": normalized_metadata,
            "original_metadata": file_metadata,
            "metadata_status": "processed",
            "content_analysis": content_analysis
        }
        
        logger.info(f"  ✅ Metadati processati: {len(normalized_metadata)} campi")
        return result
    
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza i metadati in formato standard."""
        normalized = {}
        
        # Mappatura campi standard
        field_mapping = {
            "title": ["title", "Title", "/Title"],
            "author": ["author", "Author", "/Author"],
            "subject": ["subject", "Subject", "/Subject"],
            "keywords": ["keywords", "Keywords", "/Keywords"],
            "creator": ["creator", "Creator", "/Creator"],
            "producer": ["producer", "Producer", "/Producer"],
            "creation_date": ["creation_date", "CreationDate", "/CreationDate"],
            "modification_date": ["modification_date", "ModDate", "/ModDate", "modification_date"]
        }
        
        for standard_field, possible_keys in field_mapping.items():
            for key in possible_keys:
                if key in metadata and metadata[key]:
                    normalized[standard_field] = str(metadata[key]).strip()
                    break
        
        # Normalizza date
        for date_field in ["creation_date", "modification_date"]:
            if date_field in normalized:
                normalized[date_field] = self._normalize_date(normalized[date_field])
        
        # Campi numerici
        if "pages" in metadata:
            normalized["pages"] = int(metadata["pages"])
        
        return normalized
    
    def _normalize_date(self, date_value: str) -> str:
        """Normalizza formato date PDF."""
        if not date_value:
            return ""
        
        # Rimuovi prefisso PDF (D:20231115...)
        if date_value.startswith("D:"):
            date_value = date_value[2:]
        
        # Cerca pattern data
        date_patterns = [
            r'(\\d{4})(\\d{2})(\\d{2})(\\d{2})(\\d{2})(\\d{2})',  # YYYYMMDDHHMMSS
            r'(\\d{4})-(\\d{2})-(\\d{2})',  # YYYY-MM-DD
            r'(\\d{2})/(\\d{2})/(\\d{4})'   # MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            match = re.match(pattern, date_value)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    try:
                        # Formato ISO standard
                        if len(groups) == 6:  # Full datetime
                            return f"{groups[0]}-{groups[1]}-{groups[2]}T{groups[3]}:{groups[4]}:{groups[5]}"
                        else:  # Solo data
                            return f"{groups[0]}-{groups[1]}-{groups[2]}"
                    except (ValueError, IndexError):
                        continue
        
        return date_value
    
    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Analizza il contenuto testuale per estrarre metadati aggiuntivi."""
        if not text:
            return {}
        
        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.split('\\n')),
            "language_hints": [],
            "content_type_hints": []
        }
        
        # Analisi linguaggio (euristiche semplici)
        italian_words = ["il", "la", "di", "che", "e", "è", "un", "una", "per", "con"]
        english_words = ["the", "and", "or", "of", "to", "in", "a", "is", "for", "with"]
        
        text_lower = text.lower()
        italian_score = sum(text_lower.count(word) for word in italian_words)
        english_score = sum(text_lower.count(word) for word in english_words)
        
        if italian_score > english_score:
            analysis["language_hints"].append("italian")
        elif english_score > 0:
            analysis["language_hints"].append("english")
        
        # Analisi tipo contenuto
        if re.search(r'\\b(articolo|paragrafo|sezione|capitolo)\\b', text_lower):
            analysis["content_type_hints"].append("document")
        if re.search(r'\\b(fattura|invoice|prezzo|€|\\$)\\b', text_lower):
            analysis["content_type_hints"].append("financial")
        if re.search(r'\\b(contratto|accordo|clausola)\\b', text_lower):
            analysis["content_type_hints"].append("legal")
        
        return analysis
    
    def _extract_filesystem_metadata(self, file_path: str) -> Dict[str, Any]:
        """Estrae metadati dal file system."""
        try:
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            return {
                "filename": path_obj.name,
                "file_extension": path_obj.suffix.lower(),
                "file_size_bytes": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "fs_created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "fs_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "fs_accessed": datetime.fromtimestamp(stat.st_atime).isoformat()
            }
        except Exception as e:
            logger.warning(f"Errore estrazione metadati filesystem: {e}")
            return {}
    
    def _generate_content_hash(self, content: str) -> str:
        """Genera hash SHA-256 del contenuto per deduplicazione."""
        if not content:
            return ""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        return True


# Continuiamo nel prossimo file per gli altri processori...