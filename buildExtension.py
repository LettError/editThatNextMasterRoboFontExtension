# build RF extension
# run in RF
import os
from mojo.extensions import ExtensionBundle
from mojo.UI import createModifier

#modifier = createModifier(command=True, shift=True)
#print(f"({modifier}, ']')")

# get current folder
basePath = os.path.dirname(__file__)

# folder with python files
libPath = os.path.join(basePath, 'lib')

# folder with html files
htmlPath = os.path.join(basePath, 'html')
if not os.path.exists(htmlPath):
    htmlPath = None

# folder with resources
resourcesPath = os.path.join(basePath, 'resources')
if not os.path.exists(resourcesPath):
    resourcesPath = None
    
# load license text from file
# see http://choosealicense.com/ for more open-source licenses
licensePath = os.path.join(basePath, 'license.txt')
if not os.path.exists(licensePath):
    licensePath = None
    
# boolean indicating if only .pyc should be included
pycOnly = False

# name of the compiled extension file
extensionFile = 'EditThatNextMaster.roboFontExt'

# path of the compiled extension
buildPath = basePath
extensionPath = os.path.join(buildPath, extensionFile)

# initiate the extension builder
B = ExtensionBundle()

# name of the extension
B.name = "EditThatNextMaster"

# name of the developer
B.developer = 'LettError'

# URL of the developer
B.developerURL = 'http://letterror.com/tools.html'

if resourcesPath:
    # extension icon (file path or NSImage)
    imagePath = os.path.join(resourcesPath, 'icon.png')
    B.icon = imagePath

# version of the extension
B.version = '1.5.1'

# should the extension be launched at start-up?
B.launchAtStartUp = True

# script to be executed when RF starts
B.mainScript = 'startup.py'

# does the extension contain html help files?
B.html = htmlPath is not None

# minimum RoboFont version required for this extension
B.requiresVersionMajor = '4'
B.requiresVersionMinor = '3'

# scripts which should appear in Extensions menu
B.addToMenu = [
    {
        'path' : 'editThatNext_sameWindow.py',
        'preferredName': '⏩ Next',
        'shortKey' : '',
        #'shortKey' : (1179648, ']'),
    },
    {
        'path' : 'editThatNext_newWindow.py',
        'preferredName': '⏩ Next, New Window…',
        'shortKey' : '',
        #'shortKey' : (1179648, ']'),
    },
    {
        'path' : 'editThatPrevious_sameWindow.py',
        'preferredName': '⏪ Previous',
        'shortKey' : '',
        #'shortKey' : (1179648, '['),
    },
    {
        'path' : 'editThatPrevious_newWindow.py',
        'preferredName': '⏪ Previous, New Window…',
        'shortKey' : '',
        #'shortKey' : (1179648, '['),
    },
    {
        'path' : 'editShuffle.py',
        'preferredName': '⏪ Shuffle',
        'shortKey' : '',
    },
]

if licensePath:
    # license for the extension
    with open(licensePath) as license:
        B.license = license.read()

# compile and save the extension bundle
print('building extension...', end=' ')
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=pycOnly)
print('done!')

# check for problems in the compiled extension
print()
print(B.validationErrors())
