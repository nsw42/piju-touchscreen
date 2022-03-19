import unittest
from unittest.mock import patch, call

from screenblankmgr import ScreenBlankMgr, ScreenBlankProfileNone, PlayingState


class TestSetState(unittest.TestCase):
    def test_playing_sets_active(self):
        with patch.object(ScreenBlankProfileNone, 'on_start_playing') as mock_on_start_playing:
            profile = ScreenBlankProfileNone()
            mgr = ScreenBlankMgr(profile=profile)
            self.assertEqual(mgr.state, None)
            mgr.set_state('playing')
            self.assertEqual(mgr.state, PlayingState.active)
            mock_on_start_playing.assert_called_once()

    def test_paused_sets_inactive(self):
        with patch.object(ScreenBlankProfileNone, 'on_stop_playing') as mock_on_stop_playing:
            profile = ScreenBlankProfileNone()
            mgr = ScreenBlankMgr(profile=profile)
            self.assertEqual(mgr.state, None)
            mgr.set_state('paused')
            self.assertEqual(mgr.state, PlayingState.inactive)
            mock_on_stop_playing.assert_called_once()

    def test_stopped_sets_inactive(self):
        with patch.object(ScreenBlankProfileNone, 'on_stop_playing') as mock_on_stop_playing:
            profile = ScreenBlankProfileNone()
            mgr = ScreenBlankMgr(profile=profile)
            self.assertEqual(mgr.state, None)
            mgr.set_state('stopped')
            self.assertEqual(mgr.state, PlayingState.inactive)
            mock_on_stop_playing.assert_called_once()

    def test_five_active_calls_tick(self):
        with patch.object(ScreenBlankProfileNone, 'on_playing_tick') as mock_on_playing_tick:
            profile = ScreenBlankProfileNone()
            mgr = ScreenBlankMgr(profile=profile)
            mgr.set_state('playing')  # set the baseline for playing state active
            mgr.set_state('playing')
            mgr.set_state('playing')
            mgr.set_state('playing')
            mgr.set_state('playing')
            mock_on_playing_tick.assert_not_called()
            mgr.set_state('playing')
            mock_on_playing_tick.assert_called_once()

            mgr.set_state('playing')
            mgr.set_state('playing')
            mgr.set_state('playing')
            mgr.set_state('playing')
            mock_on_playing_tick.assert_called_once()
            mgr.set_state('playing')
            calls = [call(), call()]
            mock_on_playing_tick.assert_has_calls(calls)
