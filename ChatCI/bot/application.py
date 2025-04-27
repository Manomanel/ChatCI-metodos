import logging
from mediator.mediator import Mediator
from components.components import SACIBotComponent, GroupManagerComponent, MessageManagerComponent
from database.persistence.group_persistence import GroupPersistence
from database.persistence.message_persistence import MessagePersistence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('application')

class SACIApplication:
    def __init__(self):
        self.mediator = Mediator()
        self._setup_components()
    
    def _setup_components(self):
        group_dao = GroupPersistence()
        message_dao = MessagePersistence()
        self.mediator.set_daos(group_dao, message_dao)

        self.mediator.register_component('bot', SACIBotComponent())
        self.mediator.register_component('group_manager', GroupManagerComponent())
        self.mediator.register_component('message_manager', MessageManagerComponent())
    
    def run_integration(self):
        logger.info("Starting SACI integration...")
        result = self.mediator.notify("RUN_INTEGRATION")
        
        logger.info(f"Integration complete:")
        logger.info(f"- Turmas found: {result['turmas_found']}")
        logger.info(f"- Groups created: {result['groups_created']}")
        logger.info(f"- Groups existing: {result['groups_existing']}")
        logger.info(f"- Errors: {result['errors']}")
        
        return result