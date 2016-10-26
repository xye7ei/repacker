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

            float x1 = 10.0 * (r->x)      / float(sBnd);
            float y1 = 10.0 * (r->y)      / float(sBnd);
            float x2 = 10.0 * (x1 + r->b) / float(sBnd);
            float y2 = 10.0 * (y1 + r->h) / float(sBnd);

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
    
    Scene *s = new Scene(sBnd, sBnd);

    for(int i = 0; i < N; i++) {
        int b = uniform_dist(el);
        int h = uniform_dist(el);
        auto r1 = new Rectangle(b, h);
        rs.push_back(r1);
    }

    for(int i = 0; i < 30; i++) {
        rs.push_back(new Rectangle(rMax/3, rMax/3));
        rs.push_back(new Rectangle(rMax/3*2, rMax/3*2));
    }
    
    sort(rs.begin(), rs.end(), compRectangle);
    
    double fiRa = s->plan(rs);
    auto xyBnd = s->xyBounding();

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
