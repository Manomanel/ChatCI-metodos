from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import subprocess
import os
import json
import re
from datetime import datetime
from database.persistence.group_persistence import GroupPersistence
from database.factory.user_dao_factory import UserDAOFactory
from database.persistence.message_persistence import MessagePersistence
from services.message_service import MessageService

class SACIBot:
    def __init__(self):
        self.group_dao = GroupPersistence()
        self.user_dao = UserDAOFactory.get_instance()
        self.message_dao = MessagePersistence()
        self.message_service = MessageService()
        
    def abrir_browser(self):
        """Inicializa e abre o navegador Chrome"""
        os.system("taskkill /f /im chrome.exe")
        sleep(3)
        subprocess.Popen(
            '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --log-level=3 --remote-debugging-port=9222',
            shell=True,
        )
        sleep(1)
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--no-sandbox")
        self.browser = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=self.options
        )
        self.browser.get("https://sa.ci.ufpb.br/salas/ci")

    def fechar_browser(self):
        """Fecha o navegador"""
        self.browser.quit()

    def extrair_turmas_saci(self):
        """Extrai dados das turmas do SACI"""
        self.esperar_elemento("pa-8", 10, "class")
        sleep(2)
        elements = self.browser.find_elements(By.CSS_SELECTOR, "tr")

        turmas = []

        for element in elements:
            tds = element.find_elements(By.CSS_SELECTOR, "td")
            if len(tds) == 8:
                turma = {
                    "code": tds[0].text,
                    "turma": tds[1].text,
                    "nome": tds[2].text,
                    "hora": tds[3].text,
                    "alunos": tds[4].text,
                    "departamento": tds[5].text,
                    "sala": tds[6].text,
                    "professor": tds[7].text,
                }
                turmas.append(turma)

        # Salva os dados em um arquivo JSON
        with open("turmas_saci.json", "w", encoding="UTF-8") as arq:
            json.dump(turmas, arq, indent=4, ensure_ascii=False)
        
        return turmas

    def criar_grupos_saci(self, turmas):
        """
        Cria grupos no sistema baseados nas turmas do SACI
        """
        created_groups = []
        existing_groups = []
        
        for turma in turmas:
            group_name = f"SACI - {turma['code']} - {turma['nome']} (T{turma['turma']})"

            description = f"Turma do SACI - {turma['nome']}\n"
            description += f"Código: {turma['code']}\n"
            description += f"Turma: {turma['turma']}\n"
            description += f"Professor: {turma['professor']}\n"
            description += f"Horário: {turma['hora']}\n"
            description += f"Sala: {turma['sala']}\n"
            description += f"Departamento: {turma['departamento']}\n"
            description += f"Alunos inscritos: {turma['alunos']}"
            
            # Verifica se o grupo já existe
            existing_group = self.group_dao.get_group_by_name(group_name)
            
            if not existing_group:
                try:
                    group_id = self.group_dao.create_group(group_name, description)

                    self.message_service.send_group_welcome_message(group_id)

                    self._adicionar_professor_ao_grupo(group_id, turma['professor'])
                    
                    created_groups.append({
                        "id": group_id,
                        "name": group_name,
                        "turma_data": turma
                    })
                    print(f"Grupo criado: {group_name}")
                except Exception as e:
                    print(f"Erro ao criar grupo {group_name}: {e}")
            else:
                existing_groups.append(group_name)
                print(f"Grupo já existe: {group_name}")
        
        return created_groups, existing_groups

    def _adicionar_professor_ao_grupo(self, group_id, professor_name):
        """
        Tenta adicionar o professor como membro do grupo
        """
        if professor_name and professor_name.strip():
            nome_limpo = re.sub(r'\s+', ' ', professor_name.strip())
            partes_nome = nome_limpo.split()
            
            if len(partes_nome) >= 2:
                first_name = partes_nome[0]
                last_name = ' '.join(partes_nome[1:])
                
                professor = self._buscar_professor(first_name, last_name)
                
                if professor:
                    try:
                        self.group_dao.add_member(group_id, professor['id'])
                        print(f"Professor {nome_limpo} adicionado ao grupo")

                        self.message_service.send_user_added_to_group_message(group_id, professor['id'])
                    except Exception as e:
                        print(f"Erro ao adicionar professor ao grupo: {e}")
                else:
                    print(f"Professor {nome_limpo} não encontrado no sistema")

    def _buscar_professor(self, first_name, last_name):
        """Busca um professor no sistema pelo nome"""
        all_users = self.user_dao.get_all_users()
        
        for user in all_users:
            if user['professor'] and \
               user['first_name'].lower() == first_name.lower() and \
               user['last_name'].lower() == last_name.lower():
                return user
        
        return None

    def enviar_mensagem_inicial_para_novos_usuarios(self):
        """Envia mensagem de boas-vindas para todos os usuários sem mensagens"""
        all_users = self.user_dao.get_all_users()
        
        for user in all_users:
            system_group_name = f"Mensagens do Sistema - {user['username']}"
            system_group = self.group_dao.get_group_by_name(system_group_name)
            
            if not system_group:
                self.message_service.send_welcome_message_to_new_user(user['id'])
                print(f"Mensagem de boas-vindas enviada para {user['username']}")
            else:
                messages = self.message_dao.get_group_messages(system_group['id'], limit=1)
                if not messages:
                    self.message_service.send_welcome_message_to_new_user(user['id'])
                    print(f"Mensagem de boas-vindas enviada para {user['username']}")

    def enviar_aviso_integracao(self):
        """Envia aviso sobre a integração SACI para todos os grupos"""
        system_user_id = 1 
        
        aviso_message = f"""
                **AVISO IMPORTANTE**

                Em {datetime.now().strftime('%d/%m/%Y às %H:%M')}, realizamos uma atualização na integração com o sistema SACI.

                Novidades:
                - Grupos criados automaticamente para cada turma
                - Mensagens de boas-vindas nos grupos
                - Professores adicionados automaticamente aos grupos de suas disciplinas
                """
        
        try:
            self.message_service.broadcast_message_to_all_groups(system_user_id, aviso_message)
            print("Aviso de integração enviado para todos os grupos")
        except Exception as e:
            print(f"Erro ao enviar aviso: {e}")

    def esperar_elemento(self, elemento, tempo, metodo):
        """Espera o elemento ser encontrado na página"""
        try:
            if metodo == "class":
                myElem = WebDriverWait(self.browser, tempo).until(
                    EC.presence_of_element_located((By.CLASS_NAME, elemento))
                )
            elif metodo == "xpath":
                myElem = WebDriverWait(self.browser, tempo).until(
                    EC.presence_of_element_located((By.XPATH, elemento))
                )
            elif metodo == "id":
                myElem = WebDriverWait(self.browser, tempo).until(
                    EC.presence_of_element_located((By.ID, elemento))
                )
            elif metodo == "css":
                myElem = WebDriverWait(self.browser, tempo).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, elemento))
                )
            return myElem
        except TimeoutException:
            print(f"{elemento} ainda não carregou")
            return False

    def executar_integracao_saci(self):
        """Executa o processo completo de integração com o SACI e retorna status"""
        print("Iniciando integração com SACI...")
        
        result = {
            "turmas_encontradas": 0,
            "grupos_criados": 0,
            "grupos_existentes": 0,
            "mensagens_enviadas": 0,
            "errors": []
        }
        
        try:
            print("Acessando SACI...")
            self.abrir_browser()

            print("Extraindo turmas do SACI...")
            turmas = self.extrair_turmas_saci()
            result["turmas_encontradas"] = len(turmas)

            print("Criando grupos no sistema...")
            created_groups, existing_groups = self.criar_grupos_saci(turmas)
            result["grupos_criados"] = len(created_groups)
            result["grupos_existentes"] = len(existing_groups)

            print("Enviando mensagens de boas-vindas...")
            self.enviar_mensagem_inicial_para_novos_usuarios()

            print("Enviando aviso de integração...")
            self.enviar_aviso_integracao()

            print("\nRelatório da Integração:")
            print(f"Turmas encontradas no SACI: {result['turmas_encontradas']}")
            print(f"Grupos criados: {result['grupos_criados']}")
            print(f"Grupos já existentes: {result['grupos_existentes']}")

            relatorio = {
                "data_execucao": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "turmas_encontradas": result["turmas_encontradas"],
                "grupos_criados": result["grupos_criados"],
                "grupos_existentes": result["grupos_existentes"],
                "detalhes_grupos_criados": created_groups
            }
            
            with open("relatorio_integracao_saci.json", "w", encoding="UTF-8") as arq:
                json.dump(relatorio, arq, indent=4, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Erro na integração: {e}"
            print(error_msg)
            result["errors"].append(str(e))
        finally:
            self.fechar_browser()
            print("🏁 Integração finalizada")
            
        return result

def main():
    bot = SACIBot()
    result = bot.executar_integracao_saci()
    return result