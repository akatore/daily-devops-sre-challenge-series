import json
from datetime import datetime

def analyze_buckets(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    buckets = data.get('buckets', [])
    today = datetime.now()
    
    # Data structures for our reports
    cost_report = {}
    deletion_queue = []
    cleanup_queue = []
    archival_candidates = []
    
    print("=========================================================")
    print("1. BUCKET SUMMARY")
    print("=========================================================")
    
    for b in buckets:
        name = b.get('name', 'Unknown')
        region = b.get('region', 'Unknown')
        # Assuming keys are 'sizeGB' and 'lastAccessed' (YYYY-MM-DD)
        size = b.get('sizeGB', 0) 
        versioning = b.get('versioning', False)
        
        # Calculate days unused
        last_accessed_str = b.get('lastAccessed', '2023-01-01') 
        last_accessed_date = datetime.strptime(last_accessed_str, "%Y-%m-%d")
        days_unused = (today - last_accessed_date).days

        # Task 1: Print Summary
        print(f"Name: {name} | Region: {region} | Size: {size}GB | Versioning: {versioning}")

        # Task 2: Identify >80GB and unused 90+ days
        if size > 80 and days_unused >= 90:
            archival_candidates.append({'name': name, 'size': size, 'days': days_unused})

        # Task 3 Prep: Cost Report Grouping
        # Assuming tag is 'team' based on your screenshot, fallback to 'department'
        department = b.get('tags', {}).get('team', b.get('tags', {}).get('department', 'Unknown'))
        
        # Assume standard S3 pricing of $0.023 per GB if no cost field exists
        cost = b.get('cost', size * 0.023) 
        
        if region not in cost_report:
            cost_report[region] = {}
        if department not in cost_report[region]:
            cost_report[region][department] = 0
            
        cost_report[region][department] += cost

        # Task 3 & 4 Prep: Deletion and Cleanup logic
        if size > 100 and days_unused >= 20:
            deletion_queue.append(name)
        elif size > 50:
            cleanup_queue.append(name)

    print("\n=========================================================")
    print("2. BUCKETS > 80GB & UNUSED FOR 90+ DAYS (Archival Targets)")
    print("=========================================================")
    if not archival_candidates:
        print("No buckets match this criteria.")
    for b in archival_candidates:
        print(f"- {b['name']} ({b['size']}GB, untouched for {b['days']} days)")

    print("\n=========================================================")
    print("3. COST REPORT (Grouped by Region & Department)")
    print("=========================================================")
    for region, depts in cost_report.items():
        print(f"Region: {region}")
        for dept, total_cost in depts.items():
            print(f"  - {dept}: ${total_cost:.2f}")

    print("\n=========================================================")
    print("4. ACTION ITEMS & HIGHLIGHTS")
    print("=========================================================")
    print("--- Recommended Cleanup Operations (Size > 50GB) ---")
    for name in cleanup_queue:
        print(f"  * {name} requires cleanup operations.")
        
    print("\n--- Deletion Queue (Size > 100GB & Unused 20+ Days) ---")
    for name in deletion_queue:
        print(f"  * {name} -> ACTION: DELETE")
        
    print("\n--- Archival Recommendations ---")
    for b in archival_candidates:
        # Avoid recommending archival if it's already in the deletion queue
        if b['name'] not in deletion_queue: 
            print(f"  * {b['name']} -> ACTION: Move to S3 Glacier (Unused {b['days']} days)")

if __name__ == "__main__":
    analyze_buckets('bucket.json')