from interface.interfaces import IMediator, IComponent
from commands.commands import ScrapeCommand, CreateGroupCommand, SendMessageCommand
from typing import Dict, Any, List
import logging

logger = logging.getLogger('mediator')

class Mediator(IMediator):
    def __init__(self):
        self.components = {}
        self.group_dao = None
        self.message_dao = None
    
    def set_daos(self, group_dao, message_dao):
        self.group_dao = group_dao
        self.message_dao = message_dao
    
    def register_component(self, name: str, component: IComponent):
        self.components[name] = component
        component.set_mediator(self)
    
    def notify(self, event: str, data: Dict = None) -> Any:
        if event == "SCRAPE_SACI":
            return self._handle_scrape(data)
        elif event == "CREATE_GROUPS":
            return self._handle_create_groups(data)
        elif event == "SEND_MESSAGE":
            return self._handle_send_message(data)
        elif event == "RUN_INTEGRATION":
            return self._handle_integration()
        else:
            logger.warning(f"Unknown event: {event}")
            return None
    
    def _handle_scrape(self, data: Dict) -> List[Dict]:
        url = data.get('url', 'https://sa.ci.ufpb.br/salas/ci')
        command = ScrapeCommand(url)
        return command.execute()
    
    def _handle_create_groups(self, data: Dict) -> Dict:
        turmas = data.get('turmas', [])
        results = {"created": 0, "existing": 0, "errors": 0}
        
        for turma in turmas:
            try:
                command = CreateGroupCommand(self.group_dao, turma)
                result = command.execute()
                
                if result["status"] == "created":
                    results["created"] += 1
                    self.notify("SEND_MESSAGE", {
                        "group_id": result["group_id"],
                        "user_id": 1,
                        "text": f"Bem-vindos ao grupo da disciplina {turma['nome']}!"
                    })
                else:
                    results["existing"] += 1
            except Exception as e:
                logger.error(f"Error creating group: {e}")
                results["errors"] += 1
        
        return results
    
    def _handle_send_message(self, data: Dict) -> int:
        command = SendMessageCommand(
            self.message_dao,
            data['group_id'],
            data['user_id'],
            data['text']
        )
        return command.execute()
    
    def _handle_integration(self) -> Dict:
        turmas = self.notify("SCRAPE_SACI", {"url": "https://sa.ci.ufpb.br/salas/ci"})
        
        results = self.notify("CREATE_GROUPS", {"turmas": turmas})
        
        return {
            "turmas_found": len(turmas),
            "groups_created": results["created"],
            "groups_existing": results["existing"],
            "errors": results["errors"]
        }