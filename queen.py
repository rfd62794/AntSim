# queen.py — Queen ant class and worker reproduction logic
import random
from constants import (
    NEST_POS, QUEEN_ENERGY_MAX,
    QUEEN_REPRO_COST,
    GENE_MUTATION_CHANCE, GENE_MUTATION_RANGE,
    GENE_MIN, GENE_MAX,
)


# Default gene values (baseline, unevoled colony)
DEFAULT_GENES = {
    'sensitivity':       1.0,  # pheromone detection multiplier
    'speed':             1.0,  # movement speed multiplier
    'boldness':          0.5,  # 0=cautious trail-follower, 1=bold explorer
    'lifespan':          1.0,  # multiplier for max energy before starvation
    'energy_efficiency': 1.0,  # divisor for energy drain rate
}


class Queen:
    """
    Stays at the nest center.  Produces workers when food storage is sufficient.
    Her genes are inherited (with small mutation chance) by every worker she births.
    """

    def __init__(self, x: float, y: float, genes: dict | None = None):
        self.x = x
        self.y = y
        self.energy      = QUEEN_ENERGY_MAX
        self.alive       = True
        self.genes       = genes if genes is not None else dict(DEFAULT_GENES)
        self.generation  = 0    # incremented each time a new worker is born
        self.workers_born = 0

    # ──────────────────────────────────────────────────────────────────────────

    def try_reproduce(self, food_storage: int):
        """
        Attempt to produce one worker.  Returns a new Ant if successful, else None.
        Caller deducts the food cost on success.
        """
        from ant import Ant

        if food_storage < QUEEN_REPRO_COST:
            return None

        # Build worker gene dict from queen's genes + optional mutation
        worker_genes = {}
        for gene, base in self.genes.items():
            value = base
            if random.random() < GENE_MUTATION_CHANCE:
                direction = random.uniform(1 - GENE_MUTATION_RANGE,
                                           1 + GENE_MUTATION_RANGE)
                value = base * direction
            worker_genes[gene] = max(GENE_MIN, min(GENE_MAX, value))

        worker = Ant(self.x, self.y,
                     genes=worker_genes,
                     queen_id=id(self))
        self.generation  += 1
        self.workers_born += 1
        return worker
