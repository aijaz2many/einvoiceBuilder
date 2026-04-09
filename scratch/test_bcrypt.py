from app.core.security import get_password_hash, verify_password
import bcrypt

print(f"Bcrypt version: {getattr(bcrypt, '__version__', 'unknown')}")
print(f"Bcrypt has __about__: {hasattr(bcrypt, '__about__')}")

try:
    password = "testpassword123"
    hashed = get_password_hash(password)
    print(f"Hashed: {hashed}")
    matches = verify_password(password, hashed)
    print(f"Matches: {matches}")
    if matches:
        print("Bcrypt is working correctly with passlib.")
    else:
        print("Verification failed!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
