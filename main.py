# DEV: source "/Users/mattheuspieterstearns/Desktop/Desktop Folder/Coding/CalculusCalculator/.venv/bin/activate"
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
import manim
import argparse
from itertools import islice
import sys

def readExpressions(file_path: str, numExpressions: int) -> tuple[bool, list[str] | str]:
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

def rule_to_latex(rule):
    """Recursively converts a SymPy manualintegrate rule into human-readable LaTeX."""
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
        sub = rule_to_latex(rule.second_step) if rule.second_step else ""
        return step_latex + (" \\\\ " + sub if sub else "")

    elif isinstance(rule, URule):
        return (
            f"\\text{{Substitute }} u = {latex(rule.u_func)}, "
            f"\\text{{ then }} du = d({latex(rule.u_func)})"
            + (" \\\\ " + rule_to_latex(rule.substep) if rule.substep else "")
        )

    elif isinstance(rule, ConstantTimesRule):
        return (
            f"\\text{{Constant multiple rule: }} "
            f"\\int {latex(rule.constant)}({latex(rule.other)}) \\, d{latex(rule.variable)} = "
            f"{latex(rule.constant)} \\int {latex(rule.other)} \\, d{latex(rule.variable)}"
            + (" \\\\ " + rule_to_latex(rule.substep) if rule.substep else "")
        )

    elif isinstance(rule, PowerRule):
        return (
            f"\\text{{Power rule: }} "
            f"\\int {latex(rule.base)}^{latex(rule.exp)} \\, d{latex(rule.variable)} = "
            f"\\frac{{{latex(rule.base)}^{{{latex(rule.exp + 1)}}}}}{{{latex(rule.exp + 1)}}} + C"
        )

    elif isinstance(rule, AddRule):
        substeps = [rule_to_latex(s) for s in rule.substeps]
        return (
            f"\\text{{Sum rule: }} \\int ({latex(rule.integrand)}) \\, d{latex(rule.variable)} = "
            + " + ".join(substeps)
        )

    elif isinstance(rule, AlternativeRule):
        subs = [rule_to_latex(s) for s in rule.alternatives]
        return "\\text{Alternative methods: } " + " \\text{ or } ".join(subs)

    elif isinstance(rule, RewriteRule):
        return (
            f"\\text{{Rewrite }} {latex(rule.integrand)} = {latex(rule.rewritten)}"
            + (" \\\\ " + rule_to_latex(rule.substep) if rule.substep else "")
        )

    elif isinstance(rule, (SinRule, CosRule, ExpRule, ArctanRule)):
        return (
            f"\\text{{Direct integration: }} "
            f"\\int {latex(rule.integrand)} \\, d{latex(rule.variable)}"
        )

    else:
        # Fallback
        return f"\\text{{Unhandled rule: }} {latex(rule.integrand)}"


def solveExpression(expression: str) -> list[str]:
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
        result = rule_to_latex(steps)
    print(steps)
    print(result)
    return result

def renderExpressions(renderArray: list[list[str]]):
    return 

def main():
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
        print("[DEBUG] Starting Script...")
        print(f"[DEBUG] Parsed arguments: {args}")
    
    success, result = readExpressions(args.filename, args.number)

    if args.debug:
        print(f"[DEBUG] Loaded {len(result)} expressions")

    renderArray = []

    if success:
        for expr in result:
            print(f"Processing expression: {expr}")
            renderArray.append(solveExpression(expr))
        renderExpressions(renderArray)
    else:
        print(result)
        sys.exit(1)

    if args.output:
        print(f"Results will be written to {args.output}")

    if args.debug:
        print("[DEBUG] Script finished.")



if __name__ == "__main__":
    main()
