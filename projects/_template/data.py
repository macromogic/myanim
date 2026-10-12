"""All numbers shown on screen, computed in one place. Run to print and self-check."""

EXAMPLE = [1.0, 2.0, 3.0]
TOTAL = round(sum(EXAMPLE), 2)

assert TOTAL == 6.0

if __name__ == "__main__":
    for name in ["EXAMPLE", "TOTAL"]:
        print(f"{name:8s} {globals()[name]}")
