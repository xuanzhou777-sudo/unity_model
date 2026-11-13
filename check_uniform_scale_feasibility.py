"""Check whether one uniform scale can meet all corresponding dimensional bounds.

Axes, pose and attachment datum must already match. This is a mathematical
feasibility check, not proof that either dimensional source is historically valid.
"""
import argparse
import json
import math

def assess(measured, reference, tolerance):
    if len(measured) != len(reference) or not measured:
        raise ValueError('Corresponding measured/reference dimensions required')
    if not 0 <= tolerance < 1:
        raise ValueError('Tolerance must be in [0,1)')
    if any(not math.isfinite(x) or x <= 0 for x in measured + reference):
        raise ValueError('Dimensions must be finite and positive')
    ranges = [[r * (1-tolerance)/m, r * (1+tolerance)/m]
              for m, r in zip(measured, reference)]
    lo, hi = max(x[0] for x in ranges), min(x[1] for x in ranges)
    ratios = [m/r for m, r in zip(measured, reference)]
    best = 2/(min(ratios)+max(ratios))
    errors = [best*m/r-1 for m, r in zip(measured, reference)]
    return dict(relative_tolerance=tolerance, axis_scale_intervals=ranges,
                feasible=lo <= hi, intersection=[lo, hi] if lo <= hi else None,
                best_minimax_uniform_scale=best, best_axis_relative_errors=errors,
                best_max_relative_error=max(abs(x) for x in errors))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--measured', type=float, nargs='+', required=True)
    p.add_argument('--reference', type=float, nargs='+', required=True)
    p.add_argument('--tolerance', type=float, required=True)
    a = p.parse_args()
    print(json.dumps(assess(a.measured, a.reference, a.tolerance), indent=2))
