from core.worker import Worker


def test_worker_emits_result_and_finished():
    got = {"result": None, "finished": 0, "error": None}

    def fn(a, b):
        return a + b

    worker = Worker(fn, 2, 3)
    worker.signals.result.connect(lambda value: got.__setitem__("result", value))
    worker.signals.error.connect(lambda err: got.__setitem__("error", err))
    worker.signals.finished.connect(lambda: got.__setitem__("finished", got["finished"] + 1))

    worker.run()

    assert got["result"] == 5
    assert got["error"] is None
    assert got["finished"] == 1


def test_worker_emits_error_and_finished():
    got = {"result": None, "finished": 0, "error": None}

    def fn():
        raise RuntimeError("boom")

    worker = Worker(fn)
    worker.signals.result.connect(lambda value: got.__setitem__("result", value))
    worker.signals.error.connect(lambda err: got.__setitem__("error", err))
    worker.signals.finished.connect(lambda: got.__setitem__("finished", got["finished"] + 1))

    worker.run()

    assert got["result"] is None
    assert got["error"] is not None
    assert got["error"][0] is RuntimeError
    assert "boom" in str(got["error"][1])
    assert got["finished"] == 1
