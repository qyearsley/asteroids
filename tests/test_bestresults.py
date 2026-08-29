"""Tests for the local best-results store."""

import json

import pytest

import bestresults
from constants import MODE_CLASSIC, MODE_TIME_TRIAL


@pytest.fixture
def store(tmp_path):
    """A path for the bests file that never touches the real one."""
    return str(tmp_path / "best_results.json")


def trial(time, completed=True):
    return {
        "mode": MODE_TIME_TRIAL,
        "seed": 42,
        "score": 500,
        "time": time,
        "asteroids": 25,
        "completed": completed,
    }


def classic(score):
    return {
        "mode": MODE_CLASSIC,
        "seed": None,
        "score": score,
        "time": 60.0,
        "asteroids": 10,
        "completed": False,
    }


class TestRecord:
    def test_the_first_result_for_a_seed_is_always_a_best(self, store):
        improved, previous = bestresults.record(MODE_TIME_TRIAL, 42, trial(30.0), store)
        assert improved
        assert previous is None

    def test_a_faster_trial_replaces_the_stored_one(self, store):
        bestresults.record(MODE_TIME_TRIAL, 42, trial(30.0), store)
        improved, previous = bestresults.record(MODE_TIME_TRIAL, 42, trial(25.0), store)
        assert improved
        assert previous["time"] == 30.0
        assert bestresults.best_for(bestresults.load(store), MODE_TIME_TRIAL, 42)["time"] == 25.0

    def test_a_slower_trial_is_not_saved(self, store):
        bestresults.record(MODE_TIME_TRIAL, 42, trial(25.0), store)
        improved, _ = bestresults.record(MODE_TIME_TRIAL, 42, trial(40.0), store)
        assert not improved
        assert bestresults.best_for(bestresults.load(store), MODE_TIME_TRIAL, 42)["time"] == 25.0

    def test_an_unfinished_trial_never_counts_however_fast(self, store):
        improved, _ = bestresults.record(MODE_TIME_TRIAL, 42, trial(1.0, completed=False), store)
        assert not improved
        assert bestresults.load(store) == {}

    def test_classic_runs_are_ranked_by_score(self, store):
        bestresults.record(MODE_CLASSIC, None, classic(1000), store)
        assert not bestresults.record(MODE_CLASSIC, None, classic(900), store)[0]
        assert bestresults.record(MODE_CLASSIC, None, classic(1100), store)[0]

    def test_each_seed_keeps_its_own_best(self, store):
        bestresults.record(MODE_TIME_TRIAL, 42, trial(25.0), store)
        improved, previous = bestresults.record(MODE_TIME_TRIAL, 43, trial(90.0), store)
        assert improved
        assert previous is None

    def test_modes_do_not_share_results(self, store):
        bestresults.record(MODE_TIME_TRIAL, 42, trial(25.0), store)
        bestresults.record(MODE_CLASSIC, 42, classic(10), store)
        saved = bestresults.load(store)
        assert set(saved) == {MODE_TIME_TRIAL, MODE_CLASSIC}


class TestLoad:
    def test_a_missing_file_means_no_bests_yet(self, store):
        assert bestresults.load(store) == {}
        assert bestresults.best_for(bestresults.load(store), MODE_CLASSIC, None) is None

    def test_a_damaged_file_is_ignored_rather_than_crashing(self, store):
        with open(store, "w") as f:
            f.write("{not json")
        assert bestresults.load(store) == {}

    def test_saved_results_are_plain_readable_json(self, store):
        bestresults.record(MODE_TIME_TRIAL, 42, trial(25.0), store)
        with open(store) as f:
            assert json.load(f)[MODE_TIME_TRIAL]["42"]["time"] == 25.0


def test_unseeded_runs_share_one_bucket():
    assert bestresults.seed_key(None) == "random"
    assert bestresults.seed_key(42) == "42"
