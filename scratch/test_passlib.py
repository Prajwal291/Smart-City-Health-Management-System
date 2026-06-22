from passlib.context import CryptContext
import bcrypt

print(f"Bcrypt version: {bcrypt.__version__}")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("test")
    print(f"Hashed: {hashed}")
    verified = pwd_context.verify("test", hashed)
    print(f"Verified: {verified}")
except Exception as e:
    print(f"Error: {e}")
