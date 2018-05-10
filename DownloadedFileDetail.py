import os
from difflib import SequenceMatcher
from shutil import copyfile
from shutil import move as movefile


class DownloadedFileDetail:
    def __init__(self, downloadedFileDirectory, downloadedFileName, userProfile):
        self.downloadedFileDirectory = downloadedFileDirectory
        self.downloadedFileName = downloadedFileName
        self.tokenizedFileName = ''
        self.destinationSeriesPath = ''
        self.matchRatio = 0.0
        self.seasonNo = 0
        self.episodeNos = []
        self.isNewSeries = False
        self.userProfile = userProfile

    def tokenizeSeries(self):
        i, seasonIndex = 0, -1
        while i < (len(self.downloadedFileName) - 2):
            if self.downloadedFileName[i].upper() == 'S' and '0' <= self.downloadedFileName[i + 1] <= '9' and '0' <= \
                    self.downloadedFileName[i + 2] <= '9':
                self.seasonNo = int(self.downloadedFileName[i + 1:i + 3])
                seasonIndex = i
                i += 3
            elif self.downloadedFileName[i].upper() == 'E' and '0' <= self.downloadedFileName[i + 1] <= '9' and '0' <= \
                    self.downloadedFileName[i + 2] <= '9':
                self.episodeNos.append(int(self.downloadedFileName[i + 1:i + 3]))
                i += 3
            else:
                i += 1

        if seasonIndex > 0:
            self.tokenizedFileName = self.downloadedFileName[:seasonIndex - 1].replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
        return seasonIndex > 0

    def identifySeries(self, seriesHddPath, baseSeriesList):
        rvalue = False
        matchedSeries = None
        for baseSeries in baseSeriesList:
            ratio = SequenceMatcher(None, self.tokenizedFileName,
                                    baseSeries.replace("'", "").replace(".", "")).ratio()
            if ratio > self.matchRatio:
                matchedSeries = baseSeries
                self.matchRatio = ratio
        if self.matchRatio > 0.7:
            self.destinationSeriesPath = os.path.join(seriesHddPath, matchedSeries)
            rvalue = True
        elif self.seasonNo > 0 and len(self.episodeNos) > 0:
            self.destinationSeriesPath = os.path.join(seriesHddPath, self.tokenizedFileName)
            self.isNewSeries = True
            rvalue = True
        return rvalue

    def createLocalCopy(self, src):
        if self.isNewSeries:
            videosPath = os.path.join(self.userProfile, 'Videos')
            localCopyFolderPath = os.path.join(videosPath, self.tokenizedFileName, 'Season ' + str(self.seasonNo))
            if not os.path.exists(localCopyFolderPath):
                os.makedirs(localCopyFolderPath)
            localCopyDest = os.path.join(localCopyFolderPath, self.downloadedFileName)
            print 'Creating a local copy in "' + videosPath + '"'
            copyfile(src, localCopyDest)
            print '>>> Copy complete...' + localCopyDest

    def copyOrMoveFileToDestination(self, move):
        src = os.path.join(self.downloadedFileDirectory, self.downloadedFileName)
        destDir = os.path.join(self.destinationSeriesPath, 'Season ' + str(self.seasonNo))
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        pattern, epString = '{}E{:0>2d}', ''
        for ep in self.episodeNos:
            epString = pattern.format(epString, ep)
        destFileName = '{}.S{:0>2d}{}{}'.format(self.tokenizedFileName, self.seasonNo, epString, os.path.splitext(self.downloadedFileName)[1])
        dest = os.path.join(destDir, destFileName)
        if os.path.exists(dest):
            os.remove(dest)
        if move:
            self.createLocalCopy(src)
            print 'Moving from.....' + src + '.....' + dest
            movefile(src, dest)
            print '>>> Move complete...' + dest
        else:
            print 'Copying from.....' + src + '.....' + dest
            copyfile(src, dest)
            print '>>> Copy complete...' + dest

    def __str__(self):
        return self.tokenizedFileName + '_S_' + str(self.seasonNo) + '_E' + 'E'.join(str(x) for x in self.episodeNos)
