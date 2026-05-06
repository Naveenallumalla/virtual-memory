"""
Simulator Service Layer.

Handles input validation, algorithm routing, and result aggregation.
This layer sits between the API routes and the algorithm modules.
"""

from typing import List, Dict, Any
from algorithms import ALGORITHM_REGISTRY
from config import get_config

Config = get_config()


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_input(data: Dict[str, Any]) -> None:
    """
    Validate simulation request payload.

    Raises:
        ValidationError: with a descriptive message if validation fails.
    """
    # --- reference_string ---
    ref = data.get("reference_string")
    if ref is None or ref == "":
        raise ValidationError("Reference string is required.")

    if not isinstance(ref, list):
        raise ValidationError("Reference string must be a list of integers.")

    if len(ref) == 0:
        raise ValidationError("Reference string cannot be empty.")

    if len(ref) > Config.MAX_INPUT_LENGTH:
        raise ValidationError(
            f"Reference string is too long. Maximum allowed: {Config.MAX_INPUT_LENGTH} values."
        )

    for idx, val in enumerate(ref):
        if not isinstance(val, int):
            raise ValidationError(
                f"Invalid value at position {idx + 1}: '{val}'. All values must be non-negative integers."
            )
        if val < 0:
            raise ValidationError(
                f"Negative page number at position {idx + 1}: {val}. Page numbers must be >= 0."
            )

    # --- frames ---
    frames = data.get("frames")
    if frames is None:
        raise ValidationError("Number of frames is required.")

    if not isinstance(frames, int):
        raise ValidationError("Number of frames must be an integer.")

    if frames < Config.MIN_FRAMES:
        raise ValidationError(f"Number of frames must be at least {Config.MIN_FRAMES}.")

    if frames > Config.MAX_FRAMES:
        raise ValidationError(
            f"Number of frames exceeds maximum allowed ({Config.MAX_FRAMES})."
        )

    # --- algorithms ---
    algorithms = data.get("algorithms")
    if not algorithms or not isinstance(algorithms, list) or len(algorithms) == 0:
        raise ValidationError("At least one algorithm must be selected.")

    supported = set(ALGORITHM_REGISTRY.keys())
    for algo in algorithms:
        if algo not in supported:
            raise ValidationError(
                f"Unknown algorithm: '{algo}'. Supported: {', '.join(sorted(supported))}."
            )


def run_simulation(
    reference_string: List[int],
    num_frames: int,
    algorithms: List[str],
) -> Dict[str, Any]:
    """
    Run selected page replacement algorithms and aggregate results.

    Args:
        reference_string: Page reference sequence.
        num_frames: Number of memory frames.
        algorithms: List of algorithm keys to run.

    Returns:
        Dictionary containing per-algorithm results and a summary comparison.
    """
    results: Dict[str, Any] = {}
    comparison: List[Dict[str, Any]] = []

    for algo_key in algorithms:
        algo = ALGORITHM_REGISTRY[algo_key]
        result = algo["simulate"](reference_string, num_frames)
        results[algo_key] = result
        comparison.append({
            "algorithm": algo_key,
            "algorithm_name": result["algorithm_name"],
            "page_faults": result["page_faults"],
            "page_hits": result["page_hits"],
            "hit_ratio": result["hit_ratio"],
            "fault_rate": result["fault_rate"],
            "execution_time_ms": result["execution_time_ms"],
            "total_references": result["total_references"],
        })

    # Determine best algorithm (fewest page faults, tie-break: highest hit ratio)
    best = min(comparison, key=lambda x: (x["page_faults"], -x["hit_ratio"]))

    return {
        "results": results,
        "comparison": comparison,
        "best_algorithm": best["algorithm"],
        "best_algorithm_name": best["algorithm_name"],
        "input_summary": {
            "reference_string": reference_string,
            "frames": num_frames,
            "algorithms": algorithms,
            "total_references": len(reference_string),
        },
    }


def get_algorithms_info() -> List[Dict[str, Any]]:
    """Return metadata for all supported algorithms."""
    return [
        {
            "key": key,
            "name": info["name"],
            "full_name": info["full_name"],
            "description": info["description"],
        }
        for key, info in ALGORITHM_REGISTRY.items()
    ]
