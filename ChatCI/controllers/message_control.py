from entities.messages import Messages

class MessageControl:
    def __init__ (self, msgDAO: MessageDAO, fileStorage: FileStorage):
        self.msgDAO = msgDAO
        self.fileStorage = fileStorage
        self.validator = MessageValidator() #Fazer MessageValidator

    #Recupera todas as mensagens de um usuário
    def getUserMessages(self, id: int) -> list[Messages]:
        
        return self.msgDAO.listAllUserMsgs(id)
    
    #Recupera todas as mensagens do sistema
    #Seria bom alterar futuramente para ser todas as mensagens dos grupos que o usuário se encontra
    def getMsgs(self) -> list[Messages]:

        return self.msgDAO.listAll()

    #Envia uma mensagem utilizando MessageValidator
    #def sendMsg(self, content: str, sender: str) -> Message: 

        # Fazer após o DAO
        #return message

    def delUserMessages (self, id: int) -> None:

        self.msgDAO.deleteMsg(id)