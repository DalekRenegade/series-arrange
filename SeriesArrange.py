import os
import sys
from string import ascii_uppercase
from DownloadedFileDetail import DownloadedFileDetail


def readDownloadedFileList(seriesHddPath, baseSeriesList, downloadsPath, userProfile):
    downloadedFiles = []
    allowedVideoExtensions = ('.mp4', '.mkv', '.avi')
    for file in os.listdir(downloadsPath):
        if file.endswith(allowedVideoExtensions):
            dfd = DownloadedFileDetail(downloadsPath, file, userProfile)
            if dfd.tokenizeSeries() and dfd.identifySeries(seriesHddPath, baseSeriesList):
                downloadedFiles.append(dfd)
    return downloadedFiles


def identifySeriesHddPath(userProfile):
    move, folderName, possibleDestDrives = False, 'TV Series', []
    seriesHddPath = os.path.join(userProfile, 'Desktop', folderName)
    if os.name == 'nt':
        possibleDestDrives = [c + ':\\' for c in ascii_uppercase]
    elif os.name == 'posix':
        possibleDestDrives = []
    if len(possibleDestDrives) > 0:
        for dest in possibleDestDrives:
            tryHddPath = os.path.join(dest, folderName)
            if os.path.exists(tryHddPath):
                seriesHddPath = tryHddPath
                move = True
                break
    if not move:
        if not os.path.exists(seriesHddPath):
            os.makedirs(seriesHddPath)
    return move, seriesHddPath


if __name__ == "__main__":
    userProfile = ''
    if os.name == 'nt':
        userProfile = os.environ['USERPROFILE']
    elif os.name == 'posix':
        userProfile = os.environ['HOME']
    else:
        sys.exit(0)
    downloadsPath = os.path.join(userProfile, 'Downloads')
    move, seriesHddPath = identifySeriesHddPath(userProfile)
    baseSeriesList = os.listdir(seriesHddPath)
    downloadedFiles = readDownloadedFileList(seriesHddPath, baseSeriesList, downloadsPath, userProfile)
    for dfile in downloadedFiles:
        dfile.copyOrMoveFileToDestination(move)

