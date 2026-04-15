# AntSim MVP — Game Design Document v0.1
**Status:** GDD for IDE Agent Pair Programming  
**Target:** Playable simulation in < 4 hours  
**Tech Stack:** Python + Pygame (or your agent's preference)  
**Scope:** Phase 1 Core Sim Only  

---

## North Star

Build a **dead simple ant colony sim** where:
- 10 ants wander a 2D space
- Ants follow pheromone trails to food
- Ants return food to nest
- Pheromone decays over time
- **You watch it work.**

**Non-goals (Phase 2+):**
- Genetics
- Breeding
- Multiple colonies
- UI polish
- Optimization

---

## Core Systems (MVP)

### **System 1: Spatial Map**
- **Size:** 800×600 pixels (fixed)
- **Elements:**
  - 1 Nest (center, 50px radius circle) — red
  - 3-5 Food sources (random placement, 20px radius) — green
  - Pheromone grid (10px cells, 80×60 grid)
  - Ants (10 total)

### **System 2: Ant Agent**
```
Ant {
  x, y (position)
  vx, vy (velocity)
  energy (0-100, depletes when moving/alive)
  carrying_food (bool)
  target (nest or nearest food)
}
```

**Behavior (state machine):**
- **Wander:** Move in random direction, leave pheromone trail (strength=50)
- **Follow Pheromone:** If pheromone nearby (radius 40px), move toward strongest
- **Seek Food:** If no pheromone, move toward nearest food (visual range: 100px)
- **Return to Nest:** If carrying food, move toward nest
- **Drop Food:** When touching nest, drop food, reset energy to 100
- **Die:** When energy reaches 0

**Constants:**
- Movement speed: 2 px/frame
- Energy drain: 0.5 per frame
- Pheromone emission: 50 (when moving)
- Pheromone detection radius: 40px
- Vision range: 100px

### **System 3: Pheromone Physics**
```
Pheromone Grid {
  cells[80][60]
  each cell: strength (0-255)
}
```

**Per frame:**
1. Ants moving emit pheromone at their cell
2. All pheromone decays: `strength *= 0.95`
3. Cells below 5 → 0 (cleanup)

### **System 4: Render**
- **Background:** Black (or dark)
- **Nest:** Red circle (center)
- **Food:** Green circles (random placement, respawn when empty)
- **Pheromone:** Blue heatmap overlay (alpha based on strength)
- **Ants:** White dots (or small circles)
- **Stats:** Text overlay (frame rate, ant count, total food collected)

---

## MVP Phase: What Must Work

- [ ] Ants spawn in nest
- [ ] Ants wander (random walk)
- [ ] Pheromone emits when ants move
- [ ] Pheromone decays visually
- [ ] Ants follow pheromone gradient toward food
- [ ] Ants pick up food (touch detection)
- [ ] Ants return to nest (pathfinding via pheromone)
- [ ] Food counter increments
- [ ] Ants die when energy depletes
- [ ] Sim runs at 60 FPS for 5+ minutes without crash

---

## What NOT to Build (Yet)

- ❌ Genetics
- ❌ Multiple colonies
- ❌ Breeding/selection
- ❌ UI sliders/parameters
- ❌ Saving/loading state
- ❌ Advanced pathfinding (A*, etc.)
- ❌ Ant specialization
- ❌ Queen mechanics
- ❌ Beautiful graphics

---

## Execution Checkpoint

**Success = You run the sim, watch for 2 minutes, and think "that's actually cool to watch."**

**Failure = Ants get stuck, nothing happens, or it crashes.**

If success: Phase 2 is genetics + observation UI.
If failure: Debug, simplify, retry.

---

## Implementation Notes for Agent

1. **No OOP required** — Use dicts/dataclasses for ants, simple functions
2. **Grid-based pheromone** — Easier than continuous, fast enough
3. **Random walk is fine** — Ants don't need sophisticated pathfinding yet
4. **Render every frame** — Keep it simple; performance is not a constraint at 10 ants
5. **Test in isolation:**
   - Test pheromone decay separately
   - Test ant movement separately
   - Test collision detection separately
   - Then integrate

---

## Next Phase Preview (NOT NOW)

- Add genetics to ants (speed, pheromone sensitivity)
- Breed successful colonies
- Visualize fitness tracking
- Pause/resume/mutate mid-run
- Multi-colony competition

---

**Created:** April 14, 2026  
**For:** IDE Pair Programming Agent (Antigravity or equivalent)  
**Owner:** Robert (rfd62794)
