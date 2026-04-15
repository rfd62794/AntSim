# AntSim Phase 2C — Tuning Harness Integration Guide
**For:** Coding Agent  
**Status:** Ready to integrate  
**Time:** 1-2 hours  

---

## What The Harness Does

The `tune_antsim.py` script:
1. Runs multiple simulations with different `QUEEN_DEATH_CHANCE_PER_GEN` values
2. Collects metrics from each run (final ants, food, generations, queen alive)
3. Writes results to CSV for analysis
4. Prints summary statistics

---

## Integration Steps

### **Step 1: Modify main.py to support headless mode + config files**

The harness expects `main.py` to read a config file if provided as argument:

```python
# At the top of main.py, after imports:

def load_tuning_config(config_file):
    """Load tuning configuration if provided"""
    import json
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

# In main():
config_file = sys.argv[1] if len(sys.argv) > 1 else None
tuning_config = load_tuning_config(config_file) if config_file else None

if tuning_config:
    # Override constants with config values
    QUEEN_DEATH_CHANCE_PER_GEN = tuning_config.get('QUEEN_DEATH_CHANCE_PER_GEN', QUEEN_DEATH_CHANCE_PER_GEN)
    SIMULATION_FRAMES = tuning_config.get('SIMULATION_FRAMES', 3600)
    HEADLESS_MODE = tuning_config.get('HEADLESS_MODE', False)
    OUTPUT_FILE = tuning_config.get('OUTPUT_FILE', None)
else:
    HEADLESS_MODE = False
    OUTPUT_FILE = None
```

### **Step 2: Implement headless mode in main.py**

When `HEADLESS_MODE = True`, skip Pygame initialization and just run the simulation:

```python
if HEADLESS_MODE:
    # Run simulation without GUI
    sim = Simulation()
    
    for frame in range(SIMULATION_FRAMES):
        sim.update()
        
        # Periodically print progress
        if frame % 600 == 0:
            print(f"Frame {frame} | Ants: {len(sim.ants)} | Food: {sim.food_collected}")
    
    # Output final metrics
    final_metrics = {
        'run_number': 0,
        'final_ants': len(sim.ants),
        'final_food': sim.food_collected,
        'final_generations': sim.queen.generation,
        'final_queen_alive': sim.queen.alive
    }
    
    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(final_metrics, f)
    
    print(f"\nFinal: Ants={len(sim.ants)} Food={sim.food_collected} Gen={sim.queen.generation} Alive={sim.queen.alive}")
    
else:
    # Normal GUI mode (existing code)
    # ... pygame initialization and event loop ...
```

### **Step 3: Test integration**

Run a single tuning test:

```bash
python main.py tune_config_test.json
```

This should:
- Run silently (no pygame window)
- Print progress every 10 seconds
- Output JSON file with results

### **Step 4: Run the harness**

```bash
python tune_antsim.py
```

This will:
- Run 10 simulations (5 death_chance values × 2 runs each)
- Takes ~5-10 minutes total
- Writes `antsim_tuning_results.csv`
- Prints summary statistics

---

## Expected Output

Terminal:
```
============================================================
AntSim Phase 2C Tuning Harness
Testing 5 death_chance values
2 run(s) per value
Total simulations: 10
============================================================

============================================================
Run 1: QUEEN_DEATH_CHANCE = 0.02
============================================================
Frame 0 | Ants: 10 | Food: 0
Frame 600 | Ants: 11 | Food: 35
Frame 1200 | Ants: 12 | Food: 62
...
✓ Simulation complete
  Death Chance: 0.020
  Final Ants: 18
  Final Food: 102
  Generations: 5
  Queen Alive: True

[... more runs ...]

============================================================
TUNING SUMMARY
============================================================

Death Chance    Runs     Avg Ants     Avg Food     Avg Gen    Queen Alive
----------------------------------------------------------------------
0.020           2        17.5         98.5         5.0        2/2
0.050           2        15.0         85.0         4.5        1/2
0.100           2        12.0         65.0         3.0        0/2
0.150           2        8.0          45.0         2.0        0/2
0.200           2        4.0          20.0         1.0        0/2
```

CSV file (`antsim_tuning_results.csv`):
```
death_chance,run_number,repeat,final_ants,final_food,final_generations,final_queen_alive
0.02,1,1,18,102,5,True
0.02,2,2,17,95,5,True
0.05,3,1,15,87,4,True
...
```

---

## Interpretation

From the summary:
- **0.02 death_chance:** Colonies most stable (high ants, high food, all queens survive)
- **0.05 death_chance:** Good balance (some survive, some don't)
- **0.10+ death_chance:** Colonies struggle (mostly extinction)

**Recommendation:** Pick the death_chance where colonies survive ~70% of the time with reasonable generation count.

---

## Troubleshooting

**"Output file not found"**
- Make sure main.py writes the JSON file correctly in headless mode

**"Timeout"**
- Increase timeout in tune_antsim.py if simulations take longer than 30 seconds

**"Results look wrong"**
- Check that constants are actually being overridden from the config file
- Verify HEADLESS_MODE logic in main.py

---

## Next Steps After Tuning

1. Take the optimal `QUEEN_DEATH_CHANCE_PER_GEN` value from results
2. Update `constants.py` with that value
3. Run a visual simulation to verify behavior
4. Take screenshot at 60 seconds
5. Report findings to Robert

---

**Integration Guide:** April 14, 2026  
**Target:** Today  
**Owner:** Coding Agent
