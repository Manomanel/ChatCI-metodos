from typing import List, Dict, Any, Optional
from .base_persistence import BasePersistence
import logging
from datetime import date, datetime
from ..dao.event_dao import EventDAO

logger = logging.getLogger('event_dao')

class EventPersistence(BasePersistence, EventDAO):
    """DAO para manipulação da tabela de eventos"""
    
    def create_event(self, title: str, description: str, link: str = "", event_date: date = None) -> int:
        """
        Cria um novo evento
        
        Args:
            title: Título do evento
            description: Descrição do evento
            link: Link relacionado ao evento (opcional)
            event_date: Data do evento
            
        Returns:
            ID do evento criado
        """
        if event_date is None:
            event_date = datetime.now().date()
            
        query = """
        INSERT INTO event (title, description, link, event_date)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        return self._execute_insert_returning_id(query, (title, description, link, event_date))
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um evento pelo ID
        
        Args:
            event_id: ID do evento
            
        Returns:
            Dicionário com os dados do evento ou None se não encontrado
        """
        query = "SELECT * FROM event WHERE id = %s"
        results = self._execute_query(query, (event_id,))
        return results[0] if results else None
    
    def get_events_by_title(self, title: str) -> List[Dict[str, Any]]:
        """
        Busca eventos pelo título (pesquisa parcial)
        
        Args:
            title: Título ou parte do título a ser pesquisado
            
        Returns:
            Lista de eventos encontrados
        """
        query = "SELECT * FROM event WHERE title ILIKE %s ORDER BY event_date DESC"
        return self._execute_query(query, (f'%{title}%',))
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """
        Busca todos os eventos ordenados por data
        
        Returns:
            Lista com todos os eventos
        """
        query = "SELECT * FROM event ORDER BY event_date DESC"
        return self._execute_query(query)
    
    def get_upcoming_events(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Busca eventos futuros
        
        Args:
            limit: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos futuros
        """
        query = """
        SELECT * FROM event 
        WHERE event_date >= CURRENT_DATE
        ORDER BY event_date ASC
        """
        
        if limit is not None:
            query += f" LIMIT {int(limit)}"
            
        return self._execute_query(query)
    
    def get_past_events(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Busca eventos passados
        
        Args:
            limit: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos passados
        """
        query = """
        SELECT * FROM event 
        WHERE event_date < CURRENT_DATE
        ORDER BY event_date DESC
        """
        
        if limit is not None:
            query += f" LIMIT {int(limit)}"
            
        return self._execute_query(query)
    
    def update_event(self, event_id: int, title: str = None, description: str = None, 
                    link: str = None, event_date: date = None) -> bool:
        """
        Atualiza os dados de um evento
        
        Args:
            event_id: ID do evento
            title: Novo título (opcional)
            description: Nova descrição (opcional)
            link: Novo link (opcional)
            event_date: Nova data (opcional)
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        current_event = self.get_event_by_id(event_id)
        if not current_event:
            return False

        updated_title = title if title is not None else current_event['title']
        updated_description = description if description is not None else current_event['description']
        updated_link = link if link is not None else current_event['link']
        updated_date = event_date if event_date is not None else current_event['event_date']
        
        query = """
        UPDATE event 
        SET title = %s, description = %s, link = %s, event_date = %s
        WHERE id = %s
        """
        
        rows_affected = self._execute_update(query, (
            updated_title, updated_description, updated_link, updated_date, event_id
        ))
        
        return rows_affected > 0
    
    def delete_event(self, event_id: int) -> bool:
        """
        Remove um evento
        
        Args:
            event_id: ID do evento a ser removido
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        query = "DELETE FROM event WHERE id = %s"
        rows_affected = self._execute_update(query, (event_id,))
        return rows_affected > 0