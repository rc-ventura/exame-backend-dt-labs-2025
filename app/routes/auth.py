from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

#  Create a new user
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    username_normalized = user.username.strip().lower()

    # Check if the user already exists
    existing_user = db.query(User).filter(User.username == username_normalized).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    # Minimum password length rule
    if len(user.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

    #  Create user
    new_user = User(username=username_normalized, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(id=new_user.id, username=new_user.username)

#  Authentication endpoint (login)
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(user: UserLogin, db: Session = Depends(get_db)):
    username_normalized = user.username.strip().lower()

    #  Look for the user in the database
    db_user = db.query(User).filter(User.username == username_normalized).first()

    #  Check credentials
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    #  Create JWT token
    access_token_expires = timedelta(minutes=30)
    token = create_access_token({"sub": db_user.username}, expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer"}
