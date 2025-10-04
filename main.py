import sympy
import latex2sympy2
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

    if success:
        for expr in result:
            print(f"Processing expression: {expr}")
    else:
        print(result)
        sys.exit(1)

    if args.output:
        print(f"Results will be written to {args.output}")

    if args.debug:
        print("[DEBUG] Script finished.")



if __name__ == "__main__":
    main()
