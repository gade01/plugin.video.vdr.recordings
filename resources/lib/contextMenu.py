# -*- coding: utf-8 -*-
# Copyright: GNU GPLv3
# pylint: disable=E0401
# Disable import error: E0401

import sys
import subprocess
import os
import shutil
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import kfolder
import vdrrecordingfolder
import constants

def GUIEditExportName(name):
    kb = xbmc.Keyboard('', name, False)
    kb.doModal()
    if kb.isConfirmed():
      return kb.getText()
    else:
      return None

def recursive_delete_dir(fullpath):
    '''helper to recursively delete a directory'''
    success = True
    dirs, files = xbmcvfs.listdir(fullpath)
    for file in files:
        success = xbmcvfs.delete(os.path.join(fullpath, file))
    for directory in dirs:
        success = recursive_delete_dir(os.path.join(fullpath, directory))
    success = xbmcvfs.rmdir(fullpath)
    return success 

def recursive_add_files(fullpath, files_dict):
    '''helper to recursively add all files in directory'''
    dirs, files = xbmcvfs.listdir(fullpath)
    for file in files:
        files_dict[os.path.join(fullpath, file)] = True
    for directory in dirs:
        recursive_add_files(os.path.join(fullpath, directory), files_dict)
    return


def getRootFolder():
    rootFolder = xbmcaddon.Addon('plugin.video.vdr.recordings').getSetting("rootFolder")
    lastChar = rootFolder[-1] 
    if lastChar == '/' or lastChar == '\\':
        rootFolder = rootFolder[:-1]
    return rootFolder

#xbmc.log("contextMenu: sys.argv=" + str(sys.argv), xbmc.LOGERROR)
mode = sys.argv[1]
#xbmc.log("mode=" + str(mode), xbmc.LOGERROR)

if mode == constants.ADDALLTOLIBRARY:
    rootFolder = sys.argv[2]
#   xbmc.log("rootFolder=" + str(rootFolder), xbmc.LOGERROR)
# create list of old files
    old_files = {}
    recursive_add_files(constants.LIBRARY_MOVIES, old_files)
    recursive_add_files(constants.LIBRARY_TV_SHOWS, old_files)
    recursive_add_files(constants.LIBRARY_MUSIC_VIDEOS, old_files)
# delete old files
    try: recursive_delete_dir(constants.LIBRARY_MOVIES)
    except: pass
    try: recursive_delete_dir(constants.LIBRARY_TV_SHOWS)
    except: pass
    try: recursive_delete_dir(constants.LIBRARY_MUSIC_VIDEOS)
    except: pass
    xbmcvfs.mkdirs(constants.LIBRARY_MOVIES)
    xbmcvfs.mkdirs(constants.LIBRARY_TV_SHOWS)
    xbmcvfs.mkdirs(constants.LIBRARY_MUSIC_VIDEOS)
# add current (new) files
    kfolder.kFolder(rootFolder).parseFolder(-10, '', rootFolder, old_files)
# create list of new files
    new_files = {}
    recursive_add_files(constants.LIBRARY_MOVIES, new_files)
    recursive_add_files(constants.LIBRARY_TV_SHOWS, new_files)
    recursive_add_files(constants.LIBRARY_MUSIC_VIDEOS, new_files)
# compare list of old files with lest of new filse, clean up library for files which do no longer exist
    for file in old_files.keys() - new_files.keys():
# files do no longer exist -> lean up library
      jsonCommand = {'jsonrpc': '2.0', 'method': 'VideoLibrary.Clean', 'params':{'directory':file, 'showdialogs':False}, 'id': 44}
      xbmc.executeJSONRPC(json.dumps(jsonCommand))
#    jsonCommand = {'jsonrpc': '2.0', 'method': 'VideoLibrary.Clean', 'id': 44}
#    xbmc.executeJSONRPC(json.dumps(jsonCommand))
# curl -X POST -H "content-type:application/json" http://rpi3:8080/jsonrpc -d '{"jsonrpc":"2.0","id":1,"method":"JSONRPC.Introspect"}' > ~/doc.json
# curl -X POST -H "content-type:application/json" http://rpi3:8080/jsonrpc -d '{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.Scan","params":{"directory":"/var/lib/vdr/.kodi/userdata/addon_data/plugin.video.vdr.recordings/Movies/video/Winnetou/Winnetou (2016).strm"}}'
# curl -X POST -H "content-type:application/json" http://rpi3:8080/jsonrpc -d '{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.Clean","params":{"directory":"/var/lib/vdr/.kodi/userdata/addon_data/plugin.video.vdr.recordings/Movies/video/Winnetou/Winnetou (2016).strm"}}'



  
if mode == constants.TV_SHOWS:
    recordingFolderPath = sys.argv[2]
    k_Folder = kfolder.kFolder(recordingFolderPath)    
    k_Folder.setContentType(constants.TV_SHOWS)

if mode == constants.MOVIES:
    recordingFolderPath = sys.argv[2]
#   xbmc.log("contextMenu, movies" + str(recordingFolderPath), xbmc.LOGERROR)    
    k_Folder = kfolder.kFolder(recordingFolderPath)    
    k_Folder.setContentType(constants.MOVIES)    

if mode == constants.MUSIC_VIDEOS:
    recordingFolderPath = sys.argv[2]
    k_Folder = kfolder.kFolder(recordingFolderPath)    
    k_Folder.setContentType(constants.MUSIC_VIDEOS)   

if mode == constants.EPISODE:
    recordingFolderPath = sys.argv[2]
    episode = sys.argv[3]
    k_Folder = kfolder.kFolder(recordingFolderPath)
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, 'Enter episode number', str(k_Folder.getEpisode(episode)))
    if d != '':
        k_Folder.setEpisode(int(d))
        xbmc.executebuiltin("Container.Refresh")

if mode == constants.SEASON:
    recordingFolderPath = sys.argv[2]
    season = sys.argv[3]
    k_Folder = kfolder.kFolder(recordingFolderPath)
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, 'Enter season number', str(k_Folder.getSeason(season)))
    if d != '':
        k_Folder.setSeason(int(d))
        xbmc.executebuiltin("Container.Refresh")

if mode == constants.YEAR:
    recordingFolderPath = sys.argv[2]
    year = sys.argv[3]
    if int(year) <= 0:
        year = ''
    k_Folder = kfolder.kFolder(recordingFolderPath)
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, 'Enter year', year)
    if d != '':
        k_Folder.setYear(int(d))
        xbmc.executebuiltin("Container.Refresh")


if mode == constants.DELETE:
    recordingFolderPath = sys.argv[2]
    ps = os.path.splitext(recordingFolderPath)
    if ps[1] == ".rec":
# Confirmation dialog
        dialog = xbmcgui.Dialog()
        rf = vdrrecordingfolder.VdrRecordingFolder(recordingFolderPath)
        d = dialog.yesno('Delete recording?', 'Do you want to delete "'
            + rf.title
            + '"?')
        if d == True:    
            recursive_delete_dir(recordingFolderPath)
#       os.rename(recordingFolderPath, ps[0] + '.del')
        xbmc.executebuiltin("Container.Refresh")       

if mode == constants.MOVE:
    recordingFolderPath = sys.argv[2]
    ps = os.path.splitext(recordingFolderPath)
    if ps[1] == ".rec":
        fp = os.path.split(recordingFolderPath)[0]
    else:
        fp = recordingFolderPath
    (fd, fn) = os.path.split(fp)
    k_Folder = kfolder.kFolder(fd)
    dest = k_Folder.selectFolder(getRootFolder())
    xbmc.log("constants.MOVE, dest = " + str(dest), xbmc.LOGERROR) 
    if dest != None:
        d1 = fp + ".move"
        dfin = os.path.join(dest, fn)
        if xbmcvfs.rename(fp, d1) == False:
            xbmc.log("constants.MOVE, fp = " + fp, xbmc.LOGERROR) 
            xbmc.log("constants.MOVE, d1 = " + d1, xbmc.LOGERROR)
        else:

            script = "special://home/addons/plugin.video.vdr.recordings/resources/lib/move.py"
            xbmc.executebuiltin("XBMC.RunScript(" + xbmcvfs.translatePath(script) + ", \"" + d1 + "\", \"" + dest + "\", \"" + dfin + "\")")
            xbmc.sleep(10) 
            xbmc.executebuiltin("Container.Refresh")       

if mode == constants.SEARCH:
    rootFolder = sys.argv[2]
    base_url = sys.argv[3]
    sString = GUIEditExportName("Enter search string")
    if sString != None:
       p_url = base_url + '?' + urllib.urlencode({'mode': 'search', 'searchString': sString})
#     xbmc.log("p_url=" + str(p_url), xbmc.LOGERROR)
       runner = "ActivateWindow(10025," + str(p_url) + ",return)"
       xbmc.executebuiltin(runner)   
 
if mode == constants.REFRESH:
    xbmc.executebuiltin("Container.Refresh")  

