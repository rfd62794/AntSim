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
