from database.dao.user_dao import UserDAO
from database.persistence.user_persistence import UserPersistence
import logging

logger = logging.getLogger('user_dao_factory')

class UserDAOFactory:
    """
    Fábrica para criar instâncias de UserDAO
    """
    _instance = None
    _dao_type = 'postgresql'  # Tipo padrão de DAO
    
    @classmethod
    def set_dao_type(cls, dao_type: str) -> None:
        """
        Define o tipo de DAO a ser utilizado
        """
        cls._dao_type = dao_type
        
    @classmethod
    def get_instance(cls) -> UserDAO:
        """
        Retorna uma instância do DAO configurado
        """
        if cls._dao_type == 'postgresql':
            if cls._instance is None:
                cls._instance = UserPersistence()
            return cls._instance
        else:
            raise ValueError(f"Tipo de DAO não suportado: {cls._dao_type}")
        
    @classmethod
    def create_user_dao(cls, dao_type: str = None) -> UserDAO:
        """
        Método factory que cria uma nova instância de UserDAO.
        """
        if dao_type:
            if dao_type == 'postgresql':
                return UserPersistence()
            else:
                raise ValueError(f"Tipo de DAO não suportado: {dao_type}")
        else:
            return cls.get_instance()