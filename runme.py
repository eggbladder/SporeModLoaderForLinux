from zipfile import ZipFile as zf
import os
import shutil

try:
    import config
except:
    print("config not found.. making new config file. Restart the program")
global cwd
cwd = os.getcwd()

try:
    configfile = os.open(cwd + "/config.py", flags=os.O_RDONLY)
except:
    newconfig = open(cwd + "/config.py", "x")
    newconfig.write(
        'sporedirectory = "" # Put the directory to your Spore folder here. example = "/home/user/.steam/steam/steamapps/common/Spore/"')
    newconfig.close()
    exit()
else:
    print("config found...")


def sendFile(filetuple, mod):
    thinezip = zf(cwd + "/install/" + os.path.splitext(mod)[0] + ".zip", mode='r')

    if filetuple[0] == "Spore":
        thinezip.extract(filetuple[1], config.sporedirectory + "/Data/")
        thinezip.extract(filetuple[1], config.sporedirectory + "/DataEP1/")
    elif filetuple[0] == "GalacticAdventures":
        thinezip.extract(filetuple[1], config.sporedirectory + "/Data/")
        thinezip.extract(filetuple[1], config.sporedirectory + "/DataEP1/")
    elif filetuple[0] == "ModLibs":
        thinezip.extract(filetuple[1], config.sporedirectory + "/SporeModLoader/ModLibs/")


def parseLine(line, find):
    return line.partition(find + '="')[2].partition('"')[0]


def getFile(line):
    if "game=" in line:
        return parseLine(line, "game"), line.rpartition(">")[0].rpartition(">")[2].partition("<")[0]
    else:
        if ".dll" in line or ".package" in line:

            return "ModLibs", line.rpartition(">")[0].rpartition(">")[2].partition("<")[0]
        else:
            return None, None


def uninstallMods():
    mods = os.listdir(cwd + "/uninstall")
    sporebin = os.listdir(config.sporedirectory + "/Data/")
    gabin = os.listdir(config.sporedirectory + "/DataEP1/")
    modlibs = os.listdir(config.sporedirectory + "/SporeModLoader/ModLibs/")
    for mod in mods:
        if os.path.splitext(mod)[1] == ".package":
            if mod in sporebin:
                os.remove(config.sporedirectory + "/Data/" + mod)
                shutil.move(cwd + "/uninstall/" + mod, cwd + "/uninstalled/" + mod)
        elif os.path.splitext(mod)[1] == ".sporemod" or os.path.splitext(mod)[1] == ".zip":
            if os.path.splitext(mod)[1] == ".sporemod":
                os.rename(cwd + "/uninstall/" + mod, cwd + "/uninstall/" + os.path.splitext(mod)[0] + ".zip")
            thinezip = zf(cwd + "/uninstall/" + os.path.splitext(mod)[0] + ".zip", mode='r')
            try:
                xmlf = thinezip.read("ModInfo.xml").decode().split("\n")
            except:
                pass
            else:
                for line in xmlf:
                    try:
                        filetodel = getFile(line)[1]
                        print(filetodel)
                        if filetodel in sporebin:
                            os.remove(config.sporedirectory + "/Data/" + filetodel)
                        if filetodel in gabin:
                            os.remove(config.sporedirectory + "/DataEP1/" + filetodel)
                        if filetodel in modlibs:
                            os.remove(config.sporedirectory + "/SporeModLoader/ModLibs/" + filetodel)

                    except Exception as error:
                        print(error)
                try:
                    os.rename(cwd + "/uninstall/" + os.path.splitext(mod)[0] + ".zip", cwd + "/uninstall/" + os.path.splitext(mod)[0] + ".sporemod")
                except:
                    pass
                shutil.move(cwd + "/uninstall/" + mod, cwd + "/uninstalled/" + mod)


def installMod(mod):
    downloadlist = []
    if os.path.splitext(mod)[1] == ".package":
        shutil.copy(cwd + "/install/" + mod, config.sporedirectory + "/Data/")
        shutil.copy(cwd + "/install/" + mod, config.sporedirectory + "/DataEP1/")
        shutil.move(cwd + "/install/" + mod, cwd + "/installed/" + mod)
    elif os.path.splitext(mod)[1] == ".sporemod" or os.path.splitext(mod)[1] == ".zip":
        try:
            os.rename(cwd + "/install/" + mod, cwd + "/install/" + os.path.splitext(mod)[0] + ".zip")
        except:
            pass
        thinezip = zf(cwd + "/install/" + os.path.splitext(mod)[0] + ".zip", mode='r')
        print("mod found")
        try:
            xmlf = thinezip.read("ModInfo.xml").decode().split("\n")
        except:
            pass
        else:
            for line in xmlf:
                if line.startswith("<mod"):
                    displayName = parseLine(line, "displayName")
                    print("installing " + displayName + "...")
                if line.startswith("	<componentGroup"):
                    displayName = parseLine(line, "displayName")
                    print(displayName + ", you may choose one.")
                    getoptions = False
                    option = 0
                    options = []
                    stopfornow = 0
                    for optionline in xmlf:
                        if xmlf.index(line) + 1 < xmlf.index(optionline) + 1 and stopfornow == 0:

                            if optionline.startswith("		<component"):
                                option = option + 1
                                options.append(getFile(optionline))
                                print(str(option) + " - " + parseLine(optionline, "displayName"))

                            if optionline.startswith("	</componentGroup>"):
                                xmlf.insert(xmlf.index(optionline), "please")
                                xmlf.pop(xmlf.index(optionline))
                                optiontoget = options[(int(input("what you want?: ")) - 1)]
                                downloadlist.append(optiontoget)
                                stopfornow = 1
                if line.startswith("	<component") and not line.startswith("	<componentGroup"):
                    getFile(line)
                    displayName = parseLine(line, "displayName")
                    desc = parseLine(line, "description")
                    print(displayName)
                    print(desc)
                    answer = input("Do you want " + displayName + "? Y/N/y/n/Yes/No/yes/no: ")
                    if answer == "Y" or answer == "yes" or answer == "Yes" or answer == "y":
                        print("Added. \n")
                        downloadlist.append(getFile(line))
                    else:
                        print("Not added. \n")
                if line.startswith("	<prerequisite"):
                    downloadlist.append(getFile(line))
            for download in downloadlist:
                print("installing " + download[1])
                sendFile(download, mod)
            try:
                os.rename(cwd + "/install/" + os.path.splitext(mod)[0] + ".zip",
                          cwd + "/install/" + os.path.splitext(mod)[0] + ".sporemod")
            except:
                pass
            shutil.move(cwd + "/install/" + mod, cwd + "/installed/" + mod)


def viewMods(mode="new"):
    returnlist = []
    mods = os.listdir(cwd + "/install")
    for mod in mods:
        modext = os.path.splitext(mod)[1]
        if modext == ".sporemod" or modext == ".package" or modext == ".zip":
            returnlist.append(mod)
    return returnlist


# modlist = open(cwd+"/config.py", 'r')
#            oldwrite = modlist.readlines()[0].replace("[", "['" + str(mod) + "',")
#            modlist.close()
#            modlist = open(cwd+"/config.py", 'w')
#            modlist.writelines(oldwrite)
#            modlist.close()
uninstallMods()
for mod in viewMods():
    installMod(mod)
