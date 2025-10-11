# CalculusCalculator
This is a repository that will help people solve calculus problems by solving them in their determinate and indeterminate forms, and then producing a .mp4 explaining all the steps using manim. 

```
usage: calculus-calculator [-h] [-o OUTPUT] [-d] [-n NUMBER] filename

A package that solves calculus expressions and renders a video explanation

positional arguments:
  filename             The input file (.txt) that has the latex expression of the equation to be solved

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  The output file (.mp4) that saves the render
  -d, --debug          Enable debug mode
  -n, --number NUMBER  Number of expressions to solve and render in the input file (default: 1)
```