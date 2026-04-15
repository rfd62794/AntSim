# AntSim

A dead-simple ant colony simulation written in Python + Pygame.  
Phase 1: emergent pheromone-trail foraging with 10 ants.

---

## Quick Start

```bash
# 1. Clone / navigate to the repo
cd AntSim

# 2. Install pygame (once)
pip install pygame-ce   # or: pip install pygame

# 3. Run
python main.py

# Press Q or close the window to quit.
```

> **Requires:** Python 3.10+, pygame 2.x (tested with pygame-ce 2.5.6)

---

## What You're Watching

| Element | Colour | Meaning |
|---|---|---|
| Red circle (centre) | 🔴 | Nest — ants spawn and return here |
| Green circles | 🟢 | Food sources — respawn when all eaten |
| Blue heatmap | 🔵 | Pheromone trails — brighter = stronger signal |
| Cream dots | ⚪ | Ants in wander / follow / seek state |
| Orange dots | 🟠 | Ant carrying food back to nest |
| Tiny bar above ant | — | Individual energy level (drains over time) |

### Ant State Machine

```
wander  →  (pheromone nearby?)  →  follow_pheromone
        →  (food in vision?)    →  seek_food
        →  (carrying food)      →  return_nest
        →  (energy == 0)        →  💀 removed
```

Ants that return food to the nest have their energy **fully reset**, so
successful foragers live longest. Dead ants are removed; food re-spawns
when all sources are exhausted.

### What to Look For

1. **First ~30 s** — ants fan out randomly, pheromone trails barely visible.
2. **~1 min** — first ant finds food; trail strengthens; nearby ants detour
   toward it without being told to.
3. **~2–3 min** — multiple ants converge on a food source, creating a vivid
   blue highway between nest and food.
4. **After food depletes** — trails fade (decay), ants scatter again until
   new food spawns.

That emergent cooperation? Nobody programmed it. It falls out of three
simple rules: emit pheromone, follow the gradient, reset energy on return.

---

## Terminal Output

```
AntSim started. Close the window or press Q to quit.
  Frame     FPS   Ants    Food
    300    60.0     10       3
    600    60.0     10       7
   ...
```

---

## File Layout

```
AntSim/
├── main.py        Entry point + game loop
├── sim.py         Simulation state (ants, food, pheromone grid)
├── ant.py         Ant agent + FSM behaviour
├── render.py      All Pygame drawing (nothing else draws)
├── constants.py   Every magic number in one place
└── docs/
    └── AntSim_GDD_v0.1.md
```

---

## Tuning

Edit `constants.py` — no code changes needed:

| Constant | Default | Effect |
|---|---|---|
| `ANT_COUNT` | 10 | More ants = denser trails faster |
| `ANT_SPEED` | 2.0 | px/frame |
| `ANT_ENERGY_DRAIN` | 0.5 | Higher = ants die sooner |
| `PHEROMONE_DECAY` | 0.95 | Closer to 1.0 = trails persist longer |
| `PHEROMONE_EMIT` | 50 | Stronger trails → faster convergence |
| `FOOD_COUNT` | 5 | Sources per respawn cycle |

---

## Roadmap

### Phase 1 ✅ — Core Sim (this)
- [x] Random-walk ants
- [x] Pheromone grid (emit + decay)
- [x] Pheromone following
- [x] Food pickup + nest return
- [x] Energy death + food respawn
- [x] 60 FPS stable

### Phase 2 — Genetics & Observation UI
- [ ] Per-ant gene values (speed, pheromone sensitivity, vision range)
- [ ] Fitness tracking — which lineages collect the most food?
- [ ] Breeding: top-performing ants produce offspring
- [ ] Pause / step / mutate mid-run controls
- [ ] Live fitness chart overlay

### Phase 3 — Multi-Colony Competition
- [ ] Two or more colonies with separate pheromone channels
- [ ] Territory and food competition
- [ ] Evolutionary arms race visualisation

---

**Owner:** Robert (rfd62794)  
**Phase 1 Complete:** April 14, 2026
