import requests
import os
import sys

# Configuration
DATA_DIR = "datachaos/deutsche-bahn-data"
API_URL = "https://huggingface.co/api/datasets/piebro/deutsche-bahn-data/tree/main/monthly_processed_data"
BASE_DOWNLOAD_URL = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/"

def download_file(url, dest_path):
    """Downloads a file with a progress bar."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as f:
                if total_size == 0:
                    f.write(r.content)
                else:
                    dl = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        dl += len(chunk)
                        f.write(chunk)
                        # Simple progress bar
                        done = int(50 * dl / total_size)
                        sys.stdout.write(f"\rDownloading: [{'=' * done}{' ' * (50-done)}] {dl//1024//1024}MB / {total_size//1024//1024}MB")
                        sys.stdout.flush()
            print() # Newline after progress bar
            
    except Exception as e:
        print(f"\nError downloading {url}: {e}")
        # Clean up partial file
        if os.path.exists(dest_path):
            os.remove(dest_path)

def main():
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")
    
    print(f"Fetching file list from Hugging Face API...")
    try:
        resp = requests.get(API_URL)
        resp.raise_for_status()
        files = resp.json()
    except Exception as e:
        print(f"Failed to fetch file list: {e}")
        print("Check your internet connection or the API URL.")
        return

    parquet_files = [f for f in files if f['type'] == 'file' and f['path'].endswith('.parquet')]
    print(f"Found {len(parquet_files)} parquet files to download.")
    
    for i, file_info in enumerate(parquet_files):
        path = file_info['path']
        filename = os.path.basename(path)
        dest = os.path.join(DATA_DIR, filename)
        
        print(f"[{i+1}/{len(parquet_files)}] Processing {filename}...")
        
        if os.path.exists(dest):
            print(f"  - File already exists. Skipping.")
            continue
            
        download_url = BASE_DOWNLOAD_URL + path
        download_file(download_url, dest)

    print("\nAll downloads complete.")
    print(f"Files are located in: {os.path.abspath(DATA_DIR)}")

if __name__ == "__main__":
    main()
