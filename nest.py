from enum import Enum
from dataclasses import dataclass

class ChamberType(Enum):
    NURSERY = "nursery"          # Top: eggs, larvae, pupae
    QUEEN = "queen"              # Center: queen + attendants
    STORAGE = "storage"          # Lower: cached food
    WORKER_REST = "worker_rest"  # Sides: resting workers
    WASTE = "waste"              # Bottom: waste disposal

@dataclass
class Chamber:
    chamber_type: ChamberType
    x: int              # Center X in nest view (pixels)
    y: int              # Center Y in nest view (pixels)
    width: int          # Chamber width
    height: int         # Chamber height
    max_capacity: int   # Max ants in chamber
    
    def __post_init__(self):
        self.ants = []              # Ants currently in this chamber
        self.eggs = 0               # Egg count
        self.larvae = 0             # Larva count
        self.pupae = 0              # Pupa count
        self.food_stored = 0        # Food in storage chamber
    
    def is_full(self):
        return len(self.ants) >= self.max_capacity
    
    def add_ant(self, ant):
        if not self.is_full():
            self.ants.append(ant)
            return True
        return False
    
    def remove_ant(self, ant):
        if ant in self.ants:
            self.ants.remove(ant)
            return True
        return False

class NestStructure:
    """Ant hill layout with chambers and tunnels"""
    
    def __init__(self, viewport_width=800, viewport_height=200):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        
        # Build chambers
        self.chambers = {
            'nursery': Chamber(
                chamber_type=ChamberType.NURSERY,
                x=viewport_width // 4,
                y=40,
                width=120,
                height=80,
                max_capacity=15
            ),
            'queen': Chamber(
                chamber_type=ChamberType.QUEEN,
                x=viewport_width // 2,
                y=100,
                width=150,
                height=100,
                max_capacity=20
            ),
            'storage': Chamber(
                chamber_type=ChamberType.STORAGE,
                x=3 * viewport_width // 4,
                y=100,
                width=120,
                height=80,
                max_capacity=25
            ),
            'worker_rest_left': Chamber(
                chamber_type=ChamberType.WORKER_REST,
                x=100,
                y=150,
                width=80,
                height=60,
                max_capacity=10
            ),
            'worker_rest_right': Chamber(
                chamber_type=ChamberType.WORKER_REST,
                x=viewport_width - 100,
                y=150,
                width=80,
                height=60,
                max_capacity=10
            ),
            'waste': Chamber(
                chamber_type=ChamberType.WASTE,
                x=viewport_width // 2,
                y=viewport_height - 30,
                width=100,
                height=40,
                max_capacity=10
            )
        }
        
        # Tunnel paths (list of (start_chamber, end_chamber))
        self.tunnels = [
            ('nursery', 'queen'),
            ('queen', 'storage'),
            ('queen', 'worker_rest_left'),
            ('queen', 'worker_rest_right'),
            ('queen', 'waste'),
            ('storage', 'waste'),
        ]
    
    def get_chamber(self, chamber_id):
        return self.chambers.get(chamber_id)
    
    def find_available_chamber(self, chamber_type):
        """Find a chamber of given type with space"""
        for cid, chamber in self.chambers.items():
            if chamber.chamber_type == chamber_type and not chamber.is_full():
                return cid
        return None
    
    def get_queen_chamber(self):
        return self.chambers['queen']
