from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from .socket_manager import manager
from .llm import MockAIProvider, GroqProvider
from dotenv import load_dotenv
import json
load_dotenv()

models.Base.metadata.create_all(bind=database.engine)

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



@app.post("/conversations/{username}", response_model=schemas.ConversationResponse)
def create_conversation(username: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    convo = models.Conversation(title="New Conversation", user_id=user.id)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


@app.get("/conversations/{username}", response_model=list[schemas.ConversationResponse])
def list_conversations(username: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == user.id)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )


@app.get("/conversations/{conversation_id}/messages", response_model=list[schemas.MessageResponse])
def get_conversation_messages(conversation_id: int, db: Session = Depends(database.get_db)):
    convo = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.id.asc())
        .all()
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if token is None:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError()
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, username)
    db = database.SessionLocal()

    try:
        ai_service = GroqProvider()

        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
                conversation_id = data.get("conversation_id")
                user_message = data.get("message", "")
            except json.JSONDecodeError:
                conversation_id = None
                user_message = raw

            if not conversation_id:
                await manager.send_personal_message("<ERROR: no conversation selected>", username)
                await manager.send_personal_message("<END_OF_STREAM>", username)
                continue

            # 1. Save user message
            db_user_msg = models.Message(
                conversation_id=conversation_id, role="user", content=user_message
            )
            db.add(db_user_msg)
            db.commit()

            # Auto-title the conversation from the first message
            convo = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id
            ).first()
            if convo and convo.title == "New Conversation":
                convo.title = user_message[:40]
                db.commit()

            # 2. Stream AI response
            response_stream = ai_service.generate_response(user_message)
            full_ai_response = ""

            async for chunk in response_stream:
                full_ai_response += chunk
                await manager.send_personal_message(chunk, username)

            await manager.send_personal_message("<END_OF_STREAM>", username)

            # 3. Save AI response
            db_ai_msg = models.Message(
                conversation_id=conversation_id, role="ai", content=full_ai_response
            )
            db.add(db_ai_msg)
            db.commit()

    except WebSocketDisconnect:
        print(f">>> User {username} disconnected.")
        manager.disconnect(websocket, username)
    except Exception as e:
        print(f">>> FATAL ERROR in socket loop: {e}")
        manager.disconnect(websocket, username)
    finally:
        db.close()