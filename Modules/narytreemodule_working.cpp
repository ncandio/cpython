#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <string>
#include <memory>
#include <vector>
#include <stdexcept>

// Include our enhanced C++ implementation
#include "nary_tree.cpp"

// C++ class wrapper
class NaryTreeWrapper {
public:
    NaryTree<PyObject*> tree;
    
    NaryTreeWrapper() {}
    explicit NaryTreeWrapper(PyObject* root_data) : tree(root_data) {
        Py_INCREF(root_data);
    }
    
    ~NaryTreeWrapper() {
        // Clean up all PyObject references
        if (!tree.empty()) {
            tree.for_each([](const auto& node) {
                Py_DECREF(node.data());
            });
        }
    }
};

extern "C" {

// Python object structure for NaryTree
typedef struct {
    PyObject_HEAD
    NaryTreeWrapper* tree;
} NaryTreeObject;

// Forward declaration of type (removed - will define directly)

// NaryTree methods
static PyObject* narytree_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    (void)args; (void)kwds; // Suppress unused parameter warnings
    NaryTreeObject* self = (NaryTreeObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->tree = NULL;
    }
    return (PyObject*)self;
}

static int narytree_init(NaryTreeObject* self, PyObject* args, PyObject* kwds) {
    (void)kwds; // Suppress unused parameter warning
    PyObject* root_data = NULL;
    
    if (!PyArg_ParseTuple(args, "|O", &root_data)) {
        return -1;
    }
    
    try {
        if (root_data) {
            self->tree = new NaryTreeWrapper(root_data);
        } else {
            self->tree = new NaryTreeWrapper();
        }
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    
    return 0;
}

static void narytree_dealloc(NaryTreeObject* self) {
    delete self->tree;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* narytree_set_root(NaryTreeObject* self, PyObject* args) {
    PyObject* root_data;
    if (!PyArg_ParseTuple(args, "O", &root_data)) {
        return NULL;
    }
    
    try {
        Py_INCREF(root_data);
        self->tree->tree.set_root(root_data);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject* narytree_empty(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyBool_FromLong(self->tree->tree.empty());
}

static PyObject* narytree_size(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->tree->tree.size());
}

static PyObject* narytree_depth(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->tree->tree.depth());
}

static PyObject* narytree_clear(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    // Clean up PyObject references before clearing
    if (!self->tree->tree.empty()) {
        self->tree->tree.for_each([](const auto& node) {
            Py_DECREF(node.data());
        });
    }
    self->tree->tree.clear();
    Py_RETURN_NONE;
}

static PyObject* narytree_statistics(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    auto stats = self->tree->tree.get_statistics();
    
    PyObject* dict = PyDict_New();
    if (!dict) return NULL;
    
    PyDict_SetItemString(dict, "total_nodes", PyLong_FromSize_t(stats.total_nodes));
    PyDict_SetItemString(dict, "leaf_nodes", PyLong_FromSize_t(stats.leaf_nodes));
    PyDict_SetItemString(dict, "internal_nodes", PyLong_FromSize_t(stats.internal_nodes));
    PyDict_SetItemString(dict, "max_depth", PyLong_FromSize_t(stats.max_depth));
    PyDict_SetItemString(dict, "avg_children_per_node", PyFloat_FromDouble(stats.avg_children_per_node));
    PyDict_SetItemString(dict, "max_children", PyLong_FromSize_t(stats.max_children));
    PyDict_SetItemString(dict, "min_children", PyLong_FromSize_t(stats.min_children));
    
    return dict;
}

// Balancing methods
static PyObject* narytree_balance_tree(NaryTreeObject* self, PyObject* args) {
    size_t max_children_per_node = 3;  // Default branching factor
    
    if (!PyArg_ParseTuple(args, "|n", &max_children_per_node)) {
        return NULL;
    }
    
    try {
        self->tree->tree.balance_tree(max_children_per_node);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject* narytree_needs_rebalancing(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyBool_FromLong(self->tree->tree.needs_rebalancing());
}

static PyObject* narytree_auto_balance_if_needed(NaryTreeObject* self, PyObject* args) {
    size_t max_children_per_node = 3;
    
    if (!PyArg_ParseTuple(args, "|n", &max_children_per_node)) {
        return NULL;
    }
    
    try {
        self->tree->tree.auto_balance_if_needed(max_children_per_node);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject* narytree_get_memory_stats(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    auto mem_stats = self->tree->tree.get_memory_stats();
    
    PyObject* dict = PyDict_New();
    if (!dict) return NULL;
    
    PyDict_SetItemString(dict, "node_memory_bytes", PyLong_FromSize_t(mem_stats.node_memory_bytes));
    PyDict_SetItemString(dict, "data_memory_estimate", PyLong_FromSize_t(mem_stats.data_memory_estimate));
    PyDict_SetItemString(dict, "total_estimated_bytes", PyLong_FromSize_t(mem_stats.total_estimated_bytes));
    PyDict_SetItemString(dict, "memory_per_node", PyFloat_FromDouble(mem_stats.memory_per_node));
    
    return dict;
}

static PyObject* narytree_encode_succinct(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    try {
        auto encoding = self->tree->tree.encode_succinct();
        
        PyObject* dict = PyDict_New();
        if (!dict) return NULL;
        
        // Convert bit vector to bytes
        PyObject* structure_bytes = PyBytes_FromStringAndSize(nullptr, (encoding.structure_bits.size() + 7) / 8);
        if (!structure_bytes) {
            Py_DECREF(dict);
            return NULL;
        }
        
        char* byte_data = PyBytes_AsString(structure_bytes);
        memset(byte_data, 0, (encoding.structure_bits.size() + 7) / 8); // Initialize to 0
        
        for (size_t i = 0; i < encoding.structure_bits.size(); ++i) {
            if (encoding.structure_bits[i]) {
                byte_data[i / 8] |= (1 << (i % 8));
            }
        }
        
        // Convert data array to Python list
        PyObject* data_list = PyList_New(encoding.data_array.size());
        if (!data_list) {
            Py_DECREF(structure_bytes);
            Py_DECREF(dict);
            return NULL;
        }
        
        for (size_t i = 0; i < encoding.data_array.size(); ++i) {
            PyObject* data_item = encoding.data_array[i];
            Py_INCREF(data_item);
            PyList_SetItem(data_list, i, data_item);
        }
        
        PyDict_SetItemString(dict, "structure_bits", structure_bytes);
        PyDict_SetItemString(dict, "data_array", data_list);
        PyDict_SetItemString(dict, "node_count", PyLong_FromSize_t(encoding.node_count));
        PyDict_SetItemString(dict, "memory_usage", PyLong_FromSize_t(encoding.memory_usage()));
        PyDict_SetItemString(dict, "bit_count", PyLong_FromSize_t(encoding.structure_bits.size()));
        
        Py_DECREF(structure_bytes);
        Py_DECREF(data_list);
        
        return dict;
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
}

// Method definitions with ALL balancing methods
static PyMethodDef narytree_methods[] = {
    {"set_root", (PyCFunction)narytree_set_root, METH_VARARGS, "Set the root node data"},
    {"empty", (PyCFunction)narytree_empty, METH_NOARGS, "Check if tree is empty"},
    {"size", (PyCFunction)narytree_size, METH_NOARGS, "Get tree size"},
    {"depth", (PyCFunction)narytree_depth, METH_NOARGS, "Get tree depth"},
    {"clear", (PyCFunction)narytree_clear, METH_NOARGS, "Clear the tree"},
    {"statistics", (PyCFunction)narytree_statistics, METH_NOARGS, "Get tree statistics"},
    {"balance_tree", (PyCFunction)narytree_balance_tree, METH_VARARGS, "Balance the tree with optional branching factor"},
    {"needs_rebalancing", (PyCFunction)narytree_needs_rebalancing, METH_NOARGS, "Check if tree needs rebalancing"},
    {"auto_balance_if_needed", (PyCFunction)narytree_auto_balance_if_needed, METH_VARARGS, "Automatically balance if needed"},
    {"get_memory_stats", (PyCFunction)narytree_get_memory_stats, METH_NOARGS, "Get memory usage statistics"},
    {"encode_succinct", (PyCFunction)narytree_encode_succinct, METH_NOARGS, "Encode tree as succinct data structure"},
    {NULL}
};

// Type definition
static PyTypeObject NaryTreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "narytree.NaryTree",
    .tp_basicsize = sizeof(NaryTreeObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)narytree_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "N-ary tree data structure with self-balancing",
    .tp_methods = narytree_methods,
    .tp_init = (initproc)narytree_init,
    .tp_new = narytree_new,
};

// Module definition
static PyModuleDef narytreemodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "narytree",
    .m_doc = "N-ary tree data structure module with self-balancing",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_narytree(void) {
    PyObject* m;
    
    if (PyType_Ready(&NaryTreeType) < 0) {
        return NULL;
    }
    
    m = PyModule_Create(&narytreemodule);
    if (m == NULL) {
        return NULL;
    }
    
    Py_INCREF(&NaryTreeType);
    if (PyModule_AddObject(m, "NaryTree", (PyObject*)&NaryTreeType) < 0) {
        Py_DECREF(&NaryTreeType);
        Py_DECREF(m);
        return NULL;
    }
    
    return m;
}

} // extern "C"