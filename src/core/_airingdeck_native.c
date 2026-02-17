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

static int matches_query(PyObject *entry, PyObject *query_obj, int use_query) {
    if (!use_query) {
        return 1;
    }
    PyObject *blob = PyDict_GetItemString(entry, "_search_blob"); /* borrowed */
    if (blob == NULL || !PyUnicode_Check(blob)) {
        return 0;
    }
    Py_ssize_t found = PyUnicode_Find(blob, query_obj, 0, PyUnicode_GET_LENGTH(blob), 1);
    return found >= 0;
}

static int matches_only_today(PyObject *entry, int only_today, int today_weekday) {
    if (!only_today) {
        return 1;
    }
    PyObject *day_obj = PyDict_GetItemString(entry, "calendar_day"); /* borrowed */
    if (day_obj == NULL || !PyLong_Check(day_obj)) {
        return 0;
    }
    long day = PyLong_AsLong(day_obj);
    if (PyErr_Occurred()) {
        PyErr_Clear();
        return 0;
    }
    return (int)day == today_weekday;
}

static int matches_genre(PyObject *media, PyObject *genre_obj, int use_genre) {
    if (!use_genre) {
        return 1;
    }
    if (!PyDict_Check(media)) {
        return 0;
    }
    PyObject *genres = PyDict_GetItemString(media, "genres"); /* borrowed */
    if (genres == NULL || !PyList_Check(genres)) {
        return 0;
    }

    Py_ssize_t genres_count = PyList_GET_SIZE(genres);
    for (Py_ssize_t j = 0; j < genres_count; ++j) {
        PyObject *genre = PyList_GET_ITEM(genres, j); /* borrowed */
        if (!PyUnicode_Check(genre)) {
            continue;
        }
        PyObject *lower = PyObject_CallMethod(genre, "lower", NULL);
        if (lower == NULL) {
            PyErr_Clear();
            continue;
        }
        int is_match = PyObject_RichCompareBool(lower, genre_obj, Py_EQ);
        Py_DECREF(lower);
        if (is_match < 0) {
            PyErr_Clear();
            continue;
        }
        if (is_match == 1) {
            return 1;
        }
    }
    return 0;
}

static int matches_min_score(PyObject *media, int min_score) {
    if (min_score <= 0) {
        return 1;
    }
    if (!PyDict_Check(media)) {
        return 0;
    }
    PyObject *score_obj = PyDict_GetItemString(media, "averageScore"); /* borrowed */
    if (score_obj == NULL || score_obj == Py_None) {
        return 0;
    }
    double score = PyFloat_AsDouble(score_obj);
    if (PyErr_Occurred()) {
        PyErr_Clear();
        return 0;
    }
    return score >= (double)min_score;
}

static PyObject *filter_advanced_indices(PyObject *self, PyObject *args) {
    PyObject *entries = NULL;
    PyObject *query_obj = NULL;
    PyObject *genre_obj = NULL;
    int min_score = 0;
    int only_today = 0;
    int today_weekday = -1;

    if (!PyArg_ParseTuple(args, "OOOiii", &entries, &query_obj, &genre_obj, &min_score, &only_today, &today_weekday)) {
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
    if (!PyUnicode_Check(genre_obj)) {
        PyErr_SetString(PyExc_TypeError, "selected_genre must be a string");
        return NULL;
    }

    int use_query = PyUnicode_GET_LENGTH(query_obj) > 0;
    int use_genre = PyUnicode_GET_LENGTH(genre_obj) > 0 &&
                    PyUnicode_CompareWithASCIIString(genre_obj, "all genres") != 0;

    Py_ssize_t count = PyList_GET_SIZE(entries);
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i < count; ++i) {
        PyObject *entry = PyList_GET_ITEM(entries, i); /* borrowed */
        if (!PyDict_Check(entry)) {
            continue;
        }

        if (!matches_only_today(entry, only_today, today_weekday)) {
            continue;
        }
        if (!matches_query(entry, query_obj, use_query)) {
            continue;
        }

        PyObject *media = PyDict_GetItemString(entry, "media"); /* borrowed */
        if (!matches_genre(media, genre_obj, use_genre)) {
            continue;
        }
        if (!matches_min_score(media, min_score)) {
            continue;
        }

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

static PyMethodDef AiringDeckNativeMethods[] = {
    {
        "filter_contains_indices",
        filter_contains_indices,
        METH_VARARGS,
        "Return entry indices where entry['_search_blob'] contains query."
    },
    {
        "filter_advanced_indices",
        filter_advanced_indices,
        METH_VARARGS,
        "Return indices matching query/genre/min_score/only_today filters."
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
