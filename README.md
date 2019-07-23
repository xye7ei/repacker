repacker
=====

`repacker` is a highly effective solver for 2D-rectangle-packing problem based on a dedicated data structure and heuristics like greedy algorithm.

<!-- In short, the packing problem requires to give a plan of placing rectangles in a 2D space, edges aligned, targeting the minimum bounding-box area. -->

#### Problem revisited

The 2D-rectangle-packing problem can be literally formalized as

| Item | Setting |
|---|---|
| *Input* | • A set of 2D rectangles <br/>  |
| *Output* | • Arrangement of all these rectangles in a 2D space  |
| *Constraints* | • Each rectangle is aligned to X and Y axes of the space. <br/> • No overlapping is allowed. |
| *Objective* | • Minimize the area of the bounding box aligned to axes and including all rectangles. |

The objective value is also denoted as *occupancy rate*.

<!-- This may be tricky to solve straighforwardly. -->

## First view

Given a set of 200 (random-generated) example rectangles, `repacker` delivers a highly optimized packing plan like:

<p>
	<img src="./sample_figure_200.png" width="350" height="350" />
</p>

with 93.92% occupancy rate. With another amount of example rectangles, say 1000:

<p>
	<img src="./sample_figure_1000.png" width="400" height="400" />
</p>

<!-- <sup>[1]</sup>. -->

<!-- <sub>[1]. Except when the sizes of many rectangles are same, which is the degeneracy case to be fixed in the future. </sub>
 -->


solution achieves 95.62% occupancy rate.


From testing of `repacker`, such rate is on average above 90% for input sets with size more than 50.


## Performance

The algorithm is firstly implemented in Python then ported to *C++*. The performance is heavily improved.
Given ca. 6000 rectangles, C++ code produces a output within ca. 5~6 seconds.

<p>
    <img src="./cpp/test_rand_more.png" width="50%" height="50%" />
</p>

The performance of C++ code is surprisingly good, however I do not know yet how to plot the result conveniently using
C++.


## Usage

The algorithm can be called via command-line
```
python repacker.py <input-file> [<output-file>] [-n]
```

where

- `<input-file>` is text file as a list of 2-tuples in Python syntax, representing the sizes of the rectangles.

- `<output-file` is the path to the solution file, which is a Python list.

- `-n` means producing no figure for depicting the solution.

[*] No 3rd-party module is required for solving, but module `PIL` is required for drawing the results like the figures above.


## Features of this solver

- No utilities from computational graphics or computational geometry are used, since the underlying data structure is indeed a list.
 I personally name it *threaded quad-pointers*, which is a 1D list of all modelled rectangle *corners*.
- With this structure, spatial relations can be computed via simple arithmetics, instead of any complicated geometric
 algorithm.
- The complexity is roughly O(N²). In pure Python, an input with 1000 rectangles can be solved within several seconds.
- The heuristical approach for deciding optimal placement can be categorized as a combination of strategies of *Greedy*,
 *Bottom-Left*, *Best-Fit*, which have been explored extensively in various literature.

<!--
- More performant implementation can be derived from this Python implementation with no language-specific .
-->


<!-- | *Extension* |• Any rectangle can be replaced with its 90°-rotated version. | -->

The solution to this problem may find usage in various fields. For example, given a large plate of steel, we may be required to slice it into small rectangle pieces for future assembling work according to some engineering plot and hope to use this plate most economically.


## Approach details

### Objective value representing the bounding

Based on the *threaded quad-pointers* data structure, instead of computing the occupancy rate i.e. the bounding box area,
an alternative function `F` is proved to be more effective as the objective function.
Given a rectangle `r` and potential placement of it at coordinate `c`,

```
F(r, c) = B(r, c).width + B(r, c).height
```

where `B` is the bounding box determined via placing `(r, c)`<sup>※</sup>.

A possible interpretation for `F`'s benefit is that using `B.area` may lead to the rectangle cluster growing like a
 long band, rather than growing like a box. Suppose we have already a "long" bounding box `B` where `B.height`
 is much greater than `B.width` and we are to place a rectangle `r` with roughly the size `d`,
 then placing `r` on the short leads to a huge increment of the bounding area, i.e.

```
Δ(B.area) == d * B.height
```

which is much greater than placing on the short side where

```
Δ(B.area) == d * B.width
```

As a consequence, following the trend that `r` is always placed along the long side when using `B.area` as the
evaluation function, the objective value gradually loses further chance to get improved.

In contrast, with `F`, the increment is roughly

```
Δ(F) == d
```

no matter `r` is placed on the short side or the long side. This helps avoid the "long-stacking" problem effectively
and provides more choices for rest placements since the bounding box is stably very close to a rectangle .


### Including tie-breakers (2ndary objective function)

Since there may be multiple placements of a rectangle resulting in bounding box size unchanged, the secondary
 objective function plays very important role for breaking the tie. Considering the following *Best-Fit*:

- Any corner corresponds to a "slot" for placing a rectangle. The fill-rate of such slot matters -
 the greater the better, meaning there are less holes in the stack;

- The absolute coordinate values of placement matters - the closer the placement to the axes, the more space it leaves
  for subsequent placements.

There seems to be no rule-of-thumb choosing potential tie-breakers. Ideally could be, the choice of tie-breaker is
 *adaptive to the distribution of given rectangle sizes*, which is yet to be explored systematically.



<!--
 That is, for a long-band-like stack,  an installation of new rectangle on the short side comprises a much greater increment of the bounding area than on the long side. Consequently the rest of rectangles tend to be installed further along the long side.

On the other side, the above `F` avoids such problem by treating installation on long/short side almost equally.
-->

<!--
## restrictions and todos

- when many rectangles are of the same size, which is the degeneracy case, the model suffers from the disability of arranging them like a "grid". the fix requires clear definition for how to compute space restrictions and how to maintain the "thread" when such cases raise.

 - in this unbounded space, it seems there exists a tendency to arrange rectangles along the x or y axis for some input with rectangles of near sizes. though the quantitative result looks good, but setting constraints about boundaries should be made available to make the resulted bounding area more like a square.

 -->

<!--
## Detailed approach of solving
- The model is implemented with an abstract data structure resembling the *threaded-tree*
- Incrementally, a rectangle is installed to a corner and new corners get generated by such installation. Then the new corners (only top-left corner and bottom-right corner of this rectangle are included for simplicity) are treated as children of the just used corner, which is their parent in the *tree*
- The corner object is abstracted by the object *Turning*
- There are *convex* and *concave* turnings
- Each *Turning* is associated with four pointers, pointing left/right/up/down directions. Such information is used to detect spatial restrictions affecting the feasible size of rectangle which can be installed onto this turning
- When a rectangle is installed onto a convex turning, it is "slided" left (when at upleft turning) or downwards (when at downright turning) until hitting any installed rectangle or the boundary. Such installation two new corners into the current thread and a brand new "inner thread" into the model
- When a rectangle is installed onto a concave turning, merely the new corners are inserted into the current thread
- The spatial restriction at a turning for installing a rectangle is heuristically calculated by multiplying the distance between the left/right pointer's targets as well as the distance between the up/down pointer's targets
- With **greedy** method, which seems highly profiting
-->
