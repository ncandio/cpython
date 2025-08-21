#include <Python.h>
#include <memory>
#include <vector>
#include <algorithm>
#include <cmath>
#include <array>
#include <optional>
#include <cassert>
#include <type_traits>
#include <stdexcept>
#include <iostream>
#include <iomanip>

namespace {

// Templated Point structure for flexible coordinate types
template<typename T>
class alignas(std::max(alignof(T), alignof(PyObject*))) Point3D {
private:
    T x_, y_, z_;
    PyObject* data_;

public:
    static_assert(std::is_arithmetic_v<T>, "Point3D coordinate type must be arithmetic");
    static_assert(std::is_nothrow_move_constructible_v<T>, "Coordinate type must be nothrow move constructible");
    
    // Default constructor
    constexpr Point3D() noexcept : x_(T{}), y_(T{}), z_(T{}), data_(nullptr) {}
    
    // Constructor with coordinates and optional data
    Point3D(T x, T y, T z, PyObject* data = nullptr) noexcept
        : x_(x), y_(y), z_(z), data_(data) {
        if (data_) Py_INCREF(data_);
    }
    
    // Destructor
    ~Point3D() {
        if (data_) Py_DECREF(data_);
    }
    
    // Copy constructor - explicitly deleted for performance
    Point3D(const Point3D&) = delete;
    Point3D& operator=(const Point3D&) = delete;
    
    // Move constructor
    Point3D(Point3D&& other) noexcept 
        : x_(other.x_), y_(other.y_), z_(other.z_), data_(other.data_) {
        other.data_ = nullptr;
    }
    
    // Move assignment
    Point3D& operator=(Point3D&& other) noexcept {
        if (this != &other) {
            if (data_) Py_DECREF(data_);
            x_ = other.x_;
            y_ = other.y_;
            z_ = other.z_;
            data_ = other.data_;
            other.data_ = nullptr;
        }
        return *this;
    }
    
    // Getters
    constexpr T x() const noexcept { return x_; }
    constexpr T y() const noexcept { return y_; }
    constexpr T z() const noexcept { return z_; }
    PyObject* data() const noexcept { return data_; }
    
    // Setters
    void set_x(T x) noexcept { x_ = x; }
    void set_y(T y) noexcept { y_ = y; }
    void set_z(T z) noexcept { z_ = z; }
    
    void set_data(PyObject* data) noexcept {
        if (data_) Py_DECREF(data_);
        data_ = data;
        if (data_) Py_INCREF(data_);
    }
    
    // Comparison operators
    bool operator==(const Point3D& other) const noexcept {
        if constexpr (std::is_floating_point_v<T>) {
            constexpr T epsilon = static_cast<T>(1e-9);
            return std::abs(x_ - other.x_) < epsilon && 
                   std::abs(y_ - other.y_) < epsilon && 
                   std::abs(z_ - other.z_) < epsilon;
        } else {
            return x_ == other.x_ && y_ == other.y_ && z_ == other.z_;
        }
    }
    
    bool operator!=(const Point3D& other) const noexcept {
        return !(*this == other);
    }
    
    // Distance calculation
    T distance_squared_to(const Point3D& other) const noexcept {
        const T dx = x_ - other.x_;
        const T dy = y_ - other.y_;
        const T dz = z_ - other.z_;
        return dx * dx + dy * dy + dz * dz;
    }
    
    T distance_to(const Point3D& other) const noexcept {
        return std::sqrt(distance_squared_to(other));
    }
};

// Templated Bounding Box for flexible coordinate types
template<typename T>
class BoundingBox3D {
private:
    T min_x_, min_y_, min_z_;
    T max_x_, max_y_, max_z_;
    bool valid_;

public:
    static_assert(std::is_arithmetic_v<T>, "BoundingBox3D coordinate type must be arithmetic");
    
    // Default constructor - creates invalid bounding box
    constexpr BoundingBox3D() noexcept 
        : min_x_(T{}), min_y_(T{}), min_z_(T{})
        , max_x_(T{}), max_y_(T{}), max_z_(T{})
        , valid_(false) {}
    
    // Constructor with bounds validation
    BoundingBox3D(T min_x, T min_y, T min_z, T max_x, T max_y, T max_z)
        : min_x_(min_x), min_y_(min_y), min_z_(min_z)
        , max_x_(max_x), max_y_(max_y), max_z_(max_z)
        , valid_(max_x >= min_x && max_y >= min_y && max_z >= min_z) {
        if (!valid_) {
            throw std::invalid_argument("Invalid bounding box: max values must be >= min values");
        }
    }
    
    // Getters
    constexpr T min_x() const noexcept { return min_x_; }
    constexpr T min_y() const noexcept { return min_y_; }
    constexpr T min_z() const noexcept { return min_z_; }
    constexpr T max_x() const noexcept { return max_x_; }
    constexpr T max_y() const noexcept { return max_y_; }
    constexpr T max_z() const noexcept { return max_z_; }
    constexpr bool is_valid() const noexcept { return valid_; }
    
    // Point containment test
    bool contains(const Point3D<T>& point) const noexcept {
        if (!valid_) return false;
        return point.x() >= min_x_ && point.x() <= max_x_ &&
               point.y() >= min_y_ && point.y() <= max_y_ &&
               point.z() >= min_z_ && point.z() <= max_z_;
    }
    
    // Bounding box intersection test
    bool intersects(const BoundingBox3D& other) const noexcept {
        if (!valid_ || !other.valid_) return false;
        return !(other.min_x_ > max_x_ || other.max_x_ < min_x_ ||
                 other.min_y_ > max_y_ || other.max_y_ < min_y_ ||
                 other.min_z_ > max_z_ || other.max_z_ < min_z_);
    }
    
    // Dimension getters
    constexpr T width() const noexcept { return max_x_ - min_x_; }
    constexpr T height() const noexcept { return max_y_ - min_y_; }
    constexpr T depth() const noexcept { return max_z_ - min_z_; }
    
    // Volume calculation
    constexpr T volume() const noexcept {
        return valid_ ? width() * height() * depth() : T{0};
    }
    
    // Center point calculation
    Point3D<T> center() const noexcept {
        return Point3D<T>((min_x_ + max_x_) / T(2), 
                         (min_y_ + max_y_) / T(2), 
                         (min_z_ + max_z_) / T(2));
    }
    
    // Expand bounding box to include a point
    void expand_to_include(const Point3D<T>& point) noexcept {
        if (!valid_) {
            min_x_ = max_x_ = point.x();
            min_y_ = max_y_ = point.y();
            min_z_ = max_z_ = point.z();
            valid_ = true;
        } else {
            min_x_ = std::min(min_x_, point.x());
            min_y_ = std::min(min_y_, point.y());
            min_z_ = std::min(min_z_, point.z());
            max_x_ = std::max(max_x_, point.x());
            max_y_ = std::max(max_y_, point.y());
            max_z_ = std::max(max_z_, point.z());
        }
    }
    
    // Expand bounding box to include another bounding box
    void expand_to_include(const BoundingBox3D& other) noexcept {
        if (!other.valid_) return;
        if (!valid_) {
            *this = other;
        } else {
            min_x_ = std::min(min_x_, other.min_x_);
            min_y_ = std::min(min_y_, other.min_y_);
            min_z_ = std::min(min_z_, other.min_z_);
            max_x_ = std::max(max_x_, other.max_x_);
            max_y_ = std::max(max_y_, other.max_y_);
            max_z_ = std::max(max_z_, other.max_z_);
        }
    }
};

// Templated Octree class with configurable coordinate and data types
template<typename T, size_t MaxPointsPerNode = 8, size_t MaxDepth = 16>
class Octree {
private:
    static_assert(std::is_arithmetic_v<T>, "Octree coordinate type must be arithmetic");
    static_assert(MaxPointsPerNode > 0, "MaxPointsPerNode must be positive");
    static_assert(MaxDepth > 0, "MaxDepth must be positive");
    
    BoundingBox3D<T> bounds_;
    std::vector<Point3D<T>> points_;
    std::array<std::unique_ptr<Octree>, 8> children_;
    size_t depth_;
    bool is_subdivided_;
    
    // Statistics for performance monitoring
    mutable size_t query_count_;
    mutable size_t subdivision_count_;
    
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
        const auto center = bounds_.center();
        int index = 0;
        if (point.x() >= center.x()) index |= 1;  // Right
        if (point.y() < center.y()) index |= 4;   // Bottom
        if (point.z() < center.z()) index |= 2;   // Back
        return static_cast<Octant>(index);
    }
    
    BoundingBox3D<T> getOctantBounds(Octant octant) const {
        const auto center = bounds_.center();
        
        switch (octant) {
            case TOP_LEFT_FRONT:
                return BoundingBox3D<T>(bounds_.min_x(), center.y(), center.z(), 
                                       center.x(), bounds_.max_y(), bounds_.max_z());
            case TOP_RIGHT_FRONT:
                return BoundingBox3D<T>(center.x(), center.y(), center.z(), 
                                       bounds_.max_x(), bounds_.max_y(), bounds_.max_z());
            case TOP_LEFT_BACK:
                return BoundingBox3D<T>(bounds_.min_x(), center.y(), bounds_.min_z(), 
                                       center.x(), bounds_.max_y(), center.z());
            case TOP_RIGHT_BACK:
                return BoundingBox3D<T>(center.x(), center.y(), bounds_.min_z(), 
                                       bounds_.max_x(), bounds_.max_y(), center.z());
            case BOTTOM_LEFT_FRONT:
                return BoundingBox3D<T>(bounds_.min_x(), bounds_.min_y(), center.z(), 
                                       center.x(), center.y(), bounds_.max_z());
            case BOTTOM_RIGHT_FRONT:
                return BoundingBox3D<T>(center.x(), bounds_.min_y(), center.z(), 
                                       bounds_.max_x(), center.y(), bounds_.max_z());
            case BOTTOM_LEFT_BACK:
                return BoundingBox3D<T>(bounds_.min_x(), bounds_.min_y(), bounds_.min_z(), 
                                       center.x(), center.y(), center.z());
            case BOTTOM_RIGHT_BACK:
                return BoundingBox3D<T>(center.x(), bounds_.min_y(), bounds_.min_z(), 
                                       bounds_.max_x(), center.y(), center.z());
            default:
                throw std::logic_error("Invalid octant value");
        }
    }
    
    void subdivide() {
        if (is_subdivided_ || depth_ >= MaxDepth) return;
        
        try {
            for (int i = 0; i < 8; ++i) {
                auto octant_bounds = getOctantBounds(static_cast<Octant>(i));
                children_[i] = std::make_unique<Octree>(octant_bounds, depth_ + 1);
            }
            
            // Redistribute points to children
            for (auto& point : points_) {
                auto octant = getOctant(point);
                children_[octant]->insert(std::move(point));
            }
            
            points_.clear();
            is_subdivided_ = true;
            ++subdivision_count_;
        } catch (const std::exception&) {
            // If subdivision fails, clean up any partially created children
            for (auto& child : children_) {
                child.reset();
            }
            throw;
        }
    }
    
public:
    // Constructor for octree with defined boundaries
    Octree(const BoundingBox3D<T>& bounds, size_t depth = 0)
        : bounds_(bounds), depth_(depth), is_subdivided_(false)
        , query_count_(0), subdivision_count_(0) {
        if (!bounds_.is_valid()) {
            throw std::invalid_argument("Cannot create octree with invalid bounding box");
        }
        points_.reserve(MaxPointsPerNode);
    }
    
    // Constructor with coordinate bounds
    Octree(T min_x, T min_y, T min_z, T max_x, T max_y, T max_z)
        : Octree(BoundingBox3D<T>(min_x, min_y, min_z, max_x, max_y, max_z)) {}
    
    // Destructor
    ~Octree() = default;
    
    // Move-only semantics for performance
    Octree(const Octree&) = delete;
    Octree& operator=(const Octree&) = delete;
    Octree(Octree&&) = default;
    Octree& operator=(Octree&&) = default;
    
    // Insert a point into the octree
    bool insert(Point3D<T> point) {
        if (!bounds_.contains(point)) {
            return false;
        }
        
        if (!is_subdivided_) {
            if (points_.size() < MaxPointsPerNode || depth_ >= MaxDepth) {
                points_.emplace_back(std::move(point));
                return true;
            }
            subdivide();
        }
        
        const auto octant = getOctant(point);
        return children_[octant]->insert(std::move(point));
    }
    
    // Find points within a bounding box
    std::vector<const Point3D<T>*> query(const BoundingBox3D<T>& range) const {
        std::vector<const Point3D<T>*> result;
        result.reserve(std::min(points_.size(), MaxPointsPerNode * 4)); // Reasonable initial capacity
        queryRange(range, result);
        ++query_count_;
        return result;
    }
    
    // Find points within a spherical region
    std::vector<const Point3D<T>*> queryRadius(const Point3D<T>& center, T radius) const {
        if (radius < T{0}) {
            return {}; // Invalid radius
        }
        
        std::vector<const Point3D<T>*> result;
        result.reserve(std::min(points_.size(), MaxPointsPerNode * 4));
        const T radius_squared = radius * radius;
        
        BoundingBox3D<T> search_bounds(
            center.x() - radius, center.y() - radius, center.z() - radius,
            center.x() + radius, center.y() + radius, center.z() + radius
        );
        
        queryRadiusInternal(center, radius_squared, search_bounds, result);
        ++query_count_;
        return result;
    }
    
    // Get the total number of points in the octree
    size_t size() const noexcept {
        size_t count = points_.size();
        if (is_subdivided_) {
            for (const auto& child : children_) {
                if (child) count += child->size();
            }
        }
        return count;
    }
    
    // Check if the octree is empty
    bool empty() const noexcept {
        return points_.empty() && (!is_subdivided_ || 
            std::all_of(children_.begin(), children_.end(), 
                       [](const auto& child) { return !child || child->empty(); }));
    }
    
    // Get the maximum depth of the octree
    size_t getDepth() const noexcept {
        if (!is_subdivided_) return depth_;
        
        size_t max_child_depth = depth_;
        for (const auto& child : children_) {
            if (child) {
                max_child_depth = std::max(max_child_depth, child->getDepth());
            }
        }
        return max_child_depth;
    }
    
    // Get the current depth of this node
    size_t getCurrentDepth() const noexcept {
        return depth_;
    }
    
    // Check if this node is subdivided
    bool isSubdivided() const noexcept {
        return is_subdivided_;
    }
    
    // Get query statistics
    size_t getQueryCount() const noexcept {
        return query_count_;
    }
    
    size_t getSubdivisionCount() const noexcept {
        return subdivision_count_;
    }
    
    // Clear all points from the octree
    void clear() {
        points_.clear();
        for (auto& child : children_) {
            child.reset();
        }
        is_subdivided_ = false;
        query_count_ = 0;
        subdivision_count_ = 0;
    }
    
    // Get bounds of the octree
    const BoundingBox3D<T>& getBounds() const noexcept {
        return bounds_;
    }
    
    // Get memory usage estimate in bytes
    size_t getMemoryUsage() const noexcept {
        size_t memory = sizeof(*this);
        memory += points_.capacity() * sizeof(Point3D<T>);
        
        if (is_subdivided_) {
            for (const auto& child : children_) {
                if (child) {
                    memory += child->getMemoryUsage();
                }
            }
        }
        
        return memory;
    }

private:
    void queryRange(const BoundingBox3D<T>& range, std::vector<const Point3D<T>*>& result) const {
        if (!bounds_.intersects(range)) return;
        
        // Check points in this node
        for (const auto& point : points_) {
            if (range.contains(point)) {
                result.push_back(&point);
            }
        }
        
        // Recursively check children
        if (is_subdivided_) {
            for (const auto& child : children_) {
                if (child) child->queryRange(range, result);
            }
        }
    }
    
    void queryRadiusInternal(const Point3D<T>& center, T radius_squared, 
                           const BoundingBox3D<T>& search_bounds,
                           std::vector<const Point3D<T>*>& result) const {
        if (!bounds_.intersects(search_bounds)) return;
        
        // Check points in this node
        for (const auto& point : points_) {
            const T distance_squared = point.distance_squared_to(center);
            if (distance_squared <= radius_squared) {
                result.push_back(&point);
            }
        }
        
        // Recursively check children
        if (is_subdivided_) {
            for (const auto& child : children_) {
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

// Forward declaration removed - defined below

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
    
    try {
        Point3D<double> point(x, y, z, data);
        bool success = self->octree->insert(std::move(point));
        return PyBool_FromLong(success);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

// Query points within bounding box
static PyObject* PyOctree_query(PyOctreeObject* self, PyObject* args) {
    double min_x, min_y, min_z, max_x, max_y, max_z;
    
    if (!PyArg_ParseTuple(args, "dddddd", &min_x, &min_y, &min_z, &max_x, &max_y, &max_z)) {
        return nullptr;
    }
    
    try {
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
            
            PyTuple_SetItem(tuple, 0, PyFloat_FromDouble(point->x()));
            PyTuple_SetItem(tuple, 1, PyFloat_FromDouble(point->y()));
            PyTuple_SetItem(tuple, 2, PyFloat_FromDouble(point->z()));
            
            if (point->data()) {
                Py_INCREF(point->data());
                PyTuple_SetItem(tuple, 3, point->data());
            } else {
                Py_INCREF(Py_None);
                PyTuple_SetItem(tuple, 3, Py_None);
            }
            
            PyList_SetItem(list, i, tuple);
        }
        
        return list;
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_ValueError, e.what());
        return nullptr;
    }
}

// Query points within radius
static PyObject* PyOctree_query_radius(PyOctreeObject* self, PyObject* args) {
    double center_x, center_y, center_z, radius;
    
    if (!PyArg_ParseTuple(args, "dddd", &center_x, &center_y, &center_z, &radius)) {
        return nullptr;
    }
    
    try {
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
            
            PyTuple_SetItem(tuple, 0, PyFloat_FromDouble(point->x()));
            PyTuple_SetItem(tuple, 1, PyFloat_FromDouble(point->y()));
            PyTuple_SetItem(tuple, 2, PyFloat_FromDouble(point->z()));
            
            if (point->data()) {
                Py_INCREF(point->data());
                PyTuple_SetItem(tuple, 3, point->data());
            } else {
                Py_INCREF(Py_None);
                PyTuple_SetItem(tuple, 3, Py_None);
            }
            
            PyList_SetItem(list, i, tuple);
        }
        
        return list;
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_ValueError, e.what());
        return nullptr;
    }
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

// Get query count
static PyObject* PyOctree_query_count(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->octree->getQueryCount());
}

// Get subdivision count
static PyObject* PyOctree_subdivision_count(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->octree->getSubdivisionCount());
}

// Get memory usage
static PyObject* PyOctree_memory_usage(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->octree->getMemoryUsage());
}

// Check if octree is empty
static PyObject* PyOctree_empty(PyOctreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyBool_FromLong(self->octree->empty());
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
    {"empty", (PyCFunction)PyOctree_empty, METH_NOARGS,
     "Check if the octree is empty"},
    {"query_count", (PyCFunction)PyOctree_query_count, METH_NOARGS,
     "Get the number of queries performed on the octree"},
    {"subdivision_count", (PyCFunction)PyOctree_subdivision_count, METH_NOARGS,
     "Get the number of subdivisions performed"},
    {"memory_usage", (PyCFunction)PyOctree_memory_usage, METH_NOARGS,
     "Get estimated memory usage in bytes"},
    {nullptr, nullptr, 0, nullptr}
};

// Type definition
static PyTypeObject PyOctreeType = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "octree.Octree",                    /* tp_name */
    sizeof(PyOctreeObject),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)PyOctree_dealloc,       /* tp_dealloc */
    0,                                  /* tp_vectorcall_offset */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_as_async */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "3D spatial indexing data structure", /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    PyOctree_methods,                   /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)PyOctree_init,            /* tp_init */
    0,                                  /* tp_alloc */
    PyOctree_new,                       /* tp_new */
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