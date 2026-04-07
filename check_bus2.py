from app.core.supabase_client import supabase

def check_business_2():
    print("Checking Business ID 2...")
    res = supabase.table("epay_business").select("*").eq("businessId", 2).execute()
    if not res.data:
        print("❌ Business 2 not found.")
    else:
        bus = res.data[0]
        print(f"✅ Business 2 found: {bus['businessName']}")
        print(f"📊 Template Status: {bus['templateStatus']}")
        
        # Check storage
        try:
            files = supabase.storage.from_("invoice-builder").list(str(2))
            filenames = [f['name'] for f in files] if files else []
            print(f"📁 Files in storage for business 2: {filenames}")
        except Exception as e:
            print(f"❌ Storage check failed: {str(e)}")

if __name__ == "__main__":
    check_business_2()
