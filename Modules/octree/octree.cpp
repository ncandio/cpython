#include <Python.h>
#include <memory>
#include <vector>
#include <algorithm>
#include <cmath>
#include <array>
#include <optional>
#include <cassert>
#include <type_traits>

namespace {

// Templated Point structure for flexible coordinate types
template<typename T>
struct Point3D {
    T x, y, z;
    PyObject* data;
    
    static_assert(std::is_arithmetic_v<T>, "Point3D coordinate type must be arithmetic");
    
    Point3D() : x(T{}), y(T{}), z(T{}), data(nullptr) {}
    
    Point3D(T x, T y, T z, PyObject* data = nullptr) : x(x), y(y), z(z), data(data) {
        if (data) Py_INCREF(data);
    }
    
    ~Point3D() {
        if (data) Py_DECREF(data);
    }
    
    // Move semantics for efficient memory management
    Point3D(const Point3D&) = delete;
    Point3D& operator=(const Point3D&) = delete;
    
    Point3D(Point3D&& other) noexcept 
        : x(other.x), y(other.y), z(other.z), data(other.data) {
        other.data = nullptr;
    }
    
    Point3D& operator=(Point3D&& other) noexcept {
        if (this != &other) {
            if (data) Py_DECREF(data);
            x = other.x;
            y = other.y;
            z = other.z;
            data = other.data;
            other.data = nullptr;
        }
        return *this;
    }
    
    bool operator==(const Point3D& other) const noexcept {
        if constexpr (std::is_floating_point_v<T>) {
            constexpr T epsilon = static_cast<T>(1e-9);
            return std::abs(x - other.x) < epsilon && 
                   std::abs(y - other.y) < epsilon && 
                   std::abs(z - other.z) < epsilon;
        } else {
            return x == other.x && y == other.y && z == other.z;
        }
    }
};

// Templated Bounding Box for flexible coordinate types
template<typename T>
struct BoundingBox3D {
    T min_x, min_y, min_z;
    T max_x, max_y, max_z;
    
    BoundingBox3D() = default;
    
    BoundingBox3D(T min_x, T min_y, T min_z, T max_x, T max_y, T max_z)
        : min_x(min_x), min_y(min_y), min_z(min_z)
        , max_x(max_x), max_y(max_y), max_z(max_z) {
        assert(max_x >= min_x && max_y >= min_y && max_z >= min_z);
    }
    
    bool contains(const Point3D<T>& point) const noexcept {
        return point.x >= min_x && point.x <= max_x &&
               point.y >= min_y && point.y <= max_y &&
               point.z >= min_z && point.z <= max_z;
    }
    
    bool intersects(const BoundingBox3D& other) const noexcept {
        return !(other.min_x > max_x || other.max_x < min_x ||
                 other.min_y > max_y || other.max_y < min_y ||
                 other.min_z > max_z || other.max_z < min_z);
    }
    
    T width() const noexcept { return max_x - min_x; }
    T height() const noexcept { return max_y - min_y; }
    T depth() const noexcept { return max_z - min_z; }
    
    Point3D<T> center() const noexcept {
        return Point3D<T>((min_x + max_x) / T(2), 
                         (min_y + max_y) / T(2), 
                         (min_z + max_z) / T(2));
    }
};

// Templated Octree class with configurable coordinate and data types
template<typename T, size_t MaxPointsPerNode = 8, size_t MaxDepth = 16>
class Octree {
private:
    static_assert(std::is_arithmetic_v<T>, "Octree coordinate type must be arithmetic");
    static_assert(MaxPointsPerNode > 0, "MaxPointsPerNode must be positive");
    static_assert(MaxDepth > 0, "MaxDepth must be positive");
    
    BoundingBox3D<T> bounds;
    std::vector<Point3D<T>> points;
    std::array<std::unique_ptr<Octree>, 8> children;
    size_t depth;
    bool is_subdivided;
    
    // Octant indices for the 8 children
    enum Octant {
        TOP_LEFT_FRONT = 0,     // -x, +y, +z
        TOP_RIGHT_FRONT = 1,    // +x, +y, +z
        TOP_LEFT_BACK = 2,      // -x, +y, -z
        TOP_RIGHT_BACK = 3,     // +x, +y, -z
        BOTTOM_LEFT_FRONT = 4,  // -x, -y, +z
        BOTTOM_RIGHT_FRONT = 5, // +x, -y, +z
        BOTTOM_LEFT_BACK = 6,   // -x, -y, -z
        BOTTOM_RIGHT_BACK = 7   // +x, -y, -z
    };
    
    Octant getOctant(const Point3D<T>& point) const noexcept {
        auto center = bounds.center();
        int index = 0;
        if (point.x >= center.x) index |= 1;  // Right
        if (point.y < center.y) index |= 4;   // Bottom
        if (point.z < center.z) index |= 2;   // Back
        return static_cast<Octant>(index);
    }
    
    BoundingBox3D<T> getOctantBounds(Octant octant) const noexcept {
        auto center = bounds.center();
        
        switch (octant) {
            case TOP_LEFT_FRONT:
                return BoundingBox3D<T>(bounds.min_x, center.y, center.z, center.x, bounds.max_y, bounds.max_z);
            case TOP_RIGHT_FRONT:
                return BoundingBox3D<T>(center.x, center.y, center.z, bounds.max_x, bounds.max_y, bounds.max_z);
            case TOP_LEFT_BACK:
                return BoundingBox3D<T>(bounds.min_x, center.y, bounds.min_z, center.x, bounds.max_y, center.z);
            case TOP_RIGHT_BACK:
                return BoundingBox3D<T>(center.x, center.y, bounds.min_z, bounds.max_x, bounds.max_y, center.z);
            case BOTTOM_LEFT_FRONT:
                return BoundingBox3D<T>(bounds.min_x, bounds.min_y, center.z, center.x, center.y, bounds.max_z);
            case BOTTOM_RIGHT_FRONT:
                return BoundingBox3D<T>(center.x, bounds.min_y, center.z, bounds.max_x, center.y, bounds.max_z);
            case BOTTOM_LEFT_BACK:
                return BoundingBox3D<T>(bounds.min_x, bounds.min_y, bounds.min_z, center.x, center.y, center.z);
            case BOTTOM_RIGHT_BACK:
                return BoundingBox3D<T>(center.x, bounds.min_y, bounds.min_z, bounds.max_x, center.y, center.z);
            default:
                return bounds; // Should never reach here
        }
    }
    
    void subdivide() {
        if (is_subdivided || depth >= MaxDepth) return;
        
        for (int i = 0; i < 8; ++i) {
            auto octant_bounds = getOctantBounds(static_cast<Octant>(i));
            children[i] = std::make_unique<Octree>(octant_bounds, depth + 1);
        }
        
        // Redistribute points to children
        for (auto& point : points) {
            auto octant = getOctant(point);
            children[octant]->insert(std::move(point));
        }
        
        points.clear();
        is_subdivided = true;
    }
    
public:
    // Constructor for octree with defined boundaries
    Octree(const BoundingBox3D<T>& bounds, size_t depth = 0)
        : bounds(bounds), depth(depth), is_subdivided(false) {
        points.reserve(MaxPointsPerNode);
    }
    
    // Constructor with coordinate bounds
    Octree(T min_x, T min_y, T min_z, T max_x, T max_y, T max_z)
        : Octree(BoundingBox3D<T>(min_x, min_y, min_z, max_x, max_y, max_z)) {}
    
    // Insert a point into the octree
    bool insert(Point3D<T> point) {
        if (!bounds.contains(point)) {
            return false;
        }
        
        if (!is_subdivided) {
            if (points.size() < MaxPointsPerNode || depth >= MaxDepth) {
                points.emplace_back(std::move(point));
                return true;
            }
            subdivide();
        }
        
        auto octant = getOctant(point);
        return children[octant]->insert(std::move(point));
    }
    
    // Find points within a bounding box
    std::vector<const Point3D<T>*> query(const BoundingBox3D<T>& range) const {
        std::vector<const Point3D<T>*> result;
        queryRange(range, result);
        return result;
    }
    
    // Find points within a spherical region
    std::vector<const Point3D<T>*> queryRadius(const Point3D<T>& center, T radius) const {
        std::vector<const Point3D<T>*> result;
        T radius_squared = radius * radius;
        
        BoundingBox3D<T> search_bounds(
            center.x - radius, center.y - radius, center.z - radius,
            center.x + radius, center.y + radius, center.z + radius
        );
        
        queryRadiusInternal(center, radius_squared, search_bounds, result);
        return result;
    }
    
    // Get the total number of points in the octree
    size_t size() const noexcept {
        size_t count = points.size();
        if (is_subdivided) {
            for (const auto& child : children) {
                if (child) count += child->size();
            }
        }
        return count;
    }
    
    // Check if the octree is empty
    bool empty() const noexcept {
        return size() == 0;
    }
    
    // Get the depth of the octree
    size_t getDepth() const noexcept {
        if (!is_subdivided) return depth;
        
        size_t max_child_depth = depth;
        for (const auto& child : children) {
            if (child) {
                max_child_depth = std::max(max_child_depth, child->getDepth());
            }
        }
        return max_child_depth;
    }
    
    // Clear all points from the octree
    void clear() {
        points.clear();
        for (auto& child : children) {
            child.reset();
        }
        is_subdivided = false;
    }
    
    // Get bounds of the octree
    const BoundingBox3D<T>& getBounds() const noexcept {
        return bounds;
    }

private:
    void queryRange(const BoundingBox3D<T>& range, std::vector<const Point3D<T>*>& result) const {
        if (!bounds.intersects(range)) return;
        
        for (const auto& point : points) {
            if (range.contains(point)) {
                result.push_back(&point);
            }
        }
        
        if (is_subdivided) {
            for (const auto& child : children) {
                if (child) child->queryRange(range, result);
            }
        }
    }
    
    void queryRadiusInternal(const Point3D<T>& center, T radius_squared, 
                           const BoundingBox3D<T>& search_bounds,
                           std::vector<const Point3D<T>*>& result) const {
        if (!bounds.intersects(search_bounds)) return;
        
        for (const auto& point : points) {
            T dx = point.x - center.x;
            T dy = point.y - center.y;
            T dz = point.z - center.z;
            T distance_squared = dx * dx + dy * dy + dz * dz;
            
            if (distance_squared <= radius_squared) {
                result.push_back(&point);
            }
        }
        
        if (is_subdivided) {
            for (const auto& child : children) {
                if (child) {
                    child->queryRadiusInternal(center, radius_squared, search_bounds, result);
                }
            }
        }
    }
};

// Type aliases for common use cases
using OctreeFloat = Octree<float>;
using OctreeDouble = Octree<double>;
using OctreeInt = Octree<int>;

} // namespace

// Python wrapper for Octree
struct PyOctreeObject {
    PyObject_HEAD
    std::unique_ptr<OctreeDouble> octree;
};

static PyTypeObject PyOctreeType;

// Create new Octree instance
static PyObject* PyOctree_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    PyOctreeObject* self = (PyOctreeObject*)type->tp_alloc(type, 0);
    if (self != nullptr) {
        new (&self->octree) std::unique_ptr<OctreeDouble>();
    }
    return (PyObject*)self;
}

// Initialize Octree
static int PyOctree_init(PyOctreeObject* self, PyObject* args, PyObject* kwds) {
    double min_x, min_y, min_z, max_x, max_y, max_z;
    
    if (!PyArg_ParseTuple(args, "dddddd", &min_x, &min_y, &min_z, &max_x, &max_y, &max_z)) {
        return -1;
    }
    
    try {
        self->octree = std::make_unique<OctreeDouble>(min_x, min_y, min_z, max_x, max_y, max_z);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    
    return 0;
}

// Deallocate Octree
static void PyOctree_dealloc(PyOctreeObject* self) {
    self->octree.~unique_ptr<OctreeDouble>();
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// Insert point into octree
static PyObject* PyOctree_insert(PyOctreeObject* self, PyObject* args) {
    double x, y, z;
    PyObject* data = nullptr;
    
    if (!PyArg_ParseTuple(args, "ddd|O", &x, &y, &z, &data)) {
        return nullptr;
    }
    
    Point3D<double> point(x, y, z, data);
    bool success = self->octree->insert(std::move(point));
    
    return PyBool_FromLong(success);
}

// Query points within bounding box
static PyObject* PyOctree_query(PyOctreeObject* self, PyObject* args) {
    double min_x, min_y, min_z, max_x, max_y, max_z;
    
    if (!PyArg_ParseTuple(args, "dddddd", &min_x, &min_y, &min_z, &max_x, &max_y, &max_z)) {
        return nullptr;
    }
    
    BoundingBox3D<double> range(min_x, min_y, min_z, max_x, max_y, max_z);
    auto results = self->octree->query(range);
    
    PyObject* list = PyList_New(results.size());
    if (!list) return nullptr;
    
    for (size_t i = 0; i < results.size(); ++i) {
        const auto* point = results[i];
        PyObject* tuple = PyTuple_New(4);
        if (!tuple) {
            Py_DECREF(list);
            return nullptr;
        }
        
        PyTuple_SetItem(tuple, 0, PyFloat_FromDouble(point->x));
        PyTuple_SetItem(tuple, 1, PyFloat_FromDouble(point->y));
        PyTuple_SetItem(tuple, 2, PyFloat_FromDouble(point->z));
        
        if (point->data) {
            Py_INCREF(point->data);
            PyTuple_SetItem(tuple, 3, point->data);
        } else {
            Py_INCREF(Py_None);
            PyTuple_SetItem(tuple, 3, Py_None);
        }
        
        PyList_SetItem(list, i, tuple);
    }
    
    return list;
}

// Query points within radius
static PyObject* PyOctree_query_radius(PyOctreeObject* self, PyObject* args) {
    double center_x, center_y, center_z, radius;
    
    if (!PyArg_ParseTuple(args, "dddd", &center_x, &center_y, &center_z, &radius)) {
        return nullptr;
    }
    
    Point3D<double> center(center_x, center_y, center_z);
    auto results = self->octree->queryRadius(center, radius);
    
    PyObject* list = PyList_New(results.size());
    if (!list) return nullptr;
    
    for (size_t i = 0; i < results.size(); ++i) {
        const auto* point = results[i];
        PyObject* tuple = PyTuple_New(4);
        if (!tuple) {
            Py_DECREF(list);
            return nullptr;
        }
        
        PyTuple_SetItem(tuple, 0, PyFloat_FromDouble(point->x));
        PyTuple_SetItem(tuple, 1, PyFloat_FromDouble(point->y));
        PyTuple_SetItem(tuple, 2, PyFloat_FromDouble(point->z));
        
        if (point->data) {
            Py_INCREF(point->data);
            PyTuple_SetItem(tuple, 3, point->data);
        } else {
            Py_INCREF(Py_None);
            PyTuple_SetItem(tuple, 3, Py_None);
        }
        
        PyList_SetItem(list, i, tuple);
    }
    
    return list;
}

// Get octree size
static PyObject* PyOctree_size(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->octree->size());
}

// Clear octree
static PyObject* PyOctree_clear(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    self->octree->clear();
    Py_RETURN_NONE;
}

// Get octree depth
static PyObject* PyOctree_depth(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->octree->getDepth());
}

// Method definitions
static PyMethodDef PyOctree_methods[] = {
    {"insert", (PyCFunction)PyOctree_insert, METH_VARARGS,
     "Insert a point (x, y, z, data=None) into the octree"},
    {"query", (PyCFunction)PyOctree_query, METH_VARARGS,
     "Query points within bounding box (min_x, min_y, min_z, max_x, max_y, max_z)"},
    {"query_radius", (PyCFunction)PyOctree_query_radius, METH_VARARGS,
     "Query points within radius (center_x, center_y, center_z, radius)"},
    {"size", (PyCFunction)PyOctree_size, METH_NOARGS,
     "Get the number of points in the octree"},
    {"clear", (PyCFunction)PyOctree_clear, METH_NOARGS,
     "Remove all points from the octree"},
    {"depth", (PyCFunction)PyOctree_depth, METH_NOARGS,
     "Get the maximum depth of the octree"},
    {nullptr, nullptr, 0, nullptr}
};

// Type definition
static PyTypeObject PyOctreeType = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "octree.Octree",
    .tp_doc = "3D spatial indexing data structure",
    .tp_basicsize = sizeof(PyOctreeObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyOctree_new,
    .tp_init = (initproc)PyOctree_init,
    .tp_dealloc = (destructor)PyOctree_dealloc,
    .tp_methods = PyOctree_methods,
};

// Module definition
static PyModuleDef octreemodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "octree",
    .m_doc = "3D Octree spatial data structure for efficient 3D point indexing and querying",
    .m_size = -1,
};

// Module initialization
PyMODINIT_FUNC PyInit_octree(void) {
    PyObject* module;
    
    if (PyType_Ready(&PyOctreeType) < 0) {
        return nullptr;
    }
    
    module = PyModule_Create(&octreemodule);
    if (module == nullptr) {
        return nullptr;
    }
    
    Py_INCREF(&PyOctreeType);
    if (PyModule_AddObject(module, "Octree", (PyObject*)&PyOctreeType) < 0) {
        Py_DECREF(&PyOctreeType);
        Py_DECREF(module);
        return nullptr;
    }
    
    return module;
}