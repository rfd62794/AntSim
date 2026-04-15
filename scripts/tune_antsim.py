# AntSim Phase 2C — Tuning Harness
# Automated experiment runner for testing QUEEN_DEATH_CHANCE_PER_GEN values
# Usage: python tune_antsim.py

import subprocess
import json
import csv
import os
import sys
from pathlib import Path

class TuningHarness:
    def __init__(self, results_file="tuning_results.csv"):
        self.results_file = results_file
        self.results = []
        
    def run_single_simulation(self, death_chance, run_number):
        """
        Run one simulation with a specific QUEEN_DEATH_CHANCE_PER_GEN value
        
        Returns dict with metrics
        """
        print(f"\n{'='*60}")
        print(f"Run {run_number}: QUEEN_DEATH_CHANCE = {death_chance}")
        print(f"{'='*60}")
        
        # Create a temporary config file with this death_chance
        config = {
            'QUEEN_DEATH_CHANCE_PER_GEN': death_chance,
            'SIMULATION_FRAMES': 3600,
            'HEADLESS_MODE': True,
            'OUTPUT_FILE': f'run_{run_number}_output.json'
        }
        
        # Write config to temp file
        config_file = f'tune_config_{run_number}.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Run the simulation (assumes main.py reads tune_config_N.json if present)
        # If main.py doesn't support this, you'll need to modify it to read config
        try:
            result = subprocess.run(
                [sys.executable, 'main.py', config_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output_file = config['OUTPUT_FILE']
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    metrics = json.load(f)
                print(f"✓ Simulation complete")
                return metrics
            else:
                print(f"✗ Output file not found: {output_file}")
                return self.parse_simulation_output(result.stdout, run_number)
                
        except subprocess.TimeoutExpired:
            print(f"✗ Simulation timeout")
            return None
        except Exception as e:
            print(f"✗ Error running simulation: {e}")
            return None
        finally:
            # Clean up temp config
            if os.path.exists(config_file):
                os.remove(config_file)
    
    def parse_simulation_output(self, stdout, run_number):
        """
        Parse terminal output if JSON output not available
        Looks for final metrics in stdout
        """
        metrics = {
            'run_number': run_number,
            'queen_died': False,
            'queen_recovered': False,
            'final_ants': 0,
            'final_food': 0,
            'final_generations': 0,
            'final_queen_alive': False
        }
        
        # Parse the terminal output for final stats
        # This is a fallback if the simulation doesn't write JSON
        lines = stdout.split('\n')
        for line in lines[-20:]:  # Check last 20 lines for final stats
            if 'Ants:' in line and 'Food:' in line:
                # Try to extract numbers
                try:
                    parts = line.split('|')
                    for part in parts:
                        if 'Ants:' in part:
                            metrics['final_ants'] = int(part.split(':')[1].strip())
                        elif 'Food:' in part:
                            metrics['final_food'] = int(part.split(':')[1].strip())
                        elif 'QGen:' in part:
                            metrics['final_generations'] = int(part.split(':')[1].strip())
                        elif 'Alive:' in part:
                            metrics['final_queen_alive'] = 'Yes' in part
                except:
                    pass
        
        return metrics
    
    def run_experiment(self, death_chances, runs_per_value=1):
        """
        Run full tuning experiment
        
        Args:
            death_chances: list of QUEEN_DEATH_CHANCE values to test
            runs_per_value: how many times to run each value
        """
        print(f"\n{'='*60}")
        print(f"AntSim Phase 2C Tuning Harness")
        print(f"Testing {len(death_chances)} death_chance values")
        print(f"{runs_per_value} run(s) per value")
        print(f"Total simulations: {len(death_chances) * runs_per_value}")
        print(f"{'='*60}\n")
        
        run_number = 1
        
        for death_chance in death_chances:
            for repeat in range(runs_per_value):
                metrics = self.run_single_simulation(death_chance, run_number)
                
                if metrics:
                    # Add death_chance to metrics
                    metrics['death_chance'] = death_chance
                    metrics['repeat'] = repeat + 1
                    self.results.append(metrics)
                    self.print_result(metrics)
                
                run_number += 1
        
        # Write results to CSV
        self.write_results()
        self.print_summary()
    
    def print_result(self, metrics):
        """Pretty-print a single result"""
        print(f"  Death Chance: {metrics['death_chance']:.3f}")
        print(f"  Final Ants: {metrics['final_ants']}")
        print(f"  Final Food: {metrics['final_food']}")
        print(f"  Generations: {metrics['final_generations']}")
        print(f"  Queen Alive: {metrics.get('final_queen_alive', 'Unknown')}")
    
    def write_results(self):
        """Write results to CSV file"""
        if not self.results:
            print("No results to write")
            return
        
        keys = ['death_chance', 'run_number', 'repeat', 'final_ants', 'final_food', 'final_generations', 'final_queen_alive']
        
        with open(self.results_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            
            for result in self.results:
                row = {k: result.get(k, '') for k in keys}
                writer.writerow(row)
        
        print(f"\n✓ Results written to {self.results_file}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.results:
            return
        
        print(f"\n{'='*60}")
        print(f"TUNING SUMMARY")
        print(f"{'='*60}\n")
        
        # Group by death_chance
        by_death_chance = {}
        for result in self.results:
            dc = result['death_chance']
            if dc not in by_death_chance:
                by_death_chance[dc] = []
            by_death_chance[dc].append(result)
        
        # Print summary per death_chance
        print(f"{'Death Chance':<12} {'Runs':<8} {'Avg Ants':<12} {'Avg Food':<12} {'Avg Gen':<10} {'Queen Alive':<12}")
        print(f"{'-'*70}")
        
        for dc in sorted(by_death_chance.keys()):
            results = by_death_chance[dc]
            avg_ants = sum(r['final_ants'] for r in results) / len(results)
            avg_food = sum(r['final_food'] for r in results) / len(results)
            avg_gen = sum(r['final_generations'] for r in results) / len(results)
            alive_count = sum(1 for r in results if r.get('final_queen_alive', False))
            
            print(f"{dc:<12.3f} {len(results):<8} {avg_ants:<12.1f} {avg_food:<12.1f} {avg_gen:<10.1f} {alive_count}/{len(results)}")
        
        print(f"\n{'='*60}")
        print(f"Recommendation:")
        print(f"- Highest average ants: Most survivable death_chance")
        print(f"- Highest queen_alive ratio: Most stable recovery")
        print(f"- Highest average generations: Best evolutionary pressure")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Tuning parameters to test
    death_chances = [0.02, 0.05, 0.10, 0.15, 0.20]
    runs_per_value = 2  # Run each value twice for stability
    
    harness = TuningHarness(results_file="antsim_tuning_results.csv")
    
    try:
        harness.run_experiment(death_chances, runs_per_value)
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user")
        harness.write_results()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        harness.write_results()