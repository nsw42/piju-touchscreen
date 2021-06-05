import logging
import subprocess


class PlayingState:
    Inactive = 0
    Active = 1


class ProfileBase:
    def __init__(self):
        raise NotImplementedError()

    def on_start_playing(self):
        raise NotImplementedError()

    def on_stop_playing(self):
        raise NotImplementedError()

    def on_playing_tick(self):
        raise NotImplementedError()

    def _set_timeout(self, timeout):
        self._run_xset(str(timeout))

    def _run_xset(self, s_arg):
        cmd = ['xset', 's', s_arg]
        logging.debug(cmd)
        subprocess.run(cmd)


class ScreenBlankProfileNone(ProfileBase):
    def __init__(self):
        pass

    def on_start_playing(self):
        pass

    def on_stop_playing(self):
        pass

    def on_playing_tick(self):
        pass


class ScreenBlankProfileBalanced(ProfileBase):
    def __init__(self):
        pass

    def on_start_playing(self):
        self._set_timeout(self, 300)

    def on_stop_playing(self):
        self._set_timeout(self, 30)

    def on_playing_tick(self):
        pass


class ScreenBlankProfileOnWhenPlaying(ProfileBase):
    def __init__(self):
        pass

    def on_start_playing(self):
        self._set_timeout(60 * 60)

    def on_stop_playing(self):
        self._run_xset('on')
        self._set_timeout(10)

    def on_playing_tick(self):
        self._run_xset('off')
        self._run_xset('reset')


class ScreenBlankMgr:
    def __init__(self, profile: ProfileBase):
        self.state = None
        self.profile = profile
        self.tick_countdown = 5

    def set_state(self, new_state: str):
        """
        new_state in ('playing', 'paused', 'stopped')
        """
        new_state = PlayingState.Active if (new_state == 'playing') else PlayingState.Inactive
        if self.state == new_state:
            if self.state == PlayingState.Active:
                self.tick_countdown -= 1
                if self.tick_countdown <= 0:
                    self.profile.on_playing_tick()
                    self.tick_countdown = 5
        else:
            self.state = new_state
            if self.state == PlayingState.Active:
                self.profile.on_start_playing()
            else:
                self.profile.on_stop_playing()


profiles = {
    'none': ScreenBlankProfileNone(),
    'balanced': ScreenBlankProfileBalanced(),
    'onoff': ScreenBlankProfileOnWhenPlaying()
}
