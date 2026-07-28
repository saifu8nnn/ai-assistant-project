from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="AI Assistant API")

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. The DB Check (Fail fast to save CPU)
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Hash the password securely using our auth.py logic
    hashed_password = auth.get_password_hash(user.password)
    
    # 3. Create the new user and save to PostgreSQL
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 4. Return the user info (Pydantic automatically filters out the password)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Find the user in the database
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # 2. Authenticate the password using our bcrypt function
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Create the JWT Token (The VIP Pass)
    access_token = auth.create_access_token(data={"sub": user.username})
    
    # 4. Hand the token back to the frontend
    return {"access_token": access_token, "token_type": "bearer"}