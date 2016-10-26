#include "repacker.cpp"

// #include <list>
#include <vector>
#include <algorithm>
#include <random>

using namespace std;

int main(int argc, char *argv[])
{

    vector<Rectangle*> rs = {};
    random_device r;

    default_random_engine el(r());
    uniform_int_distribution<int> uniform_dist(10, 100);
    
    Scene *s = new Scene(1000000, 1000000);

    for(int i = 0; i < 1000; i++) {
        int b = uniform_dist(el);
        int h = uniform_dist(el);
        auto r1 = new Rectangle(b, h);
        rs.push_back(r1);
    }

    for(int i = 0; i < 30; i++) {
        rs.push_back(new Rectangle(33, 33));
        rs.push_back(new Rectangle(66, 66));
    }
    
    sort(rs.begin(), rs.end(), compRectangle);

    double fiRa = s->plan(rs);
    auto xyBnd = s->xyBounding();
    double b_over_h = double(xyBnd.first) / double(xyBnd.second);
    
    cout << "Occupancy: " << fiRa << endl;
    cout << "Aspect ratio: " << b_over_h << endl;

    return 0;
}
