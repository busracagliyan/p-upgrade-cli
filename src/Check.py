import distro
import requests
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

class Check(object):
    def __init__(self):
        self.codename = distro.codename().lower()

    def check_version(self):
        URL = "http://depo.pardus.org.tr/pardus/dists/"

        response = requests.get(URL)
        for line in response.text.split("\n"):
            if line.strip().startswith("<a href=\"ondokuz/\">"):
                codename_ondokuz = "ondokuz"
            if line.strip().startswith("<a href=\"onyedi/\">"):
                codename_onyedi = "onyedi"
            if line.strip().startswith("<a href=\"yirmibir/\">"):
                codename_yirmibir = "yirmibir"

        if self.codename == codename_yirmibir:
            #self.notify("Sürümünüz güncel", "Pardus 21")
            print("Sürümünüz güncel -> Pardus 21")
            return False
        elif self.codename == codename_ondokuz:
            #self.notify("Yeni bir sürüm mevcut","Pardus 21'e yükseltilebilir.")
            print("Yeni bir sürüm mevcut -> Pardus 21'e yükseltilebilir.")
            return True
        elif self.codename == codename_onyedi:
            #self.notify("Yeni bir sürüm mevcut","Pardus 19'a yükseltilebilir.")
            print("Yeni bir sürüm mevcut -> Pardus 19'a yükseltilebilir.")
            return True

    """def notify(self, message_title, message_text):
        Notify.init("Pardus Upgrade Notification")
        n = Notify.Notification.new(message_title, message_text)
        n.show()"""

    def check_sourceslist(self):
        with open("/etc/apt/sources.list", "r") as file:
            sourceslist = file.read()
        for line in sourceslist.split("\n"):
            if line.startswith("deb http://"):
                if "depo.pardus.org.tr/pardus" in line:
                    return True
                else:
                    return False