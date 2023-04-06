# menuTitle : Edit That Previous Master

import time

"""

    If you're editing masters or whatever
    and you want to switch to the same glyph in the other master
    and you spend a lot of time moving glyph windows around
    or you've had to divide your massive pixel real estate into small lots.

    Add this script to RF and wire it to a key command
    and then woosh woosh woosh cycle between the masters.
    The other script, "editThatNextMaster.py" wooshes the other direction.

    The order in which these scripts woosh through the fonts: alphabetically sorted filepath.

    With massive help from @typemytype
    @letterror
    
    20190523

"""

import AppKit
import random
from mojo.UI import *
from mojo.roboFont import CurrentFont, CurrentGlyph, AllFonts, OpenWindow, version
from mojo.events import addObserver, removeObserver, publishEvent

try:
    from mm4.menubar import SharedMenubar
    from mm4.mmScripting import _getMainWindowControllerForFont, MetricsMachineScriptingError
    #mm4.mmScripting.MetricsMachineScriptingError
    #MetricsMachineScriptingError
    import mm4.mmScripting
    from metricsMachine import SetPairList, SetCurrentPair
    import metricsMachine
    hasMetricsMachine = True
except ImportError:
    hasMetricsMachine = False
    
def copySelection(g):
    pointSelection = []
    compSelection = []
    anchorSelection = []
    for ci, c in enumerate(g.contours):
        for pi, p in enumerate(c.points):
            if p.selected:
                pointSelection.append((ci, pi))
    for compi, comp in enumerate(g.components):
        if comp.selected:
            compSelection.append(compi)
    for anchori, anchor in enumerate(g.anchors):
        if anchor.selected:
            anchorSelection.append(anchori)
    return pointSelection, compSelection, anchorSelection

def applySelection(g, pointSelection, compSelection, anchorSelection):
    # reset current selected points
    for ci, c in enumerate(g.contours):
        c.selected = False
    for ci, c in enumerate(g.components):
        c.selected = False
    for ai, a in enumerate(g.anchors):
        a.selected = False
    for ci, pi in pointSelection:
        if g.contours and len(g.contours) >= ci + 1:
            if len(g.contours[ci].points) >= pi + 1:
                g.contours[ci].points[pi].selected = True
    for ci in compSelection:
        if g.components and len(g.components) >= ci + 1:
            g.components[ci].selected = True
    for ai in anchorSelection:
        if g.anchors and len(g.anchors) >= ai + 1:
            g.anchors[ai].selected = True

def getCurrentFontAndWindowFlavor():
    """ Try to find what type the current window is and which font belongs to it."""
    windows = [w for w in AppKit.NSApp().orderedWindows() if w.isVisible()]
    skip = ["PreferencesWindow", "ScriptingWindow"]
    for window in windows:
        if hasattr(window, "windowName"):
            windowName = window.windowName()
            if windowName in skip:
                continue
            if windowName == "MetricsMachineMainWindow":
                if hasattr(window, "windowName") and window.windowName() == "MetricsMachineMainWindow":
                    delegate = window.delegate()
                    mmController = delegate.vanillaWrapper()
                    return mmController.font.path, windowName
            if hasattr(window, "document"):
                obj = window.document()
                # could be an extension Help window
                if obj is not None:
                    if hasattr(obj, "font"):
                        return obj.font.path, windowName
    return None, None

def getGlyphWindowPosSize():
    w = CurrentGlyphWindow()
    if w is None:
        return
    x,y, width, height = w.window().getPosSize()
    settings = getGlyphViewDisplaySettings()
    view = w.getGlyphView()
    viewFrame = view.visibleRect()
    viewScale = w.getGlyphViewScale()
    return (x, y), (width, height), settings, viewFrame, viewScale

def setGlyphWindowPosSize(glyph, pos, size, animate=False, settings=None, viewFrame=None, viewScale=None, layerName=None):
    OpenGlyphWindow(glyph=glyph, newWindow=False)
    w = CurrentGlyphWindow()
    view = w.getGlyphView()
    w.window().setPosSize((pos[0], pos[1], size[0], size[1]), animate=animate)
    if viewScale is not None:
        w.setGlyphViewScale(viewScale)
    if viewFrame is not None:
        view.scrollRectToVisible_(viewFrame)
    if settings is not None:
        setGlyphViewDisplaySettings(settings)
    if layerName is not None:
        w.setLayer(layerName, toToolbar=True)
    
def setSpaceCenterWindowPosSize(font, targetLayer=None, forceNewWindow=False):
    if version >= "3.3" and not forceNewWindow:
        current = CurrentSpaceCenterWindow()
        current.setFont(font)
        return

    w = CurrentSpaceCenterWindow()
    g = CurrentGlyph()
    if g is not None:
        currentGlyphName = g.name
    else:
        currentGlyphName = None

    posSize = w.window().getPosSize()
    px, py, oldWidth, oldHeight = posSize
    c = w.getSpaceCenter()

    if targetLayer is None:
        targetLayer = c.getLayerName()

    rawText = c.getRaw()
    prefix = c.getPre()
    suffix = c.getAfter()
    gnameSuffix = c.getSuffix()
    size = c.getPointSize()
    
    w = OpenSpaceCenter(font, newWindow=False)
    new = CurrentSpaceCenterWindow()
    newPosSize = new.window().getPosSize()
    if posSize[2:] == newPosSize[2:] and posSize[:2] != newPosSize[:2]:
        new.window().setPosSize(newPosSize)
    else:
        new.window().setPosSize(posSize)
    w.setRaw(rawText)
    w.setPre(prefix)
    w.setAfter(suffix)
    w.setSuffix(gnameSuffix)
    w.setPointSize(size)
    if targetLayer is not None:
        w.setLayerName(targetLayer)

def getOtherMaster(nextFont=True, shuffleFont=False):
    cf = CurrentFont()
    orderedFonts = []
    fonts = {}
    for f in AllFonts():
        if f.path is None:
            continue
        fonts[f.path]=f
    sortedPaths = list(fonts.keys())
    sortedPaths.sort()
    #
    if shuffleFont:
        shufflePaths = sortedPaths[:]
        shufflePaths.remove(cf.path)
        shuffledPath = random.choice(shufflePaths)
        return fonts[shuffledPath]

    for i in range(len(sortedPaths)):
        if cf.path == fonts[sortedPaths[i]].path:
            prev = fonts[sortedPaths[i-1]]
            nxt = fonts[sortedPaths[(i+1)%len(sortedPaths)]]
            if nextFont:
                return nxt
            else:
                return prev

def focusOnMetricsMachine(font):
    try:
        controller = _getMainWindowControllerForFont(font)
        controller.w.makeKey()
    except MetricsMachineScriptingError:
        font.document().getMainWindow().show()
        menuItem = SharedMenubar().getItem("fileOpenMetricsMachine")
        menuItem.target().action_(None)
        controller = _getMainWindowControllerForFont(font)
    return controller

def switch(direction=1, shuffle=False, forceNewWindow=False):
    currentPath, windowType = getCurrentFontAndWindowFlavor()
    # maybe here
    nextMaster = None
    nextLayer = None
    currentLayerName = None
    try:
        app = AppKit.NSApp()
        if hasattr(app, "getNextSkateboardMasterCallback"):
            callback = app.getNextSkateboardMasterCallback
            if callback:
                r = callback(direction, windowType)
                if r is not None:
                    nextMaster, nextLayer = r
    except:
        print("EditNext: problem calling Skateboard")
    if nextMaster is None:
        nextMaster = getOtherMaster(direction==1, shuffle==True)
    f = CurrentFont()
    if windowType == "FontWindow":
        fontWindow = CurrentFontWindow()
        selectedGlyphs = f.selectedGlyphNames if version >= '3.2' else f.selection
        currentFontWindowQuery = fontWindow.getGlyphCollection().getQuery()
        selectedSmartList = fontWindow.fontOverview.views.smartList.getSelection()
        posSize = fontWindow.window().getPosSize()
        nextWindow = nextMaster.document().getMainWindow()
        nextSelectedGlyphs = [s for s in selectedGlyphs if s in nextMaster]
        if version >= '3.2':
            nextMaster.selectedGlyphNames = nextSelectedGlyphs
        else:
            nextMaster.selection = nextSelectedGlyphs
        nextWindow.setPosSize(posSize)
        nextWindow.show()
        # set the selected smartlist
        fontWindow = CurrentFontWindow()
        try:
            fontWindow.fontOverview.views.smartList.setSelection(selectedSmartList)
            fontWindow.getGlyphCollection().setQuery(currentFontWindowQuery)    # sorts but does not fill it in the form
        except:
            pass
    elif windowType == "SpaceCenter":
        setSpaceCenterWindowPosSize(nextMaster, nextLayer, forceNewWindow)
    elif windowType == "GlyphWindow":
        if nextMaster is None:
            switch(direction)
            return
        g = CurrentGlyph()
        selectedPoints, selectedComps, selectedAnchors = copySelection(g)
        currentMeasurements = g.naked().measurements
        if g is not None:
            # wrap possible UFO3 / fontparts objects
            if version >= "3.0":
                # RF 3.x
                if nextLayer is not None:
                    # wait nextlayer can be None
                    # if we're jumping from a source with a layername
                    # to a source without one
                    currentLayerName = nextLayer
                else:
                    currentLayerName = g.layer.name
            else:
                # RF 1.8.x
                currentLayerName = g.layerName
            if not g.name in nextMaster:
                # Frank suggests:
                #nextMaster = getOtherMaster(direction==1, shuffle==True)
                #OpenWindow(AddSomeGlyphsWindow, f, nextMaster, g.name)
                #AppKit.NSBeep()
                return None
            nextGlyph = nextMaster[g.name]
            applySelection(nextGlyph, selectedPoints, selectedComps, selectedAnchors)
            nextGlyph.naked().measurements = currentMeasurements
            if nextGlyph is not None:
                if version >= "3.3" and not forceNewWindow:
                    # use the 3.3 new window.setGlyph so we don't have to create a new window
                    w = CurrentGlyphWindow()
                    view = w.getGlyphView()
                    viewFrame = view.visibleRect()        #    necessary?
                    viewScale = w.getGlyphViewScale()     #    necessary?
                    w.setGlyph(nextGlyph)
                    w.setGlyphViewScale(viewScale)        #    necessary?
                    view.scrollRectToVisible_(viewFrame)  #    necessary?    
                    if currentLayerName is not None:
                        w.setLayer(currentLayerName, toToolbar=True)
                else:
                    # can't set a new glyph to the same window
                    # then make a new window and copy the state
                    rr = getGlyphWindowPosSize()
                    if rr is not None:
                        p, s, settings, viewFrame, viewScale = rr
                        setGlyphWindowPosSize(nextGlyph, p, s, settings=settings, viewFrame=viewFrame, viewScale=viewScale, layerName=currentLayerName)
    elif windowType == "SingleFontWindow":
        selectedPoints = None
        selectedComps = None
        currentMeasurements = None
        nextGlyph = None
        fontWindow = CurrentFontWindow()
        selectedGlyphs = f.selectedGlyphNames if version >= "3.2" else f.selection
        nextWindow = nextMaster.document().getMainWindow()
        nextWindow = nextWindow.vanillaWrapper()
        g = CurrentGlyph()
        if g is not None:
            selectedPoints, selectedComps, selectedAnchors = copySelection(g)
            currentMeasurements = g.naked().measurements
            nextGlyph = nextMaster[g.name]
        # copy the posSize
        posSize = fontWindow.window().getPosSize()
        nextWindow.window().setPosSize(posSize)
        nextWindow.window().show()
        # set the new current glyph
        nextWindow.setGlyphByName(g.name)
        # set the viewscale
        currentView = fontWindow.getGlyphView()
        viewFrame = currentView.visibleRect()
        viewScale = fontWindow.getGlyphViewScale()
        nextView = nextWindow.getGlyphView()
        nextWindow.setGlyphViewScale(viewScale)
        nextView.scrollRectToVisible_(viewFrame)
        # maybe the viewframe needs to be seen as a factor of the rect

        nextSelectedGlyphs = [s for s in selectedGlyphs if s in nextMaster]
        if version >= "3.0":
            nextMaster.selectedGlyphNames = nextSelectedGlyphs
        else:
            nextMaster.selection = nextSelectedGlyphs

        if nextGlyph is not None:
            applySelection(nextGlyph, selectedPoints, selectedComps, selectedAnchors)
            nextGlyph.naked().measurements = currentMeasurements

        rawText = fontWindow.spaceCenter.getRaw()
        prefix = fontWindow.spaceCenter.getPre()
        suffix = fontWindow.spaceCenter.getAfter()
        gnameSuffix = fontWindow.spaceCenter.getSuffix()
        size = fontWindow.spaceCenter.getPointSize()

        nextWindow.spaceCenter.setRaw(rawText)
        nextWindow.spaceCenter.setPre(prefix)
        nextWindow.spaceCenter.setAfter(suffix)
        nextWindow.spaceCenter.setSuffix(gnameSuffix)
        nextWindow.spaceCenter.setPointSize(size)
    elif windowType == "MetricsMachineMainWindow":
        # this handles any metricsMachine windows that might be open.
        # copy the pairlist and the current pair to the next window
        # maybe also adjust the window position?
        # thanks to Tal and Frederik
        pointSizes = [50, 75, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500]

        currentPair = metricsMachine.GetCurrentPair(font=f)
        currentList = metricsMachine.GetPairList(font=f)
        MMcontroller = focusOnMetricsMachine(nextMaster)
        MMcontroller.w.show()
        metricsMachine.SetPairList(currentList, font=nextMaster)
        metricsMachine.SetCurrentPair(currentPair, font=nextMaster)

        MMcontroller.pairList.setSelection(currentPair)

        otherMMcontroller = focusOnMetricsMachine(f)
        pointSize = otherMMcontroller.editView.pairView.getPointSize()

        if pointSize in pointSizes:
            MMcontroller.editView.pairView.setPointSize(pointSize)

if __name__ == "__main__":
    switch(-1)
