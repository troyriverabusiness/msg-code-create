import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
import random

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
            tree = ET.parse(SIRI_PATH)
            root = tree.getroot()
            
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

    def get_delay(self, train_number: str) -> int:
        # Return known delay or 0
        # For demo "aliveness", we can add random jitter
        if train_number in self.delays:
            return self.delays[train_number]
        
        # Randomly delay 10% of other trains
        # Use hash of train number to be consistent
        h = hash(train_number)
        if h % 10 == 0:
            return (h % 15) + 1 # 1-15 min delay
            
        return 0

    def get_messages(self) -> list[str]:
        return [
            "Signal failure at Frankfurt Hbf",
            "Construction work on line RB82"
        ]
