from manim import Scene
import pickle
from .renderer import CalculusRenderer

class DynamicCalculusScene(Scene):
    """A scene that loads and renders calculus steps from a temp file"""
    
    def construct(self):
        try:
            with open("temp_render_data.pkl", "rb") as f:
                latex_steps = pickle.load(f)
            
            renderer = CalculusRenderer()
            renderer.render_calculus_steps(latex_steps, "Calculus Solutions")
            
        except FileNotFoundError:
            # Fallback for testing
            renderer = CalculusRenderer()
            renderer.render_calculus_steps([
                "\\int x^2 \\, dx = \\frac{x^3}{3} + C",
                "\\int \\sin(x) \\, dx = -\\cos(x) + C",
            ], "Calculus Solutions")