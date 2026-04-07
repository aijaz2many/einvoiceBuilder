from app.core.supabase_client import supabase
import sys

def test_connection():
    try:
        print("Testing Supabase connection...")
        # Try to select from epay_users
        res = supabase.table("epay_users").select("*", count="exact").limit(1).execute()
        print("SUCCESS: Connection successful!")
        print(f"Table 'epay_users' exists. Count: {res.count}")
    except Exception as e:
        print(f"FAILED: Connection failed: {str(e)}")
        # Print more details about the exception
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
