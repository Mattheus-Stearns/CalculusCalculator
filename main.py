# DEV: source "/Users/mattheusstearns/Desktop/Desktop Folder/Coding/CalculusCalculator/.venv/bin/activate"
from sympy import sin, cos, tan, exp, log, integrate, diff
from sympy.integrals.manualintegrate import (
    PartsRule,
    ConstantRule,
    AddRule,
    PowerRule,
    ExpRule,
    TrigRule,
    SinRule,
    CosRule,
    ArctanRule,
    RewriteRule,
    AlternativeRule,
    manualintegrate,
    URule,
    ConstantTimesRule,
    integral_steps,
)
from sympy.printing.latex import latex
from latex2sympy2 import latex2sympy, latex2latex
from manim import MathTex, Write, FadeOut, Scene, DOWN, UP, LEFT, RIGHT, VGroup
import argparse
from itertools import islice
import sys
import os
import pickle


class renderScene(Scene):
    def construct(self):
        """Main Manim method - called automatically when rendering"""
        # We need to get the latex_steps data somehow
        # Option 1: Load from file
        try:
            with open("temp_render_data.pkl", "rb") as f:
                latex_steps = pickle.load(f)
            self.render_steps(latex_steps)
        except FileNotFoundError:
            # Option 2: Use default data for testing
            self.render_steps(
                [
                    "\\int x^2 \\, dx = \\frac{x^3}{3} + C",
                    "\\int \\sin(x) \\, dx = -\\cos(x) + C",
                ]
            )

    def render_steps(self, latex_steps: list[str]):
        """Replaces the old renderExpressions method"""
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

    def readExpressions(
        self, file_path: str, numExpressions: int
    ) -> tuple[bool, list[str] | str]:
        arrayLines = []
        try:
            with open(file_path, "r") as file:
                for line in islice(file, numExpressions):
                    arrayLines.append(line.strip())
            return True, arrayLines
        except FileNotFoundError:
            return False, f"Error: The file '{file_path}' was not found."
        except Exception as e:
            return False, f"An error occurred: {e}"

    def rule_to_latex(self, rule, depth=0):
        """Recursively converts a SymPy manualintegrate rule into human-readable LaTeX."""

        def format_integral(integrand, variable):
            return f"\\int {integrand} \\, d{variable}"

        def recurse(subrule):
            return self.rule_to_latex(subrule, depth + 1)

        try:
            if isinstance(rule, PartsRule):
                # Integration by parts: ∫u dv = uv - ∫v du
                u = latex(rule.u)
                v_integrand = latex(rule.v_step.integrand) if rule.v_step else ""
                step_latex = (
                    f"\\text{{Integration by parts: }} "
                    f"{format_integral(latex(rule.integrand), latex(rule.variable))} = "
                    f"{u} \\cdot \\int {v_integrand} \\, d{latex(rule.variable)} - "
                    f"\\int \\left( \\int {v_integrand} \\, d{latex(rule.variable)} \\right) \\, d({u})"
                )
                return step_latex

            elif isinstance(rule, URule):
                # U-substitution
                u_func = latex(rule.u_func)
                step_latex = f"\\text{{U-substitution: }} u = {u_func}"
                if rule.substep:
                    step_latex += f", \\quad \\text{{then }} {recurse(rule.substep)}"
                return step_latex

            elif isinstance(rule, ConstantTimesRule):
                # Constant multiple rule
                step_latex = (
                    f"\\text{{Constant multiple: }} "
                    f"{format_integral(latex(rule.integrand), latex(rule.variable))} = "
                    f"{latex(rule.constant)} \\cdot {format_integral(latex(rule.other), latex(rule.variable))}"
                )
                if rule.substep:
                    step_latex += f" = {latex(rule.constant)} \\cdot \\left( {recurse(rule.substep)} \\right)"
                return step_latex

            elif isinstance(rule, PowerRule):
                # Power rule: ∫xⁿ dx = xⁿ⁺¹/(n+1) + C
                base = latex(rule.base)
                exp = latex(rule.exp)
                new_exp = latex(rule.exp + 1)

                # Handle special case where base is the variable
                if base == latex(rule.variable):
                    integral_expr = f"{base}^{{{exp}}}"
                    result_expr = f"\\frac{{{base}^{{{new_exp}}}}}{{{new_exp}}}"
                else:
                    integral_expr = f"{base}^{{{exp}}}"
                    result_expr = f"\\frac{{{base}^{{{new_exp}}}}}{{{new_exp}}}"

                return (
                    f"\\text{{Power rule: }} "
                    f"{format_integral(integral_expr, latex(rule.variable))} = "
                    f"{result_expr} + C"
                )

            elif isinstance(rule, AddRule):
                # Sum rule - be careful with recursion here
                if depth > 5:  # Prevent infinite recursion
                    return format_integral(latex(rule.integrand), latex(rule.variable))

                substeps = []
                for substep in rule.substeps[
                    :2
                ]:  # Limit to first 2 steps to avoid complexity
                    try:
                        substeps.append(recurse(substep))
                    except:
                        substeps.append("...")

                step_latex = f"\\text{{Sum rule: }} {format_integral(latex(rule.integrand), latex(rule.variable))}"
                if substeps:
                    step_latex += f" = {' + '.join(substeps)}"
                return step_latex

            elif isinstance(rule, AlternativeRule):
                # Just take the first alternative to avoid complexity
                if rule.alternatives:
                    return recurse(rule.alternatives[0])
                return format_integral(latex(rule.integrand), latex(rule.variable))

            elif isinstance(rule, RewriteRule):
                # Rewrite the integrand
                step_latex = f"\\text{{Rewrite: }} {latex(rule.integrand)} = {latex(rule.rewritten)}"
                if rule.substep:
                    step_latex += f" \\\\ \\Rightarrow {recurse(rule.substep)}"
                return step_latex

            elif isinstance(rule, SinRule):
                return f"\\int \\sin({latex(rule.variable)}) \\, d{latex(rule.variable)} = -\\cos({latex(rule.variable)}) + C"

            elif isinstance(rule, CosRule):
                return f"\\int \\cos({latex(rule.variable)}) \\, d{latex(rule.variable)} = \\sin({latex(rule.variable)}) + C"

            elif isinstance(rule, ExpRule):
                base = latex(rule.base)
                if base == "E":
                    return f"\\int e^{{{latex(rule.variable)}}} \\, d{latex(rule.variable)} = e^{{{latex(rule.variable)}}} + C"
                else:
                    return f"\\int {base}^{{{latex(rule.variable)}}} \\, d{latex(rule.variable)} = \\frac{{{base}^{{{latex(rule.variable)}}}}}{{\\ln({base})}} + C"

            elif isinstance(rule, ArctanRule):
                return f"\\int \\frac{{1}}{{{latex(rule.variable)}^2 + 1}} \\, d{latex(rule.variable)} = \\arctan({latex(rule.variable)}) + C"

            elif isinstance(rule, ConstantRule):
                return f"\\int {latex(rule.constant)} \\, d{latex(rule.variable)} = {latex(rule.constant)}{latex(rule.variable)} + C"

            elif hasattr(rule, "integrand") and hasattr(rule, "variable"):
                # Fallback for unhandled rules
                return f"\\int {latex(rule.integrand)} \\, d{latex(rule.variable)}"

            else:
                return f"\\text{{Apply integration}}"

        except Exception as e:
            debugging(f"Error in rule_to_latex for {type(rule).__name__}: {e}")
            return f"\\text{{Step}}"

    def debug_rule_structure(self, rule, indent=0):
        """Debug method to understand the rule structure"""
        prefix = "  " * indent
        debugging(
            f"{prefix}{type(rule).__name__}: {getattr(rule, 'integrand', 'No integrand')}"
        )

        # Recursively debug substeps
        if hasattr(rule, "substep") and rule.substep:
            self.debug_rule_structure(rule.substep, indent + 1)
        if hasattr(rule, "substeps") and rule.substeps:
            for i, substep in enumerate(rule.substeps):
                debugging(f"{prefix}  Substep {i}:")
                self.debug_rule_structure(substep, indent + 2)
        if hasattr(rule, "second_step") and rule.second_step:
            debugging(f"{prefix}  Second step:")
            self.debug_rule_structure(rule.second_step, indent + 1)

    def solveExpression(self, expression: str) -> str:
        tex = expression
        if r"\int" in tex:
            operation = "integrate"
        elif r"\frac{d" in tex or r"\partial" in tex:
            operation = "differentiate"
        else:
            operation = "evaluate"

        sympy_expr = latex2sympy(tex)

        if operation == "integrate":
            steps = integral_steps(sympy_expr.function, sympy_expr.variables[0])

            # Debug the rule structure
            debugging("=== RULE STRUCTURE ===")
            self.debug_rule_structure(steps)
            debugging("=====================")

            result = self.rule_to_latex(steps)
            debugging(f"Final LaTeX: {result}")

            return result
        else:
            return f"\\text{{Operation '{operation}' not yet implemented}}"


def debugging(statement: str):
    if os.path.exists("Log.txt"):
        with open("Log.txt", "a") as file:
            file.write(f"{statement}")
            file.write("\n")
    else:
        return


def main():
    parser = argparse.ArgumentParser(
        description="A package that solves calculus expressions and renders a video explanation alongside a geometric expression of what is happening."
    )

    parser.add_argument(
        "filename",
        help="The input file (.txt) that has the latex expression of the equation to be solved",
    )

    parser.add_argument(
        "-o", "--output", help="The output file (.mp4) that saves the render"
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=1,
        help="Number of expressions to solve and render in the input file (default: 1)",
    )

    args = parser.parse_args()

    if args.debug:
        with open("Log.txt", "w") as file:
            file.write(
                "=========================\n\n     Log     Message\n\n=========================\n\n"
            )

    debugging("[DEBUG] Starting Script...")
    debugging(f"[DEBUG] Parsed arguments: {args}")

    # Read expressions
    success, result = renderScene().readExpressions(args.filename, args.number)

    debugging(f"[DEBUG] Loaded {len(result)} expressions")

    renderArray = []

    if success:
        for expr in result:
            debugging(f"Processing expression: {expr}")
            renderArray.append(renderScene().solveExpression(expr))

        # Instead of manually calling render, let Manim handle it
        # We need to pass the data to the scene differently

        # Save the renderArray to a temporary file or use class variable
        with open("temp_render_data.pkl", "wb") as f:
            pickle.dump(renderArray, f)

        # Now render using manim command line
        output_flag = f"-o {args.output}" if args.output else ""
        cmd = f"manim main.py renderScene {output_flag} --format=mp4"
        debugging(f"Running command: {cmd}")
        os.system(cmd)

    else:
        debugging(result)
        sys.exit(1)

    debugging("[DEBUG] Script finished.")


if __name__ == "__main__":
    main()
