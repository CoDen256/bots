import PySimpleGUI as sg
import os.path
from utils import *
from player import Player



# --------------------------------- Define Layout ---------------------------------
def btn(name):  # a PySimpleGUI "User Defined Element" (see docs)
    return sg.Button(name, size=(6, 1), pad=(1, 1))
# First the window layout...2 columns

left_col = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))]]

# For now will only show the name of the file that was chosen
images_col = [[sg.Text('You choose from the list:')],
              [sg.Text(size=(40,1), key='-TOUT-')],
              [sg.Image(key='-IMAGE-', size=(300, 170))],
              [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')]]

# ----- Full layout -----
layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),sg.Column(images_col, element_justification='c')]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('Multiple Format Image Viewer', layout,finalize=True, resizable=True)


player = Player(window['-IMAGE-'].Widget.winfo_id())



class LambdaHandler:
    def __init__(self, handle, handlable) -> None:
        self.handle = handle
        self.handlable = handlable
    def handle(self, event, values):
        self.handle(event, values)
    def can_handle(self, event):
        return self.handlable(event)
        
class EventHandler(LambdaHandler):
    def __init__(self, handle, *events) -> None:
        super().__init__(handle, lambda evt: evt in events)

class Window:
    def __init__(self, window) -> None:
        self.running = True
        self.window = window
        self.handlers = \
            [
                EventHandler(self.destroy, sg.WIN_CLOSED, 'Exit'),
                LambdaHandler(, sg.WIN_CLOSED, 'Exit')
                Handler(player.stop, sg.WIN_CLOSED, 'Exit')
                Handler(self.destroy, sg.WIN_CLOSED, 'Exit')
                Handler(self.destroy, sg.WIN_CLOSED, 'Exit')
                Handler(self.destroy, sg.WIN_CLOSED, 'Exit')
                Handler(self.destroy, sg.WIN_CLOSED, 'Exit')
            ]
        
    def run(self):
        while self.running:
            event, values = window.read()
            for handler in self.handlers:
                if handler.can_handle(event):
                    handler.handle(event, values)

    def destroy(self, evt, values):
        self.running = False

    def player_method(self, evt, values):
        getattr(player, evt)()
# ----- Run the Event Loop -----
# --------------------------------- Event Loop ---------------------------------
while True:
    event, values = window.read()
    if player.playing(): getattr(player, event)() # ooooh fuck its dirty
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp", ".mp4"))]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)

            if filename.lower().endswith(".mp4"):
                player.pause()
                player.stop()
                window['-IMAGE-'].update(data=None)
                player.add(filename)
                player.play()
            else:
                new_size = int(values['-W-']), int(values['-H-']) if values['-W-'] and values['-H-'] else 500, 500
                window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
                player.stop()
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename

        
# --------------------------------- Close & Exit ---------------------------------
window.close()
