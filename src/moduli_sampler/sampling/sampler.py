"""Main sampling module for algebraic curve families.

This module implements the core sampling logic for generating
families of algebraic curves based on parameter specifications.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

import numpy as np

from .params_schema import SamplingParams
from ..geometry.curves import P1Curve, EllipticCurve, HyperellipticCurve, PlaneCurve
from ..geometry.invariants import (
    compute_p1_family_invariants,
    compute_elliptic_family_invariants,
    compute_hyperelliptic_family_invariants,
    compute_plane_curve_family_invariants,
)


class Sampler:
    """Main sampler class for algebraic curve families.
    
    This class handles the generation of curve families based on
    parameter specifications and sampling strategies.
    """
    
    def __init__(self, params: SamplingParams):
        """Initialize sampler with parameters.
        
        Args:
            params: Validated sampling parameters
        """
        self.params = params
        self.rng = np.random.RandomState(params.sampling.seed)
    
    def sample_p1_family(self, n_samples: int) -> List[Dict[str, Any]]:
        """Sample P^1 family with line bundles O(d).
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            List of dictionaries with curve data and invariants
        """
        if "degree" not in self.params.constraints:
            raise ValueError("P1 family requires degree constraint")
        
        degree_range = self.params.constraints.degree
        if isinstance(degree_range, list):
            min_deg, max_deg = degree_range
        else:
            # Single degree value
            min_deg = max_deg = degree_range
        
        # Generate degree samples
        if self.params.sampling.strategy == "grid":
            degrees = list(range(min_deg, max_deg + 1))
            # Limit to requested number of samples
            degrees = degrees[:n_samples]
        elif self.params.sampling.strategy == "random":
            degrees = self.rng.choice(
                range(min_deg, max_deg + 1),
                size=min(n_samples, max_deg - min_deg + 1),
                replace=False
            ).tolist()
        else:  # lhs strategy (simplified)
            degrees = self.rng.choice(
                range(min_deg, max_deg + 1),
                size=min(n_samples, max_deg - min_deg + 1),
                replace=False
            ).tolist()
        
        # Compute invariants
        invariants = compute_p1_family_invariants(
            (min(degrees), max(degrees)),
            self.params.invariants.compute
        )
        
        # Add sampling metadata
        for inv in invariants:
            inv["sampling_strategy"] = self.params.sampling.strategy
            inv["seed"] = self.params.sampling.seed
        
        return invariants
    
    def sample_elliptic_family(self, n_samples: int) -> List[Dict[str, Any]]:
        """Sample elliptic curve family y² = x³ + ax + b.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            List of dictionaries with curve data and invariants
        """
        if "coefficient_ranges" not in self.params.constraints:
            raise ValueError("Elliptic family requires coefficient_ranges")
        
        coeff_ranges = self.params.constraints.coefficient_ranges
        a_range = coeff_ranges.get("a", [-3, 3])
        b_range = coeff_ranges.get("b", [-3, 3])
        
        # Generate coefficient samples
        if self.params.sampling.strategy == "grid":
            # Grid sampling for small ranges
            a_values = list(range(a_range[0], a_range[1] + 1))
            b_values = list(range(b_range[0], b_range[1] + 1))
            coefficient_pairs = [(a, b) for a in a_values for b in b_values]
            # Limit to requested number of samples
            coefficient_pairs = coefficient_pairs[:n_samples]
        elif self.params.sampling.strategy == "random":
            a_values = self.rng.choice(
                range(a_range[0], a_range[1] + 1),
                size=n_samples,
                replace=True
            )
            b_values = self.rng.choice(
                range(b_range[0], b_range[1] + 1),
                size=n_samples,
                replace=True
            )
            coefficient_pairs = list(zip(a_values, b_values))
        else:  # lhs strategy (simplified)
            a_values = self.rng.choice(
                range(a_range[0], a_range[1] + 1),
                size=n_samples,
                replace=True
            )
            b_values = self.rng.choice(
                range(b_range[0], b_range[1] + 1),
                size=n_samples,
                replace=True
            )
            coefficient_pairs = list(zip(a_values, b_values))
        
        # Filter for smooth curves if requested
        if self.params.constraints.smoothness_check:
            smooth_pairs = []
            for a, b in coefficient_pairs:
                curve = EllipticCurve(a, b)
                if curve.is_smooth():
                    smooth_pairs.append((a, b))
                if len(smooth_pairs) >= n_samples:
                    break
            coefficient_pairs = smooth_pairs
        
        # Compute invariants
        invariants = compute_elliptic_family_invariants(
            coefficient_pairs,
            self.params.invariants.compute
        )
        
        # Add sampling metadata
        for inv in invariants:
            inv["sampling_strategy"] = self.params.sampling.strategy
            inv["seed"] = self.params.sampling.seed
        
        return invariants
    
    def sample_hyperelliptic_family(self, n_samples: int) -> List[Dict[str, Any]]:
        """Sample hyperelliptic curve family y² = f(x).
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            List of dictionaries with curve data and invariants
        """
        if "genus" not in self.params.constraints:
            raise ValueError("Hyperelliptic family requires genus constraint")
        if "coefficient_ranges" not in self.params.constraints:
            raise ValueError("Hyperelliptic family requires coefficient_ranges")
        
        genus = self.params.constraints.genus
        coeff_ranges = self.params.constraints.coefficient_ranges
        
        # Determine polynomial degree based on genus
        # For genus g, we need deg(f) = 2g + 1 or 2g + 2
        poly_degree = 2 * genus + 1
        
        # Generate coefficient samples
        coefficient_lists = []
        attempts = 0
        max_attempts = n_samples * 10  # Prevent infinite loops
        
        while len(coefficient_lists) < n_samples and attempts < max_attempts:
            attempts += 1
            
            # Generate random coefficients
            coeffs = []
            for i in range(poly_degree + 1):
                if i in coeff_ranges:
                    min_val, max_val = coeff_ranges[i]
                    coeff = self.rng.randint(min_val, max_val + 1)
                else:
                    # Default range if not specified
                    coeff = self.rng.randint(-2, 3)
                coeffs.append(coeff)
            
            # Check if polynomial is squarefree (basic smoothness)
            if self.params.constraints.smoothness_check:
                curve = HyperellipticCurve(coeffs)
                if not curve.is_smooth():
                    continue
            
            coefficient_lists.append(coeffs)
        
        # Compute invariants
        invariants = compute_hyperelliptic_family_invariants(
            coefficient_lists,
            self.params.invariants.compute
        )
        
        # Add sampling metadata
        for inv in invariants:
            inv["sampling_strategy"] = self.params.sampling.strategy
            inv["seed"] = self.params.sampling.seed
        
        return invariants
    
    def sample_plane_curve_family(self, n_samples: int) -> List[Dict[str, Any]]:
        """Sample plane curve family F(x,y,z) = 0.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            List of dictionaries with curve data and invariants
        """
        if "degree" not in self.params.constraints:
            raise ValueError("PlaneCurve family requires degree constraint")
        
        degree = self.params.constraints.degree
        coeff_ranges = self.params.constraints.coefficient_ranges or {}
        
        # Generate coefficient samples for monomials
        degree_coefficient_pairs = []
        attempts = 0
        max_attempts = n_samples * 10
        
        while len(degree_coefficient_pairs) < n_samples and attempts < max_attempts:
            attempts += 1
            
            # Generate coefficients for degree d monomials
            coefficients = {}
            
            # Add some standard monomials
            if degree >= 1:
                coefficients["x^" + str(degree)] = self.rng.randint(-2, 3)
                coefficients["y^" + str(degree)] = self.rng.randint(-2, 3)
                coefficients["z^" + str(degree)] = self.rng.randint(-2, 3)
            
            # Add mixed terms
            if degree >= 2:
                for i in range(1, degree):
                    j = degree - i
                    if i <= j:
                        coefficients[f"x^{i}*y^{j}"] = self.rng.randint(-2, 3)
                        coefficients[f"x^{i}*z^{j}"] = self.rng.randint(-2, 3)
                        coefficients[f"y^{i}*z^{j}"] = self.rng.randint(-2, 3)
            
            # Check smoothness if requested
            if self.params.constraints.smoothness_check:
                curve = PlaneCurve(degree, coefficients)
                if not curve.is_smooth():
                    continue
            
            degree_coefficient_pairs.append((degree, coefficients))
        
        # Compute invariants
        invariants = compute_plane_curve_family_invariants(
            degree_coefficient_pairs,
            self.params.invariants.compute
        )
        
        # Add sampling metadata
        for inv in invariants:
            inv["sampling_strategy"] = self.params.sampling.strategy
            inv["seed"] = self.params.sampling.seed
        
        return invariants
    
    def sample_family(self, n_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Sample curve family based on parameters.
        
        Args:
            n_samples: Number of samples (uses default if None)
            
        Returns:
            List of dictionaries with curve data and invariants
        """
        if n_samples is None:
            n_samples = self.params.sampling.n_samples_default
        
        if self.params.family_type == "P1":
            return self.sample_p1_family(n_samples)
        elif self.params.family_type == "Elliptic":
            return self.sample_elliptic_family(n_samples)
        elif self.params.family_type == "Hyperelliptic":
            return self.sample_hyperelliptic_family(n_samples)
        elif self.params.family_type == "PlaneCurve":
            return self.sample_plane_curve_family(n_samples)
        else:
            raise ValueError(f"Unsupported family type: {self.params.family_type}")
    
    def save_family(self, family_data: List[Dict[str, Any]], output_dir: Path) -> Path:
        """Save sampled family to output directory.
        
        Args:
            family_data: List of curve data dictionaries
            output_dir: Directory to save output files
            
        Returns:
            Path to the saved family file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save family data
        family_file = output_dir / "family.json"
        with open(family_file, "w", encoding="utf-8") as f:
            json.dump(family_data, f, indent=2, ensure_ascii=False)
        
        return family_file
