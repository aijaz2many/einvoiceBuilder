from app.core.supabase_client import supabase

def check_setup():
    print("Checking current status...")
    
    # Check business 1
    bus = supabase.table("epay_business").select("*").eq("businessId", 1).execute()
    if not bus.data:
        print("❌ Business ID 1 not found. Please create a business first.")
    else:
        print(f"✅ Business 1 found: {bus.data[0]['businessName']}")

    # Check Storage Buckets
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        print(f"Current buckets: {bucket_names}")
        
        if "invoice-builder" not in bucket_names:
            print("❌ Bucket 'invoice-builder' not found!")
            print("Attempting to create bucket...")
            try:
                supabase.storage.create_bucket("invoice-builder", options={"public": True})
                print("✅ Bucket 'invoice-builder' created successfully!")
            except Exception as e:
                print(f"❌ Failed to create bucket: {str(e)}")
                print("Please create it manually in Supabase Dashboard -> Storage.")
        else:
            print("✅ Bucket 'invoice-builder' exists.")
            
    except Exception as e:
        print(f"❌ Could not access Storage: {str(e)}")

if __name__ == "__main__":
    check_setup()
