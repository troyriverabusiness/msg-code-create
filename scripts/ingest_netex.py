import sqlite3
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import time

# Configuration
NETEX_DIR = Path("datachaos/Netex-Datensatz/netex-data")
DB_PATH = Path("server/data/travel.db")

# Namespaces
NS = {'netex': 'http://www.netex.org.uk/netex'}

def init_db():
    return sqlite3.connect(DB_PATH)

def parse_netex_file(filepath, conn):
    try:
    try:
        # Use iterparse for memory efficiency with large XML files
        context = ET.iterparse(filepath, events=("end",))
        
        platforms_data = []
        
        for event, elem in context:
            if elem.tag == f"{{{NS['netex']}}}StopPlace":
                sp = elem
                # Process StopPlace
                sp_global_id = None
                for kv in sp.findall(".//netex:KeyValue", NS):
                    k = kv.find("netex:Key", NS)
                    v = kv.find("netex:Value", NS)
                    if k is not None and k.text == "GlobalID":
                        sp_global_id = v.text
                        break
                
                if sp_global_id:
                     # Find Quays (Platforms) within this StopPlace
                    quays = sp.findall(".//netex:Quay", NS)
                    for quay in quays:
                        q_global_id = None
                        for kv in quay.findall(".//netex:KeyValue", NS):
                            k = kv.find("netex:Key", NS)
                            v = kv.find("netex:Value", NS)
                            if k is not None and k.text == "GlobalID":
                                q_global_id = v.text
                                break
                        
                        if q_global_id:
                            q_name = quay.find("netex:Name", NS)
                            name = q_name.text if q_name is not None else "Unknown Platform"
                            length = 0.0
                            height = 0.0
                            platforms_data.append((q_global_id, name, height, length, sp_global_id))

                # Clear element to save memory
                elem.clear()

        
        if platforms_data:
            conn.executemany(
                "INSERT OR REPLACE INTO platforms (global_id, name, height, length, parent_station_id) VALUES (?, ?, ?, ?, ?)",
                platforms_data
            )
            conn.commit()
            return len(platforms_data)
            
    except Exception as e:
        # print(f"Error parsing {filepath}: {e}")
        return 0
    return 0

def main():
    print("Starting NeTEx Enrichment...")
    start_time = time.time()
    conn = init_db()
    
    # Get list of files
    # We only care about files that might contain stops. 
    # Since we found them in LINE files, we have to scan them.
    # To save time, we could limit to files modified recently or just scan all.
    # There are 7000 files. Parsing all might take a few minutes.
    
    files = list(NETEX_DIR.rglob("*.xml"))
    print(f"Found {len(files)} XML files.")
    
    total_platforms = 0
    processed_files = 0
    
    for f in files:
        count = parse_netex_file(f, conn)
        total_platforms += count
        processed_files += 1
        
        if processed_files % 100 == 0:
            print(f"Processed {processed_files}/{len(files)} files. Found {total_platforms} platforms...", end='\r')
            
    print(f"\nEnrichment complete. Found {total_platforms} platforms in {time.time() - start_time:.2f} seconds.")
    conn.close()

if __name__ == "__main__":
    main()
