#include "repacker.cpp"

#include <random>
#include <algorithm>

#include <GL/gl.h>
#include <GL/glut.h>
#include <GL/glu.h>

using namespace std;

static vector<Rectangle*> rs = {};

static const int N = 50;
static const int rMin = 1, rMax = 5;
static const int sBnd = rMax * (N + 1);

void display()
{
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    for(auto r : rs) {

        glBegin(GL_POLYGON);

            glColor3f(0.0, 0.0, 1.0);

            double x1 = 10.0 * (r->x)      / double(sBnd);
            double y1 = 10.0 * (r->y)      / double(sBnd);
            double x2 = 10.0 * (x1 + r->b) / double(sBnd);
            double y2 = 10.0 * (y1 + r->h) / double(sBnd);

            cout << x1 << ',' << y1 << endl;

            glVertex2f(x1, y1);
            glVertex2f(x1, y2);
            glVertex2f(x2, y2);
            glVertex2f(x2, y1);

        glEnd();

    }
    glFlush();
}


int main(int argc, char *argv[])
{

    random_device r;

    default_random_engine el(r());
    uniform_int_distribution<int> uniform_dist(rMin, rMax);
    
    Scene s = Scene(sBnd, sBnd);

    for(int i = 0; i < N; i++) {
        int b = uniform_dist(el);
        int h = uniform_dist(el);
        rs.push_back(new Rectangle(b, h));
    }

    for(int i = 0; i < 30; i++) {
        rs.push_back(new Rectangle(rMax/3, rMax/3));
        rs.push_back(new Rectangle(rMax/3*2, rMax/3*2));
    }
    
    sort(rs.begin(), rs.end(), [](auto ra, auto rb){
                                   return ra->area > rb->area;
                               });
    
    double fiRa = s.plan(rs);
    auto xyBnd = s.xyBounding();

    double b_over_h = double(xyBnd.first) / double(xyBnd.second);

    cout << "Occupancy: " << fiRa << endl;
    cout << "Aspect ratio: " << b_over_h << endl;

    glutInit(&argc, argv);
    glutCreateWindow("Rectangle packing.");
    // glutInitWindowSize(xyBnd.first, xyBnd.second);
    // glutInitWindowPosition(xyBnd.first, xyBnd.second);
    glutInitWindowSize(500, 500);
    glutInitWindowPosition(0, 0);

    glutDisplayFunc(display);

    glutMainLoop();
    
    return 0;
}
