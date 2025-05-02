from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from business.report_generator import ReportGenerator

class LoginPdfReportGenerator(ReportGenerator):
    """
    Gera relatório de login em PDF usando ReportLab.
    """

    def __init__(self):
        self.data = None

    def collectData(self, user):
        # Mesma lógica para extrair usuário e timestamp
        if isinstance(user, dict):
            username = user.get('username', 'desconhecido')
        else:
            username = getattr(user, 'username', 'desconhecido')
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.data = f"Usuário {username} efetuou login em {timestamp}"

    def formatData(self):
        # devolve uma lista de linhas (poderia ser só uma, mas facilita extensão)
        return [self.data]

    def saveReport(self):
        lines = self.formatData()
        pdf_path = 'login_report.pdf'
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        y = height - 50  # margem superior
        for linha in lines:
            if y < 50:    # margem inferior, nova página
                c.showPage()
                y = height - 50
            c.drawString(50, y, linha)
            y -= 15      # espaçamento entre linhas

        c.save()
        print(f"PDF gerado com sucesso em: {os.path.abspath(pdf_path)}")
