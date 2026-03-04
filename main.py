from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import asyncio
import certifi
from dotenv import load_dotenv

from routes import auth, users, reports, tasks, dashboard, leaves, password_reset, upload, export

load_dotenv()

# MongoDB connection
mongodb_client = None
database = None

async def create_mongodb_client():
    """Create MongoDB client with Windows SSL compatibility"""
    uri = os.getenv("MONGODB_URI")
    
    if not uri:
        print("[ERROR] MONGODB_URI not found in environment variables")
        return None

    # Try multiple connection strategies
    strategies = [
        {
            "name": "Standard SSL with certifi",
            "params": {
                "tls": True,
                "tlsCAFile": certifi.where(),
                "serverSelectionTimeoutMS": 5000,
            }
        },
        {
            "name": "TLS without certificate verification (Fix for Windows SSL Issues)",
            "params": {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 5000,
            }
        },
        {
            "name": "TLS Insecure mode",
            "params": {
                "tlsInsecure": True,
                "serverSelectionTimeoutMS": 5000,
            }
        },
        {
            "name": "Direct connection without TLS verification",
            "params": {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "tlsAllowInvalidHostnames": True,
                "directConnection": False,
                "serverSelectionTimeoutMS": 5000,
            }
        }
    ]
    
    last_error = ""
    for strategy in strategies:
        try:
            print(f"[INFO] Trying: {strategy['name']}...")
            client = AsyncIOMotorClient(uri, **strategy['params'])
            # The ping command is the most reliable way to check connection
            await asyncio.wait_for(client.admin.command('ping'), timeout=5.0)
            print(f"[SUCCESS] MongoDB connected using: {strategy['name']}")
            return client
        except Exception as e:
            last_error = str(e)
            print(f"[FAILED] {strategy['name']}: {last_error[:100]}...")
            continue
    
    # If all strategies fail, provide helpful error message
    print("\n" + "="*60)
    print("ERROR: Could not connect to MongoDB Atlas")
    print(f"Last Error: {last_error}")
    print("="*60)
    print("\nPossible causes:")
    print("1. IP address not whitelisted in MongoDB Atlas (check Network Access)")
    print("2. MongoDB Atlas cluster is paused or not running")
    print("3. Incorrect credentials in .env file (check username/password)")
    print("4. Network/firewall blocking connection on port 27017")
    print("5. Windows SSL/TLS compatibility issue with Python 3.12")
    print("\nSolutions:")
    print("1. Add '0.0.0.0/0' to Network Access in Atlas for testing")
    print("2. Check MongoDB Atlas dashboard - ensure cluster is running")
    print("3. Verify MONGODB_URI in .env file looks like: mongodb+srv://user:pass@cluster...")
    print("="*60 + "\n")
    
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongodb_client, database
    try:
        mongodb_client = await create_mongodb_client()
        
        if mongodb_client:
            database = mongodb_client.molecule_workflow
            app.mongodb_client = mongodb_client
            app.database = database
            print("[SUCCESS] Application startup complete with database")
        else:
            # Server starts without database
            app.mongodb_client = None
            app.database = None
            print("[WARNING] Application started WITHOUT database connection")
            print("[WARNING] Database-dependent endpoints will return errors")
        
    except Exception as e:
        print(f"[ERROR] Startup error: {e}")
        # Don't raise - allow server to start
        app.mongodb_client = None
        app.database = None
        print("[WARNING] Server starting in limited mode (no database)")
    
    yield
    
    # Shutdown
    if mongodb_client:
        mongodb_client.close()
        print("[INFO] Disconnected from MongoDB")

app = FastAPI(title="Molecule WorkFlow Pro API", lifespan=lifespan)

# CORS middleware - Allow your production domain
origins = [
    "https://reporting.webconferencesolutions.com",
    "*"  # Allow all for development - remove in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(leaves.router, prefix="/api", tags=["Leaves"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(password_reset.router, prefix="/api/auth", tags=["Password Reset"])
app.include_router(export.router, prefix="/api", tags=["Export"])

@app.get("/")
async def root():
    return {"message": "Molecule WorkFlow Pro API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
