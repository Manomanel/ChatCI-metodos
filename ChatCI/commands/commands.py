from interface.interfaces import ICommand
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from typing import List, Dict
import os
import platform

logger = logging.getLogger(__name__)

class ScrapeCommand(ICommand):
    def __init__(self, url: str):
        self.url = url
    
    def execute(self) -> List[Dict]:
        try:
            chrome_options = webdriver.ChromeOptions()

            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            if platform.system() == 'Linux':
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-software-rasterizer')
                chrome_options.add_argument('--window-size=1920,1080')

            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"Failed to initialize with ChromeDriverManager: {e}")

                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception as e2:
                    logger.error(f"Failed to initialize Chrome driver: {e2}")
                    raise Exception("Could not initialize Chrome driver. Please ensure Chrome is installed.")

            driver.get(self.url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pa-8"))
            )
            time.sleep(2)

            rows = driver.find_elements(By.CSS_SELECTOR, "tr")
            turmas = []
            
            for row in rows:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if len(cells) == 8:
                    turma = {
                        "code": cells[0].text,
                        "turma": cells[1].text,
                        "nome": cells[2].text,
                        "hora": cells[3].text,
                        "alunos": cells[4].text,
                        "departamento": cells[5].text,
                        "sala": cells[6].text,
                        "professor": cells[7].text,
                    }
                    turmas.append(turma)

            with open("turmas_saci.json", "w", encoding="UTF-8") as f:
                json.dump(turmas, f, indent=4, ensure_ascii=False)
            
            return turmas
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            if 'driver' in locals():
                driver.quit()

class CreateGroupCommand(ICommand):
    def __init__(self, group_dao, turma_data: Dict):
        self.group_dao = group_dao
        self.turma_data = turma_data
    
    def execute(self) -> Dict:
        group_name = f"SACI - {self.turma_data['code']} - {self.turma_data['nome']} (T{self.turma_data['turma']})"
        
        description = f"""Turma do SACI - {self.turma_data['nome']}
                Código: {self.turma_data['code']}
                Turma: {self.turma_data['turma']}
                Professor: {self.turma_data['professor']}
                Horário: {self.turma_data['hora']}
                Sala: {self.turma_data['sala']}
                Departamento: {self.turma_data['departamento']}
                Alunos inscritos: {self.turma_data['alunos']}"""

        existing = self.group_dao.get_group_by_name(group_name)
        if existing:
            return {"status": "exists", "group": existing}

        group_id = self.group_dao.create_group(group_name, description)
        return {"status": "created", "group_id": group_id, "name": group_name}

class SendMessageCommand(ICommand):
    def __init__(self, message_dao, group_id: int, user_id: int, text: str):
        self.message_dao = message_dao
        self.group_id = group_id
        self.user_id = user_id
        self.text = text
    
    def execute(self) -> int:
        return self.message_dao.create_message(self.group_id, self.user_id, self.text)