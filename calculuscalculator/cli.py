#!/usr/bin/env python3
import argparse
import os
import sys
import pickle
from manim import Scene, MathTex, Write, FadeOut, VGroup, UP, DOWN, LEFT, RIGHT

from calculuscalculator.core import CalculusSolver, debugging


class CalculusSolutionScene(Scene):
    """A Manim scene that renders calculus solutions"""
    
    def construct(self):
        """Main animation method"""
        try:
            with open("temp_render_data.pkl", "rb") as f:
                latex_steps = pickle.load(f)
            self.render_steps(latex_steps)
        except FileNotFoundError:
            # Fallback for testing
            self.render_steps([
                "\\int x^2 \\, dx = \\frac{x^3}{3} + C",
                "\\int \\sin(x) \\, dx = -\\cos(x) + C",
            ])

    def render_steps(self, latex_steps: list[str]):
        """Render calculus steps"""
        # Title
        title = MathTex("\\text{Integration Steps}")
        title.scale(1.5)
        title.to_edge(UP)

        # Steps group
        steps_group = VGroup()
        current_position = 2.0

        for i, step in enumerate(latex_steps):
            try:
                clean_step = step.replace("\n", " ").strip()

                step_label = MathTex(f"\\text{{Step {i + 1}}}")
                step_label.scale(0.9)
                step_label.to_edge(LEFT)
                step_label.shift(DOWN * current_position)

                content = MathTex(clean_step)
                content.scale(0.8)
                content.next_to(step_label, RIGHT, buff=0.5)

                step_pair = VGroup(step_label, content)
                steps_group.add(step_pair)

                current_position += 1.2

            except Exception as e:
                debugging(f"Error creating mobject for step {i}: {e}")
                error_tex = MathTex(f"\\text{{Error in step {i + 1}}}")
                error_tex.scale(0.8)
                error_tex.to_edge(LEFT)
                error_tex.shift(DOWN * current_position)
                steps_group.add(error_tex)
                current_position += 0.8

        # Animations
        self.play(Write(title))
        self.wait(1)
        self.play(Write(steps_group))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(steps_group))


def main():
    parser = argparse.ArgumentParser(
        description="A package that solves calculus expressions and renders a video explanation"
    )

    parser.add_argument(
        "filename",
        help="The input file (.txt) that has the latex expression of the equation to be solved"
    )

    parser.add_argument(
        "-o", "--output",
        help="The output file (.mp4) that saves the render"
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=1,
        help="Number of expressions to solve and render in the input file (default: 1)"
    )

    args = parser.parse_args()

    if args.debug:
        with open('Log.txt', 'w') as file:
            file.write("=========================\n\n     Log     Message\n\n=========================\n\n")
    
    debugging("[DEBUG] Starting Script...")
    
    solver = CalculusSolver()
    success, result = solver.read_expressions(args.filename, args.number)

    if success:
        renderArray = []
        for expr in result:
            debugging(f"Processing expression: {expr}")
            solution = solver.solve_expression(expr)
            debugging(f"Solution: {solution}")
            renderArray.append(solution)
        
        # Save the steps to a file
        with open('temp_render_data.pkl', 'wb') as f:
            pickle.dump(renderArray, f)
        
        # Run manim on our scene class
        output_flag = f"-o {args.output}" if args.output else ""
        cmd = f"uv run manim calculuscalculator/cli.py CalculusSolutionScene {output_flag}"
        debugging(f"Running: {cmd}")
        os.system(cmd)
        
        # Clean up
        if os.path.exists('temp_render_data.pkl'):
            os.remove('temp_render_data.pkl')
        
    else:
        debugging(result)
        sys.exit(1)

    debugging("[DEBUG] Script finished.")


if __name__ == "__main__":
    main()