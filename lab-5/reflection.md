# Reflection

**1. Which issues were the easiest and hardest to fix?**
Flake8 issues were the easiest because they were mechanical: spacing, blank lines and line length. The hardest was the Bandit shell-injection finding, because it needed a real change in design (validate the input and drop the shell) rather than a formatting edit, and the first obvious fix (`subprocess`) would have created new low-severity warnings.

**2. Did the tools report any false positives, or miss anything?**
The hardcoded-password warning was technically a true positive but low risk, since the value was unused demo text. Removing it was still the right call. None of the tools caught the logic question in `calculate_units`: a backwards meter reading prints a warning and bills zero units, but the customer still pays the fixed charge. That is a design decision a tool can't judge.

**3. How could static analysis fit into a real development workflow?**
Run Flake8 and Pylint as a pre-commit hook and in CI so style and quality problems never reach review, and run Bandit in CI to block high-severity findings from merging. That keeps reviewers focused on logic instead of formatting.

**4. What improvements did the fixes make to the code?**
Security improved (no shell injection, safe XML parsing, no secret in source). The mutable default argument was a real bug that would have caused shared state between calls. Naming, docstrings and formatting made the code more readable and consistent, and the Pylint score went from 5.44 to 10.00 with the program's output unchanged.
