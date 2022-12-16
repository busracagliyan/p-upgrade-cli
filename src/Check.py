import os
import shutil
import distro
import requests
from pathlib import Path

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
            print("Sürümünüz güncel -> Pardus 21")
            return False
        elif self.codename == codename_ondokuz:
            print("Yeni bir sürüm mevcut -> Pardus 21'e yükseltilebilir.")
            return True
        elif self.codename == codename_onyedi:
            print("Yeni bir sürüm mevcut -> Pardus 19'a yükseltilebilir.")
            return True

    def check_sourceslist(self):
        with open("/etc/apt/sources.list", "r") as file:
            sourceslist = file.read()
        for line in sourceslist.split("\n"):
            if line.startswith("deb http://"):
                if "depo.pardus.org.tr/pardus" in line:
                    return True
                else:
                    return False

    def checkcorrectsourceslist(self):
        with open("/etc/apt/sources.list", "r") as file:
            sourceslist = file.read()

        source = ""
        for line in sourceslist.split("\n"):
            if "depo.pardus.org.tr" in line:
                if "onyedi" in line:
                    line = line.replace("onyedi", "ondokuz")
                if "ondokuz" in line:
                    line = line.replace("ondokuz", "yirmibir")
                """if "yirmibir" in line:
                    line = line.replace("yirmibir", "yirmiuc")"""
                source += line + "\n"
            else:
                source += line + "\n"

        tmpfile = "/etc/apt/sources.list.d/tmp/"
        if os.path.exists("/etc/apt/sources.list.d/*"):
            shutil.copy("/etc/apt/sources.list.d/",tmpfile, follow_symlinks=True)
        shutil.rmtree("/etc/apt/sources.list.d", ignore_errors=True)
        shutil.rmtree("/var/lib/apt/lists/", ignore_errors=True)
        Path("/etc/apt/sources.list.d").mkdir(parents=True, exist_ok=True)
        sfile = open("/etc/apt/sources.list", "w")
        sfile.write(source)
        sfile.flush()
        sfile.close()
