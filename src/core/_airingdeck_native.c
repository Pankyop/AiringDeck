#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *filter_contains_indices(PyObject *self, PyObject *args) {
    PyObject *entries = NULL;
    PyObject *query_obj = NULL;

    if (!PyArg_ParseTuple(args, "OO", &entries, &query_obj)) {
        return NULL;
    }

    if (!PyList_Check(entries)) {
        PyErr_SetString(PyExc_TypeError, "entries must be a list");
        return NULL;
    }

    if (!PyUnicode_Check(query_obj)) {
        PyErr_SetString(PyExc_TypeError, "query must be a string");
        return NULL;
    }

    Py_ssize_t query_len = PyUnicode_GET_LENGTH(query_obj);
    Py_ssize_t count = PyList_GET_SIZE(entries);

    PyObject *result = PyList_New(0);
    if (result == NULL) {
        return NULL;
    }

    if (query_len == 0) {
        for (Py_ssize_t i = 0; i < count; ++i) {
            PyObject *idx = PyLong_FromSsize_t(i);
            if (idx == NULL || PyList_Append(result, idx) < 0) {
                Py_XDECREF(idx);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(idx);
        }
        return result;
    }

    for (Py_ssize_t i = 0; i < count; ++i) {
        PyObject *entry = PyList_GET_ITEM(entries, i); /* borrowed */
        if (!PyDict_Check(entry)) {
            continue;
        }

        PyObject *blob = PyDict_GetItemString(entry, "_search_blob"); /* borrowed */
        if (blob == NULL || !PyUnicode_Check(blob)) {
            continue;
        }

        Py_ssize_t found = PyUnicode_Find(blob, query_obj, 0, PyUnicode_GET_LENGTH(blob), 1);
        if (found >= 0) {
            PyObject *idx = PyLong_FromSsize_t(i);
            if (idx == NULL || PyList_Append(result, idx) < 0) {
                Py_XDECREF(idx);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(idx);
        }
    }

    return result;
}

static PyMethodDef AiringDeckNativeMethods[] = {
    {
        "filter_contains_indices",
        filter_contains_indices,
        METH_VARARGS,
        "Return entry indices where entry['_search_blob'] contains query."
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef airingdeck_native_module = {
    PyModuleDef_HEAD_INIT,
    "_airingdeck_native",
    "Native acceleration helpers for AiringDeck.",
    -1,
    AiringDeckNativeMethods
};

PyMODINIT_FUNC PyInit__airingdeck_native(void) {
    return PyModule_Create(&airingdeck_native_module);
}
