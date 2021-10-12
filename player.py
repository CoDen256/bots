import vlc

class Player:

    def __init__(self, window_id) -> None:
        self.instance = vlc.Instance()
        self.player = self.instance.media_list_player_new()

        self.list = self.instance.media_list_new([])
        self.player.set_media_list(self.list)

        self.player.get_media_player().set_xwindow(window_id)
        self.is_playing = False


    def play(self):
        self.player.play()
        self.is_playing = True
    def pause(self):
        self.player.pause()
    def stop(self):
        self.stop()
        self.is_playing = True

    def playing(self):
        return self.is_playing

    def add(self, file):
        self.list.add_media(file)
        self.player.set_media_list(self.list)