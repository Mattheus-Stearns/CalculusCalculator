#!/usr/bin/env python3
"""
Basic usage example of the calculuscalculator library
"""

from calculuscalculator import create_calculus_scene

# Create a scene with some integration steps
IntegrationScene = create_calculus_scene(
    [r"\int x^2 \, dx", r"\frac{x^3}{3} + C", r"\int \sin(x) \, dx", r"-\cos(x) + C"],
    "Basic Integrals",
)

# To render: uv run manim examples/basic_usage.py IntegrationScene
