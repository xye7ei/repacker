#!usr/bin/env python3
import time
from datetime import datetime
from pprint import pformat, pprint


class Rectangle(object):
    
    def __init__(self, b, h):
        self.b, self.h = b, h
        self.area = b * h
        self.xy = None

    def __repr__(self):
        return '[{}x{}@{}]'.format(self.b, self.h, self.xy)

    def __lt__(self, other):
        return self.area < other.area

    @property
    def xy2(self):
        x, y = self.xy
        return (x + self.b, y + self.h)

    def color(self):
        import math
        b, h = self.b, self.h
        if b > h: c = b / h
        else:     c = - h / b
        fei = math.atan(c)
        red = int(50 * fei + 128) # c[max] ~= 100, 50*atan(c) + 128 in [50, 206]
        grn = int( 5 * fei + 128)
        blu = int( 5 * fei + 128)
        fill = "#%02X%02X%02X" % (red, grn, blu)
        return fill
        

class Corner(object):

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.xy = x, y
        for k in 'left right up down prev next'.split():
            setattr(self, k, None)

    def __repr__(self):
        # return 'N{}{}'.format(self.id, self.xy)
        return 'N{}'.format(self.xy)

    @staticmethod
    def link(n1, n2):
        n1.next = n2
        n2.prev = n1

    def shape(self):
        """Categorize the shape of a corner, which is not static due to
        the prev/next context.

        """
        x_in = self.x - self.prev.x
        x_out = self.next.x - self.x
        y_in = self.y - self.prev.y
        y_out = self.next.y - self.y
        # NOTE: x_out and y_in may be 0
        # Very tricky to catogorize!
        if y_in < 0:
            if x_out < 0: return 'D'
            else:         return 'L'
        elif y_in == 0:
            if x_out < 0: return 'D'
            else:         return 'L'
        else:
            if x_out <= 0: return 'T'
            else:         return 'F'

    def x_put(self):
        s = self.shape()
        if s == 'L': return self.x
        elif s == 'D': return self.x
        elif s == 'F': return self.left.x
        else: raise

    def y_put(self):
        s = self.shape()
        if s == 'L': return self.y
        elif s == 'D': return self.down.y
        elif s == 'F': return self.y
        else: raise


    def plant(self, rect):

        b, h = rect.b, rect.h

        # Determine whether `self` is still in the chain.
        # Different cases:
        # - `self` is a L-shaped corner:
        #   + plant rectangle exactly at `self`
        #   + `self` is dropped from the chain
        if self.shape() == 'L':

            na = Corner(self.x, self.y + h)
            nb = Corner(self.x + b, self.y)

            Corner.link(self.prev, na)
            Corner.link(na, nb)
            Corner.link(nb, self.next)

            na.down = na           
            na.up = self.up        
            nb.left = nb           
            nb.right = self.right  

            rect.xy = self.xy

        # - `self` is a D-shaped corner:
        #   + plant rectangle at the intersection pointed by `self.down`
        #   + `self` is NOT dropped from the chain
        elif self.shape() == 'D':
            tar = self.down
            na = Corner(self.x, tar.y + h)
            nb = Corner(self.x + b, tar.y)
            nn = tar.next
            Corner.link(tar, na)
            Corner.link(na, nb)
            Corner.link(nb, nn)
            na.down = na           
            na.up = self.up        
            nb.left = nb           
            nb.right = tar.right  

            rect.xy = (self.x, tar.y)

        # - `self` is a F-shaped corner
        #   + plant rectangle at the intersection pointed by `self.left`
        #   + `self` is NOT dropped from the chain
        elif self.shape() == 'F':
            tar = self.left
            na = Corner(tar.x, self.y + h)
            nb = Corner(tar.x + b, self.y)
            np = tar.prev
            Corner.link(np, na)
            Corner.link(na, nb)
            Corner.link(nb, tar)
            na.down = na           
            na.up = tar.up        
            nb.left = nb           
            nb.right = self.right  

            rect.xy = (tar.x, self.y)

        else:
            assert 0

        # Trial: No overlapping removal!
        # Drop one of the overlapping points!
        # if na.prev.y == na.y:
        #     # drop `na` 
        #     Corner.link(na.prev, na.next)
        #     # na.prev.next = na.next
        #     # na.next.prev = na.prev
        #     na = na.prev
        #     # FIXME: what if na.prev.x >= na.x???
        # if nb.next.x == nb.x:
        #     # drop `nb`
        #     Corner.link(nb.prev, nb.next)
        #     # nb.prev.next = nb.next
        #     # nb.next.prev = nb.prev
        #     nb = nb.next

        # Memo self.up and self.right before updating!
        # Since in 'F' case `self.up` would be mutated before assignment of `nb.up`!
        # Since in 'D' case `self.right` would be mutated before assignment of `na.right`!
        up0 = na.up
        right0 = nb.right


        # Updating started from `na`
        # tour leftwards
        # update others' right pointing
        n = na.prev
        while n.y < na.y:
            n.right = na
            n = n.left.prev
        assert n.y >= na.y      # n overlooks na rightwards
        na.left = n.next

        # tour upwards
        # update others' down pointing
        n = up0
        while n.x <= nb.x:      # `nb` may be replaced during overlapping removal
            n.down = na
            n = n.up            # NEVER n == n.up
        assert n.x > na.x
        nb.up = n
        while n.x <= nb.next.x:
            n.down = nb
            if n.shape() == 'T': break
            else: n = n.up

        # Updating started from `nb`
        # tour downwards
        # update others' up pointing
        n = nb.next
        while n.x < nb.x:
            n.up = nb
            n = n.down.next
        assert n.x >= nb.x
        nb.down = n.prev

        # tour rightwards
        # update others' left pointing
        n = right0
        while n.y <= na.y:
            n.left = nb
            n = n.right         # NEVER n == n.right
        assert n.y > nb.y + h
        na.right = n
        while n.y <= na.prev.y:
            n.left = na
            if n.shape() == 'T': break
            else: n = n.right

        # assert all attributes are set
        for k in 'up down left right prev next'.split():
            assert getattr(na, k)
            assert getattr(nb, k)
            
        return na, nb

    @staticmethod
    def _update_down_up(d, x_stop, u):
        d.up = u
        while d.x <= x_stop:
            d1 = d.down.next
            while up.x <= d1.x:
                u.down = d.prev
                if u.shape() == 'T':
                    break
                else:
                    u = u.up
            if d1.shape() == 'T':
                break
            else:
                d.up = u
                d = d1

    @staticmethod
    def _update_left_right(l, y_stop, r):
        l.right = r
        while l.y <= y_stop:
            l1 = l.left.prev
            while r.y <= l1.y:
                r.left = l
                if r.shape() == 'T':
                    break
                else:
                    r = r.right
            assert r.shape() == 'T' or r.y > l1.y
            if l1.shape() == 'T':
                break
            else:
                l1.right = r
                l = l1

    def walk(self):
        n = self
        while 1:
            yield n
            n = n.next
            if n == self:
                break

    def slot(self):
        """Estimate slot size for putting rectangles."""
        s = self.shape()
        if s == 'L':
            dx = (self.right.x - self.x)
            dy = (self.up.y - self.y)
        elif s == 'D':
            dx = (self.down.right.x - self.x)
            dy = (self.up.y - self.down.y)
        elif s == 'F':
            dx = (self.right.x - self.left.x)
            dy = (self.left.up.y - self.y)
        else:
            assert 0
        return (dx, dy)

    def can_plant(self, rect, x_max, y_max):
        
        # Mind the gap when aligning.
        s = self.shape()
        if s == 'D':
            dy = self.y - self.down.y
            if dy >= rect.h:
                return False
        elif s == 'F':
            dx = self.x - self.left.x
            if dx >= rect.b:
                return False

        # Not overstepping the bound!
        if (self.x_put() + rect.b > x_max or
            self.y_put() + rect.h > y_max):
            return False
    
        (sx, sy) = self.slot()
        # return sx > rect.b and sy > rect.h
        return sx >= rect.b and sy >= rect.h

    def slot_fill_rate(self, rect):
        dx, dy = self.slot()
        return rect.area / (dx * dy)


class Scene(object):

    def __init__(self, x_max, y_max):

        self.x_max = x_max
        self.y_max = y_max

        top = Corner(x_max, y_max)
        ori = Corner(0, 0)

        top.left = ori
        top.right = top
        top.up = top
        top.down = ori

        ori.left = ori
        ori.right = top
        ori.up = top
        ori.down = ori

        top.next = top.prev = ori
        ori.next = ori.prev = top

        self.top = top
        self.ori = ori

    def xy_bounding(self):
        x_bnd = 0
        y_bnd = 0
        w = self.top.walk()
        next(w)
        for n in w:
            if n.x > x_bnd:
                x_bnd = n.x
            if n.y > y_bnd:
                y_bnd = n.y
        return (x_bnd, y_bnd)
            
    def walk_find_best(self, rect):

        x_bnd, y_bnd = self.xy_bounding()

        def assess(n):
            "Smaller the better."
            x_bnd1 = max(n.x_put() + rect.b, x_bnd)
            y_bnd1 = max(n.y_put() + rect.h, y_bnd)
            fr = n.slot_fill_rate(rect)
            # Heuristics
            return (x_bnd1 + y_bnd1,
                    # rather than (x_bnd1 * y_bnd1) to avoid long-band stacking
                    # x_bnd1 / y_bnd1, # aspect ratio
                    # abs(x_bnd1 - y_bnd1),
                    n.x + n.y,
                    -fr)                  # NEGATIVE fill rate in any slot

        w = self.top.walk()
        next(w)                 # ignore `top`

        try:
            n_best = min((n for n in w if n.can_plant(rect, self.x_max, self.y_max)),
                        default=self.top.next,
                        key=assess)
            return n_best
        except TypeError as e:
            print('No viable corner to put a rectangle.')
            print('NEED LOGGING HERE.')

    def validate_linking(self):
        for a, b in zip(self.top.walk(), self.top.next.walk()):
            if a != b.prev:
                # import pdb; pdb.set_trace()
                raise Exception('Linking inconsistent!')

    def prepare(self, rects, **sortkw):
        'Prepare rectangles to be planned, which is a copied list.'
        self.rects = sorted(rects, reverse=True, **sortkw)
        # self.rects = rects[:]

    def plan(self):
        assert hasattr(self, 'rects')
        rects = self.rects
        try:
            sa = 0
            for r in rects:
                n = self.walk_find_best(r)
                n.plant(r)
                # self.validate_linking()
                sa += r.area
            x_bnd, y_bnd = self.xy_bounding()
            occu_rate = (sa) / (x_bnd * y_bnd)
            # print('Success with occu_rate: ', occu_rate)
            self.occu_rate = occu_rate
            return occu_rate
        except (AttributeError, Exception) as e:
            import time
            import pprint
            t = time.time()
            with open('RandError {}.log'.format(t), 'w') as o:
                for r in rects:
                    if r.xy:
                        o.write('({}, {}) at ({}, {})\n'.format(r.b, r.h, *r.xy))
                o.write('# {}\n'.format(e))
            figure(rects, 'RandError {}.png'.format(t))

    def figure(scene, name=None):

        from PIL import Image, ImageFont, ImageDraw

        rects = scene.rects
        x_max, y_max = scene.xy_bounding()
        x_max = int(x_max * 1.02)
        y_max = int(y_max * 1.02)

        im = Image.new('RGB', (x_max, y_max), (255, 255, 255))
        dr = ImageDraw.Draw(im)

        for r in scene.rects:
            if r.xy:
                x, y = r.xy
                # reverse x
                dr.rectangle(((x, y_max - y),
                              x + r.b, y_max - (y + r.h)),
                             fill=r.color(),
                             outline='black')
        if not name:
            im.save('{}_{}x{}_{:.4f}_{}.png'.format(
                'output',
                x_max, y_max,
                scene.occu_rate,
                int(time.time()),
            ))
        else:
            im.save(name)


def show(scene):

    import matplotlib.pyplot as plt
    import matplotlib.patches as pch
    import io

    plt.rc('font')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for r in scene.rects:
        if r.xy:
            p_r = pch.Rectangle(r.xy, r.b, r.h,
                                edgecolor='#101010',
                                alpha=0.9,
                                facecolor=r.color())
            ax.add_patch(p_r)

    ax.axis('equal')
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    plt.plot()
    plt.show()


class Gen(object):

    @staticmethod
    def gen_inp(N, w_min=10, w_max=100, h_min=10, h_max=100):
        "Generate a list of tuples randomly for reading into model."
        import random
        tps = []
        for _ in range(N):
            w = random.randint(w_min, w_max)
            h = random.randint(h_min, h_max)
            tps.append((w, h))
        return tps

    @staticmethod
    def from_file(filename):
        "Read a list of tuples from a file."
        with open(filename, 'r') as o:
            return eval(o.read())


def solve_file(inpfile, outfile, nofigure=True):
    
    tps = Gen.from_file(inpfile)
    N = len(tps)
    scn_max = int(max(max(*tp) for tp in tps) * N * 1.01)
    s = Scene(scn_max, scn_max)
    rects = [Rectangle(*tp) for tp in tps]
    s.prepare(rects)
    oc_rt = s.plan()
    
    res = [[r.xy, r.xy2] for r in rects]
    xb, yb = s.xy_bounding()

    if outfile == '':
        outfile = 'output_for__{}___{}x{}_{:.4f}'.format(inpfile, xb, yb, oc_rt)

    with open(outfile, 'w') as o:
        o.write('# Output file for input file "{}"\n'.format(inpfile))
        o.write('# Bounding: {}x{}\n'.format(xb, yb))
        o.write('# Aspect ratio of bounding: {}/{} == {:.4f}\n'.format(xb, yb, xb/yb))
        o.write('# Occupacy rate: {}\n'.format(oc_rt))
        o.write('# Schema: [(x1, y1), (x2, y2)]\n')
        o.write(pformat(res))

    if not nofigure:
        s.figure(outfile + '_figure.png')
        

if __name__ == '__main__':

    from argparse import ArgumentParser
    p = ArgumentParser(description='Specify solver options.')

    p.add_argument(
        # '-i', '--inpfile',
        'inpfile',
        help=('File that stores rectangles '
              'which is a list of 2-tuples.'))
    p.add_argument(
        # '-o', '--outfile',
        '--outfile',
        help=('Output file. '
              'Default: postfixing "out" to input file'),
        action='store',
        default='')
    p.add_argument(
        '-n', '--nofigure',
        help=('No figure output.'),
        default=False)

    args = p.parse_args()

    solve_file(**args.__dict__)
    # print(args.__dict__)

    print('Solution done.\n')


