from pymouse import PyMouse
from pykeyboard import PyKeyboard
from time import sleep
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from PIL import Image
import pytesseract
import cv2
import os

from mycroft import MycroftSkill, intent_file_handler

class GoogleDuo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.call_active = False

    @intent_file_handler('call.duo.intent')
    def handle_call_duo(self, message):
        m = PyMouse()
        k = PyKeyboard()
        contacts = ["dad", "slayer", "mom"]
        name = message.data['contact'].lower()
        if name == "kevin":
            name = "slayer"

        if name in contacts:
            response = {'contact': name}
            self.speak_dialog('call.duo', data=response)
            command = "wmctrl -a \"Google Duo\""
            os.system(command)
            sleep(.5)
            m.click(420,90) # Click in the Duo text box
            sleep(0.5)
            k.tap_key('Delete',n=6,interval=0.05) # Delete existing characters
            k.type_string(name) # Type name of Duo contact
            sleep(0.2)
            k.tap_key('Return') # Hit Return to select contact
            sleep(1.5)
            m.click(470,380) # Click on Video Call button
            self.call_active = True
            sleep(7)
            m.click(467,127)
            m.move(799,479)
        else:
            response = {'contact': name}
            self.speak_dialog('nocontact.duo', data=response)

    @intent_file_handler('answer.duo.intent')
    def handle_answer_duo(self, message):
        if is_call_incoming():
            m = PyMouse()
            m.click(470,440) # Click Answer button
            self.call_active = True
        else:
            self.speak_dialog('noincoming.duo')

    @intent_file_handler('ignore.duo.intent')
    def handle_ignore_duo(self, message):
        if is_call_incoming():
            m = PyMouse()
            m.click(320,430) # Click Decline button
        else:
            self.speak_dialog('noincoming.duo')

    @intent_file_handler('end.duo.intent')
    def handle_end_duo(self, message):
        if self.call_active:
            command = "wmctrl -a \"Google Duo\""
            os.system(command)
            sleep(.25)
            m = PyMouse()
            m.click(400,440) # Click Hang Up button
            self.call_active = False
        else:
            self.speak_dialog('noactive.duo')

def create_skill():
    return GoogleDuo()

def screenshotocr(filename, x, y, w, h):
    win = Gdk.get_default_root_window()
    pb = Gdk.pixbuf_get_from_window(win, x, y, w, h)

    if (pb != None):
        pb.savev(filename,"png", (), ())
        # load the example image and convert it to grayscale
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # write the grayscale image to disk as a temporary file so we can
        # apply OCR to it
        filename = "/tmp/{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)

        # load the image as a PIL/Pillow image, apply OCR, and then delete
        # the temporary file
        text = pytesseract.image_to_string(Image.open(filename))
        return text

def is_call_incoming():
    command = "wmctrl -a \"Google Duo\""
    os.system(command)
    sleep(.25)
#    return True
    k = screenshotocr("/tmp/screenshot.png", 280, 95, 250, 50)

    if(k == "Duo video call" or k == "Duo voice call"):
        b = screenshotocr("/tmp/screenshot1.png", 280, 130, 150, 75)
        return True
        #check if caller is valid contact
        #if b.lower() in contacts:
        #    return True
        #else:
        #    return True
    else:
        return False
