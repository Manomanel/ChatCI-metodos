from datetime import datetime
import os
from business.report_generator import ReportGenerator

class LoginTxtReportGenerator(ReportGenerator):
    """
    Gera apenas o relatório de login em texto (TXT).
    """

    def __init__(self):
        self.data = None

    def collectData(self, user):
        # pega username de objeto ou dict
        if isinstance(user, dict):
            username = user.get('username', 'desconhecido')
        else:
            username = getattr(user, 'username', 'desconhecido')
        self.data = (
            f"Usuário {username} efetuou login em "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

    def formatData(self):
        # para TXT basta o texto puro
        return self.data

    def saveReport(self):
        # anexa uma linha ao arquivo login_report.txt
        with open('login_report.txt', 'a', encoding='utf-8') as file:
            file.write(self.formatData() + '\n')
