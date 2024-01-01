import logging
import subprocess
from typing import Optional


class PlayingState:
    inactive = 0
    active = 1


class ProfileBase:
    def __init__(self):
        raise NotImplementedError()

    def on_start_playing(self):
        """
        Callback called on the transition from 'not playing' to 'playing'
        """
        raise NotImplementedError()

    def on_stop_playing(self):
        """
        Callback called on the transition from 'playing' to 'not playing'
        """
        raise NotImplementedError()

    def on_playing_tick(self):
        """
        Callback called every 5 'playing' updates
        """
        raise NotImplementedError()

    def on_stopped_delayed(self):
        """
        Callback called once, 10 updates after the transition from 'playing' to 'not playing'
        """
        raise NotImplementedError()

    def _set_timeout(self, timeout):
        self._run_xset(str(timeout))

    def _run_xset(self, s_arg):
        cmd = ['xset', 's', s_arg]
        logging.debug(cmd)
        subprocess.run(cmd, check=False)  # Although it's not ideal if it fails, raising an Exception won't help

    def _blank_screen_now(self):
        self._run_xset('activate')


class ScreenBlankProfileNone(ProfileBase):
    def __init__(self):
        "Do nothing except prevent the NotImplementedError"

    def on_start_playing(self):
        "Do nothing except prevent the NotImplementedError"

    def on_stop_playing(self):
        "Do nothing except prevent the NotImplementedError"

    def on_playing_tick(self):
        "Do nothing except prevent the NotImplementedError"

    def on_stopped_delayed(self):
        "Do nothing except prevent the NotImplementedError"


class ScreenBlankProfileBalanced(ProfileBase):
    def __init__(self):
        "Do nothing except prevent the NotImplementedError"

    def on_start_playing(self):
        self._set_timeout(300)

    def on_stop_playing(self):
        self._set_timeout(30)

    def on_playing_tick(self):
        "Do nothing except prevent the NotImplementedError"

    def on_stopped_delayed(self):
        self._blank_screen_now()


class ScreenBlankProfileOnWhenPlaying(ProfileBase):
    def __init__(self):
        "Do nothing except prevent the NotImplementedError"

    def on_start_playing(self):
        self._set_timeout(60 * 60)

    def on_stop_playing(self):
        self._run_xset('on')
        self._set_timeout(10)

    def on_playing_tick(self):
        self._run_xset('off')
        self._run_xset('reset')

    def on_stopped_delayed(self):
        self._blank_screen_now()


class ScreenBlankMgr:
    def __init__(self, profile: ProfileBase):
        self.state: Optional[int] = None
        self.profile = profile
        self.tick_countdown = 5

    def set_state(self, new_state_str: str):
        """
        new_state in ('playing', 'paused', 'stopped')
        """
        new_state = PlayingState.active if (new_state_str == 'playing') else PlayingState.inactive
        if self.state == new_state:
            self.tick_countdown -= 1
            if self.state == PlayingState.active:
                if self.tick_countdown <= 0:
                    self.profile.on_playing_tick()
                    self.tick_countdown = 5
            else:
                if self.tick_countdown == 0:
                    self.profile.on_stopped_delayed()
        else:
            self.state = new_state
            if self.state == PlayingState.active:
                self.profile.on_start_playing()
                self.tick_countdown = 5
            else:
                self.profile.on_stop_playing()
                self.tick_countdown = 10


profiles = {
    'none': ScreenBlankProfileNone(),
    'balanced': ScreenBlankProfileBalanced(),
    'onoff': ScreenBlankProfileOnWhenPlaying()
}
