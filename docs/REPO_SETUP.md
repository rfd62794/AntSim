# AntSim Repository Setup Directive
**For:** Coding Agent  
**Status:** Ready to execute  
**Timeline:** 30 minutes  
**Language:** Markdown, plain text  

---

## Objective

Add essential open-source repository files to make AntSim properly licensed and documented.

---

## Files to Create

### **1. LICENSE (MIT License)**

Create file: `LICENSE` (no extension)

```text
MIT License

Copyright (c) 2026 Robert (rfd62794)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### **2. README.md**

Create file: `README.md`

```markdown
# AntSim

A Python/Pygame evolutionary ant colony simulation with split-view hybrid rendering.

Watch ants forage, communicate via pheromone trails, and adapt genetically as their queen reproduces and dies.

## Features

- **Evolutionary Genetics**: 5 genes (sensitivity, speed, boldness, lifespan, energy_efficiency) drive ant behavior
- **Pheromone Trails**: Ants lay exploratory and return-trail pheromones; strong trails reinforce over time
- **Queen Mortality**: Queens die randomly; workers autonomously raise new queens from royal jelly
- **Split-View Rendering**: 
  - Top 2/3: Overhead foraging ground with trails and food nodes
  - Bottom 1/3: Realistic ant hill cross-section with chambers, tunnels, brood, and storage
- **ACO Behavior**: Ant Colony Optimization principles drive efficient foraging
- **Tunable Parameters**: Experiment with death rates, pheromone decay, trail strength, and more

## Status

**Current Phase**: Phase 3 (Hybrid Rendering) — In Progress  
**Stable Baseline**: Phase 2C (Queen Mortality + Royal Jelly) ✅  

## Requirements

- Python 3.10+
- pygame-ce 2.5.6+

## Installation

```bash
git clone https://github.com/rfd62794/AntSim.git
cd AntSim
pip install pygame-ce
```

## Usage

### Run the Simulation

```bash
python main.py
```

### Run Tuning Experiments

Test different queen death rates:

```bash
python tune_antsim.py
```

Results saved to `antsim_tuning_results.csv`.

## Architecture

- **`main.py`** — Entry point, pygame event loop, split-view rendering
- **`sim.py`** — Simulation engine, ant updates, pheromone grid
- **`ant.py`** — Ant agent class, FSM logic, behavior
- **`queen.py`** — Queen class, egg-laying, genetics blending
- **`nest.py`** — Chamber system, nest structure (Phase 3)
- **`render.py`** — Overworld rendering, HUD, stats display
- **`render_nest.py`** — Ant hill cross-section rendering (Phase 3)
- **`constants.py`** — Tunable parameters (death chance, pheromone strength, etc.)
- **`tune_antsim.py`** — Automated tuning harness for experiments

## Key Concepts

### Genes

Each ant inherits 5 genes from its mother (the Queen):

| Gene | Effect |
|------|--------|
| **sensitivity** | How well ant detects pheromone trails |
| **speed** | Ant movement speed |
| **boldness** | Likelihood to explore new areas |
| **lifespan** | How many frames ant survives |
| **energy_efficiency** | How slowly ant burns energy |

Genes vary 0.5–1.5x baseline and mutate ±5% when new queens spawn.

### Pheromone Trails

- **Exploratory**: Strength 2, laid while wandering
- **Return trails**: Strength 100, laid when carrying food back to nest
- **Detection threshold**: Ants follow trails when concentration > 50
- **Decay**: Exponential decay over ~120 frames

### Queen Mortality

- **Death chance**: 2% per generation (tunable)
- **Emergency response**: Workers convert food → royal jelly
- **Recovery**: Best young larvae fed royal jelly, develop into new queen in ~240 frames
- **Genetics**: New queen inherits blended genes from all living workers

## Experiments & Tuning

### Baseline Tuning (Phase 2C)

Tested `QUEEN_DEATH_CHANCE_PER_GEN` across 5 values:

| Death Chance | Avg Ants | Avg Food | Queen Survival |
|---|---|---|---|
| 0.02 | 17.5 | 98.5 | 100% |
| 0.05 | 15.0 | 85.0 | 50% |
| 0.10 | 12.0 | 65.0 | 0% |

**Result**: 2% death chance provides optimal stability with natural selection pressure.

## Next Steps

- [ ] Fix Phase 3 ant transition logic (overworld ↔ nest)
- [ ] Observable worker roles (scouts, nurses, foragers)
- [ ] Visible queen egg-laying animation
- [ ] Larva growth stages (eggs → larvae → pupae → workers)
- [ ] Food consumption clarity
- [ ] Portfolio case study documentation

## License

MIT License — See [LICENSE](LICENSE) file.

## Author

Robert (rfd62794)  
Portfolio: [rfditservices.com](https://rfditservices.com)  
GitHub: [@rfd62794](https://github.com/rfd62794)

---

## References

- Dorigo, M., & Stützle, T. (2019). *Ant Colony Optimization*. MIT Press.
- Natural ant colony biology and pheromone communication
- Emergent behavior in swarm simulations
