import os
import re
import subprocess

from utilities.cli import HiddenPrints
from utilities.GeneralUtilities import IS_MACOS, IS_WIN

try:
    from gtts import gTTS
    from pydub import AudioSegment, playback
    # patch pydup - hide std output
    FNULL = open(os.devnull, 'w')
    _subprocess_call = playback.subprocess.call
    playback.subprocess.call = lambda cmd: _subprocess_call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)

    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


if IS_MACOS:
    from os import system
else:
    try:
        import pyttsx3
        HAS_PYTTSX3 = True
    except ImportError:
        HAS_PYTTSX3 = False


def remove_ansi_escape_seq(text):
    """
    This method removes ANSI escape sequences (such as a colorama color
    code) from a string so that they aren't spoken.
    :param text: The text that may contain ANSI escape sequences.
    :return: The text with ANSI escape sequences removed.
    """
    if text:
        text = re.sub(r'''(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]''', '', text)
    return text


class JarvisVoice:
    QUAITY = 1

    def __init__(self, jarvis):
        self.jarvis = jarvis
        self.speech_rate = self.jarvis.get_data('speech_rate')

        if not self.speech_rate:
            self.speech_rate = 120

    def get_name():
        return 'Jarvis voice'

    def start(self):
        ggts_status = self.jarvis.get_data('gtts_status')
        self.backend = create_voice(self, ggts_status, rate=self.speech_rate)

    def stop(self):
        self.backend.destroy()

    def say(self, text, color=''):
        if len(text) == 0:
            return
        self.backend.text_to_speech(text)

    def show_prompt(self):
        self.say('What can I do for you?')

    def input(self, *args):
        # VOICE CANNOT INPUT ANYTHING
        pass

    def change_speech_rate(self, delta):
        self.speech_rate += delta
        self.backend.change_rate(delta)


def create_voice(self, gtts_status, rate=180):
    """
    Checks that status of gtts engine, and calls the correct speech engine
    :param rate: Speech rate for the engine (if supported by the OS)
    """

    if HAS_GTTS and gtts_status is True:
        return VoiceGTTS()
    else:
        if IS_MACOS:
            return VoiceMac()
        elif IS_WIN:
            return VoiceWin(rate)
        else:
            try:
                return VoiceLinux(rate)
            except OSError:
                return VoiceNotSupported()


class Voice:
    def change_rate(self, delta):
        print('Speech rate change not implemented')

    def destroy(self):
        pass


class VoiceGTTS(Voice):
    def text_to_speech(self, speech):
        with HiddenPrints():
            speech = remove_ansi_escape_seq(speech)
            tts = gTTS(speech, lang="en")
            tts.save("voice.mp3")
            audio = AudioSegment.from_mp3('voice.mp3')
            playback.play(audio)
            os.remove("voice.mp3")


class VoiceMac(Voice):
    def text_to_speech(self, speech):
        speech = remove_ansi_escape_seq(speech)
        speech = speech.replace("'", "\\'")
        system('say $\'{}\''.format(speech))


class VoiceLinux(Voice):
    """
     ABOUT: This class is the Voice of Jarvis.
         The methods included in this class
         generate audio output of Jarvis while
         interacting with the user.
     DOCUMENTATION on pyttsx3:
         https://pyttsx3.readthedocs.io/en/latest/
    """

    def __init__(self, rate):
        self.rate = rate
        self.min_rate = 50
        self.max_rate = 500
        self.create()

    def create(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.rate)

    def destroy(self):
        """
        Destroys a pyttsx3 object in order
        to create a new one in the next interaction.
        """
        del self.engine

    def text_to_speech(self, speech):
        """
        :param speech: The text we want Jarvis to generate as audio
        :return: Nothing to return.
        A bug in pyttsx3 causes segfault if speech is '', so used 'if' to avoid that.
        Instability in the pyttsx3 engine can cause problems if the engine is
        not created and destroyed every time it is used.
        """
        if speech != '':
            speech = remove_ansi_escape_seq(speech)
            with HiddenPrints():
                self.create()
                self.engine.say(speech)
                self.engine.runAndWait()
                self.destroy()

    def change_rate(self, delta):
        """
        Changes the speech rate which is used to set the speech
        engine rate. Restrict the rate to a usable range.
        :param delta: The amount to modify the rate from the current rate.
        Note: The actual engine rate is set by create().
        """
        if self.rate + delta > self.max_rate:
            self.rate = self.max_rate
        elif self.rate + delta < self.min_rate:
            self.rate = self.min_rate
        else:
            self.rate = self.rate + delta


class VoiceWin(Voice):
    def __init__(self, rate):
        self.rate = rate
        self.min_rate = 50
        self.max_rate = 500
        self.create()

    def create(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.rate)

    def destroy(self):
        """
        This method destroys a pyttsx3 object in order
        to create a new one in the next interaction.
        :return: Nothing to return.
        """
        del self.engine

    def text_to_speech(self, speech):
        """
        This method converts a text to speech.
        :param speech: The text we want Jarvis to generate as audio
        :return: Nothing to return.

        Instability in the pyttsx3 engine can cause problems if the engine is
        not created and destroyed every time it is used.
        """
        speech = remove_ansi_escape_seq(speech)
        self.create()
        self.engine.setProperty('rate', 170)  # setting up new voice rate
        voices = self.engine.getProperty('voices')  # getting details of current voice
        self.engine.setProperty('voices', voices[1].id)  # changing index, changes voices. 1 for female
        self.engine.say(speech)
        self.engine.runAndWait()
        self.destroy()

    def change_rate(self, delta):
        """
        This method changes the speech rate which is used to set the speech
        engine rate. Restrict the rate to a usable range.
        :param delta: The amount to modify the rate from the current rate.

        Note: The actual engine rate is set by create().
        """
        if self.rate + delta > self.max_rate:
            self.rate = self.max_rate
        elif self.rate + delta < self.min_rate:
            self.rate = self.min_rate
        else:
            self.rate = self.rate + delta


class VoiceNotSupported(Voice):
    def __init__(self):
        self.warning_print = False

    def text_to_speech(self, speech):
        if not self.warning_print:
            print(
                "Speech not supported! Please install pyttsx3 text-to-speech engine (sapi5, nsss or espeak)")
            self.warning_print = True
