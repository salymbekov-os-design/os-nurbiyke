import sys
from memsim import load, run


if len(sys.argv) < 2:
    print("Использование: python3 run_ops1.py first|best|worst")
    sys.exit(1)

strategy = sys.argv[1]

if strategy not in ("first", "best", "worst"):
    print("Стратегия должна быть: first, best или worst")
    sys.exit(1)

operations = load("ops1.txt")

run(
    operations,
    strategy,
    coalesce=False,
    verbose=True
)
