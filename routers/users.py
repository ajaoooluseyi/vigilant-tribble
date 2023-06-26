from dependencies import engine, get_db
from models import Base, User
import schemas
import services
from sqlalchemy.orm import Session

from fastapi import Body, Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Users"])


@router.get("/", response_model=list[schemas.UserSchema], status_code=status.HTTP_200_OK)
def read_users(session: Session = Depends(get_db)):
    users = services.get_users(session)

    return users


@router.post(
    "/signup", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED
)
def signup(payload: schemas.UserCreate = Body(), session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = services.get_password_hash(payload.password)
    user = User(username=payload.username, hashed_password=hashed_password)
    return services.create_user(session, user=user)


@router.post("/login", response_model=schemas.Token, status_code=status.HTTP_202_ACCEPTED)
def login(
    payload: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    user = services.authenticate_user(payload.username, payload.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = services.create_access_token(
        data={"sub": user.username}, expires_delta=services.access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme)):
    services.revoked_tokens.add(token)
    return {"Success": "Logged out successfully"}


