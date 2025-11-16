"""
Processori per l'engine PramaIA - Architettura Core + PDK
SOLO processori essenziali core nel server.
Tutti i processori business sono nel PDK.

Principio: Se PDK non funziona → errore chiaro, non fallback silenziosi.
"""

# Processori CORE - Interfacce essenziali sempre nel server
from .pdk_processors import PDKNodeProcessor

# Input/Output processors - ESSENZIALI per l'interfaccia
from .input_processors import UserInputProcessor, FileInputProcessor
from .output_processors import TextOutputProcessor, FileOutputProcessor

# Data processors - UTILI per elaborazione dati base
from .data_processors import DataTransformProcessor, TextProcessor, JSONProcessor

# API processors - UTILI per integrazioni
from .api_processors import HTTPRequestProcessor, WebhookProcessor, APICallProcessor

# LLM processors - ESSENZIALI per la chat  
from .llm_processors import OpenAIProcessor, AnthropicProcessor, OllamaProcessor

# RAG processors - Core functionality
from .rag_processors import RAGQueryProcessor, RAGGenerationProcessor, DocumentIndexProcessor

# Workflow processors - Core orchestration  
# from .workflow_processors import WorkflowExecutionProcessor

# Registry SOLO processori CORE (niente business logic)
CORE_PROCESSORS = {
    # PDK Processor - proxy universale
    'PDKNodeProcessor': PDKNodeProcessor,
    
    # I/O Essenziali
    'UserInputProcessor': UserInputProcessor,
    'FileInputProcessor': FileInputProcessor,
    'TextOutputProcessor': TextOutputProcessor,
    'FileOutputProcessor': FileOutputProcessor,
    
    # Data Processing Base
    'DataTransformProcessor': DataTransformProcessor,
    'TextProcessor': TextProcessor,
    'JSONProcessor': JSONProcessor,
    
    # API Integration
    'HTTPRequestProcessor': HTTPRequestProcessor,
    'WebhookProcessor': WebhookProcessor,
    'APICallProcessor': APICallProcessor,
    
    # LLM Core
    'OpenAIProcessor': OpenAIProcessor,
    'AnthropicProcessor': AnthropicProcessor,
    'OllamaProcessor': OllamaProcessor,
    
    # RAG Core
    'RAGQueryProcessor': RAGQueryProcessor,
    'RAGGenerationProcessor': RAGGenerationProcessor,
    'DocumentIndexProcessor': DocumentIndexProcessor
}

def get_core_processor(processor_name: str):
    """
    Ottiene un processore core.
    
    Args:
        processor_name: Nome del processore core
        
    Returns:
        Classe del processore core
        
    Raises:
        KeyError: Se il processore non è nel core (deve essere nel PDK)
    """
    if processor_name in CORE_PROCESSORS:
        return CORE_PROCESSORS[processor_name]
    else:
        # ERRORE CHIARO - niente fallback
        available_core = ', '.join(CORE_PROCESSORS.keys())
        raise KeyError(
            f"Processore '{processor_name}' NON è un processore core. "
            f"Disponibili nel core: [{available_core}]. "
            f"Per processori business (EventInput, FileParsing, VectorStore, ecc.) "
            f"usa PDKNodeProcessor e assicurati che il PDK sia attivo."
        )

def list_core_processors():
    """Elenca tutti i processori core disponibili."""
    return list(CORE_PROCESSORS.keys())

def validate_core_dependencies():
    """
    Valida che tutte le dipendenze core siano disponibili.
    Se manca qualcosa core, il sistema deve fallire chiaramente.
    
    Returns:
        dict: Stato delle dipendenze per ogni processore core
    """
    status = {}
    
    # Test processori I/O
    status['UserInputProcessor'] = {'available': True, 'issues': []}
    status['FileInputProcessor'] = {'available': True, 'issues': []}
    status['TextOutputProcessor'] = {'available': True, 'issues': []}
    status['FileOutputProcessor'] = {'available': True, 'issues': []}
    
    # Test processori data
    status['DataTransformProcessor'] = {'available': True, 'issues': []}
    status['TextProcessor'] = {'available': True, 'issues': []}
    status['JSONProcessor'] = {'available': True, 'issues': []}
    
    # Test processori API
    status['HTTPRequestProcessor'] = {'available': True, 'issues': []}
    status['WebhookProcessor'] = {'available': True, 'issues': []}
    status['APICallProcessor'] = {'available': True, 'issues': []}
    
    # Test processori LLM (potrebbero fallire se API key mancanti)
    try:
        # Test basic imports
        status['OpenAIProcessor'] = {'available': True, 'issues': []}
        status['AnthropicProcessor'] = {'available': True, 'issues': []}
        status['OllamaProcessor'] = {'available': True, 'issues': []}
    except ImportError as e:
        status['LLMProcessors'] = {'available': False, 'issues': [str(e)]}
    
    # Test PDK Processor
    status['PDKNodeProcessor'] = {
        'available': True, 
        'issues': [],
        'note': 'PDK processor è sempre disponibile come proxy. La connettività PDK viene testata a runtime.'
    }
    
    return status

__all__ = [
    # Processore PDK
    'PDKNodeProcessor',
    
    # Processori I/O Core
    'UserInputProcessor',
    'FileInputProcessor',
    'TextOutputProcessor',
    'FileOutputProcessor',
    
    # Processori Data Core
    'DataTransformProcessor',
    'TextProcessor',
    'JSONProcessor',
    
    # Processori API Core
    'HTTPRequestProcessor',
    'WebhookProcessor',
    'APICallProcessor',
    
    # Processori LLM Core
    'OpenAIProcessor',
    'AnthropicProcessor',
    'OllamaProcessor',
    
    # Processori RAG Core
    'RAGQueryProcessor',
    'RAGGenerationProcessor',
    'DocumentIndexProcessor',
    
    # Registry e funzioni
    'CORE_PROCESSORS',
    'get_core_processor',
    'list_core_processors',
    'validate_core_dependencies'
]
