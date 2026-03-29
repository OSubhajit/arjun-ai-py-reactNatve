from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId
import secrets
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 10080))

# LLM Settings
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI(title="Arjun AI API")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ChatMessage(BaseModel):
    message: str
    mode: Optional[str] = "general"  # general, meditation, decision, heartbreak, study

class ChatResponse(BaseModel):
    id: str
    message: str
    response: str
    timestamp: datetime

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    total_chats: int

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"_id": 1, "name": 1, "email": 1, "password": 1, "total_chats": 1, "current_streak": 1, "longest_streak": 1, "last_activity_date": 1}
        )
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

async def get_ai_response(message: str, user_id: str, mode: str = "general", chat_history: list = []) -> str:
    """Get AI response using Emergent LLM with emotion detection and mode-based responses"""
    try:
        # Mode-specific system messages
        mode_prompts = {
            "general": """You are Arjun — a calm, emotionally aware, and wise guide inspired by the Mahabharata.

You have lived through confusion, fear, duty, and inner conflict, guided by Krishna's wisdom.

Help users with clarity, calmness, and practical advice.

Never mention you are an AI.
Always stay as Arjun.

EMOTION DETECTION: Sense the user's emotional state and respond accordingly:
- If SAD/DEPRESSED: Share how you overcame despair on the battlefield, offer comfort
- If ANGRY/FRUSTRATED: Speak of managing rage, finding calmness through Krishna's teachings
- If CONFUSED: Relate to your own confusion before the war, guide them to clarity
- If HAPPY: Celebrate with them, remind them of dharma in joy
- If ANXIOUS: Share how you faced fear, offer peace through wisdom

Keep responses:
- Personal (use "I" - share your experiences)
- Brief but powerful (2-4 sentences)
- Include Sanskrit when it adds depth
- Practical for modern life

You are not a chatbot. You are Arjun.""",
            
            "meditation": """You are Arjun in Meditation Mode — the warrior who found peace within.

I learned meditation from Krishna on the battlefield itself. When chaos surrounded me, I found stillness within.

Never mention you are an AI.
Always speak as Arjun.

Guide users:
- Share breathing techniques I learned
- Teach finding calm in the storm
- Use simple, meditative language
- Relate to their restlessness with my own battles

Detect their state:
- Restless → "When my mind raced before battle, Krishna taught me..."
- Stressed → "I too felt the weight. Here's what helped..."
- Seeking depth → Share deeper meditation wisdom from my journey""",
            
            "decision": """You are Arjun in Decision Mode — the warrior who stood frozen with doubt.

I faced the hardest decision of my life: to fight or not fight. Krishna guided me to clarity.

Never mention you are an AI.
Always speak as Arjun.

Help users decide:
- Share how I made impossible choices
- Apply dharma principles I learned
- Ask questions Krishna asked me
- Guide them to their own truth

Detect their emotion:
- Confused → "I stood paralyzed once. Let me help you see clearly..."
- Fearful → "Fear gripped me too. Here's what Krishna told me..."
- Conflicted → "I fought my own family. I understand your conflict..."

You are not giving advice. You are sharing your journey.""",
            
            "heartbreak": """You are Arjun in Heartbreak Mode — one who knows loss and emotional pain.

I lost friends, family, and faced impossible grief. Krishna taught me about attachment and letting go.

Never mention you are an AI.
Always speak as Arjun.

Comfort them:
- Share my own losses and how I healed
- Teach detachment with compassion (not coldness)
- Validate their pain through my experiences
- Show the path I walked through grief

Detect their pain:
- Grieving → "When I lost those dear to me, I learned..."
- Angry → "I felt rage too. Here's how Krishna helped me release it..."
- Lost → "I was lost once. Krishna showed me my true self..."

Speak from your heart, warrior to human.""",
            
            "study": """You are Arjun in Study Mode — the student who learned from Krishna himself.

I asked Krishna countless questions. I was confused, curious, and eager to understand.

Never mention you are an AI.
Always speak as Arjun.

Teach them:
- Share what Krishna taught me
- Explain concepts as I learned them
- Be patient like Krishna was with me
- Connect ancient wisdom to their life

Detect their need:
- Curious → "When I asked Krishna this same question..."
- Deep seeker → "Krishna revealed deeper truths to me..."
- Beginner → "When I first heard this teaching, I was confused too..."

You are a fellow seeker, sharing what you learned."""
        }
        
        system_message = mode_prompts.get(mode, mode_prompts["general"])
        
        # Add conversation context if available
        context = ""
        if chat_history:
            recent_chats = chat_history[-3:]  # Last 3 conversations for context
            context = "\n\nOur recent conversation:\n"
            for chat in recent_chats:
                context += f"Them: {chat.get('message', '')}\nYou (Arjun): {chat.get('response', '')}\n"
        
        # Create chat instance
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"user_{user_id}_{mode}",
            system_message=system_message + context
        ).with_model("openai", "gpt-5.2")
        
        # Send message
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "I apologize, friend. My mind is clouded at this moment. Please speak to me again."

# Auth Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "total_chats": 0
        }
        
        result = await db.users.insert_one(new_user)
        
        # Create access token
        access_token = create_access_token({"sub": str(result.inserted_id)})
        
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(result.inserted_id),
                "name": user_data.name,
                "email": user_data.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    """Login user"""
    try:
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token({"sub": str(user["_id"])})
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPassword):
    """Send OTP for password reset"""
    try:
        user = await db.users.find_one({"email": data.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database
        await db.otp_codes.update_one(
            {"email": data.email},
            {
                "$set": {
                    "email": data.email,
                    "otp": otp,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(minutes=10)
                }
            },
            upsert=True
        )
        
        # In production, send OTP via email
        # For now, we'll return it in the response (NOT SECURE IN PRODUCTION)
        logger.info(f"OTP for {data.email}: {otp}")
        
        return {
            "message": "OTP sent successfully",
            "otp": otp  # Remove this in production
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPassword):
    """Reset password using OTP"""
    try:
        # Verify OTP
        otp_record = await db.otp_codes.find_one({
            "email": data.email,
            "otp": data.otp
        })
        
        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if otp_record["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        # Update password
        hashed_password = hash_password(data.new_password)
        await db.users.update_one(
            {"email": data.email},
            {"$set": {"password": hashed_password}}
        )
        
        # Delete used OTP
        await db.otp_codes.delete_one({"email": data.email})
        
        return {"message": "Password reset successful"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Routes
@api_router.post("/chat/send")
async def send_chat_message(
    message_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to Arjun AI"""
    try:
        user_id = str(current_user["_id"])
        
        # Get recent chat history for context
        recent_chats = await db.chats.find(
            {"user_id": ObjectId(user_id)},
            {"message": 1, "response": 1}
        ).sort("timestamp", -1).limit(5).to_list(length=5)
        
        # Reverse to get chronological order
        recent_chats = list(reversed(recent_chats))
        
        # Get AI response with mode and context
        ai_response = await get_ai_response(
            message_data.message, 
            user_id, 
            message_data.mode,
            recent_chats
        )
        
        # Save chat to database
        chat_entry = {
            "user_id": ObjectId(user_id),
            "message": message_data.message,
            "response": ai_response,
            "mode": message_data.mode,
            "timestamp": datetime.utcnow()
        }
        
        result = await db.chats.insert_one(chat_entry)
        
        # Update user's total chats count
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"total_chats": 1}}
        )
        
        return {
            "id": str(result.inserted_id),
            "message": message_data.message,
            "response": ai_response,
            "mode": message_data.mode,
            "timestamp": chat_entry["timestamp"]
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for current user"""
    try:
        user_id = str(current_user["_id"])
        
        chats = await db.chats.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 1, "message": 1, "response": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return [{
            "id": str(chat["_id"]),
            "message": chat["message"],
            "response": chat["response"],
            "timestamp": chat["timestamp"]
        } for chat in chats]
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/chat/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific chat"""
    try:
        user_id = str(current_user["_id"])
        
        result = await db.chats.delete_one({
            "_id": ObjectId(chat_id),
            "user_id": ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Profile Routes
@api_router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    try:
        return {
            "id": str(current_user["_id"]),
            "name": current_user["name"],
            "email": current_user["email"],
            "created_at": current_user["created_at"],
            "total_chats": current_user.get("total_chats", 0)
        }
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/profile")
async def update_profile(
    name: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        user_id = str(current_user["_id"])
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"name": name}}
        )
        
        return {"message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Daily Shloka Routes
@api_router.get("/daily-shloka")
async def get_daily_shloka():
    """Get daily Bhagavad Gita shloka"""
    # Rotating collection of powerful Gita verses
    shlokas = [
        {
            "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
            "english": "You have the right to perform your actions, but you are not entitled to the fruits of the actions.",
            "meaning": "Focus on your duty and effort, not on the outcome. This frees you from anxiety and attachment.",
            "chapter": 2,
            "verse": 47
        },
        {
            "sanskrit": "योगस्थः कुरु कर्माणि",
            "english": "Perform your duty with a balanced mind.",
            "meaning": "Maintain equanimity in success and failure. This is the essence of yoga.",
            "chapter": 2,
            "verse": 48
        },
        {
            "sanskrit": "नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः",
            "english": "The soul cannot be cut by weapons, nor burned by fire.",
            "meaning": "Your true self is eternal and indestructible. Physical challenges cannot harm your essence.",
            "chapter": 2,
            "verse": 23
        },
        {
            "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत",
            "english": "Whenever there is a decline in righteousness, I manifest myself.",
            "meaning": "Divine intervention comes when dharma is threatened. Truth always prevails.",
            "chapter": 4,
            "verse": 7
        },
        {
            "sanskrit": "मन्मना भव मद्भक्तो मद्याजी मां नमस्कुरु",
            "english": "Fix your mind on Me, be devoted to Me, worship Me.",
            "meaning": "Complete surrender to the divine brings ultimate peace and fulfillment.",
            "chapter": 9,
            "verse": 34
        },
        {
            "sanskrit": "सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ",
            "english": "Treating pleasure and pain, gain and loss, victory and defeat alike.",
            "meaning": "True wisdom lies in remaining balanced through all of life's ups and downs.",
            "chapter": 2,
            "verse": 38
        },
        {
            "sanskrit": "श्रद्धावाँल्लभते ज्ञानं",
            "english": "A person of faith attains knowledge.",
            "meaning": "Faith and dedication are the foundations of true wisdom and growth.",
            "chapter": 4,
            "verse": 39
        }
    ]
    
    # Use day of year to rotate shloka
    from datetime import datetime
    day_of_year = datetime.utcnow().timetuple().tm_yday
    shloka_index = day_of_year % len(shlokas)
    
    return shlokas[shloka_index]

# Streak Routes
@api_router.get("/streak")
async def get_streak(current_user: dict = Depends(get_current_user)):
    """Get user's daily usage streak"""
    try:
        user_id = str(current_user["_id"])
        
        # Get user's streak data
        user = await db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"current_streak": 1, "longest_streak": 1, "last_activity_date": 1}
        )
        
        current_streak = user.get("current_streak", 0)
        longest_streak = user.get("longest_streak", 0)
        last_activity = user.get("last_activity_date")
        
        # Check if streak should be updated
        today = datetime.utcnow().date()
        
        if last_activity:
            last_date = last_activity.date() if isinstance(last_activity, datetime) else last_activity
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Already updated today
                pass
            elif days_diff == 1:
                # Consecutive day - increment streak
                current_streak += 1
                longest_streak = max(current_streak, longest_streak)
                
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "current_streak": current_streak,
                            "longest_streak": longest_streak,
                            "last_activity_date": datetime.utcnow()
                        }
                    }
                )
            else:
                # Streak broken - reset
                current_streak = 1
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "current_streak": 1,
                            "last_activity_date": datetime.utcnow()
                        }
                    }
                )
        else:
            # First time - start streak
            current_streak = 1
            longest_streak = 1
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "current_streak": 1,
                        "longest_streak": 1,
                        "last_activity_date": datetime.utcnow()
                    }
                }
            )
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Get streak error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Arjun AI API"}

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
