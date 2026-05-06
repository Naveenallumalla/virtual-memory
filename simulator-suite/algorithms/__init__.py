# Algorithms package
from .fifo import simulate as fifo_simulate
from .lru import simulate as lru_simulate
from .optimal import simulate as optimal_simulate

ALGORITHM_REGISTRY = {
    "fifo": {
        "name": "FIFO",
        "full_name": "First In First Out",
        "description": "Replaces the page that has been in memory the longest.",
        "simulate": fifo_simulate,
    },
    "lru": {
        "name": "LRU",
        "full_name": "Least Recently Used",
        "description": "Replaces the page that has not been used for the longest time.",
        "simulate": lru_simulate,
    },
    "optimal": {
        "name": "Optimal",
        "full_name": "Optimal (Bélády's Algorithm)",
        "description": "Replaces the page that will not be used for the longest time in future.",
        "simulate": optimal_simulate,
    },
}
