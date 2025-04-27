from interface.interfaces import IComponent
from typing import Dict, Any

class SACIBotComponent(IComponent):
    def process_event(self, event: str, data: Dict) -> Any:
        if event == "SCRAPE":
            return self._mediator.notify("SCRAPE_SACI", data)
        return None

class GroupManagerComponent(IComponent):
    def process_event(self, event: str, data: Dict) -> Any:
        if event == "CREATE":
            return self._mediator.notify("CREATE_GROUPS", data)
        return None

class MessageManagerComponent(IComponent):
    def process_event(self, event: str, data: Dict) -> Any:
        if event == "SEND":
            return self._mediator.notify("SEND_MESSAGE", data)
        return None