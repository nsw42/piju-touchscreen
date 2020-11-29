import subprocess


class PlayingState:
    Inactive = 0
    Active = 1


class ScreenBlankMgr:
    def __init__(self):
        self.state = None

    def set_state(self, new_state: str):
        """
        new_state in ('playing', 'paused', 'stopped')
        """
        new_state = PlayingState.Active if (new_state == 'playing') else PlayingState.Inactive
        if self.state == new_state:
            return
        timeout = 300 if (new_state == PlayingState.Active) else 30
        subprocess.run(['xset', 's', timeout])
