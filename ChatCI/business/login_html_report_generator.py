from datetime import datetime
import os
from business.report_generator import ReportGenerator

class LoginHtmlReportGenerator(ReportGenerator):
    """
    Gera apenas o relatório de login em HTML.
    """

    def __init__(self):
        self.data = None

    def collectData(self, user):
        if isinstance(user, dict):
            username = user.get('username', 'desconhecido')
        else:
            username = getattr(user, 'username', 'desconhecido')
        self.data = (
            f"Usuário {username} efetuou login em "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

    def formatData(self):
        # envolve em parágrafo HTML
        return f"<p>{self.data}</p>\n"

    def saveReport(self):
        entry = self.formatData()
        html_file = 'login_report.html'

        if not os.path.exists(html_file):
            # cria esqueleto HTML
            with open(html_file, 'w', encoding='utf-8') as hf:
                hf.write("<!DOCTYPE html>\n<html lang='pt-BR'>\n<head>\n")
                hf.write("  <meta charset='UTF-8'>\n")
                hf.write("  <title>Relatório de Login</title>\n")
                hf.write("</head>\n<body>\n")
                hf.write(entry)
                hf.write("</body>\n</html>")
        else:
            # injeta antes de </body>
            with open(html_file, 'r+', encoding='utf-8') as hf:
                content = hf.read()
                idx = content.rfind("</body>")
                if idx != -1:
                    new_content = content[:idx] + entry + content[idx:]
                    hf.seek(0)
                    hf.write(new_content)
                    hf.truncate()
                else:
                    hf.seek(0, os.SEEK_END)
                    hf.write(entry)
