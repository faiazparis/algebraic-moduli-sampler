"""Command-line interface for Algebraic Moduli Sampler.

This module provides the CLI commands:
- validate: Validate parameter files
- sample: Sample curve families
- invariants: Compute invariants for existing families
- pipeline: Run complete sampling and invariant computation pipeline
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import rich.console
import rich.table
from rich import print as rprint

from .sampling import Sampler, load_params_from_file
from .geometry.invariants import summarize_family_invariants, validate_invariants_consistency
from .io import save_metadata


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Algebraic Moduli Sampler: Sheaf Cohomology on Curves.
    
    A zero-cost, local-first, reproducible, and test-driven Python library
    for sampling algebraic curve families and computing sheaf-cohomology-based invariants.
    
    All mathematics is grounded in trusted references with explicit citations.
    """
    pass


@main.command()
@click.argument("params_file", type=click.Path(exists=True, path_type=Path))
def validate(params_file: Path):
    """Validate a parameter file against the schema.
    
    This command checks that the parameter file conforms to the
    expected JSON schema and family-specific constraints.
    """
    console = rich.console.Console()
    
    try:
        with console.status("[bold green]Validating parameters..."):
            params = load_params_from_file(params_file)
        
        console.print(f"[bold green]✓[/bold green] Parameters valid!")
        console.print(f"Family type: [bold blue]{params.family_type}[/bold blue]")
        console.print(f"Sampling strategy: [bold blue]{params.sampling.strategy}[/bold blue]")
        console.print(f"Default samples: [bold blue]{params.sampling.n_samples_default}[/bold blue]")
        console.print(f"Seed: [bold blue]{params.sampling.seed}[/bold blue]")
        console.print(f"Invariants: [bold blue]{', '.join(params.invariants.compute)}[/bold blue]")
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Validation failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("params_file", type=click.Path(exists=True, path_type=Path))
@click.option("--seed", type=int, help="Override random seed")
@click.option("--n", type=int, help="Number of samples to generate")
@click.option("--out", type=click.Path(path_type=Path), default="./output", help="Output directory")
def sample(params_file: Path, seed: Optional[int], n: Optional[int], out: Path):
    """Sample a curve family based on parameters.
    
    This command generates a family of curves according to the
    specified parameters and saves the results.
    """
    console = rich.console.Console()
    
    try:
        with console.status("[bold green]Loading parameters..."):
            params = load_params_from_file(params_file)
        
        # Override seed if specified
        if seed is not None:
            params.sampling.seed = seed
        
        with console.status("[bold green]Sampling curve family..."):
            sampler = Sampler(params)
            family_data = sampler.sample_family(n)
        
        with console.status("[bold green]Saving results..."):
            family_file = sampler.save_family(family_data, out)
            
            # Save metadata
            metadata = {
                "command": "sample",
                "params_file": str(params_file),
                "seed": params.sampling.seed,
                "n_samples": len(family_data),
                "family_type": params.family_type,
                "sampling_strategy": params.sampling.strategy,
                "invariants_computed": params.invariants.compute,
            }
            metadata_file = out / "metadata.json"
            save_metadata(metadata, metadata_file)
        
        console.print(f"[bold green]✓[/bold green] Sampling complete!")
        console.print(f"Generated [bold blue]{len(family_data)}[/bold blue] curves")
        console.print(f"Family data: [bold blue]{family_file}[/bold blue]")
        console.print(f"Metadata: [bold blue]{metadata_file}[/bold blue]")
        
        # Display summary
        summary = summarize_family_invariants(family_data)
        if summary:
            table = rich.table.Table(title="Family Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in summary.items():
                table.add_row(key, str(value))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Sampling failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("family_file", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default="./invariants.json", help="Output file")
def invariants(family_file: Path, out: Path):
    """Compute invariants for an existing curve family.
    
    This command loads a previously sampled family and computes
    additional invariants or validates existing ones.
    """
    console = rich.console.Console()
    
    try:
        with console.status("[bold green]Loading family data..."):
            with open(family_file, "r", encoding="utf-8") as f:
                family_data = json.load(f)
        
        with console.status("[bold green]Computing invariants..."):
            # Validate consistency of existing invariants
            consistency = validate_invariants_consistency(family_data)
            
            # Compute summary statistics
            summary = summarize_family_invariants(family_data)
        
        with console.status("[bold green]Saving results..."):
            results = {
                "family_file": str(family_file),
                "consistency_check": consistency,
                "summary": summary,
                "curve_data": family_data,
            }
            
            with open(out, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[bold green]✓[/bold green] Invariants computed!")
        console.print(f"Results saved to: [bold blue]{out}[/bold blue]")
        
        # Display consistency results
        if consistency["validation_errors"]:
            console.print(f"[bold yellow]⚠[/bold yellow] Found {len(consistency['validation_errors'])} validation errors")
            for error in consistency["validation_errors"][:3]:  # Show first 3
                console.print(f"  Curve {error['curve_index']}: {', '.join(error['errors'])}")
        else:
            console.print("[bold green]✓[/bold green] All consistency checks passed")
        
        # Display summary
        if summary:
            table = rich.table.Table(title="Family Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in summary.items():
                table.add_row(key, str(value))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Invariant computation failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("params_file", type=click.Path(exists=True, path_type=Path))
@click.option("--seed", type=int, help="Override random seed")
@click.option("--n", type=int, help="Number of samples to generate")
@click.option("--out", type=click.Path(path_type=Path), default="./pipeline_output", help="Output directory")
def pipeline(params_file: Path, seed: Optional[int], n: Optional[int], out: Path):
    """Run complete sampling and invariant computation pipeline.
    
    This command combines sampling and invariant computation in a
    single workflow for convenience.
    """
    console = rich.console.Console()
    
    try:
        with console.status("[bold green]Running complete pipeline..."):
            # Step 1: Load and validate parameters
            params = load_params_from_file(params_file)
            if seed is not None:
                params.sampling.seed = seed
            
            # Step 2: Sample curve family
            sampler = Sampler(params)
            family_data = sampler.sample_family(n)
            
            # Step 3: Save family data
            family_file = sampler.save_family(family_data, out)
            
            # Step 4: Compute invariants and validate
            consistency = validate_invariants_consistency(family_data)
            summary = summarize_family_invariants(family_data)
            
            # Step 5: Save complete results
            results = {
                "family_file": str(family_file),
                "consistency_check": consistency,
                "summary": summary,
                "curve_data": family_data,
            }
            
            results_file = out / "results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Step 6: Save metadata
            metadata = {
                "command": "pipeline",
                "params_file": str(params_file),
                "seed": params.sampling.seed,
                "n_samples": len(family_data),
                "family_type": params.family_type,
                "sampling_strategy": params.sampling.strategy,
                "invariants_computed": params.invariants.compute,
                "consistency_checks_passed": len(consistency["validation_errors"]) == 0,
            }
            metadata_file = out / "metadata.json"
            save_metadata(metadata, metadata_file)
        
        console.print(f"[bold green]✓[/bold green] Pipeline complete!")
        console.print(f"Generated [bold blue]{len(family_data)}[/bold blue] curves")
        console.print(f"Family data: [bold blue]{family_file}[/bold blue]")
        console.print(f"Results: [bold blue]{results_file}[/bold blue]")
        console.print(f"Metadata: [bold blue]{metadata_file}[/bold blue]")
        
        # Display consistency results
        if consistency["validation_errors"]:
            console.print(f"[bold yellow]⚠[/bold yellow] Found {len(consistency['validation_errors'])} validation errors")
        else:
            console.print("[bold green]✓[/bold green] All consistency checks passed")
        
        # Display summary
        if summary:
            table = rich.table.Table(title="Pipeline Results Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in summary.items():
                table.add_row(key, str(value))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
