class User:
    def __init__ (self, userid: int, username: str, email: str, password: str, first_name: str, last_name: str, student: bool, professor: bool, email_verified: bool, is_staff: bool, is_superuser: bool):
        self.userid = userid
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.student = student
        self.professor = professor
        self.email_verified = email_verified
        self.is_staff = is_staff
        self.is_superuser = is_superuser