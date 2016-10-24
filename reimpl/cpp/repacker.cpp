#include <iostream>
#include <cassert>
#include <utility>
#include <tuple>
#include <list>


class Rectangle
{
public:
    int b, h, area;
    int x, y;

    Rectangle(int b_, int h_)
    {
        b = b_; h = h_;
        area = b_ * h_;
    }

};


class Corner
{
public:

    int x, y;
    Corner *left, *right, *up, *down;
    Corner *prev, *next;

    Corner(int x_, int y_)
    {
        x = x_; y = y_;
    }

    static inline void link(Corner *self, Corner *other)
    {
        self->next = other;
        other->prev = self;
    }

    inline char shape()
    {
        // int xIn = x - prev->x;
        int yIn = y - prev->y;
        int xOut = next->x - x;
        // int yOut = next->y - y;
        if (yIn < 0)
            return xOut < 0 ? 'D' : 'L';
        else
            return xOut < 0 ? 'T' : 'F';
    }

    Corner*
    plant(int b, int h)
    {
        Rectangle *r = new Rectangle(b, h);
        return plant(r);
    }

    Corner*
    plant(Rectangle *r)
    {
        int b = r->b; 
        int h = r->h;

        Corner *na, *nb, *tar, *ntmp, *n;

        switch (shape()) {
        case 'L':
            na = new Corner(x, y + h);
            nb = new Corner(x + b, y);
            link(prev, na); link(na, nb); link(nb, next);
            na->down = na; na->up = up;
            nb->left = nb; nb->right = right; 
            r->x = x; r->y = y;
            break;
        case 'D':
            tar = down;
            na = new Corner(x, tar->y + h);
            nb = new Corner(x + b, tar->y);
            ntmp = tar->next;
            link(tar, na); link(na, nb); link(nb, ntmp);
            na->down = na; na->up = up;
            nb->left = nb; nb->right = tar->right;
            r->x = x; r->y = tar->y;
            break;
        case 'F':
            tar = left;
            na = new Corner(tar->x, y + h);
            nb = new Corner(tar->x + b, y);
            ntmp = tar->prev;
            link(ntmp, na); link(na, nb); link(nb, tar);
            na->down = na; na->up = tar->up;
            nb->left = nb; nb->right = right;
            r->x = tar->x; r->y = y;
            break;
        default:
            std::cout << "ERROR!" << std::endl;
            throw 0;
        }

        // Drop overlapping points!
        // if (na->prev->y == na->y) {
        //     link(na->prev, na->next);
        //     na = na->prev;
        // }
        // if (nb->next->x == nb->x) {
        //     link(nb->prev, nb->next);
        //     nb = nb->next;
        // }
 
        Corner *up0 = up;
        Corner *right0 = right;

        // * na
        // tour leftwards
        n = na->prev;
        while (n->y < na->y) {
            n->right = na;
            n = n->left->prev;
        }
        na->left = n->next;

        // tour upwards
        n = up0;
        while (n->x <= nb->x) {
            n->down = na;
            n = n->up;
        }
        nb->up = n;
        while (n->x <= nb->next->x) {
            n->down = nb;
            if (n->shape() == 'T') break;
            else n = n->up;
        }

        // * nb
        // tour downwards
        n = nb->next;
        while (n->x < nb->x) {
            n->up = nb;
            n = n->down->next;  // FIXME: segment fault
        }
        nb->down = n->prev;

        // tour rightwards
        n = right0;
        while (n->y <= na->y) {
            n->left = nb;
            n = n->right;
        }
        na->right = n;
        while (n->y <= na->prev->y) {
            n->left = na;
            if (n->shape() == 'T') break;
            else n = n->right;
        }

        // return std::make_pair(na, nb);
        return na;
    }

    inline int xPut() {
        return (shape() == 'F') ? left->x : x;
    }

    inline int yPut() {
        return (shape() == 'D') ? down->y : y;
    }

    inline std::pair <int, int> slot()
    {
        int dx, dy;
        switch (shape()) {
        case 'L':
            dx = right->x - x;
            dy = up->y - y;
            break;
        case 'D':
            dx = down->right->x - x;
            dy = up->y - down->y;
            break;
        case 'F':
            dx = right->x - left->x;
            dy = left->up->y - y;
            break;
        default:
            throw 0;
        }
        return std::make_pair(dx, dy);
    }

    inline bool canPlant(Rectangle *r, int xBnd, int yBnd)
    {
        // Mind the gap.
        char s = shape();
        if (s == 'D') {
            if (y - down->y > r->h)
                return false;
            if (down->next->x == x)
                return false;
        } else if (s == 'F') {
            if (x - left->x > r->b)
                return false;
            if (left->prev->y == y)
                return false;
        }

        if (xPut() + r->b > xBnd || yPut() + r->h > yBnd)
            return false;

        std::pair <int, int> sxy = slot();
        // return sxy.first > r->b && sxy.second > r->h;
        return sxy.first >= r->b && sxy.second >= r->h;
    }

    float slotFillRate(Rectangle *r)
    {
        std::pair <int, int> sxy = slot();
        return r->area / (sxy.first * sxy.second);
    }

};


class Scene
{
public:
    Corner *top;
    Corner *ori;

    Scene(int xMax, int yMax)
    {
        top = new Corner(xMax, yMax);
        ori = new Corner(0, 0);
        
        top->next = top->prev = ori;
        ori->next = ori->prev = top;

        top->left = top->down = ori;
        top->up = top->right = top;

        ori->left = ori->down = ori;
        ori->up = ori->right = top;
    }

    inline std::pair <int, int>
    xyBounding()
    {
        int xBnd = 0, yBnd = 0;
        Corner *iter = top->next;
        while (iter != top) {
            if (iter->x > xBnd)
                xBnd = iter->x;
            if (iter->y > yBnd)
                yBnd = iter->y;
            iter = iter->next;
        }
        return std::make_pair(xBnd, yBnd);
    }

    Corner *
    walkFindBest(Rectangle *rect)
    {
        std::pair<int, int> p = xyBounding();
        int xBnd = p.first, yBnd = p.second;

        // std::tuple<int, int, float> valBest =
        auto valBest = std::make_tuple(xBnd + yBnd,
                                       xBnd + yBnd,
                                       0.0);

        Corner *iter = top->next, *cBest = top->next;
        while (iter != top) {
            if (iter->canPlant(rect, xBnd, yBnd)) {
                int xBnd1 = iter->xPut() + rect->b;
                if (xBnd1 < xBnd) xBnd1 = xBnd;
                int yBnd1 = iter->yPut() + rect->h;
                if (yBnd1 < yBnd) yBnd1 = yBnd;

                auto val =
                    std::make_tuple(xBnd1 + yBnd1,
                                    iter->x + iter->y,
                                    -iter->slotFillRate(rect));

                if (val < valBest) {
                    valBest = val;
                    cBest = iter;
                }
            }
            iter = iter->next;
        }

        // NOTE: if cBest has no value, no planting is viable,
        // maybe the bound space is too small.
        return cBest;
    }

    float plan(std::list<Rectangle*> rects)
    {
        float sArea = 0.0;

        for(auto r : rects) {
            Corner *cBest = walkFindBest(r);
            cBest->plant(r);
            sArea += r->area;
        }

        auto xyBnd = xyBounding();
        float bndArea = xyBnd.first * xyBnd.second;

        return sArea / bndArea;
    }
};


bool compRectangle(Rectangle *r1, Rectangle *r2)
{
    // return r1->area > r2->area;
    // return r1->b > r2->b;
    return std::make_pair(r1->area, r1->b) > std::make_pair(r2->area, r2->b);
}
