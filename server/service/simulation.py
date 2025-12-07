import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
import random
import sqlite3

# For MVP, we use the sample message.txt as our "Live Feed" source
SIRI_PATH = Path("datachaos/message.txt")

class SimulationService:
    def __init__(self):
        self.delays: Dict[str, int] = {} # Train Number -> Delay in Minutes
        self.load_siri_data()

    def load_siri_data(self):
        if not SIRI_PATH.exists():
            print(f"Warning: SIRI file {SIRI_PATH} not found. Using random simulation.")
            return

        try:
            with open(SIRI_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Wrap in a root element to handle multiple <s> elements
            # and remove potential trailing junk like '%' and XML declarations
            content = content.strip().rstrip('%')
            if content.startswith("<?xml"):
                content = content.split("?>", 1)[1]
            
            xml_content = f"<root>{content}</root>"
            
            root = ET.fromstring(xml_content)
            
            # Namespace map (SIRI often uses namespaces)
            # We'll just search by tag name for simplicity in MVP
            
            # Logic: Find <n> (Train Number) and look for delay info
            # In the sample message.txt provided earlier, we saw <n>25169</n>
            # We need to find where delay is stored. 
            # Often it's in <Arrival><Delay> or <Departure><Delay>
            
            # Let's assume a simple structure based on what we saw or standard SIRI
            # For the Hackathon, we can also just generate some "interesting" delays
            # for the trains we know exist (like ICE 690).
            
            # Mocking the extraction for now as the file might be complex
            # and we want to ensure the demo works.
            self.delays["690"] = 5 # ICE 690 has 5 min delay
            self.delays["82"] = 2 # RB 82 has 2 min delay
            self.delays["25169"] = 12 # RB from sample
            
        except Exception as e:
            print(f"Error parsing SIRI: {e}")

    def get_delay(self, train_number: str, station_name: str = None, hour: int = None) -> int:
        """
        Get simulated delay based on historical patterns.
        """
        # 1. Try to query DB if station and hour are provided
        if station_name and hour is not None:
            try:
                conn = sqlite3.connect("server/data/travel.db")
                cursor = conn.cursor()
                
                # Clean train number (remove letters)
                import re
                clean_number = re.search(r'\d+', str(train_number))
                clean_number = clean_number.group(0) if clean_number else train_number
                
                cursor.execute("""
                    SELECT avg_delay FROM delay_patterns 
                    WHERE train_number = ? AND station_name = ? AND hour_of_day = ?
                """, (clean_number, station_name, hour))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return int(row[0])
            except Exception as e:
                print(f"Simulation DB Error: {e}")

        # 2. Fallback: Return known delay from manual overrides
        if train_number in self.delays:
            return self.delays[train_number]
        
        # 3. Fallback: Random simulation
        h = hash(train_number)
        if h % 10 == 0:
            return (h % 15) + 1 # 1-15 min delay
            
        return 0

    def get_historical_delay(self, train_number: str, station_name: str = None, hour: int = None) -> Optional[float]:
        """
        Get historical average delay if available. Returns None if no data found.
        """
        try:
            # Use absolute path relative to this file
            db_path = Path(__file__).parent.parent / "data" / "travel.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Clean train number (remove letters and leading zeros)
            import re
            clean_number = re.search(r'\d+', str(train_number))
            clean_number = clean_number.group(0) if clean_number else train_number
            # Remove leading zeros by converting to int then str
            try:
                clean_number = str(int(clean_number))
            except:
                pass
            
            # If station/hour not provided, just get global average for this train
            if not station_name or hour is None:
                cursor.execute("""
                    SELECT avg(avg_delay) FROM delay_patterns 
                    WHERE train_number = ?
                """, (clean_number,))
            else:
                cursor.execute("""
                    SELECT avg_delay FROM delay_patterns 
                    WHERE train_number = ? AND station_name = ? AND hour_of_day = ?
                """, (clean_number, station_name, hour))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] is not None:
                return float(row[0])
        except Exception as e:
            print(f"Simulation DB Error: {e}")
            
        return None

    def get_messages(self) -> list[str]:
        return [
            "Signal failure at Frankfurt Hbf",
            "Construction work on line RB82"
        ]

    def get_load(self, train_number: str) -> list[int]:
        """
        Get simulated wagon load percentages (0-100).
        Returns a list of integers representing load for each wagon.
        """
        # Deterministic simulation based on hash
        h = hash(train_number)
        random.seed(h)
        
        # Determine number of wagons (5-12)
        num_wagons = (h % 8) + 5
        
        loads = []
        for _ in range(num_wagons):
            # Generate load with some variance
            # Base load 30-80%
            base = random.randint(30, 80)
            loads.append(base)
            
        return loads
