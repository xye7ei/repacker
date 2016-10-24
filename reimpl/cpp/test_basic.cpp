#include "repacker.cpp"

int main(int argc, char **argv)
{
    Scene *s = new Scene(1000, 1000);
    Corner *t = s->top;
    Corner *o = s->ori;

    Corner *n1 = o->plant(30, 5);
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

    Corner *n3 = n1->plant(10, 30);
    Corner *n4 = n3->next;
    assert(n3->up == t);
    assert(n3->right == t);
    assert(n3->down == n3);
    assert(n3->left == n3);
    assert(n4->up == t);
    assert(n4->right == t);
    assert(n4->down == n4);
    assert(n4->left == n4);

    Corner *n5 = n3->plant(30, 5);
    Corner *n6 = n5->next;
    assert(n5->up == t);
    assert(n5->right == t);
    assert(n5->down == n5);
    assert(n5->left == n5);
    assert(n6->left == n6);
    assert(n6->right == t);
    assert(n6->up == t);
    assert(n6->down == n4);

    // n7, n8 = n2->plant(5, 37);
    Rectangle *r = new Rectangle(5, 5);
    Corner *nBest = s->walkFindBest(r);
    std::cout << nBest->x << ", " << nBest->y << std::endl;
    std::cout << "Hello" << std::endl;

    return 0;
}
