"""Compute the one-sided Clopper–Pearson upper bound for release error."""

from argparse import ArgumentParser

from scipy.stats import beta


def upper_bound(errors, released, alpha=0.05):
    if released < 1 or not 0 <= errors <= released:
        raise ValueError("Provide at least one release and a valid error count.")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between zero and one.")
    if errors == released:
        return 1.0
    return float(beta.ppf(1 - alpha, errors + 1, released - errors))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("errors", type=int)
    parser.add_argument("released", type=int)
    args = parser.parse_args()
    try:
        bound = upper_bound(args.errors, args.released)
    except ValueError as error:
        parser.error(str(error))
    print(f"Observed error: {args.errors}/{args.released}")
    print(f"One-sided 95% upper bound: {bound:.2%}")
