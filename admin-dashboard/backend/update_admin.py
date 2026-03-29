import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def update_admin_credentials():
    print("🔐 Update Admin Credentials")
    print("-" * 50)
    
    # Get new credentials from user
    new_username = input("Enter new username (press Enter to keep 'admin'): ").strip() or "admin"
    new_password = input("Enter new password: ").strip()
    
    if not new_password:
        print("❌ Password cannot be empty!")
        return
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    # Hash the new password
    hashed_password = pwd_context.hash(new_password)
    
    # Update admin credentials
    result = await db.admins.update_one(
        {"role": "super_admin"},  # Find super admin
        {
            "$set": {
                "username": new_username,
                "password": hashed_password
            }
        }
    )
    
    if result.modified_count > 0:
        print("\n✅ Admin credentials updated successfully!")
        print(f"   Username: {new_username}")
        print(f"   Password: {new_password}")
        print("\n⚠️  Please use these credentials to login now!")
    else:
        print("\n❌ Failed to update. Admin might not exist.")
        print("   Try creating a new admin with seed_admin.py")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_admin_credentials())
