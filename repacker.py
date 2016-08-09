import pprint
import pdb
import random
import math
import operator as op


class Record(object):
    """This class serves as an interface between model and general
    optimizer scheme, such that the optimizer can choose item with
    respect to its feature or value.

    The classes who implement this class's methods can contain further
    properties for the action(mutation/application/reversion) of
    corresponded data model.

    """

    def __init__(self, feature, value):
        self._feature = feature
        self._value = value

    def __repr__(self):
        return 'Feature: %s;  Value: %8.3f' % (self.feature, self.value)

    def __getitem__(self, i):
        """ Implement the interface of reading table contents.
        For the optimizer, a vector of motions are indexed by
        0 with 'id' and 1 with 'value'. """
        if i == 0:
            return self.feature
        else:
            return self.value

    def __lt__(self, other):
        """Ordability: `self.value1 may be a tuple. """
        assert isinstance(other, Record), 'Compare only Record to Record.'
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self

    @property
    def feature(self):
        return self._feature

    @property
    def value(self):
        return self._value


class Motion(Record):
    """Extending a record class, which is to be accepted by the optimizer.

    """

    def __init__(self, rect, rect_paren, child, rotated, params):
        super(Motion, self).__init__(
            rect.id,
            # Or apply some specified weight function.
            # params[0] + params[1] / 10000.0)
            # HOWTO define weight function to evaluate
            # some state of the data model?
            # Possible parameters:
            # 0. Bounding size;
            # 1. Fitting-grade in slot;
            # 2. Location (x, y) of target turning;
            # 3. Area of moved rectangle;
            # 4. Whether inducing a new subhanger;
            # ...
            # params[0] + params[1] + params[2] / 100.0
            params
        )
        self.rect = rect
        self.rect_paren = rect_paren
        self.child = child
        self.rotated = rotated
        self.params = params

    def __repr__(self):
        return 'R{0} TO R{1}.child:{2}, Params: {3}, Rotd: {4}'.format(
            self.rect.id, self.rect_paren.id, self.child,
            self.params, self.rotated)

    @property
    def target_turning(self):
        return self.rect_paren.turning.children[self.child]


class Turning(object):
    """`Turning` is a custom type as component of the outline of stacked
    boxes.  It describes a vertical walk into and then a horizontal
    walk out of a turning point of outline (a wall and a
    platform/ceiling), which can be of four possibilities:

    > downwards in, rightwards out: L-Type (most common)

    > upwards in, rightwards out: F-Type

    > downwards in, leftwards out: D-Type

    > upwards in, leftwards out: T-Type (only for hangers in this
      model)

    Each `Turning` maintains coordinates p(x, y) as well as four
    pointers L, R, U and D with each of them points a turnings which
    can be 'shoot' with an arrow radiating from p. Each type of
    turning has specified arrows pointing to itself. In the following
    table, '?' means non-self target turning pointed by the pointer.

    ----------   L     R     U     D    --------
      L-Type    self   ?     ?    self
      F-Type     ?     ?    NONE  self
      D-Type    self   ?     ?     ?
      T-Type     ?    self  self   ?
    --------------------------------------------
    
    The 'Chain' of turnings exactly represent the 'outline' of the
    rectangle stack.
    
    A scene model maintains a set of chains, each represented by a
    'hanger' turning (hanging a cycle-chain).

    """

    counter = 0

    def __init__(self, x, y, parent, hanger_pool=None, assoc_rect=None):
        self.x = x
        self.y = y
        self.l_ext = None
        self.r_ext = None
        self.u_ext = None
        self.d_ext = None
        self.prev = None
        self.fllw = None
        self.parent = None
        self.children = []      # Used to find dependants which assocect splitting.
        self.bending_before = None
        self.assoc_rect = assoc_rect
        if parent:
            self.hanger_pool = parent.hanger_pool
        else:
            self.hanger_pool = hanger_pool
        self.id = Turning.counter
        Turning.counter += 1
        return

    def __repr__(self):
        if self.is_hanger:
            return 'Hg_%s[%2d, %2d]' % (self.id, self.x, self.y)
        else:
            return "%s_%s[%2d, %2d]" % (self.bending, self.id, self.x, self.y)

    def __getitem__(self, n):
        i = 0
        p = self
        while i < n:
            p = p.fllw
            i += 1
        return p

    def __call__(self, n):
        for t in self.cycle:
            if t.id == n: return t
        assert 0, 'No such turning in %s`s cycle! ID:%s' % n

    class Frame:
        """For validation of some merge with new rectangle at some
        turning.

        """
        def __init__(self, tng):
            self.turning = tng
            self.x1 = tng.x_put
            self.y1 = tng.y_put
            self.x2 = min(
                tng.u_ext.r_ext.x if not tng.u_ext.is_hanger else tng.u_ext.x,
                tng.slide_d().r_ext.x)
            self.y2 = min(
                tng.slide_l().u_ext.y,
                tng.r_ext.u_ext.y if not tng.r_ext.is_hanger else tng.r_ext.y)

        def __repr__(self):
            return "Fm[%4d * %4d]|[xg=%4d, yg=%4d]@%s" % \
                (self.b, self.h, self.x_gap, self.y_gap, self.turning)

        @property
        def b(self): return self.x2 - self.x1

        @property
        def h(self): return self.y2 - self.y1

        @property
        def x_gap(self): return self.turning.x - self.x1

        @property
        def y_gap(self): return self.turning.y - self.y1

        @property
        def area(self): return self.b * self.h

        def fill_rest_of(self, rect):
            """ Returns either False or fill rate. """
            if self.x_gap < rect.b <= self.b and \
               self.y_gap < rect.h <= self.h:
                return self.area - rect.b * rect.h
            else:
                return -1

    @staticmethod
    def reset_counter():
        Turning.counter = 0

    @staticmethod
    def initialize_hanger(x_min, y_min, x_max, y_max):
        Turning.reset_counter()
        hanger = Turning(x_max, y_max, None, hanger_pool=set())
        hanger.hanger_pool.add(hanger)
        origin = Turning(x_min, y_min, None, hanger_pool=hanger.hanger_pool)
        hanger.chain_next(origin)
        origin.chain_next(hanger)
        virtual = Turning(-1, -1, None, None)
        virtual.children.append(origin)
        virtual.assoc_rect = Rectangle(-1, 0, 0)
        virtual.assoc_rect.turning = virtual
        origin.parent = virtual
        origin.l_ext = origin.d_ext = origin
        origin.r_ext = origin.u_ext = hanger
        # l_ext and d_ext of `hanger wound not ever be changed.
        hanger.l_ext = hanger.d_ext = \
        hanger.u_ext = hanger.r_ext = hanger
        return hanger

    # All wrapped properties are dynamic properties.
    # They are mainly helpers for printing and debugging.
    @property
    def index_as_child(self):
        return self.parent.children.index(self)

    @property
    def x_put(self):
        "X-value for installing a rectangle to this turning."
        if self.bending is 'T' and self.bending_before is 'F':
            return self.fllw.x
        elif self.bending is 'F':
            return self.slide_l().x
        else:
            return self.x

    @property
    def y_put(self):
        "Y-value for installing a rectangle to this turning."
        if self.bending is 'T' and self.bending_before is 'D':
            return self.prev.y
        elif self.bending is 'D':
            return self.slide_d().y
        else:
            return self.y

    @property
    def xy_put(self):
        "Coordinates for installing a rectangle to this turning."
        return (self.x_put, self.y_put)

    @property
    def xy(self):
        "Representation of turning as its point coordinates. "
        return (self.x, self.y)

    @property
    def bending(self):
        # !! Strictly
        d_in = (self.prev.y > self.y)
        r_in = (self.prev.x > self.x and self.prev.y == self.y)
        r_out = (self.fllw.x > self.x)
        u_out = (self.y < self.fllw.y and self.x == self.fllw.x)
        # Handle degenerency -
        # IF two consecutive turnings are at the same
        # xy-position.
        if self.prev.xy == self.xy:
            return 'L'
        elif d_in and r_out:
            return 'L'
        elif (d_in or r_in) and not r_out: #
            return 'D'
        elif not d_in and (r_out or u_out):
            return 'F'
        else:
            return 'T'

    @property
    def cycle(self):
        c = [] ; seen = set()
        p = self
        while True:
            c.append(p) ; seen.add(p)
            p = p.fllw
            if p is self:
                break
            elif p in seen:
                assert False, "Wrong cycle: %s" % str(c)
        return c

    @property
    def cycle_rev(self):
        c = [] ; seen = set()
        p = self
        while True:
            c.append(p) ; seen.add(p)
            p = p.prev
            if p is self:
                break
            elif p in seen:
                c.append(p)
                print("Wrong cycle: %s" % str(c))
                return c
        return c

    @property
    def bounding(self):
        x = y = 0
        for tng in self.cycle:
            if not tng.is_hanger:
                if tng.x > x: x = tng.x
                if tng.y > y: y = tng.y
        return (x, y)

    @property
    def bounder_turning_pair(self):
        """Assusme `self` is a hanger, find maximum of turnings with x and y
        as bounder.

        """
        curr = self.fllw
        bnd_tng_x = bnd_tng_y = curr
        for tng in curr.fllw.cycle:
            if tng.x > bnd_tng_x.x: bnd_tng_x = tng
            if tng.y > bnd_tng_y.y: bnd_tng_y = tng
        return (bnd_tng_x, bnd_tng_y)

    @property
    def exts(self):
        "Inspect the extents of this turning."
        return list(zip(
                ['Left ', 'Right', 'Up  ', 'Down'],
                [self.l_ext, self.r_ext, self.u_ext, self.d_ext])
        )

    @property
    def info(self):
        pat = "\t".join(["%s"] * 5) + "\n"
        return pat % tuple(t.id for t in
                          [self, self.l_ext, self.r_ext, self.u_ext, self.d_ext])

    @property
    def is_hanger(self):
        return self.bending is 'T' and self.prev.bending is not 'T'

    @property
    def frame(self):
        """Return a conservative available size of some platform.  This is
        dependent to the ways of merging rectangles into outline,
        i.e. whether merge-corner, merge-floor or merge-wall, etc.

        """
        return Turning.Frame(self)

    @property
    def state_table(self):
        tbl = [tuple(map(lambda p: (p.x, p.y),
                         (p,
                          p.l_ext, p.r_ext, p.u_ext, p.d_ext)))
               for p in self.cycle[1:]
        ]
        return tbl

    @property
    def descedants(self):
        """Descedants are PARENT turnings, which lie not on the outline.

        """
        que_trav = [self] ; stk_split = []
        while que_trav:
            t = que_trav.pop(0)
            if t.children:
                if t in stk_split: # Keep the seen at newest position.
                    stk_split.remove(t)
                stk_split.append(t)
                que_trav.extend(t.children)
                c1, c2 = t.children
                if c1.fllw.is_hanger and c1.fllw:
                    que_trav.append(c1.fllw)
                if c2.prev.is_hanger and c2.prev:
                    que_trav.append(c2.prev)
        return stk_split

    def slide_l(self, until=-1):
        "Detect how far a rectangle can slide leftwards."
        p = self
        # What if p.l_ext.prev is hanger AND p.l_ext.prev == p.y ?
        # Hanger is excluded.
        # while p.bending is 'F' and \
        while p.l_ext.prev.y == p.y and \
              until < p.l_ext.prev.x <= p.x:
            p = p.l_ext.prev
        # IF p.l_ext is 'L' and p.l_ext.y == p.y, then return the p.l_ext
        return p.l_ext          # Only slide, not iterate!

    def slide_d(self, until=-1):
        "Detect how far a rectangle can slide downwards."
        p = self
        # while p.bending is 'D' and \
        while p.d_ext.fllw.x == p.x and \
              until < p.d_ext.fllw.y <= p.y: # Guard crawling up!
            p = p.d_ext.fllw
        # What if now p is 'L-type and p.x == self.x ?
        return p.d_ext

    def chain_next(self, nt):
        """Chain `self` and `nt`.

        !! How to handle overlapping turnings? This may happen when
        e.g. 4 * (10*10) Rectangles are juxtaposed.

        """
        self.fllw = nt
        nt.prev = self

    def print_map(self):
        th = "\t".join([" ID  |", "L", "R", "U", "D",]) + "\n"
        tb = "\n".join([
            "\t".join('%s_%s' % (x.bending, x.id)
                      for x in
                      [t, t.l_ext, t.r_ext, t.u_ext, t.d_ext])
            for t in self.cycle
        ])
        print(th)
        print(tb)

    @staticmethod
    def _update_left_right(lft, y_stop, rgt):
        lft.r_ext = rgt
        # At start: lft.y < rgt.y
        while lft.y <= y_stop:
            lft1 = lft.l_ext.prev
            # INV: lft.y < rgt.y AND lft1.y >= lft.y
            #
            # Consider updating the hanged of a D-hanger:
            # `rgt is the hanger itself as given argument,
            # `lft is the hanger's down strecth's left stretch,
            # `y_stop is the hanger's y-level.
            # Suppose `lft1 comes to some turning which is not the hanger
            # but has the same y-level with the hanger, then next loop is
            # not entered since lft.y == y_stop before next loop.
            # As a result the "tall" turnings' right-extents are not updated
            # during this loop!
            while rgt.y <= lft1.y:
                # Including updating for rgt.is_hanger.
                # Including updating for lft1.is_hanger.
                if lft1.y > lft.y: # GUARD fast lane!!
                    rgt.l_ext = lft1.fllw
                if rgt.is_hanger: break
                else: rgt = rgt.r_ext
            # INV: rgt.is_hanger OR lft1.y < rgt.y
            # IF `rgt is hanger since here, then in all following rounds,
            # all `lft's right-extents are to be set to this hanger.
            if lft1.is_hanger: break
            else: lft1.r_ext = rgt ; lft = lft1
        return

    @staticmethod
    def _update_down_up(dwn, x_stop, up):
        dwn.u_ext = up
        while dwn.x <= x_stop:
            dwn1 = dwn.d_ext.fllw
            while up.x <= dwn1.x:
                if dwn1.x > dwn.x:
                    up.d_ext = dwn1.prev
                if up.is_hanger: break
                else: up = up.u_ext
            if dwn1.is_hanger: break
            else: dwn1.u_ext = up ; dwn = dwn1
        return

    def mergable(self, rect):
        if self.is_hanger or self.bending is 'T':
            return False
        else:
            # Case 1: Same x-level with previous;
            # Case 2: Same y-level with follow;
            # Case 3: Two non-consecutive turnings are of identical xy,
            #         i.e. C-jaw-shape.
            # return \
            #     self.fllw.x != self.x and self.prev.y != self.y and \
            #     self.l_ext.prev.xy != self.xy and self.d_ext.fllw.xy != self.xy and \
            #     self.frame.fill_rest_of(rect) >= 0
            if (self.fllw.x != self.x and self.prev.y != self.y) and \
               (self.l_ext.prev.xy != self.xy and self.d_ext.fllw.xy != self.xy) and \
               (self.frame.fill_rest_of(rect) >= 0):
                return True
            else:
                return False

    def merge(self, rect, update=True):
        if not self.mergable(rect):
            print('Failed merging %s at %s ' % (rect, self))
            pdb.set_trace()

        rect.put_at(self)
        self.assoc_rect = rect

        nt1 = Turning(self.x_put, self.y_put + rect.h, self)
        nt2 = Turning(self.x_put + rect.b, self.y_put, self)
        nt1.parent = nt2.parent = self

        self.children.extend([nt1, nt2])

        # General chaining.
        if self.bending is 'L':
            nt2.chain_next(self.fllw)
            nt1.chain_next(nt2)
            self.prev.chain_next(nt1)
        elif self.bending is 'F':
            nt2.chain_next(self.fllw)
            nt1.chain_next(nt2)
            self.slide_l().prev.chain_next(nt1)
        elif self.bending is 'D':
            nt2.chain_next(self.slide_d().fllw)
            nt1.chain_next(nt2)
            self.prev.chain_next(nt1)

        # Update.
        if update:
            nt2.l_ext = nt2
            nt1.d_ext = nt1
            # Lefter
            p = nt1.prev
            while p.y < nt1.y:
                p.r_ext = nt1
                p = p.l_ext.prev # Update all in the same y-level.
            nt1.l_ext = p.fllw
            # Downer
            p = nt2.fllw
            while p.x < nt2.x:
                p.u_ext = nt2 ; p = p.d_ext.fllw
            nt2.d_ext = p.prev
            Turning._update_left_right(
                nt2,
                max(nt1.y, nt1.prev.y),
                self.slide_d().r_ext)
            Turning._update_down_up(
                nt1,
                max(nt2.x, nt2.fllw.x),
                self.slide_l().u_ext)

        if self.bending is 'L':
            self.bending_before = 'L'
            # self.l_ext.bending_before = 'L' # Handle when self.l_ext.xy = self.xy
            pass

        elif self.bending is 'F':
            assert self.d_ext is self
            # Must chain first, then update.
            self.chain_next(self.slide_l())
            # Tricky for cascaded split??
            # The mission of finding children(including subcycle hanger)
            # is delegated to the method `descedants.
            self.hanger_pool.add(self)
            self.bending_before = 'F'
            if update:
                self._update_left_right(self.prev, self.y, self)
                self._update_down_up(self.fllw, self.x, self)

        elif self.bending is 'D':
            assert self.l_ext is self
            self.slide_d().chain_next(self)
            # self.prev.children.append(self)
            self.hanger_pool.add(self)
            self.bending_before = 'D'
            if update:
                self._update_left_right(self.prev, self.y, self)
                self._update_down_up(self.fllw, self.x, self)

        else:
            pass

        # For error debugging. After merging, all extents must be in
        # the same cycle except the hanger.
        # Turning.check_cycle(self, nt1.prev, rect)
        # if self.is_hanger:
        #     Turning.check_cycle(self, self, rect)

    def merge_rotate(self, rect):
        rect.rotate()
        self.merge(rect)

    @staticmethod
    def check_cycle(at, tng, rect, info='MERGE'):
        cyc_set = set(tng.cycle)
        for c in cyc_set:
            if c.is_hanger:
                continue
            else:
                for j, e in c.exts:
                    if e not in cyc_set:
                        # print('\n! Error merging %s' % c.assoc_rect)
                        print('\n!! %s handling %s' % (info, at))
                        print('!! When moving %s' % rect)
                        print('!! Check cycle: wrong content of %s: %s - %s:' % \
                              (c, j, e))
                        print(tng.cycle, '\n')
                        tng.print_map()
                        import pdb ; pdb.set_trace()
                        raise ValueError(c, e)

    @property
    def splittable(self):
        """`self must be a PARENT.  A rectangle at `self can only be splitted
        IFF two children of `self are outline-turnings, i.e. both of
        them have no children and also they're consecutive in the
        chaining.

        If the condition above doesn't hold, then only cascaded split
        at `self` is possible.

        """
        if self.children:
            nt1, nt2 = self.children
            # !! If `nt1.fllw != `nt2, then `nt1 and `nt2
            # are not in the same cycle, thus not splittable!
            return \
                nt1.fllw is nt2 and \
                nt2.prev is nt1 and \
                nt1.children == nt2.children == [] # and \
                # nt1.x is self.x_put and \
                # nt2.y is self.y_put
        else:
            return False

    def split(self, update=True):
        """Assume `self` is not actually on the outline, but marks the
        position of some rectangle, i.e. being referenced by such
        rectangle's `turning` property.

        For a splittable internal turning, its two children are just
        two consecutive turnings along the outline (if it is legal to
        split the rectangle here) and both of them have no children.

        """
        assert self.splittable

        ot = self
        t1, t2 = ot.children

        # Reset hanger before chaining! Thus a hanger is not valid
        # with its exts.
        #
        # Seperated from inversed process of _update_hanged!

        if ot.bending_before is 'L': #ot.d_ext is ot.l_ext is ot:
            assert ot.bending is 'L', ot + '\n' + ot.cycle
            ot.u_ext = t1.u_ext
            ot.r_ext = t2.r_ext
            t1.prev.chain_next(ot)
            ot.chain_next(t2.fllw)
            Turning._update_left_right(ot, t1.y, t2.r_ext)
            Turning._update_down_up   (ot, t2.x, t1.u_ext)

        elif ot.bending_before is 'F': # ot.d_ext is ot:
            t1.prev.chain_next(ot.fllw)
            ot.chain_next(t2.fllw)
            # ot.l_ext = t1.prev.fllw
            ot.r_ext = t2.r_ext
            ot.d_ext = ot
            Turning._update_left_right(ot, t1.y, t2.r_ext)
            Turning._update_down_up   (ot.slide_l(), t2.x, t1.u_ext)
            ot.hanger_pool.remove(ot)

        elif ot.bending_before is 'D': # ot.l_ext is ot:
            ot.prev.chain_next(t2.fllw) # Mind order of chaining.
            t1.prev.chain_next(ot)
            # ot.d_ext = t2.fllw.prev
            # What if ot.x == t1.x and there's somae p.x == ot.x between them?
            ot.u_ext = t1.u_ext
            ot.l_ext = ot
            Turning._update_left_right(ot.slide_d(), t1.y, t2.r_ext)
            Turning._update_down_up   (ot, t2.x, t1.u_ext)
            # ot.r_ext is to be updated
            # import pdb ; pdb.set_trace()
            ot.hanger_pool.remove(ot)

        else:
            assert False, "%s Illegal merged. " % self

        rect = ot.assoc_rect
        ot.assoc_rect = None
        rect.take_off()
        ot.children.clear()

        Turning.check_cycle(self, ot, rect, 'SPLIT')
        return rect

    def cascaded_split(self, update=True):
        # """
        # `self must be a parent turning which is not on outline.
        # """
        sub = list(self.descedants)
        rects = []
        while sub:
            t = sub.pop()
            assert t.splittable
            rects.append(t.split())
        return rects

    def deconstruct(self, level):
        # leaves = {leaf.assoc_rect for leaf in self.}
        return


class Rectangle(object):

    x_dflt = 0 ; y_dflt = 0

    def __init__(self, i, b, h):
        self.b = b
        self.h = h
        self.x1 = self.y1 = 0
        self.turning = None
        self.turning_before = None
        self.is_rotated = False
        self.id = i

    def __repr__(self):
        return "Rt_%s[%s * %s]@%s" % (self.id, self.b, self.h, self.turning)

    @staticmethod
    def set_default_xy(x, y):
        Rectangle.x_dflt = x
        Rectangle.y_dflt = y

    @property
    def width(self):
        return self.b
    @property
    def height(self):
        return self.h

    @property
    def x2(self):
        return self.x1 + self.b
    @property
    def y2(self):
        return self.y1 + self.h
    @property
    def pos(self):
        return (self.x1, self.y1)
    @property
    def area(self):
        return self.b * self.h
    @property
    def child1(self):
        return self.turning.children[0]
    @property
    def child2(self):
        return self.turning.children[1]
    @property
    def splittable(self):
        return self.turning.splittable
    @property
    def xyxy(self):
        x = y = None
        if self.turning:
            x, y = self.x1, self.y1
        else:
            x, y = Rectangle.x_dflt, Rectangle.y_dflt
        return (x, y, x + self.b, y + self.h)
    @property
    def xymid(self):
        return ((self.x1 + self.x2)/2, (self.y1 + self.y2)/2)

    def split(self):
        self.turning.split()
        # Consistency ?
        # Keep unused rectangles unrotated!
        # What're the effects on split_and_assess or assess_with_rect ??
        if self.is_rotated:
            self.rotate()

    def put_at(self, tng):
        self.x1 = tng.x_put
        self.y1 = tng.y_put
        self.turning = tng

    def take_off(self):
        self.turning_before = self.turning
        self.turning = None

    def merge_by(self, r_par, c):
        """ `c should be either 0 or 1. """
        child = r_par.turning.children[c]
        assert child.mergable(self)
        child.merge(self)

    def rotate(self):
        self.b, self.h = self.h, self.b
        self.is_rotated = not self.is_rotated

    # Representative informations.

    def repr_make_geom(self):
        elem = {
            'geom' : 'rectangle',
            'args' : self.xyxy, # json would convert typle into array
            'kwargs' : {
                'tag' : 'self%s' % self.id,
                'fill' : self.color,
                'outline' : 'gray',
            }
        }
        text = {
            'text' : '%s' % self.id,
            'args' : self.xymid,
            'kwargs' : {
                'tag' : 'T%s' % self.id,
                'text' : '%s' % self.id,
                'fill' : 'white',
            }
        }
        # Return dicts first, wrap them into
        # json outside.
        return [elem, text]

    def repr_active_state(self):
        info_r = {
            'tag' : 'R%s' % self.id,
            'args' : self.xyxy,
        }
        info_t = {
            'tag' : 'T%s' % self.id,
            'args' : self.xymid,
        }
        return [info_r, info_t]

    @property
    def color(self):
        b, h = self.b, self.h
        if b > h:
            c = b / h
        else:
            c = - h / b
        # Property of `fei:
        # if c -> +inf, then color stronger in red, and vice versa.
        fei = math.atan(c)
        red = int(50 * fei + 128) # max: 87
        grn = int( 5 * fei + 128)
        blu = int( 5 * fei + 128)
        fill = "#%02X%02X%02X" % (red, grn, blu)
        return fill


class Scene(object):
    """This object wraps a `hanger object, encapsulates method for state
    transferring in order to interface with generalized algorithms.
    This is also the object which plays the role of data model of
    corresponded problems and interfaces with outside.

    """

    def __init__(self, x_max=1000, y_max=1000):
        self.main_hanger = Turning.initialize_hanger(0, 0, x_max, y_max)
        self.origin = self.main_hanger.fllw
        self.rects = tuple()
        self.reservoir = []
        self.x_max = x_max
        self.y_max = y_max
        self.value_lower_bound = float('inf')

    def __repr__(self):
        return 'Scene{\n %s }' % ';\n'.join(
            pprint.pformat(_.cycle) for _ in self.hanger_col)

    def read_input(self, inp_tpls):
        """ Register the inputted Rectangle-tuples into the
        immutable naming-list `self.rects.
        Cache these Rectangles into self's reservoir, thus
        waiting to be merged. """
        self.rects = tuple(Rectangle(i,b,h) for i,(b,h) in enumerate(inp_tpls))
        self.reservoir.extend(self.rects)
        self.value_lower_bound = sum(_.area for _ in self.reservoir)

    def merge_at(self, r_id, tng_id):
        r = self.rects[r_id]
        assert r in self.reservoir
        tng = next(t for t in self.turning_col if t.id == tng_id)
        assert tng.mergable(r)
        self.reservoir.remove(r)
        tng.merge(r)

    def merge_by(self, r_id, rp_id, c):
        r = self.rects[r_id]
        assert r in self.reservoir
        t = self.rects[rp_id].turning.children[c]
        assert t.mergable(r)
        self.reservoir.remove(r)
        t.merge(r)

    def split(self, r_id):
        r = self.rects[r_id]
        assert r.splittable
        r.split()
        self.reservoir.append(r)

    def split_more(self, r_id):
        r = self.rects[r_id]
        assert r.splittable
        rs = r.cascaded_split()
        self.reservoir.extend(rs)

    def random_init(self):
        """ Randomly arrange all the rectangles. Thus to form a
        random state which is a start point in searching space.
        """
        self.random_merge()

    def greedy_init(self):
        """ Use First-Fit strategy to initialize the scene, which
        incrementally puts each rectangle into its first-fit frame.
        """
        self.greedy_merge()

    def random_merge(self):
        """ Extract all rectangles in the reservoir and randomly
        merge them into current outline. """
        while self.reservoir:
            r = self.reservoir.pop(0)    # 0!
            mots = self._assess_cycles_with_rect(r)
            mot = random.choice(mots)
            self.apply_motion(mot)

    def greedy_merge(self):
        """ Extract all rectangles in the reservoir and greedly
        merge them into current outline. """
        while self.reservoir:
            r = self.reservoir.pop(0)
            mots = self._assess_cycles_with_rect(r)
            mot = min(mots, key=lambda x:x.value)
            self.apply_motion(mot)

    @property
    def hanger_col(self):
        """ Find all hangers. """
        return self.main_hanger.hanger_pool

    @property
    def turning_col(self):
        return [_
                for h in self.hanger_col
                for _ in h.cycle ]

    @property
    def turning_xys(self):
        return [(tng.x, tng.y) for tng in self.main_hanger.cycle]

    @property
    def rect_xyxys(self):
        return [r.xyxy for r in self.rects]

    @property
    def outlines(self):
        def _outline_plist(hng):
            outl_ps = []
            for tng in hng.cycle:
                outl_ps.append((tng.x, tng.y))
                outl_ps.append((tng.fllw.x, tng.y))
            return outl_ps
        return [_outline_plist(hng) for hng in self.hanger_col]

    @property
    def object_value(self):
        x, y = self.main_hanger.bounding
        return x * y

    @property
    def color(self):
        b, h = self.b, self.h
        if b > h:
            c = b / h
        else:
            c = - h / b
        fei = math.atan(c)
        red = int(50 * fei + 128) # max: 87
        grn = int( 5 * fei + 128)
        blu = int( 5 * fei + 128)
        fill = "#%02X%02X%02X" % (red, grn, blu)
        return fill

    def _assess_one_cycle_with_rect(self, hg, rect):
        """Suppose `rect` is splitted out.  Find feasible merge of `rect` into
        outline, associated with new bounding box values if merged
        thereby.  `rect` bybrings the previous turning out of which it
        was splitted.

        Temp var `tbl` holds some `tng` and associated assessment of
        merging rect there i.e.,

            - (rect, rect_parent, child_num, rotated, (qualification ...))
        the former is a pointer to `Turning object and the
        latter appears in a comparable structure,
        in order to qualify some possible merging action at
        `tng, e.g.

            - (new_bounding_area, )

            - (new_bounding_area, fill_rest, other_qualification, )

            - ...

        Also some form of weighted function can be applied for
        assessment.

        """
        tbl = []
        # `self.bounding is dynamic.
        assert not rect.is_rotated
        bnd_x, bnd_y = self.main_hanger.bounding
        for tng in hg.cycle:
            # if tng is not rect.turning_before:
            if tng.mergable(rect):
                n_bnd_x = max(tng.x_put + rect.b, bnd_x)
                n_bnd_y = max(tng.y_put + rect.h, bnd_y)
                n_bnd_a = n_bnd_x * n_bnd_y
                fill_rest = tng.frame.fill_rest_of(rect)
                tbl.append(
                    Motion(rect, tng.parent.assoc_rect,
                                 tng.parent.children.index(tng),
                                 False,
                           # (n_bnd_a, tng.x + tng.y, fill_rest),
                           # (n_bnd_a, fill_rest, (tng.x + tng.y)**2, ),
                           # (n_bnd_a + (tng.x + tng.y), fill_rest),
                           # (n_bnd_x + n_bnd_y, fill_rest),
                           # (tng.x + tng.y, n_bnd_a, fill_rest),
                           (n_bnd_x + n_bnd_y, tng.x + tng.y)
                    ))
            rect.rotate()
            if tng.mergable(rect):
                n_bnd_x = max(tng.x_put + rect.b, bnd_x)
                n_bnd_y = max(tng.y_put + rect.h, bnd_y)
                n_bnd_a = n_bnd_x * n_bnd_y
                fill_rest = tng.frame.fill_rest_of(rect)
                tbl.append(
                    Motion(rect, tng.parent.assoc_rect,
                                 tng.parent.children.index(tng),
                                 True,
                           # (n_bnd_a, fill_rest, (tng.x + tng.y)**2, ),
                           # (n_bnd_a + (tng.x + tng.y), fill_rest),
                           # (n_bnd_a, tng.x + tng.y, fill_rest),
                           # (tng.x + tng.y, n_bnd_a, fill_rest),
                           # (n_bnd_x + n_bnd_y, fill_rest),
                           (n_bnd_x + n_bnd_y, tng.x + tng.y)
                    ))
            rect.rotate()
        return tbl

    def _assess_cycles_with_rect(self, rect):
        tbl = []
        for hg in self.hanger_col:
            tbl.extend(self._assess_one_cycle_with_rect(hg, rect))
        return tbl

    def assess(self):
        """Returns a list, with index of splittable rectangle and value as a
        list of feasible mergable positions.

        """
        mots = []
        rs_splittable = [r
                         for r in self.rects
                         if r not in self.reservoir and r.splittable]
        for r in rs_splittable:
            rotated = r.is_rotated
            r.split()
            mots.extend(
                mot for mot in self._assess_cycles_with_rect(r))
            if rotated:
                r.turning_before.merge_rotate(r)
            else:
                r.turning_before.merge(r)
        return mots

    def apply_motion(self, mot):
        if mot:
            if mot.rect.turning:
                mot.rect.split()
            tng = mot.target_turning
            if mot.rotated:
                tng.merge_rotate(mot.rect)
            else:
                tng.merge(mot.rect)

    def revert_motion(self, mot):
        """ Assume after splitting `mot.rect becomes
        unrotated. """
        if mot:
            mot.rect.split()

    def mutate(self, mot):
        """
        `mot is an instance of class Motion, the selection of
        some motion out of a motion list is delegated to the
        controller i.e. the optimizer.
        """
        # !! Since new instances of `Turning's are
        # created during assessment, the chosen
        # turning object could be obscelete, only
        # it's same-located exists in current outline.
        # Infomation
        self.apply_motion(mot)
        return {'id'      : mot.rect.id,
                'coords'  : mot.rect.xyxy,  }

    def pertubate(self, r_id):
        """ Cut a subtree off the tree rooted on the turning of
        Rectangle `r_id, cache them into the reservoir.
        Then some strategy is to be chosen to merge the
        members in reservoir back.
        """
        rs = self.rects[r_id].turning.cascaded_split()
        # Keep splitted unrotated.
        for r in rs:
            if r.is_rotated:
                r.rotate()
        self.reservoir.extend(rs)

    def deconstruct_all(self):
        if self.origin.assoc_rect is not None:
            r_id = self.origin.assoc_rect.id
            self.pertubate(r_id)

    def sort(self, keyattr=None, key=lambda r: r.area):
        if keyattr:
            self.reservoir.sort(key=op.attrgetter(keyattr), reverse=True)
        else:
            self.reservoir.sort(key=key, reverse=True)

    def shuffle(self):
        random.shuffle(self.reservoir)

    def complete(self, greedy=0):
        if greedy:
            self.greedy_merge()
        else:
            self.random_merge()

    def search_tree(self):
        """ Construct a decision tree.
        Use depth-first to increment/decrement stepwise.
        `util is supposed to be a quasi-linked list, which
        supports `prev and `next operations.
        """
        # tree: (mot, children, i_next, marked)
        # Empty motion None should be legal to apply.
        # Sugar:
        util = self.reservoir
        n = len(util)
        def mark(t):
            t[-1] = True
        def explore(t):
            mot, cs, i, m = t
            return [[_, [], i+1, False] for _ in self._assess_cycles_with_rect(util[i])]
        children =      lambda t: t[1]
        marked =        lambda t: t[-1]
        step =          lambda t: self.apply_motion(t[0])
        backstep =      lambda t: self.revert_motion(t[0])
        can_reach_more =lambda t: t[2] < n
        # General tree construction scheme.
        tree = [None, [], 0, False]
        frontier = [ tree ]
        while frontier:
            t = frontier[-1]
            if marked(t):
                backstep(t)
                frontier.pop()
            elif can_reach_more(t):
                mark(t)
                step(t)
                for tt in explore(t):
                    frontier.append(tt)
                    children(t).append(tt)
            # `t is leaf...
            else:
                frontier.pop()
        return tree

    def backstep_tree(self, n):
        """ The inserved version of search_tree, whereas search_tree
        constructs decision tree with application/revert of merging
        motions, backstep_tree constructs a tree with application/revert
        of splitting motion.
        *. Need the informative structure of motion be specified? """
        # tree: (mot, children, i_next, marked)
        # Empty motion None should be legal to apply.
        # Sugar:
        def mark(t):
            t[-1] = True
        # SHOULD DO on Scene level!
        # No direct operations on rectangle or turning objects!!
        def explore(t):
            """ Structure of motion of splitting? """
            i = t[2]
            return [[(_.id, _.turning.parent.assoc_rect.id,
                      _.turning.index_as_child, _.is_rotated),
                     [], i+1, False]
                    for _ in self.rects
                    if _ not in self.reservoir and _.splittable]
        def step(t):
            mot = t[0]
            if mot is not None:
                self.split(mot[0]) # split at scene level!
        def backstep(t):
            mot = t[0]
            if mot:
                rid, rpid, c, rotd = mot
                if rid is not None:
                    if rotd: self.rects[rid].rotate()
                    self.merge_by(rid, rpid, c) # merge at scene level
        children =      lambda t: t[1]
        can_reach_more =lambda t: t[2] < n
        marked =        lambda t: t[3]
        # General tree construction scheme.
        tree = [None, [], 0, False]
        frontier = [ tree ]
        while frontier:
            t = frontier[-1]
            if marked(t):
                backstep(t)
                frontier.pop()
            elif can_reach_more(t):
                mark(t)
                step(t)
                for tt in explore(t):
                    frontier.append(tt)
                    children(t).append(tt)
            # `t is leaf...
            else:
                frontier.pop()
        return tree

    @staticmethod
    def best_in_search_tree(tree):
        """ t[1] is list of children. """
        if tree[1]: # if `tree is not leaf.
            mot = tree[0]
            bst, val = min((Scene.best_in_search_tree(c)
                            for c in tree[1]),
                           key=lambda p:p[1])
            return [mot]+bst, val
        else:
            return [tree[0]], tree[0].value

    @staticmethod
    def all_leaves(tree):
        """ Retrieve all leaves of decision tree. """
        if tree[1]:
            return [l
                    for c in tree[1]
                    for l in Scene.all_leaves(c)]
        else:
            return [tree[0]]


class SceneDataModel(Scene):
    """ Simple wrapper of data model. """

    def __init__(self):
        super(SceneDataModel, self).__init__()

    @property
    def elements(self):
        "Retrieve the coordinates of rectangles."
        return self.rect_xyxys
    @property
    def helpers(self):
        """Retrieve the outline of rectangle heaps, including inner
        outline.

        """
        return self.outlines
    @property
    def objects(self):
        """Retrieve the objects in the model."""
        return self.rects

    def reset(self):
        """Reset the model."""
        self.deconstruct_all()

    @property
    def figure_state(self):
        "Generate the figure for the current state as byte stream."

        import matplotlib.pyplot as plt
        import matplotlib.patches as pch
        import io

        plt.rc('font', family='Times New Roman')
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')
        ax.set_title(
            'Bounding : {} x {};    Fill rate: {:.2f}'.format(
                self.main_hanger.bounding[0],
                self.main_hanger.bounding[1],
                self.value_lower_bound / self.object_value),
            fontsize=13)
        # Find the relative tight boundary.
        x_max = y_max = 0
        for rect in self.rects:
            ax.add_patch(
                pch.Rectangle(
                    (rect.x1, rect.y1), rect.b, rect.h,
                    edgecolor="#101010",
                    alpha=0.9,
                    facecolor=rect.color))
            if rect.x2 > x_max:
                x_max = rect.x2
            if rect.y2 > y_max:
                y_max = rect.y2
        x_max = y_max = max(x_max, y_max)
        ax.set_xlim(0, x_max)
        ax.set_ylim(0, y_max)
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        with io.BytesIO() as f:
            fig.savefig(f)
            f.seek(0)
            return f.read()

    @property
    def figure_3schemes(self):
        import io

        import matplotlib.pyplot as plt
        import matplotlib.patches as pch

        plt.rc('font', family='Times New Roman')
        attrs = ['area', 'width', 'height']

        fig = plt.figure()
        fig.set_size_inches(25, 12)

        for i, attr in enumerate(attrs, start=1):

            # Compute
            self.reset()
            self.sort(attr)
            self.greedy_init()

            # Info
            ax = fig.add_subplot(
                1, len(attrs), i,
                aspect='equal')
            ax.set_title(
                '\n'.join([
                    'Key: {};'.format(attr),
                    'Bounding: {} * {}; '.format(
                        *self.main_hanger.bounding),
                    'Fill rate: {:.2f}'.format(
                        sum(r.area for r in self.rects) / self.object_value),
                ]),
                fontsize=13)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

            # Find the relative tight boundary.
            x_max = y_max = 0
            for rect in self.rects:
                ax.add_patch(
                    pch.Rectangle(
                        (rect.x1, rect.y1), rect.b, rect.h,
                        edgecolor="#101010",
                        alpha=0.9,
                        facecolor=rect.color))
                if rect.x2 > x_max:
                    x_max = rect.x2
                if rect.y2 > y_max:
                    y_max = rect.y2
            x_max = y_max = max(x_max, y_max)
            ax.set_xlim(0, x_max)
            ax.set_ylim(0, y_max)

        with io.BytesIO() as f:
            fig.savefig(f)
            f.seek(0)
            return f.read()
    
    def greedy_solve(self):
        self.greedy_init()

    # @staticmethod
    # def solve(tps, sortkey=lambda rect: rect.width):
    #     s = SceneDataModel()
    #     s.read_input(tps)
    #     s.sort(key=sortkey)
    #     s.greedy_solve()
    #     return s


class Gen:

    @staticmethod
    def gen_inp(N, w_min=10, w_max=100, h_min=10, h_max=100):
        """Generate a list of tuples randomly for reading into model."""
        import random
        tps = []
        for _ in range(N):
            w = random.randint(w_min, w_max)
            h = random.randint(h_min, h_max)
            tps.append((w, h))
        return tps

    @staticmethod
    def from_file(filename):
        """Read from a file with each line as two integers. Returns a list of tuples.

        """
        inp = []
        with open(filename, 'r') as o:
            lns = o.readlines()
        for l, ln in enumerate(lns):
            if ln and not ln.startswith('#'):
                if ln.startswith('('):
                    assert ln.endswith(')'), 'Unmatched parenthesis at line {}'.format(l)
                    ln = ln[:-1]
                bh_txt = ln.split()
                if len(bh_txt) == 2:
                    b, h = bh_txt
                    inp.append((int(b), int(h)))
        return inp


def solve_file(filename, key='area'):

    # Parse file
    inp = Gen.from_file(filename)

    # Init and solve
    s = SceneDataModel()
    s.read_input(inp)
    s.sort(key)
    s.greedy_init()
    oup = [(r.id, r.b, r.h, (r.x1, r.y1), (r.x2, r.y2), r.is_rotated) for r in s.rects]

    # Output
    with open(filename + '_out', 'w') as o:
        cnt = '# (ID, width, height, (x1, y1), (x2, y2), rotated)\n'
        cnt += '\n'.join(map(str, oup))
        o.write(cnt)

    try:
        fig = s.figure_state
        with open(filename + '_out.png', 'wb') as o:
            o.write(fig)
    except ImportError as e:
        # import warnings
        # warnings.warn('matplotlib unavailable. No figure generated.')
        # print(e)
        print('Module matplotlib unavailable. No figure generated.')

    return


if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    solve_file(f)
    print('Solution done.\n')

