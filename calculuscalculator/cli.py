#!/usr/bin/env python3
import argparse
import os
import sys
import pickle
from manim import Scene, MathTex, Write, FadeOut, VGroup, UP, DOWN, LEFT, RIGHT, ORIGIN, AnimationGroup

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
        """Render calculus steps with improved layout and error handling"""
        if not latex_steps:
            self._render_empty_message()
            return

        # Title with configurable options
        title = self._create_title("Integration Steps")
        
        # Steps with automatic spacing
        steps_group, final_height = self._create_steps_layout(latex_steps)
        
        # Center everything if it doesn't take full height
        if final_height < 6:  # Adjust based on your screen size
            steps_group.center()
        
        # Smooth animations with configurable timing
        self._animate_scene(title, steps_group)

    def _create_title(self, text: str) -> MathTex:
        """Create a styled title"""
        title = MathTex(f"\\text{{{text}}}")
        title.scale(1.5)
        title.to_edge(UP, buff=0.5)
        title.set_color("#4CAF50")  # Green color for better visual
        return title

    def _create_steps_layout(self, latex_steps: list[str]) -> tuple[VGroup, float]:
        """Create steps layout with automatic spacing"""
        steps_group = VGroup()
        current_position = 2.0
        max_width = 0
        
        for i, step in enumerate(latex_steps):
            try:
                step_group = self._create_single_step(i, step, current_position)
                steps_group.add(step_group)
                
                # Track maximum width for centering
                step_width = step_group.width
                max_width = max(max_width, step_width)
                
                current_position += 1.2
                
            except Exception as e:
                error_group = self._create_error_step(i, current_position)
                steps_group.add(error_group)
                current_position += 0.8
                debugging(f"Error in step {i}: {e}")
        
        # Center all steps horizontally if they're narrow
        if max_width < 10:  # Adjust based on your typical content width
            steps_group.move_to(ORIGIN).shift(DOWN * 1.0)
        
        return steps_group, current_position

    def _create_single_step(self, index: int, latex: str, y_position: float) -> VGroup:
        """Create a single step with proper formatting"""
        clean_latex = latex.replace("\n", " ").strip()
        
        # Step label
        step_label = MathTex(f"\\text{{Step {index + 1}:}}")
        step_label.scale(0.9)
        step_label.to_edge(LEFT, buff=0.5)
        step_label.shift(DOWN * y_position)
        step_label.set_color("#2196F3")  # Blue color for step numbers
        
        # Content - handle multi-line expressions
        content = MathTex(clean_latex)
        content.scale(0.8)
        content.next_to(step_label, RIGHT, buff=0.3)
        
        # Auto-scale content if it's too wide
        max_content_width = 10  # Maximum content width
        if content.width > max_content_width:
            scale_factor = max_content_width / content.width
            content.scale(scale_factor * 0.8)  # Additional 0.8 to be safe
        
        step_group = VGroup(step_label, content)
        return step_group

    def _create_error_step(self, index: int, y_position: float) -> VGroup:
        """Create an error step placeholder"""
        error_tex = MathTex(f"\\text{{Error in step {index + 1}}}")
        error_tex.scale(0.8)
        error_tex.to_edge(LEFT, buff=0.5)
        error_tex.shift(DOWN * y_position)
        error_tex.set_color("#F44336")  # Red color for errors
        return error_tex

    def _animate_scene(self, title: MathTex, steps_group: VGroup):
        """Animate the scene with better timing and effects"""
        # Title animation
        self.play(Write(title), run_time=1.5)
        self.wait(0.5)
        
        # Steps animation - sequential with lag
        animations = [Write(step) for step in steps_group]
        self.play(AnimationGroup(*animations, lag_ratio=0.3), run_time=2)
        self.wait(1)
        
        # Final display time based on content complexity
        display_time = min(3 + len(steps_group) * 0.5, 8)
        self.wait(display_time)
        
        # Smooth fade out
        self.play(
            FadeOut(title),
            FadeOut(steps_group),
            run_time=1.5
        )

    def _render_empty_message(self):
        """Render message when no steps are provided"""
        message = MathTex("\\text{No integration steps to display}")
        message.scale(1.2)
        message.set_color("#FF9800")  # Orange color for warnings
        self.play(Write(message))
        self.wait(2)
        self.play(FadeOut(message))


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