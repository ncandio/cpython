// A simple Point structure (using int for coordinates as in source example)
struct Point {
    int x;
    int y;
    int z;
    Point() : x(-1), y(-1), z(-1) {} // Sentinel for empty point
    Point(int a, int b, int c) : x(a), y(b), z(c) {}
};

class Octree {
private:
    Point* point; // Stores the point if this is a leaf node, nullptr if internal/empty
    Point* topLeftFront; // Min coordinates of the octant
    Point* bottomRightBack; // Max coordinates of the octant
    std::vector<Octree*> children; // Pointers to the 8 sub-octants

public:
    // Constructor for an empty node
    Octree() : point(new Point()) {}

    // Constructor for a node holding a point
    Octree(int x, int y, int z) : point(new Point(x, y, z)) {}

    // Constructor for an octree with defined boundaries
    Octree(int x1, int y1, int z1, int x2, int y2, int z2) {
        // Basic validation for boundaries
        if (x2 < x1 || y2 < y1 || z2 < z1) {
            // Error handling, e.g., throw exception or print message
            return;
        }
        point = nullptr; // This is an internal node, not holding a direct point
        topLeftFront = new Point(x1, y1, z1);
        bottomRightBack = new Point(x2, y2, z2);
        children.assign(8, nullptr); // Initialize 8 children pointers to null
        // Optionally, initialize each child as an empty Octree node
        for (int i = 0; i < 8; ++i) {
            children[i] = new Octree(); // Create empty child nodes
        }
    }

    // Destructor to clean up allocated memory for points and children
    ~Octree() {
        delete point;
        delete topLeftFront;
        delete bottomRightBack;
        for (Octree* child : children) { // C++11 range-for loop [8]
            delete child;
        }
    }
    // ... insert and find methods below ...
};