repacker
=====

This is a effective solver for 2D-rectangle-packing problem, which can find potential usage in various fields.

# Target
The target problem is formalized as a typical optimization problem within such framework:

| Item | Setting |
|---|---|
| *Input* | • A set of 2D rectangles <br/>  |
| *Output* | • A complete arrangement of these rectangles in a 2D space |
| *Constraints* | • Each rectangle is aligned to X and Y axis of the space. <br/> • No overlapping is allowed. |
| *Objective* | • Minimize the area of the axis-aligning bounding box covering all rectangles. |
| *Extension* |• Any rectangle can be replaced with its 90°-rotated version. |

It is like given a large piece of cloth and required is a set of small pieces for some assembling work. The objective is to cut off these required pieces with least consumption of the large cloth.


# Sample output

As a simple example, an arrangement for 500 random generated rectangles (with uniform distribution for width/height length) is delivered by this solver, plotted with `pyplot`:

<p align="center">
    <img src="./sample_figure.png"
    width="70%"
    height="70%" />
</p>

Averagely, the fill-rate ranges above 90% for various input. But restriction can raise when the size of rectangles are near due to degeneracy of implemented methods.


# Approach

Supported by a Threaded-Tree like data structure, the killer heuristics for this solver is the assessment function `F` guiding installation of each rectangle `r` at potential position `c`:

``` python
 F(r, c) = B(r, c).width + B(r, c).height
```

where `B(r, c)` is the new bounding box after this installation. Note the object value to be minimized is `B(r, c).width * B(r, c).height`, that is `B(r, c).area`, which is different.

A possible interpretation for this assessment is that using `B.area` may lead to augmenting the rectangle stack to grow like a long-band, rather than grow like a square, since for a long-band-like stack, installation of new coming rectangle towards the short side comprises a large increment of object value.


## Characteristics of this solver

- No utilities from computational graphics or computational geometry are used, since the underlying data structure resembles a Threaded-Tree, which is more abstract.
- With this structure, spatial restrictions can be detected by simple arithmetics, rather than applying geometric algorithms.
- This approach sacrifices completeness of by considering stacking direction merely upwardsrightwards. However, the results seem satisfying.
- Much more performant implementation can be derived from this Python implementation with no dependencies required.


# Restrictions and TODOs

- When many rectangles are of the same size, which is the degeneracy case, the model suffers from the disability of arranging them like a "grid".

<!-- - In this unbounded space, it seems there exists a tendency to arrange rectangles along the X or Y axis for some input with rectangles of near sizes. Though the quantitative result looks good, but setting constraints about boundaries should be made available to make the resulted bounding area more like a square.

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