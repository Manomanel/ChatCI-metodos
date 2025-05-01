from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    """
    Classe abstrata para geração de relatórios.
    Define o Template Method.
    """

    def generateReport(self, user=None):
        """
        Template Method que define a sequência de passos para gerar o relatório.
        """
        self.collectData(user)
        self.formatData()
        self.saveReport()

    @abstractmethod
    def collectData(self, user=None):
        """
        Método para coletar os dados que serão usados no relatório.
        """
        pass

    @abstractmethod
    def formatData(self):
        """
        Método para formatar os dados coletados.
        """
        pass

    @abstractmethod
    def saveReport(self):
        """
        Método para salvar o relatório gerado.
        """
        pass
