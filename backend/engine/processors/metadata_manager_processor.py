"""
Metadata Manager Processor - Gestione metadati documenti
Processore per gestione, arricchimento e normalizzazione metadati.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class MetadataManagerProcessor(BaseNodeProcessor):
    """
    Processore reale per gestione metadati documenti.
    
    Gestisce arricchimento, normalizzazione e validazione metadati.
    """
    
    def __init__(self):
        self.required_fields = ["document_id", "file_path"]
        self.metadata_schema = {
            "document_id": str,
            "file_path": str,
            "title": str,
            "author": str,
            "creation_date": str,
            "modification_date": str,
            "tags": list,
            "category": str,
            "language": str,
            "file_hash": str,
            "processing_metadata": dict
        }
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Gestisce e arricchisce metadati documento.
        """
        logger.info(f"📊 Metadata Manager Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Estrai metadati esistenti
        existing_metadata = input_data.get("metadata", {})
        file_info = input_data.get("file_info", {})
        
        # Unisci e normalizza metadati
        enriched_metadata = await self._enrich_metadata(
            existing_metadata, file_info, input_data
        )
        
        # Valida metadati
        validation_result = self._validate_metadata(enriched_metadata)
        
        # Aggiungi informazioni di processing
        enriched_metadata["processing_metadata"] = {
            "processed_at": datetime.now().isoformat(),
            "processor_version": "1.0.0",
            "validation_status": validation_result["status"],
            "validation_errors": validation_result.get("errors", [])
        }
        
        result = {
            "metadata": enriched_metadata,
            "validation_result": validation_result,
            "metadata_completeness": self._calculate_completeness(enriched_metadata)
        }
        
        logger.info(f"  ✅ Metadati processati: {result['metadata_completeness']:.1%} completezza")
        return result
    
    async def _enrich_metadata(self, existing_metadata: Dict[str, Any], 
                             file_info: Dict[str, Any], 
                             input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Arricchisce i metadati con informazioni aggiuntive."""
        
        enriched = {}
        
        # Metadati base da file_info
        if file_info:
            enriched.update({
                "file_path": file_info.get("file_path", ""),
                "file_name": file_info.get("file_name", ""),
                "file_size": file_info.get("file_size", 0),
                "file_extension": file_info.get("file_extension", ""),
                "processing_timestamp": file_info.get("processing_timestamp", "")
            })
        
        # Unisci metadati esistenti
        enriched.update(existing_metadata)
        
        # Genera document_id se mancante
        if not enriched.get("document_id"):
            enriched["document_id"] = self._generate_document_id(enriched)
        
        # Calcola hash file se disponibile
        file_path = enriched.get("file_path")
        if file_path and os.path.exists(file_path) and not enriched.get("file_hash"):
            enriched["file_hash"] = await self._calculate_file_hash(file_path)
        
        # Normalizza date
        enriched = self._normalize_dates(enriched)
        
        # Pulisci e normalizza stringhe
        enriched = self._clean_string_fields(enriched)
        
        # Gestisci tags
        enriched["tags"] = self._normalize_tags(enriched.get("tags", []))
        
        # Auto-detect language se mancante
        if not enriched.get("language"):
            text_content = input_data.get("text", "")
            enriched["language"] = self._detect_language(text_content)
        
        # Genera titolo se mancante
        if not enriched.get("title"):
            enriched["title"] = self._generate_title(enriched, input_data.get("text", ""))
        
        return enriched
    
    def _generate_document_id(self, metadata: Dict[str, Any]) -> str:
        """Genera un ID unico per il documento."""
        file_path = metadata.get("file_path", "")
        file_name = metadata.get("file_name", "")
        timestamp = metadata.get("processing_timestamp", datetime.now().isoformat())
        
        # Crea hash basato su path, nome e timestamp
        id_string = f"{file_path}|{file_name}|{timestamp}"
        return hashlib.md5(id_string.encode()).hexdigest()
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calcola hash SHA256 del file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Errore calcolo hash file: {e}")
            return ""
    
    def _normalize_dates(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza i campi data nel formato ISO."""
        date_fields = ["creation_date", "modification_date", "processing_timestamp"]
        
        for field in date_fields:
            date_value = metadata.get(field)
            if date_value and isinstance(date_value, str):
                # Prova a parsare e re-formattare
                try:
                    if date_value.startswith("D:"):  # PDF date format
                        # Rimuovi prefisso PDF
                        clean_date = date_value[2:16]  # YYYYMMDDHHMMSS
                        if len(clean_date) >= 8:
                            formatted_date = f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:8]}"
                            if len(clean_date) >= 14:
                                formatted_date += f"T{clean_date[8:10]}:{clean_date[10:12]}:{clean_date[12:14]}"
                            metadata[field] = formatted_date
                    elif not date_value.count("-") == 2:  # Non è già ISO format
                        # Mantieni come stringa se non riconosciuto
                        pass
                except Exception:
                    # Mantieni valore originale se parsing fallisce
                    pass
        
        return metadata
    
    def _clean_string_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Pulisce i campi stringa rimuovendo caratteri non desiderati."""
        string_fields = ["title", "author", "subject", "creator", "producer", "category"]
        
        for field in string_fields:
            value = metadata.get(field)
            if value and isinstance(value, str):
                # Rimuovi caratteri di controllo e normalizza spazi
                cleaned = value.strip().replace("\\n", " ").replace("\\t", " ")
                cleaned = " ".join(cleaned.split())  # Normalizza spazi multipli
                metadata[field] = cleaned
        
        return metadata
    
    def _normalize_tags(self, tags: Any) -> List[str]:
        """Normalizza e pulisce i tags."""
        if not tags:
            return []
        
        if isinstance(tags, str):
            # Split su virgole e spazi
            tags = [t.strip() for t in tags.replace(",", " ").split()]
        
        if not isinstance(tags, list):
            return []
        
        # Pulisci e normalizza
        normalized_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                clean_tag = tag.strip().lower()
                if clean_tag not in normalized_tags:
                    normalized_tags.append(clean_tag)
        
        return normalized_tags
    
    def _detect_language(self, text: str) -> str:
        """Rileva la lingua del testo (implementazione semplice)."""
        if not text or len(text) < 50:
            return "unknown"
        
        # Parole comuni per rilevamento lingua
        italian_words = ["il", "la", "di", "che", "e", "a", "un", "per", "con", "da"]
        english_words = ["the", "and", "of", "to", "a", "in", "for", "is", "on", "that"]
        
        text_lower = text.lower()
        italian_count = sum(1 for word in italian_words if f" {word} " in text_lower)
        english_count = sum(1 for word in english_words if f" {word} " in text_lower)
        
        if italian_count > english_count:
            return "it"
        elif english_count > italian_count:
            return "en"
        else:
            return "unknown"
    
    def _generate_title(self, metadata: Dict[str, Any], text: str) -> str:
        """Genera un titolo se mancante."""
        
        # Prima prova con il nome file
        file_name = metadata.get("file_name", "")
        if file_name:
            title = Path(file_name).stem
            # Pulisci underscore e capitalizza
            title = title.replace("_", " ").replace("-", " ")
            title = " ".join(word.capitalize() for word in title.split())
            if len(title) > 5:  # Titolo decente
                return title
        
        # Prova con le prime parole del testo
        if text and len(text) > 20:
            first_line = text.split("\\n")[0].strip()
            if len(first_line) > 10 and len(first_line) < 100:
                return first_line[:80] + "..." if len(first_line) > 80 else first_line
        
        # Fallback
        return "Documento senza titolo"
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Valida i metadati secondo lo schema."""
        errors = []
        warnings = []
        
        # Controllo campi richiesti
        for field in self.required_fields:
            if not metadata.get(field):
                errors.append(f"Campo richiesto mancante: {field}")
        
        # Controllo tipi
        for field, expected_type in self.metadata_schema.items():
            value = metadata.get(field)
            if value is not None and not isinstance(value, expected_type):
                errors.append(f"Tipo errato per {field}: atteso {expected_type.__name__}")
        
        # Controlli specifici
        file_path = metadata.get("file_path")
        if file_path and not os.path.exists(file_path):
            warnings.append(f"File non esistente: {file_path}")
        
        document_id = metadata.get("document_id")
        if document_id and len(document_id) < 10:
            warnings.append("Document ID troppo corto")
        
        status = "valid" if not errors else "invalid"
        if warnings and not errors:
            status = "valid_with_warnings"
        
        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "field_count": len(metadata),
            "required_fields_present": sum(1 for f in self.required_fields if metadata.get(f))
        }
    
    def _calculate_completeness(self, metadata: Dict[str, Any]) -> float:
        """Calcola la percentuale di completezza dei metadati."""
        total_fields = len(self.metadata_schema)
        present_fields = sum(1 for field in self.metadata_schema.keys() 
                           if metadata.get(field))
        
        return present_fields / total_fields if total_fields > 0 else 0.0
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        # Validazioni future per configurazioni specifiche
        return True