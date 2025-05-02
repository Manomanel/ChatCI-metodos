from datetime import datetime
import os
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
        Salva o relatório em:
         - login_report.txt (anexando uma linha)
         - login_report.html (anexando um <p> dentro de um arquivo HTML)
        """
        # Prepara o conteúdo em texto
        report_text = self.formatData() + '\n'
        # Salva no TXT
        with open('login_report.txt', 'a', encoding='utf-8') as file:
            file.write(report_text)

        # Prepara a entrada em HTML
        entry_html = f"<p>{self.formatData()}</p>\n"
        html_file = 'login_report.html'

        # Se não existir, cria o esqueleto do HTML e já adiciona a primeira entrada
        if not os.path.exists(html_file):
            with open(html_file, 'w', encoding='utf-8') as hf:
                hf.write("<!DOCTYPE html>\n")
                hf.write("<html lang='pt-BR'>\n<head>\n")
                hf.write("  <meta charset='UTF-8'>\n")
                hf.write("  <title>Relatório de Login</title>\n")
                hf.write("</head>\n<body>\n")
                hf.write(entry_html)
                hf.write("</body>\n</html>")
        else:
            # Se já existe, insere antes de </body>
            with open(html_file, 'r+', encoding='utf-8') as hf:
                content = hf.read()
                idx = content.rfind("</body>")
                if idx != -1:
                    new_content = content[:idx] + entry_html + content[idx:]
                    hf.seek(0)
                    hf.write(new_content)
                    hf.truncate()
                else:
                    # fallback: apenda ao final
                    hf.seek(0, os.SEEK_END)
                    hf.write(entry_html)
