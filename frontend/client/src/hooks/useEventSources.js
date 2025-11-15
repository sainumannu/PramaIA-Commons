/**
 * Hook personalizzato per gestire le sorgenti di eventi dinamiche
 * Sostituisce gli array hardcoded con chiamate API dinamiche
 */
import { useState, useEffect, useCallback } from 'react';
import { PDK_SERVER_BASE_URL } from '../config/appConfig';
import axios from 'axios';

export const useEventSources = () => {
  const [eventSources, setEventSources] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [sourcesLoading, setSourcesLoading] = useState(true);
  const [sourcesError, setSourcesError] = useState(null);

  console.log('[useEventSources] Hook state update:', {
    eventSources: eventSources.length,
    eventTypes: eventTypes.length,
    sourcesLoading,
    sourcesError
  });

  // Carica tutte le sorgenti di eventi disponibili
  const loadEventSources = useCallback(async () => {
    try {
      setSourcesLoading(true);
      // Aggiungiamo timestamp per evitare cache
      const timestamp = new Date().getTime();
      // Chiama il server PDK invece del server principale
      const response = await axios.get(`${PDK_SERVER_BASE_URL}/api/event-sources?t=${timestamp}`);
      console.log('[useEventSources] Event sources response:', response.data);
      setEventSources(response.data || []);
      setSourcesError(null);
    } catch (err) {
      console.error('Errore nel caricamento delle sorgenti:', err);
      setSourcesError('Impossibile caricare le sorgenti di eventi');
      // Fallback a sorgenti hardcoded per compatibilità
      setEventSources([
        { id: 'system', name: 'Sistema', description: 'Eventi interni del sistema' },
        { id: 'api-webhook', name: 'API Webhook', description: 'Endpoint HTTP per eventi esterni' }
      ]);
    } finally {
      setSourcesLoading(false);
    }
  }, []);

  // Carica tutti i tipi di eventi disponibili
  const loadAllEventTypes = useCallback(async () => {
    console.log('[useEventSources] Loading all event types...');
    try {
      // Chiama il server PDK invece del server principale
      const response = await axios.get(`${PDK_SERVER_BASE_URL}/api/event-sources/events/all`);
      console.log('[useEventSources] Event types response:', response.data);
      
      // Converte la struttura dei dati dal server alla struttura attesa dal componente
      const eventTypesData = response.data.eventTypes || response.data || [];
      const convertedEventTypes = eventTypesData.map(eventType => ({
        type: eventType.id || eventType.type,
        label: eventType.name || eventType.label,
        description: eventType.description,
        sourceId: eventType.sourceId,
        sourceName: eventType.sourceName
      }));
      
      console.log('[useEventSources] Converted event types:', convertedEventTypes);
      setEventTypes(convertedEventTypes);
    } catch (err) {
      console.error('Errore nel caricamento dei tipi di eventi:', err);
      // Fallback a tipi hardcoded
      setEventTypes([
        { 
          type: 'document_uploaded', 
          label: 'Upload Documento', 
          description: 'Quando un documento viene caricato nel sistema',
          sourceId: 'document-monitor',
          sourceName: 'Document Monitor'
        },
        { 
          type: 'webhook_received', 
          label: 'Webhook Ricevuto', 
          description: 'Quando viene ricevuta una chiamata webhook',
          sourceId: 'api-webhook',
          sourceName: 'API Webhook'
        }
      ]);
    }
  }, []);

  // Carica tipi di eventi per una sorgente specifica
  const loadEventTypesForSource = useCallback(async (sourceId) => {
    try {
      // Aggiungiamo timestamp per evitare cache
      const timestamp = new Date().getTime();
      // Chiama il server PDK invece del server principale
      const response = await axios.get(`${PDK_SERVER_BASE_URL}/api/event-sources/${sourceId}/events?t=${timestamp}`);
      console.log(`[useEventSources] Events for ${sourceId}:`, response.data);
      
      const eventTypesData = response.data.eventTypes || response.data || [];
      
      // Converte la struttura dei dati dal server alla struttura attesa dal componente
      const convertedEventTypes = eventTypesData.map(eventType => ({
        type: eventType.id || eventType.type,
        label: eventType.name || eventType.label,
        description: eventType.description,
        sourceId: eventType.sourceId || sourceId,
        sourceName: eventType.sourceName
      }));
      
      console.log(`[useEventSources] Converted events for ${sourceId}:`, convertedEventTypes);
      return convertedEventTypes;
    } catch (err) {
      console.error(`Errore nel caricamento eventi per ${sourceId}:`, err);
      return [];
    }
  }, []);

  // Carica dettagli di una sorgente specifica
  const loadEventSource = useCallback(async (sourceId) => {
    try {
      // Chiama il server PDK invece del server principale
      const response = await axios.get(`${PDK_SERVER_BASE_URL}/api/event-sources/${sourceId}`);
      return response.data;
    } catch (err) {
      console.error(`Errore nel caricamento sorgente ${sourceId}:`, err);
      return null;
    }
  }, []);

  useEffect(() => {
    console.log('[useEventSources] Hook initialized, calling loadEventSources and loadAllEventTypes');
    loadEventSources();
    loadAllEventTypes();
  }, [loadEventSources, loadAllEventTypes]);

  return {
    eventSources,
    eventTypes,
    sourcesLoading,
    sourcesError,
    loadEventSources,
    loadAllEventTypes,
    loadEventTypesForSource,
    loadEventSource
  };
};

export default useEventSources;
