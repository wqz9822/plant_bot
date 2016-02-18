import subprocess
from datetime import datetime

class myCamera(object):

    def __init__(self):
        self.path = "pictures/"
        self.extension = '.jpg'

    def uploadFile(self):
        localPath = self.fileToSave
        remotePath = '/labot/'+ self.timeNow + self.extension
        # Upload the file to dropbox codeLab folder
        subprocess.call(['/home/pi/Dropbox-Uploader/dropbox_uploader.sh','-s','upload',localPath,remotePath], shell=False)
        shareOutput = subprocess.check_output(['/home/pi/Dropbox-Uploader/dropbox_uploader.sh','-s','share',remotePath], shell=False)
        shareOutput = shareOutput.decode("utf-8")
        index = shareOutput.find(':')
        shareLink = shareOutput[index+2:]
        return shareLink

    def makeTimeStamp(self):
        FORMAT = '%Y_%m_%d_%H_%M_%S'
        now = datetime.now()
        timeStamp = now.strftime(FORMAT)
        return timeStamp

    def takePicture(self, labot, timeStamp):
        # Get the current time, format it as the file name
        self.timeNow = self.makeTimeStamp()
        self.fileToSave = self.path + self.timeNow + self.extension
        subprocess.call(['fswebcam','--scale','384x288','--no-banner',self.fileToSave], shell=False)
        labot.updateMessage(timeStamp, "Uploading...")
        shareLink = self.uploadFile()
        labot.updateMessage(timeStamp, "Done.")
        return shareLink
