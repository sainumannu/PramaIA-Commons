# Registry Completo dei Nodi PramaIA

**Documentazione di tutti i tipi di nodi disponibili nel sistema**

## 📊 Panoramica

Questo documento mantiene traccia di tutti i processori di nodi implementati in PramaIA, organizzati per categoria con specifiche dettagliate di input, output e configurazione.

**Ultima aggiornamento:** 16 Novembre 2025  
**Versione Sistema:** PramaIA v2.2.0 - Architettura PDK Pura

## 🏗️ **ARCHITETTURA PDK PURA** - Novembre 2025

⚠️ **CAMBIO ARCHITETTURALE IMPORTANTE:**

L'architettura è stata completamente ridisegnata per separare processori **CORE** (server) da processori **BUSINESS** (PDK).

### 📍 Processori nel SERVER (Core Only)

**✅ Disponibili sempre, anche senza PDK:**

| Categoria | Processore | Tipo | Descrizione |
|-----------|------------|------|-------------|
| **I/O Core** | `UserInputProcessor` | Core | Input utente chat/web |
| **I/O Core** | `FileInputProcessor` | Core | Upload file base |  
| **I/O Core** | `TextOutputProcessor` | Core | Output testo |
| **I/O Core** | `FileOutputProcessor` | Core | Output file |
| **LLM Core** | `OpenAIProcessor` | Core | GPT-3.5/GPT-4 |
| **LLM Core** | `AnthropicProcessor` | Core | Claude |
| **LLM Core** | `OllamaProcessor` | Core | Modelli locali |
| **API Core** | `HTTPRequestProcessor` | Core | HTTP calls |
| **API Core** | `WebhookProcessor` | Core | Webhook handler |
| **Data Core** | `DataTransformProcessor` | Core | Trasformazione dati |
| **Data Core** | `TextProcessor` | Core | Elaborazione testo |
| **Data Core** | `JSONProcessor` | Core | Manipolazione JSON |
| **RAG Core** | `RAGQueryProcessor` | Core | Query RAG |
| **RAG Core** | `RAGGenerationProcessor` | Core | Generazione RAG |

### 🔌 Processori nel PDK (Business Only)

**⚠️ Richiedono PDK attivo, errore chiaro se PDK down:**

| Plugin | Processore | Descrizione | Status |
|--------|------------|-------------|---------|
| `core-business-processors-plugin` | `event_input` | 📨 Gestione eventi workflow | ✅ Implementato |
| `core-business-processors-plugin` | `file_parsing` | 📄 Parsing PDF PyPDF2/pdfplumber | ✅ Implementato |
| `core-business-processors-plugin` | `metadata_manager` | 📊 Gestione metadati | 🔄 Da implementare |
| `core-business-processors-plugin` | `document_processor` | 📝 Chunking documenti | 🔄 Da implementare |
| `core-business-processors-plugin` | `vector_store` | 🔍 Operazioni ChromaDB | 🔄 Da implementare |
| `core-business-processors-plugin` | `event_logger` | 📋 Logging avanzato | 🔄 Da implementare |

### 🎯 Come Usare i Processori

**Core (sempre disponibili):**
```python
# ✅ Funziona sempre
user_processor = get_core_processor('UserInputProcessor')
```

**Business (tramite PDK):**
```python  
# ✅ Funziona solo se PDK attivo
pdf_processor = PDKNodeProcessor(
    plugin_id='core-business-processors-plugin',
    node_id='file_parsing'
)
```

**Errore se business richiesto dal core:**
```python
# ❌ KeyError esplicito - niente fallback
event_processor = get_core_processor('EventInputProcessor')  # ERRORE CHIARO
```

---

## 🎯 Input Processors

### `input_user` - UserInputProcessor
**Scopo:** Gestisce input dall'utente tramite interfaccia chat/web

**Input:**
```json
{
  "user_message": "string",
  "user_id": "string", 
  "session_id": "string"
}
```

**Output:**
```json
{
  "text": "string",
  "user_context": {
    "user_id": "string",
    "timestamp": "ISO datetime"
  }
}
```

**Configurazione:**
```json
{
  "max_length": 1000,          // Lunghezza massima input
  "sanitize_html": true,       // Rimuove tag HTML
  "trim_whitespace": true      // Rimuove spazi extra
}
```

### `input_file` - FileInputProcessor
**Scopo:** Gestisce upload e lettura file

**Input:**
```json
{
  "file_path": "string",
  "mime_type": "string",
  "file_size": "number"
}
```

**Output:**
```json
{
  "content": "string",
  "metadata": {
    "filename": "string",
    "size": "number",
    "type": "string"
  }
}
```

**Configurazione:**
```json
{
  "max_file_size": 10485760,   // 10MB default
  "allowed_extensions": [".txt", ".pdf", ".docx"],
  "encoding": "utf-8"
}
```

---

## 🧠 LLM Processors

### `llm_openai` - OpenAIProcessor  
**Scopo:** Interfaccia con modelli OpenAI (GPT-3.5, GPT-4)

**Input:**
```json
{
  "prompt": "string",
  "context": "string",          // Opzionale
  "max_tokens": "number"        // Opzionale
}
```

**Output:**
```json
{
  "response": "string",
  "usage": {
    "prompt_tokens": "number",
    "completion_tokens": "number",
    "total_tokens": "number"
  },
  "model": "string"
}
```

**Configurazione:**
```json
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "api_key": "string"
}
```

### `llm_anthropic` - AnthropicProcessor
**Scopo:** Interfaccia con modelli Anthropic (Claude)

**Input/Output:** Simile a OpenAIProcessor

**Configurazione:**
```json
{
  "model": "claude-3-sonnet",
  "temperature": 0.7,
  "max_tokens": 1000,
  "api_key": "string"
}
```

### `llm_ollama` - OllamaProcessor
**Scopo:** Interfaccia con modelli Ollama locali

**Input/Output:** Simile a OpenAIProcessor

**Configurazione:**
```json
{
  "model": "llama2",
  "host": "http://localhost:11434",
  "temperature": 0.7
}
```

---

## 📤 Output Processors

### `output_text` - TextOutputProcessor
**Scopo:** Formatta output testuale per l'utente

**Input:**
```json
{
  "text": "string",
  "format": "string"           // markdown, plain, html
}
```

**Output:**
```json
{
  "formatted_text": "string",
  "display_format": "string"
}
```

**Configurazione:**
```json
{
  "default_format": "markdown",
  "word_wrap": 80,
  "escape_html": true
}
```

### `output_file` - FileOutputProcessor
**Scopo:** Salva output su file

**Input:**
```json
{
  "content": "string",
  "filename": "string",
  "format": "string"
}
```

**Output:**
```json
{
  "file_path": "string",
  "bytes_written": "number",
  "success": "boolean"
}
```

**Configurazione:**
```json
{
  "output_directory": "./output",
  "auto_timestamp": true,
  "overwrite": false
}
```

---

## 🔄 Data Processors

### `data_transform` - DataTransformProcessor
**Scopo:** Trasforma e manipola strutture dati

**Input:**
```json
{
  "data": "any",
  "transform_rules": "array"
}
```

**Output:**
```json
{
  "transformed_data": "any",
  "applied_rules": "array"
}
```

**Configurazione:**
```json
{
  "rules": [
    {
      "field": "name",
      "operation": "uppercase",
      "target": "display_name"
    }
  ]
}
```

### `text_processor` - TextProcessor
**Scopo:** Elaborazione e analisi testuale

**Input:**
```json
{
  "text": "string"
}
```

**Output:**
```json
{
  "processed_text": "string",
  "statistics": {
    "word_count": "number",
    "char_count": "number",
    "sentences": "number"
  }
}
```

**Configurazione:**
```json
{
  "operations": ["clean", "tokenize", "analyze"],
  "language": "it",
  "preserve_formatting": false
}
```

---

## 🌐 API Processors

### `http_request` - HTTPRequestProcessor
**Scopo:** Effettua chiamate HTTP a API esterne

**Input:**
```json
{
  "url": "string",
  "method": "GET|POST|PUT|DELETE",
  "headers": "object",
  "body": "any"
}
```

**Output:**
```json
{
  "status_code": "number",
  "response": "any",
  "headers": "object",
  "success": "boolean"
}
```

**Configurazione:**
```json
{
  "timeout": 30,
  "retry_attempts": 3,
  "default_headers": {
    "User-Agent": "PramaIA/2.0"
  }
}
```

### `webhook` - WebhookProcessor
**Scopo:** Invia notifiche webhook

**Input/Output:** Simile a HTTPRequestProcessor

**Configurazione:**
```json
{
  "webhook_url": "string",
  "secret": "string",
  "retry_on_failure": true
}
```

---

## 🔍 RAG Processors

### `rag_query` - RAGQueryProcessor
**Scopo:** Gestisce query per sistema RAG

**Input:**
```json
{
  "query": "string",
  "context": "string",
  "filters": "object"
}
```

**Output:**
```json
{
  "processed_query": "string",
  "search_vector": "array",
  "metadata": "object"
}
```

**Configurazione:**
```json
{
  "embedding_model": "text-embedding-ada-002",
  "max_query_length": 500,
  "expand_query": true
}
```

### `document_index` - DocumentIndexProcessor
**Scopo:** Indicizza documenti per ricerca

**Input:**
```json
{
  "document": "string",
  "metadata": "object",
  "chunks": "array"
}
```

**Output:**
```json
{
  "indexed": "boolean",
  "document_id": "string",
  "chunks_count": "number"
}
```

**Configurazione:**
```json
{
  "chunk_size": 1000,
  "chunk_overlap": 100,
  "index_name": "default"
}
```

---

## ⚡ Real Processors (Nuovi - Nov 2025)

### `event_input_node` - SimpleEventInputProcessor
**Scopo:** Gestisce eventi di input reali dal sistema di trigger

**Input:**
```json
{
  "event_type": "string",
  "event_source": "string", 
  "payload": "object",
  "timestamp": "ISO datetime"
}
```

**Output:**
```json
{
  "event_data": {
    "event_type": "string",
    "timestamp": "ISO datetime",
    "execution_id": "string"
  },
  "payload": "object",
  "file_path": "string"
}
```

**Configurazione:**
```json
{
  "validate_payload": true,
  "log_events": true
}
```

### `file_parsing` - SimpleFileParsingProcessor
**Scopo:** Estrazione reale di testo da file PDF e documenti

**Input:**
```json
{
  "file_path": "string"
}
```

**Output:**
```json
{
  "text": "string",
  "metadata": {
    "pages": "number",
    "title": "string",
    "author": "string"
  },
  "extraction_status": "success|failed",
  "file_path": "string"
}
```

**Configurazione:**
```json
{
  "extraction_method": "pypdf2|pdfplumber|auto",
  "clean_text": true,
  "extract_metadata": true,
  "max_file_size": 52428800
}
```

### `metadata_manager` - SimpleMetadataManagerProcessor
**Scopo:** Gestione e arricchimento metadati documenti

**Input:**
```json
{
  "metadata": "object",
  "text": "string",
  "file_path": "string"
}
```

**Output:**
```json
{
  "processed_metadata": {
    "text_length": "number",
    "word_count": "number", 
    "content_hash": "string",
    "processed_at": "ISO datetime",
    "processor_version": "string"
  },
  "metadata_status": "processed"
}
```

**Configurazione:**
```json
{
  "generate_hash": true,
  "analyze_content": true,
  "include_file_stats": true
}
```

### `document_processor` - SimpleDocumentProcessorProcessor
**Scopo:** Elaborazione documenti con chunking intelligente

**Input:**
```json
{
  "text": "string",
  "processed_metadata": "object"
}
```

**Output:**
```json
{
  "document_id": "string",
  "processed_document": {
    "document_id": "string",
    "original_text": "string",
    "chunks": "array",
    "metadata": "object"
  },
  "chunks": "array",
  "processing_stats": {
    "chunks_created": "number",
    "total_length": "number"
  }
}
```

**Configurazione:**
```json
{
  "chunk_size": 500,
  "chunk_overlap": 50,
  "chunking_method": "word_based|sentence_based",
  "preserve_sentences": true
}
```

### `vector_store_operations` - SimpleVectorStoreOperationsProcessor
**Scopo:** Operazioni su vector database (indicizzazione, ricerca)

**Input:**
```json
{
  "operation": "index|search|update|delete",
  "document_id": "string",
  "chunks": "array",
  "query": "string"
}
```

**Output:**
```json
{
  "status": "success|failed|simulated_success",
  "operation": "string",
  "document_id": "string",
  "indexed_count": "number",
  "results": "array",
  "message": "string"
}
```

**Configurazione:**
```json
{
  "operation": "index",
  "collection_name": "prama_documents",
  "embedding_model": "all-MiniLM-L6-v2",
  "limit": 10
}
```

### `event_logger` - SimpleEventLoggerProcessor
**Scopo:** Logging strutturato eventi e audit trail

**Input:**
```json
{
  "workflow_data": "any"
}
```

**Output:**
```json
{
  "event": {
    "event_id": "string",
    "timestamp": "ISO datetime",
    "workflow_id": "string",
    "execution_id": "string"
  },
  "logging_stats": {
    "event_logged": "boolean",
    "event_id": "string"
  },
  "status": "logged"
}
```

**Configurazione:**
```json
{
  "log_to_file": true,
  "log_to_db": false,
  "log_level": "info|debug|warning|error",
  "log_file": "workflow_events_simple.log"
}
```

---

## 🔧 PDK Processors (Remote)

### `pdk_node` - PDKNodeProcessor
**Scopo:** Proxy per esecuzione nodi su PramaIA-PDK

**Input:**
```json
{
  "node_data": "any",
  "pdk_config": "object"
}
```

**Output:**
```json
{
  "result": "any",
  "execution_time": "number",
  "pdk_status": "string"
}
```

**Configurazione:**
```json
{
  "pdk_url": "http://localhost:8001",
  "timeout": 60,
  "retry_attempts": 2
}
```

---

## 📊 Statistiche Registry

**Totale Processori:** 20  
**Categorie:** 7  
**Processori Attivi:** 20  
**Processori Legacy:** 0  

### Per Categoria:
- **Input:** 2 processori
- **LLM:** 3 processori  
- **Output:** 2 processori
- **Data:** 2 processori
- **API:** 3 processori
- **RAG:** 2 processori
- **Real/Document:** 6 processori

---

## 🔄 Changelog

### v2.1.0 (15 Nov 2025)
- ✅ Aggiunti 6 processori reali per sostituire stub
- ✅ Implementazione PDF parsing con PyPDF2
- ✅ Sistema logging strutturato
- ✅ Document chunking intelligente
- ❌ Rimossi processori stub legacy

### v2.0.0 (precedente)
- ✅ Migrazione architettura PDK  
- ✅ Sistema RAG completo
- ✅ Processori LLM multi-provider

---

## 🔍 Quick Reference

### Registry Access
```python
from backend.engine.node_registry import NodeRegistry
registry = NodeRegistry()
processor = registry.get_processor("node_type_name")
```

### Available Node Types
```python
registry.list_available_processors()
```

### Validation Test
```python
processor.validate_config(config_dict)
```

---

## ⚡ Performance Notes

**Processori Veloci:** input_user, text_processor, data_transform  
**Processori Medi:** file_parsing, document_processor, http_request  
**Processori Lenti:** llm_*, vector_store_operations, pdk_node  

**Memory Usage:**
- Basso: Tutti i processori text/data
- Medio: File processors, RAG
- Alto: LLM processors, Vector operations

---

**Per aggiornamenti a questo documento, vedere:** `docs/development/NODE_IMPLEMENTATION_GUIDE.md`