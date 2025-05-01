from datetime import datetime
from business.report_generator import ReportGenerator

class LoginReportGenerator(ReportGenerator):
    """
    Subclasse de ReportGenerator para gerar relatórios de login dos usuários.
    """

    def __init__(self):
        self.data = None

    def collectData(self, user):
       # Suporta tanto objeto com .username quanto dict
        if isinstance(user, dict):
           username = user.get('username', 'desconhecido')
        else:
            username = getattr(user, 'username', 'desconhecido')
        self.data = f"Usuário {username} efetuou login em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def formatData(self):
        """
        Formata os dados coletados (nesse caso, apenas retorna o texto).
        """
        return self.data

    def saveReport(self):
        """
        Salva o relatório em um arquivo .txt chamado 'login_report.txt'.
        """
        with open('login_report.txt', 'a', encoding='utf-8') as file:
            file.write(self.formatData() + '\n')
