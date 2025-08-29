#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

// Include our C++ implementation
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

// Python object structure for Node
typedef struct {
    PyObject_HEAD
    void* node_ptr;
    NaryTreeObject* tree_obj;
} NodeObject;

static void narytree_dealloc(NaryTreeObject* self) {
    delete self->tree;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* narytree_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    NaryTreeObject* self = (NaryTreeObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->tree = nullptr;
    }
    return (PyObject*)self;
}

static int narytree_init(NaryTreeObject* self, PyObject* args, PyObject* kwds) {
    PyObject* root_data = nullptr;
    
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

static PyObject* narytree_set_root(NaryTreeObject* self, PyObject* args) {
    PyObject* root_data;
    if (!PyArg_ParseTuple(args, "O", &root_data)) {
        return nullptr;
    }
    
    try {
        Py_INCREF(root_data);
        self->tree->tree.set_root(root_data);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
    
    Py_RETURN_NONE;
}

static PyObject* narytree_empty(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyBool_FromLong(self->tree->tree.empty());
}

static PyObject* narytree_size(NaryTreeObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyLong_FromSize_t(self->tree->tree.size());
}

static PyMethodDef narytree_methods[] = {
    {"set_root", (PyCFunction)narytree_set_root, METH_VARARGS, "Set the root node data"},
    {"empty", (PyCFunction)narytree_empty, METH_NOARGS, "Check if tree is empty"},
    {"size", (PyCFunction)narytree_size, METH_NOARGS, "Get tree size"},
    {nullptr, nullptr, 0, nullptr}
};

static PyTypeObject NaryTreeType = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "narytree.NaryTree",           /* tp_name */
    sizeof(NaryTreeObject),        /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)narytree_dealloc,  /* tp_dealloc */
    0,                             /* tp_vectorcall_offset */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_as_async */
    0,                             /* tp_repr */
    0,                             /* tp_as_number */
    0,                             /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    0,                             /* tp_hash */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "N-ary tree data structure",   /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    narytree_methods,              /* tp_methods */
    0,                             /* tp_members */
    0,                             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)narytree_init,       /* tp_init */
    0,                             /* tp_alloc */
    narytree_new,                  /* tp_new */
};

static PyModuleDef narytreemodule = {
    PyModuleDef_HEAD_INIT,
    "narytree",
    "N-ary tree data structure module",
    -1,
    nullptr, nullptr, nullptr, nullptr, nullptr
};

PyMODINIT_FUNC PyInit_narytree(void) {
    PyObject* m;
    
    if (PyType_Ready(&NaryTreeType) < 0) {
        return nullptr;
    }
    
    m = PyModule_Create(&narytreemodule);
    if (m == nullptr) {
        return nullptr;
    }
    
    Py_INCREF(&NaryTreeType);
    if (PyModule_AddObject(m, "NaryTree", (PyObject*)&NaryTreeType) < 0) {
        Py_DECREF(&NaryTreeType);
        Py_DECREF(m);
        return nullptr;
    }
    
    return m;
}

} // extern "C"