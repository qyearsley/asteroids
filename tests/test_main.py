"""Tests for the parts of `main` that don't need a window: arguments, run summaries, screen text.

The frame loop, key handling and drawing are deliberately left out -- they need
an initialized display.
"""

import pytest

from constants import MODE_CLASSIC, MODE_TIME_TRIAL, TIME_TRIAL_TARGET_ASTEROIDS
import main


class TestParseArgs:
    def test_defaults_to_classic_with_no_seed(self):
        args = main.parse_args([])
        assert args.mode == MODE_CLASSIC
        assert args.seed is None

    def test_reads_the_mode_and_seed(self):
        args = main.parse_args(["--mode", MODE_TIME_TRIAL, "--seed", "1234"])
        assert args.mode == MODE_TIME_TRIAL
        assert args.seed == 1234

    def test_rejects_an_unknown_mode(self):
        with pytest.raises(SystemExit):
            main.parse_args(["--mode", "hyperspace"])


class TestMakeResult:
    def test_a_trial_that_hits_the_target_is_complete(self):
        result = main.make_result(MODE_TIME_TRIAL, 42, 500, TIME_TRIAL_TARGET_ASTEROIDS, 31.416)
        assert result["completed"]
        assert result["time"] == 31.42  # Rounded to hundredths for storage.
        assert result["seed"] == 42

    def test_a_trial_cut_short_is_not_complete(self):
        result = main.make_result(MODE_TIME_TRIAL, 42, 500, TIME_TRIAL_TARGET_ASTEROIDS - 1, 31.4)
        assert not result["completed"]

    def test_a_classic_run_is_never_marked_complete(self):
        result = main.make_result(MODE_CLASSIC, None, 500, 999, 31.4)
        assert not result["completed"]


class TestFormatTime:
    @pytest.mark.parametrize(
        "seconds,expected",
        [(0, "0:00.00"), (9.5, "0:09.50"), (61.25, "1:01.25"), (600, "10:00.00")],
    )
    def test_reads_as_minutes_and_seconds(self, seconds, expected):
        assert main.format_time(seconds) == expected


class TestResultLines:
    def finished_trial(self):
        return main.make_result(MODE_TIME_TRIAL, 42, 500, TIME_TRIAL_TARGET_ASTEROIDS, 30.0)

    def test_a_finished_trial_reports_its_time_score_and_seed(self):
        text = " ".join(main.result_lines(self.finished_trial(), None, improved=False))
        assert "0:30.00" in text
        assert "Score: 500" in text
        assert "Seed: 42" in text

    def test_a_record_says_so(self):
        text = " ".join(main.result_lines(self.finished_trial(), None, improved=True))
        assert "New best!" in text

    def test_otherwise_it_shows_the_time_to_beat(self):
        best = main.make_result(MODE_TIME_TRIAL, 42, 700, TIME_TRIAL_TARGET_ASTEROIDS, 25.0)
        text = " ".join(main.result_lines(self.finished_trial(), best, improved=False))
        assert "0:25.00" in text

    def test_an_unfinished_trial_says_how_far_you_got(self):
        result = main.make_result(MODE_TIME_TRIAL, 42, 100, 4, 12.0)
        text = " ".join(main.result_lines(result, None, improved=False))
        assert f"4 of {TIME_TRIAL_TARGET_ASTEROIDS}" in text

    def test_a_classic_run_reports_game_over_and_the_score(self):
        result = main.make_result(MODE_CLASSIC, None, 320, 8, 45.0)
        text = " ".join(main.result_lines(result, None, improved=False))
        assert "Game over" in text
        assert "Score: 320" in text
        assert "Seed" not in text  # Unseeded classic runs have nothing to replay.


class TestTitleLines:
    def test_a_trial_explains_the_objective_and_shows_the_seed(self):
        text = " ".join(main.title_lines(MODE_TIME_TRIAL, 42, None))
        assert str(TIME_TRIAL_TARGET_ASTEROIDS) in text
        assert "Seed: 42" in text

    def test_a_stored_best_is_shown_before_you_start(self):
        best = main.make_result(MODE_TIME_TRIAL, 42, 500, TIME_TRIAL_TARGET_ASTEROIDS, 30.0)
        text = " ".join(main.title_lines(MODE_TIME_TRIAL, 42, best))
        assert "0:30.00" in text
