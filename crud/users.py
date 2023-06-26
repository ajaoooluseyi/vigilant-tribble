import models
import schemas
from sqlalchemy.orm import Session


class UserCRUD:
    def __init__(self, session: Session) -> None:
        self.db = session

    def get_user(self, username: str):
        return self.db.query(models.User).filter(models.User.username == username).first()


    def get_users(self):
        return self.db.query(models.User).all()


    def create_user(self, user: schemas.UserCreate):
        db_user = models.User(username=user.username, hashed_password=user.hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
