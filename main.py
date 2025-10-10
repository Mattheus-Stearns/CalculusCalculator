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
    integral_steps
)
from sympy.printing.latex import latex
from latex2sympy2 import latex2sympy, latex2latex
from manim import MathTex, Write, FadeOut, Scene
import argparse
from itertools import islice
import sys
import os

class renderScene(Scene):

    def readExpressions(self, file_path: str, numExpressions: int) -> tuple[bool, list[str] | str]:
        arrayLines = []
        try:
            with open(file_path, 'r') as file:
                for line in islice(file, numExpressions):
                    arrayLines.append(line.strip())
            return True, arrayLines
        except FileNotFoundError:
            return False, f"Error: The file '{file_path}' was not found."
        except Exception as e:
            return False, f"An error occurred: {e}"

    def rule_to_latex(self, rule):
        """Recursively converts a SymPy manualintegrate rule into human-readable LaTeX."""
        renderSceneInstance = renderScene()
        if isinstance(rule, PartsRule):
            # Integration by parts
            u = latex(rule.u)
            dv = latex(rule.dv)
            v_expr = latex(rule.v_step.integrand)
            step_latex = (
                f"\\text{{Integration by parts: }} "
                f"\\int {latex(rule.integrand)} \\, d{latex(rule.variable)} = "
                f"{u} \\cdot ({v_expr}) - \\int ({v_expr}) \\, d({u})"
            )
            sub = renderSceneInstance.rule_to_latex(rule.second_step) if rule.second_step else ""
            return step_latex + (" \\\\ " + sub if sub else "")

        elif isinstance(rule, URule):
            return (
                f"\\text{{Substitute }} u = {latex(rule.u_func)}, "
                f"\\text{{ then }} du = d({latex(rule.u_func)})"
                + (" \\\\ " + renderSceneInstance.rule_to_latex(rule.substep) if rule.substep else "")
            )

        elif isinstance(rule, ConstantTimesRule):
            return (
                f"\\text{{Constant multiple rule: }} "
                f"\\int {latex(rule.constant)}({latex(rule.other)}) \\, d{latex(rule.variable)} = "
                f"{latex(rule.constant)} \\int {latex(rule.other)} \\, d{latex(rule.variable)}"
                + (" \\\\ " + renderSceneInstance.rule_to_latex(rule.substep) if rule.substep else "")
            )

        elif isinstance(rule, PowerRule):
            return (
                f"\\text{{Power rule: }} "
                f"\\int {latex(rule.base)}^{latex(rule.exp)} \\, d{latex(rule.variable)} = "
                f"\\frac{{{latex(rule.base)}^{{{latex(rule.exp + 1)}}}}}{{{latex(rule.exp + 1)}}} + C"
            )

        elif isinstance(rule, AddRule):
            substeps = [renderSceneInstance.rule_to_latex(s) for s in rule.substeps]
            return (
                f"\\text{{Sum rule: }} \\int ({latex(rule.integrand)}) \\, d{latex(rule.variable)} = "
                + " + ".join(substeps)
            )

        elif isinstance(rule, AlternativeRule):
            subs = [renderSceneInstance.rule_to_latex(s) for s in rule.alternatives]
            return "\\text{Alternative methods: } " + " \\text{ or } ".join(subs)

        elif isinstance(rule, RewriteRule):
            return (
                f"\\text{{Rewrite }} {latex(rule.integrand)} = {latex(rule.rewritten)}"
                + (" \\\\ " + renderSceneInstance.rule_to_latex(rule.substep) if rule.substep else "")
            )

        elif isinstance(rule, (SinRule, CosRule, ExpRule, ArctanRule)):
            return (
                f"\\text{{Direct integration: }} "
                f"\\int {latex(rule.integrand)} \\, d{latex(rule.variable)}"
            )

        else:
            return f"\\text{{Unhandled rule: }} {latex(rule.integrand)}"

    def solveExpression(self, expression: str) -> list[str]:
        renderSceneInstance = renderScene()
        tex = expression
        if r"\int" in tex:
            operation = "integrate"
        elif r"\frac{d" in tex or r"\partial" in tex:
            operation = "differentiate"
        else:
            operation = "evaluate"
        sympy = latex2sympy(tex)
        if operation == "integrate":
            steps = integral_steps(sympy.function, sympy.variables[0])
            result = renderSceneInstance.rule_to_latex(steps)
        debugging(steps)
        debugging(result)
        return result

    def renderExpressions(self, latex_steps: list[list[str]]):
        for step in latex_steps:
            tex = MathTex(step)
            tex.scale(1.2)
            self.play(Write(tex))
            self.wait(1)
            self.play(FadeOut(tex)) 
            

def debugging(statement: str):
    if os.path.exists('Log.txt'):
        with open('Log.txt', 'a') as file:
            file.write(f"{statement}")
            file.write('\n')
    else:
        return

def main():

    renderSceneInstance = renderScene()

    parser = argparse.ArgumentParser(
        description="A package that solves calculus expressions and renders a video explanation alongside a geometric expression of what is happening."
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
    debugging(f"[DEBUG] Parsed arguments: {args}")
    
    success, result = renderSceneInstance.readExpressions(args.filename, args.number)

    debugging(f"[DEBUG] Loaded {len(result)} expressions")

    renderArray = []

    if success:
        for expr in result:
            debugging(f"Processing expression: {expr}")
            renderArray.append(renderSceneInstance.solveExpression(expr))
        renderSceneInstance.renderExpressions(renderArray)
    else:
        debugging(result)
        sys.exit(1)

    if args.output:
        print(f"Results will be written to {args.output}")
        debugging(f"Results will be written to {args.output}")

    debugging("[DEBUG] Script finished.")



if __name__ == "__main__":
    main()
