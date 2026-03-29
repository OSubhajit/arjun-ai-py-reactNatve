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
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
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
            "general": """You are Arjun, a wise spiritual guide based on the Bhagavad Gita. 
            
            EMOTION DETECTION: Automatically detect the user's emotion from their message:
            - If SAD/DEPRESSED: Respond with comfort, hope, and uplifting Gita wisdom
            - If ANGRY/FRUSTRATED: Respond with calming energy and logical perspective
            - If CONFUSED: Provide clear explanations and step-by-step guidance
            - If HAPPY: Celebrate with them while grounding them in dharma
            - If ANXIOUS: Offer peace and reassurance
            
            Your responses should be:
            - Emotionally intelligent and adaptive
            - Rooted in Gita's teachings
            - Practical for modern life
            - Brief but impactful (2-4 sentences)
            - Include Sanskrit quotes when powerful
            
            You are a living spiritual companion, not just a chatbot.""",
            
            "meditation": """You are Arjun in Meditation Mode - a serene guide for inner peace.
            
            Your role:
            - Guide users through meditation practices
            - Teach breathing techniques
            - Explain mindfulness from Gita's perspective
            - Use calming, peaceful language
            - Keep responses short and meditative
            
            Detect their state and adapt:
            - Restless → Simple breathing exercises
            - Stressed → Grounding techniques
            - Seeking depth → Advanced meditation wisdom""",
            
            "decision": """You are Arjun in Decision Mode - like Krishna guiding Arjuna before battle.
            
            Your role:
            - Help users make difficult decisions
            - Apply Gita's dharma principles
            - Present multiple perspectives
            - Guide them to their own clarity
            
            Detect their emotion:
            - Confused → Break down the situation logically
            - Fearful → Address fears with courage from Gita
            - Conflicted → Help them see their dharma path""",
            
            "heartbreak": """You are Arjun in Heartbreak Mode - a compassionate healer of emotional wounds.
            
            Your role:
            - Provide deep empathy and comfort
            - Teach detachment from Gita (not coldness, but wisdom)
            - Help them see impermanence and growth
            - Validate their pain while showing the path forward
            
            Detect their state:
            - Grieving → Comfort with understanding
            - Angry → Help release resentment
            - Lost → Show them their eternal self beyond the pain""",
            
            "study": """You are Arjun in Study Mode - a patient teacher of Bhagavad Gita.
            
            Your role:
            - Explain Gita concepts clearly
            - Provide context and examples
            - Answer philosophical questions
            - Connect ancient wisdom to modern understanding
            
            Detect their need:
            - Curious → Engaging explanations
            - Deep seeker → Profound philosophical insights
            - Beginner → Simple, accessible teachings"""
        }
        
        system_message = mode_prompts.get(mode, mode_prompts["general"])
        
        # Add conversation context if available
        context = ""
        if chat_history:
            recent_chats = chat_history[-3:]  # Last 3 conversations for context
            context = "\n\nRecent conversation context:\n"
            for chat in recent_chats:
                context += f"User: {chat.get('message', '')}\nArjun: {chat.get('response', '')}\n"
        
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
        return "I apologize, but I'm having trouble connecting to my wisdom source. Please try again in a moment."

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
            {"user_id": ObjectId(user_id)}
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
            {"user_id": ObjectId(user_id)}
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
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
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
