#include <Python.h>

// Step 1: Define the Position Class in C++
class Position {
    public:
        Position(double entry_price, double exit_price): entry_price(entry_price), exit_price(exit_price) {}
        double profit() const { return exit_price - entry_price; }

    private:
        double entry_price;
        double exit_price;
};



// Step 2: Create Wrapper Functions for Python
extern "C" {

    static PyObject *Position_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
    {
        double entry_price = 0.0;
        double exit_price = 0.0;
        if (!PyArg_ParseTuple(args, "dd", &entry_price, &exit_price))
        {
            return nullptr;
        }
        Position *self = new Position(entry_price, exit_price);
        return PyCapsule_New(self, "Position", nullptr);
    }

    static void Position_dealloc(PyObject *self)
    {
        delete PyCapsule_GetPointer(self, "Position");
    }

    static PyObject *Position_profit(PyObject *self, PyObject *Py_UNUSED(ignored))
    {
        Position *position = static_cast<Position *>(PyCapsule_GetPointer(self, "Position"));
        return PyFloat_FromDouble(position->profit());
    }

    static PyMethodDef Position_methods[] =
    {
        {"profit", Position_profit, METH_NOARGS, "calculate the profit of the position."},
        {nullptr, nullptr, 0, nullptr}  // Sentinel
    };

    static PyTypeObject PositionType =
    {
        PyVarObject_HEAD_INIT(nullptr, 0)
        .tp_name = "cppext.Position",
        .tp_doc = "position objects",
        .tp_basicsize = sizeof(PyObject*),
        .tp_itemsize = 0,
        .tp_flags = Py_TPFLAGS_DEFAULT,
        .tp_new = Position_new,
        .tp_dealloc = Position_dealloc,
        .tp_methods = Position_methods,
    };

    static PyModuleDef cppextmodule =
    {
        PyModuleDef_HEAD_INIT,
        .m_name = "cppext",
        .m_doc = "example module that creates an extension type.",
        .m_size = -1,
    };


    PyMODINIT_FUNC PyInit_cpp_position(void)
    {
        if (PyType_Ready(&PositionType) < 0)
            return nullptr;

        PyObject *m = PyModule_Create(&cppextmodule);
        if (m == nullptr)
            return nullptr;

        Py_INCREF(&PositionType);
        if (PyModule_AddObject(m, "Position", (PyObject *) &PositionType) < 0)
        {
            Py_DECREF(&PositionType);
            Py_DECREF(m);
            return nullptr;
        }

        return m;
    }

} // extern "C"

