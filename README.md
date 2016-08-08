# Rectangle packing solver

This is a effective solver for 2D-rectangle-packing problem, which is a typical combinatorial optimization problem having wide usage in various fields.

## Problem description
- Input a set of rectangles
- Output the complete arrangement of these rectangles
- Constraints
    + Each rectangle is aligned to X and Y axis
    + No overlapping is allowed
- Objective
    + Mimize the area of the bounding box covering all rectangles
- Analogy
    + It is like given a large piece of cloth and required is a set of small pieces for some assembling work. The objective is to cut off these required pieces with least consumption of the large cloth.

## Highlight of this approach
- No utilities from computational graphicscomputational geometry are used, the underlying data structure resembles a Threaded-Tree.
- This means, spatial restrictions can be detected by simple arithmetics, rather than applying geometric algorithms.
- This approach sacrifices completeness of by considering stacking direction merely upwardsrightwards. However, the results seem satisfying.
- Greedy method comprises good solutions already. Extension with further optimization schemes is possible.
- Much more performant implementation can be derived from this Python implementation with no dependencies required.