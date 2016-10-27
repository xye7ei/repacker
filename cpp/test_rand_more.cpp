#include "repacker.cpp"

// #include <list>
#include <vector>
#include <algorithm>
#include <random>

using namespace std;

int main(int argc, char *argv[])
{

    vector<Rectangle *> rs = {};
    random_device r;

    default_random_engine el(r());
    uniform_int_distribution<int> uniform_dist(10, 100);
    
    Scene s = Scene(1000000, 1000000);

    for(int i = 0; i < 5000; i++) {
        int b = uniform_dist(el);
        int h = uniform_dist(el);
        rs.push_back(new Rectangle(b, h));
    }

    for(int i = 0; i < 1000; i++) {
        rs.push_back(new Rectangle(33, 33));
        rs.push_back(new Rectangle(66, 66));
    }
    
    sort(rs.begin(), rs.end(), [](auto r1, auto r2) {
                                   // return r1->area > r2->area;
                                   return r1->b + r1->h > r2->b + r2->h;
                               });

    double fiRa = s.plan(rs);
    auto xyBnd = s.xyBounding();
    double b_over_h = double(xyBnd.first) / double(xyBnd.second);
    
    cout << "Occupancy: " << fiRa << endl;
    cout << "Aspect ratio: " << b_over_h << endl;

    // writeRectangles(rs, "test_rand_more.py");
    return 0;
}
