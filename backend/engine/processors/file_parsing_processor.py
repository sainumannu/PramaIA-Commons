"""
File Parsing Processor - Estrazione testo da PDF
Processore per estrazione testo da file PDF usando PyPDF2 e pdfplumber.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from io import BytesIO
import re

import PyPDF2
import pdfplumber

from backend.engine.node_registry import BaseNodeProcessor
from backend.engine.execution_context import ExecutionContext
from backend.utils import get_logger

logger = get_logger()


class FileParsingProcessor(BaseNodeProcessor):
    """
    Processore reale per estrazione testo da file PDF.
    
    Utilizza PyPDF2 e pdfplumber per estrazione testo robusta.
    """
    
    def __init__(self):
        self.supported_formats = [".pdf"]
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    async def execute(self, node, context: ExecutionContext) -> Dict[str, Any]:
        """
        Estrae testo e metadati da file PDF.
        """
        logger.info(f"📄 File Parsing Processor: '{node.name}'")
        
        input_data = context.get_input_for_node(node.node_id)
        
        # Ottengo il file path
        file_path = input_data.get("file_path")
        if not file_path:
            raise ValueError("file_path richiesto per il parsing")
            
        # Validazione file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
            
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Formato file non supportato: {file_extension}")
            
        # Controllo dimensione file
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File troppo grande: {file_size} bytes")
        
        # Estrazione contenuto
        if file_extension == ".pdf":
            extraction_result = await self._extract_pdf_content(file_path)
        else:
            raise ValueError(f"Formato {file_extension} non implementato")
        
        # Aggiungi informazioni del file
        extraction_result["file_info"] = {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "file_size": file_size,
            "file_extension": file_extension,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"  ✅ File processato: {len(extraction_result.get('text', ''))} caratteri estratti")
        return extraction_result
    
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
                            # Aggiorna info pagina se già esiste
                            if page_num < len(pages_info):
                                pages_info[page_num]["pdfplumber_length"] = len(page_text)
                    except Exception as e:
                        logger.warning(f"Errore pdfplumber pagina {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Errore con pdfplumber: {e}")
            pdfplumber_text = ""
        
        # Scegli il testo migliore
        if len(pdfplumber_text.strip()) > len(pypdf2_text.strip()):
            text_content = pdfplumber_text
            extraction_method = "pdfplumber"
        else:
            text_content = pypdf2_text
            extraction_method = "PyPDF2"
        
        # Pulizia testo
        text_content = self._clean_text(text_content)
        
        return {
            "text": text_content,
            "metadata": metadata,
            "pages_info": pages_info,
            "extraction_method": extraction_method,
            "extraction_status": "success" if text_content else "no_text_extracted"
        }
    
    def _clean_text(self, text: str) -> str:
        """Pulisce e normalizza il testo estratto."""
        if not text:
            return ""
        
        # Rimuovi caratteri di controllo ma mantieni spazi e newlines
        text = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F-\\x9F]', '', text)
        
        # Normalizza spazi multipli
        text = re.sub(r' +', ' ', text)
        
        # Normalizza newlines multipli  
        text = re.sub(r'\\n\\s*\\n', '\\n\\n', text)
        
        # Rimuovi spazi a inizio/fine
        text = text.strip()
        
        return text
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida la configurazione del processore."""
        max_size = config.get("max_file_size_mb")
        if max_size and (not isinstance(max_size, (int, float)) or max_size <= 0):
            return False
        return True