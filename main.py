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

def extractSteps(step) -> list[str]:
    steps = []
    if isinstance(step, PartsRule):
        steps.append("Integration by parts:")
        steps.append(f"{step.integrand} by {step.variable}")
        steps.append(f"u: {step.u}")
        steps.append(f"dv: {step.dv}")
        steps.append(f"du: {diff(step.u, step.variable)}")
        steps.append(f"v: {integrate(step.v_step.integrand, step.variable)}")
        steps.append(f"I: {step.second_step.integrand} by {step.second_step.variable}")
    elif isinstance(step, ArctanRule):
        steps.append("Arctan rule:")
        steps.append(f"{step.integrand} by {step.variable}")
        steps.append(r"\int{\frac{1}{ax^2 + bx + c}}{dx}=\frac{2}{\sqrt{4ac-b^2}}\arctan(\frac{2ax+b}{\sqrt{4ac-b^2}})+C")
        steps.append(f"where a = {step.a}, b = {step.b}, and c = {step.c}")
        steps.append(f"{integrate(step.integrand, step.variable)}")
    else:
        steps.append("")
    return steps


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
        result = extractSteps(steps)
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
