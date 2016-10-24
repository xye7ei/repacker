#include "repacker.cpp"

// #include <list>
#include <random>

using namespace std;

int main(int argc, char *argv[])
{

    list<Rectangle*> rs = {};
    random_device r;

    default_random_engine el(r());
    // uniform_int_distribution<int> uniform_dist(5, 50);
    uniform_int_distribution<int> uniform_dist(10, 100);
    
    Scene *s = new Scene(1000000, 1000000);

    for(int i = 0; i < 500; i++) {
        // cout << uniform_dist(el) << endl;
        int b = uniform_dist(el);
        int h = uniform_dist(el);
        auto r1 = new Rectangle(b, h);
        rs.push_back(r1);
    }

    for(int i = 0; i < 30; i++) {
        rs.push_back(new Rectangle(33, 33));
        rs.push_back(new Rectangle(66, 66));
    }
    
    rs.sort(compRectangle);
    
    // float sumA = 0;
    // for(int i = 0; i < 100; i++) {
    //     // cout << uniform_dist(el) << endl;
    //     int b = uniform_dist(el);
    //     int h = uniform_dist(el);
    //     auto r1 = new Rectangle(b, h);
    //     sumA += r1->area;
    //     auto n = s->walkFindBest(r1);
    //     n->plant(r1);
    // }

    // auto xyBnd = s->xyBounding();
    // // cout << xyBnd.first << ' ' << xyBnd.second << endl;
    // float fiRa = sumA / float(xyBnd.first * xyBnd.second);

    float fiRa = s->plan(rs);

    cout << fiRa << endl;

    return 0;
}
