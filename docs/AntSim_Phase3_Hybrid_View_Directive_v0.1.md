# AntSim Phase 3 — Real Ant Hill Cross-Section + Split-View Rendering
**For:** IDE Pair Programming Agent  
**Status:** Ready to execute  
**Timeline:** 3-4 hours  
**Language:** Python 3.10+  
**Framework:** Pygame 2.x (extending Phase 2C codebase)  

---

## Objective

Transform AntSim from abstract overhead view to **split-screen hybrid visualization:**

**Top 2/3:** Overhead foraging ground (current, unchanged)
**Bottom 1/3:** Realistic ant hill cross-section showing:
- Queen in center chamber
- Eggs/larvae visible around queen
- Food storage pile
- Workers moving through tunnels
- Tunnel network connecting chambers

---

## Architecture Overview

### **New Files**

1. **`nest.py`** — Chamber system, ant chamber tracking
2. **`render_nest.py`** — Cross-section rendering, tunnel drawing, entity placement
3. **Modified `main.py`** — Split-view viewport logic

### **Core Concept**

Ants exist in two coordinate systems:
- **Overworld (x, y):** Foraging ground, trails, food nodes
- **Nest (chamber_id):** Which chamber the ant currently occupies

When ant reaches nest entrance (center of overworld):
- Ant moves to nest view
- Occupies a chamber (nursery, queen, storage, etc.)
- Performs task (deposit food, feed larvae, rest)
- Returns to overworld when task complete

---

## Implementation Detail

### **A. Chamber System (`nest.py`)**

```python
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
```

### **B. Ant Chamber Integration**

**Modify `ant.py`:**

```python
class Ant:
    def __init__(self, x, y, genes=None, nest=None):
        # ... existing code ...
        self.nest = nest  # Reference to NestStructure
        self.chamber_id = None  # Current chamber (None = in overworld)
        self.in_nest = False  # Bool: is ant currently in nest?
        self.task = None  # Current task: "deposit_food", "feed_larvae", "rest"
        self.task_progress = 0  # Frames until task complete
        self.task_duration = 30  # Frames to complete task
    
    def enter_nest(self, chamber_id):
        """Ant moves from overworld to nest"""
        self.in_nest = True
        self.chamber_id = chamber_id
        self.x = None  # Not tracked in overworld anymore
        self.y = None
    
    def exit_nest(self, exit_x=400, exit_y=300):
        """Ant moves from nest back to overworld"""
        self.in_nest = False
        self.chamber_id = None
        self.x = exit_x
        self.y = exit_y
    
    def perform_task(self, task_type, duration=30):
        """Start a task in the chamber"""
        self.task = task_type
        self.task_progress = 0
        self.task_duration = duration
    
    def update_task(self):
        """Progress task toward completion"""
        if self.task:
            self.task_progress += 1
            if self.task_progress >= self.task_duration:
                return self.task  # Task complete, return type
        return None
```

### **C. Nest Rendering (`render_nest.py`)**

```python
import pygame
from enum import Enum

class NestRenderer:
    """Render ant hill cross-section"""
    
    def __init__(self, viewport_width=800, viewport_height=200):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.soil_color = (139, 101, 86)  # Brown soil
        self.soil_light = (160, 120, 100)
    
    def render_nest(self, surface, nest_structure, queen, ants_in_nest, food_storage):
        """Draw complete nest cross-section"""
        
        # Background (soil)
        pygame.draw.rect(surface, self.soil_color, (0, 0, self.viewport_width, self.viewport_height))
        
        # Add soil texture (optional: subtle gradient)
        for y in range(self.viewport_height):
            alpha = int(255 * (y / self.viewport_height) * 0.3)
            color = tuple(int(c - alpha) for c in self.soil_color)
            pygame.draw.line(surface, color, (0, y), (self.viewport_width, y))
        
        # Draw tunnels first (behind chambers)
        self._render_tunnels(surface, nest_structure)
        
        # Draw chambers
        self._render_chambers(surface, nest_structure)
        
        # Draw ants in chambers
        self._render_nest_ants(surface, nest_structure, ants_in_nest)
        
        # Draw queen
        if queen and queen.in_nest:
            self._render_queen(surface, nest_structure)
        
        # Draw eggs/larvae in nursery
        self._render_brood(surface, nest_structure)
        
        # Draw food storage
        self._render_food_storage(surface, nest_structure, food_storage)
        
        # Draw chamber labels (optional)
        self._render_labels(surface, nest_structure)
    
    def _render_tunnels(self, surface, nest):
        """Draw tunnel network connecting chambers"""
        tunnel_color = (100, 70, 50)
        tunnel_width = 8
        
        for start_id, end_id in nest.tunnels:
            start_chamber = nest.chambers[start_id]
            end_chamber = nest.chambers[end_id]
            
            pygame.draw.line(
                surface,
                tunnel_color,
                (start_chamber.x, start_chamber.y),
                (end_chamber.x, end_chamber.y),
                tunnel_width
            )
    
    def _render_chambers(self, surface, nest):
        """Draw chamber shapes"""
        chamber_colors = {
            'nursery': (200, 150, 100),
            'queen': (180, 140, 80),
            'storage': (170, 130, 70),
            'worker_rest': (190, 145, 95),
            'waste': (120, 90, 60),
        }
        
        for cid, chamber in nest.chambers.items():
            color_type = chamber.chamber_type.value
            color = chamber_colors.get(color_type, (150, 120, 90))
            
            # Draw as irregular circle (chamber shape)
            pygame.draw.ellipse(
                surface,
                color,
                pygame.Rect(
                    chamber.x - chamber.width // 2,
                    chamber.y - chamber.height // 2,
                    chamber.width,
                    chamber.height
                )
            )
            
            # Border
            pygame.draw.ellipse(
                surface,
                (80, 60, 40),
                pygame.Rect(
                    chamber.x - chamber.width // 2,
                    chamber.y - chamber.height // 2,
                    chamber.width,
                    chamber.height
                ),
                2
            )
    
    def _render_nest_ants(self, surface, nest, ants_in_nest):
        """Draw ants in their chambers"""
        ant_color = (0, 0, 0)
        
        for ant in ants_in_nest:
            if ant.chamber_id and ant.chamber_id in nest.chambers:
                chamber = nest.chambers[ant.chamber_id]
                
                # Random position within chamber
                import random
                random.seed(hash(ant) % (2**32))  # Consistent per ant
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-20, 20)
                
                x = chamber.x + offset_x
                y = chamber.y + offset_y
                
                # Draw ant (small circle)
                pygame.draw.circle(surface, ant_color, (int(x), int(y)), 2)
    
    def _render_queen(self, surface, nest):
        """Draw queen in queen chamber"""
        queen_chamber = nest.chambers['queen']
        queen_color = (255, 100, 200)  # Magenta
        queen_size = 8
        
        pygame.draw.circle(
            surface,
            queen_color,
            (int(queen_chamber.x), int(queen_chamber.y)),
            queen_size
        )
    
    def _render_brood(self, surface, nest):
        """Draw eggs, larvae, pupae in nursery"""
        nursery = nest.chambers['nursery']
        
        # Eggs (tiny white circles)
        egg_color = (255, 255, 255)
        egg_size = 1
        for i in range(nursery.eggs):
            import random
            random.seed(hash(('egg', i)) % (2**32))
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-30, 30)
            pygame.draw.circle(
                surface,
                egg_color,
                (int(nursery.x + offset_x), int(nursery.y + offset_y)),
                egg_size
            )
        
        # Larvae (small light circles)
        larva_color = (200, 200, 100)
        larva_size = 2
        for i in range(nursery.larvae):
            import random
            random.seed(hash(('larva', i)) % (2**32))
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-30, 30)
            pygame.draw.circle(
                surface,
                larva_color,
                (int(nursery.x + offset_x), int(nursery.y + offset_y)),
                larva_size
            )
        
        # Pupae (slightly larger)
        pupa_color = (180, 180, 80)
        pupa_size = 3
        for i in range(nursery.pupae):
            import random
            random.seed(hash(('pupa', i)) % (2**32))
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-30, 30)
            pygame.draw.circle(
                surface,
                pupa_color,
                (int(nursery.x + offset_x), int(nursery.y + offset_y)),
                pupa_size
            )
    
    def _render_food_storage(self, surface, nest, food_amount):
        """Draw food pile in storage chamber"""
        storage = nest.chambers['storage']
        food_color = (255, 165, 0)  # Orange
        
        # Draw food as stacked circles
        food_count = min(int(food_amount / 5), 10)  # Cap at 10 visual units
        for i in range(food_count):
            size = 4 - (i * 0.3)  # Diminishing size for stack effect
            y_offset = i * 3
            pygame.draw.circle(
                surface,
                food_color,
                (int(storage.x), int(storage.y + y_offset)),
                int(max(1, size))
            )
    
    def _render_labels(self, surface, nest):
        """Draw chamber type labels (optional)"""
        font = pygame.font.Font(None, 10)
        label_color = (255, 255, 255)
        
        for cid, chamber in nest.chambers.items():
            label = chamber.chamber_type.value[:3].upper()
            text = font.render(label, True, label_color)
            surface.blit(text, (chamber.x - 10, chamber.y - 5))
```

### **D. Simulation Integration (`sim.py`)**

Add to Simulation class:

```python
from nest import NestStructure
from render_nest import NestRenderer

class Simulation:
    def __init__(self):
        # ... existing code ...
        self.nest = NestStructure(viewport_width=800, viewport_height=200)
        self.nest_renderer = NestRenderer(800, 200)
        self.ants_in_nest = []  # Ants currently in nest
    
    def check_ant_at_nest_entrance(self, ant):
        """Check if ant reached nest (center of map)"""
        nest_x, nest_y = self.nest_pos
        dist_to_nest = ((ant.x - nest_x)**2 + (ant.y - nest_y)**2)**0.5
        
        if dist_to_nest < 50:  # Threshold for entering nest
            return True
        return False
    
    def process_ant_nest_entry(self, ant):
        """Move ant from overworld to nest"""
        if ant.in_nest:
            return
        
        # Determine task based on ant state
        if ant.carrying_food:
            # Deposit food in storage
            chamber_id = 'storage'
            task = 'deposit_food'
        else:
            # Rest or wait in nursery
            chamber_id = 'nursery'
            task = 'rest'
        
        # Enter nest
        ant.enter_nest(chamber_id)
        self.ants_in_nest.append(ant)
        self.ants.remove(ant)  # Remove from overworld
        
        # Assign task
        ant.perform_task(task, duration=20)
    
    def process_ant_nest_exit(self, ant):
        """Move ant from nest back to overworld"""
        if not ant.in_nest:
            return
        
        # Handle task completion effects
        if ant.task == 'deposit_food':
            self.food_storage += 20  # Add to storage
            ant.carrying_food = False
            self.food_collected += 20
        
        # Return ant to overworld near nest entrance
        ant.exit_nest(exit_x=self.nest_pos[0], exit_y=self.nest_pos[1])
        self.ants_in_nest.remove(ant)
        self.ants.append(ant)
    
    def update_ants_in_nest(self):
        """Update ants performing tasks in nest"""
        ants_to_exit = []
        
        for ant in self.ants_in_nest:
            task_complete = ant.update_task()
            
            if task_complete:
                ants_to_exit.append(ant)
        
        for ant in ants_to_exit:
            self.process_ant_nest_exit(ant)
    
    def update(self):
        """Main update loop"""
        # ... existing code ...
        
        # Check ants at nest entrance
        for ant in self.ants[:]:  # Copy list
            if self.check_ant_at_nest_entrance(ant):
                self.process_ant_nest_entry(ant)
        
        # Update ants in nest
        self.update_ants_in_nest()
        
        # ... rest of update ...
```

### **E. Main Rendering (`main.py`)**

Modify render loop to split viewport:

```python
def render(screen, sim, nest_renderer):
    """Split-view rendering"""
    
    # Top 2/3: Overworld
    overworld_rect = pygame.Rect(0, 0, 800, 400)
    overworld_surface = pygame.Surface((800, 400))
    
    # Render overworld (existing code)
    render_overworld(overworld_surface, sim)
    
    screen.blit(overworld_surface, (0, 0))
    
    # Bottom 1/3: Nest
    nest_rect = pygame.Rect(0, 400, 800, 200)
    nest_surface = pygame.Surface((800, 200))
    
    # Render nest cross-section
    nest_renderer.render_nest(
        nest_surface,
        sim.nest,
        sim.queen,
        sim.ants_in_nest,
        sim.food_storage
    )
    
    screen.blit(nest_surface, (0, 400))
    
    # Border between views
    pygame.draw.line(screen, (100, 100, 100), (0, 400), (800, 400), 2)
    
    pygame.display.flip()
```

---

## Implementation Steps

### **Step 1: Create nest.py** (1 hour)
- Define ChamberType enum
- Implement Chamber class
- Implement NestStructure class
- Test: chambers created, accessible

### **Step 2: Create render_nest.py** (1 hour)
- Implement NestRenderer
- Draw soil background
- Draw tunnels, chambers, labels
- Test: visual output correct, chambers visible

### **Step 3: Modify ant.py** (30 min)
- Add chamber tracking to Ant
- Add in_nest flag, task system
- Add enter_nest(), exit_nest(), perform_task()
- Test: ants can transition between systems

### **Step 4: Integrate into sim.py** (1 hour)
- Add NestStructure instance
- Add ant entry/exit logic
- Add task update logic
- Test: ants enter nest, complete tasks, exit

### **Step 5: Modify main.py rendering** (30 min)
- Split screen into top/bottom
- Render overworld top 2/3
- Render nest bottom 1/3
- Test: both views visible, separated

### **Step 6: Verify end-to-end** (30 min)
- Run simulation 60 seconds
- Watch ants forage (top)
- Watch ants in nest (bottom)
- Take screenshot

---

## Acceptance Criteria

✅ NestStructure created with 6 chambers
✅ Chambers connected by visible tunnels
✅ Queen visible in center chamber
✅ Eggs/larvae visible in nursery (rendered as small objects)
✅ Food pile visible in storage chamber
✅ Ants move to overworld → collect food → enter nest → deposit in storage → exit to overworld
✅ Split-view layout: top 2/3 overworld, bottom 1/3 nest
✅ Ant count visible in each chamber
✅ Nest rendering shows accurate chamber positions and tunnel connections
✅ Simulation runs stable at 60 FPS with ants transitioning between views

---

## Success Checkpoint (120 seconds visual observation)

**You watch the screen and see:**

**Top 2/3 (Overworld):**
- 10-15 ants foraging
- Pheromone trails visible
- Food nodes being collected
- Ants returning to nest center

**Bottom 1/3 (Ant Hill):**
- Brown soil background with gradient
- 6 chambers: nursery (top-left), queen (center), storage (top-right), worker rest (sides), waste (bottom)
- Tunnels connecting all chambers
- Queen visible (large magenta circle in center)
- 5-10 eggs in nursery (white dots)
- 3-5 larvae (yellow-tan dots)
- Ants moving in/out of storage chamber (depositing food)
- Orange food pile in storage chamber growing
- Labels: "NUR", "QUE", "STO", etc.

**Terminal output shows:**
```
Frame 600  | FPS: 60.1 | Ants: 12 (3 in nest) | Food: 45 | Storage: 80 | Gen: 1
Frame 1200 | FPS: 60.0 | Ants: 14 (2 in nest) | Food: 60 | Storage: 120 | Gen: 1
```

---

## Troubleshooting

**Ants not entering nest:**
- Check `check_ant_at_nest_entrance()` threshold (50 pixels)
- Verify nest position matches overworld center

**Chambers overlapping:**
- Adjust chamber x, y, width, height in NestStructure.__init__()
- Use viewport dimensions to space them

**Food pile not visible:**
- Check food_storage value passed to render_food_storage()
- Adjust food_count calculation if pile appears too small

**Ants stuck in nest:**
- Verify task_duration is reasonable (20-30 frames)
- Check exit coordinates are valid

---

## Next Steps After Phase 3

1. Add **visible worker roles** (scouts, nurses, foragers) based on behavior
2. Add **queen egg-laying animation**
3. Add **larva growth stages** (eggs → larvae → pupae → workers)
4. Experiment with **food consumption clarity** (workers eating from storage)
5. Document as **portfolio case study**

---

**Directive Created:** April 15, 2026  
**Target Completion:** Today  
**Owner:** Robert (rfd62794)
