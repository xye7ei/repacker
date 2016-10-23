#include <iostream>
#include <cassert>
#include <utility>
#include <tuple>


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

    Corner* merge(int b, int h)
    {
        Rectangle *r = new Rectangle(b, h);
        return merge(r);
    }

    Corner* merge(Rectangle *r)
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
            throw 0;
        }

        // Drop overlapping points!
        if (na->prev->y == na->y) {
            link(na->prev, na->next);
            na = na->prev;
        }
        if (nb->next->x == nb->x) {
            link(nb->prev, nb->next);
            nb = nb->next;
        }

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
            n = n->down->next;
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

    inline bool canMerge(Rectangle *r)
    {
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
        std::pair <int, int> sxy = slot();
        return sxy.first > r->b && sxy.second > r->h;
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
        int xBnd = -1, yBnd = -1;
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
    walkFindBest(Rectangle* rect)
    {
        std::pair<int, int> p = xyBounding();
        int xBnd = p.first, yBnd = p.second;

        // std::tuple<int, int, float> valBest =
        auto valBest =
            std::make_pair<int, float>(xBnd + yBnd, 0.0);

        Corner *iter = top->next, *cBest;
        while (iter != top) {
            if (iter->canMerge(rect)) {
                int xBnd1 = iter->xPut() + rect->b;
                if (xBnd1 > xBnd) xBnd = xBnd1;
                int yBnd1 = iter->yPut() + rect->h;
                if (yBnd1 > yBnd) yBnd = yBnd1;

                auto val = std::make_pair<int, float>(xBnd1 + yBnd1, -iter->slotFillRate(rect));

                if (val < valBest) {
                    valBest = val;
                    cBest = iter;
                }
            }
            iter = iter->next;
        }

        return cBest;
    }

};


int main(int argc, char **argv)
{
    Scene *s = new Scene(1000, 1000);
    Corner *t = s->top;
    Corner *o = s->ori;

    Corner *n1 = o->merge(30, 5);
    Corner *n2 = n1->next;

    assert(n1->left == n1);
    assert(n1->right == t);
    assert(n1->up == t);
    assert(n1->down == n1);
    assert(n2->left == n2);
    assert(n2->right == t);
    assert(n2->up == t);
    assert(n2->down == n2);
    assert(t->next == n1);
    assert(n1->next == n2);
    assert(n2->next == t);

    Corner *n3 = n1->merge(10, 30);
    Corner *n4 = n3->next;
    assert(n3->up == t);
    assert(n3->right == t);
    assert(n3->down == n3);
    assert(n3->left == n3);
    assert(n4->up == t);
    assert(n4->right == t);
    assert(n4->down == n4);
    assert(n4->left == n4);

    Corner *n5 = n3->merge(30, 5);
    Corner *n6 = n5->next;
    assert(n5->up == t);
    assert(n5->right == t);
    assert(n5->down == n5);
    assert(n5->left == n5);
    assert(n6->left == n6);
    assert(n6->right == t);
    assert(n6->up == t);
    assert(n6->down == n4);

    // n7, n8 = n2->merge(5, 37);
    Rectangle *r = new Rectangle(5, 5);
    Corner *nBest = s->walkFindBest(r);
    std::cout << nBest->x << ", " << nBest->y << std::endl;
    std::cout << "Hello" << std::endl;

    return 0;
}
