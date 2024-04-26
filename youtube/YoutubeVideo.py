from pathlib import Path
from typing import List
from youtube.YoutubeGrabber import YoutubeGrabber

class YoutubeVideo:
    """
    A class to handle the information from the fetched youtube video

    Attributes:
        videoInfo (dict): The information of the video
        videoId (str): The id of the video
        title (str): The title of the video
        description (str): The description of the video
        channelId (str): The channel id of the video
        keywords (List[str]): The keywords of the video
        splitVideos (List[Path]): The paths to the split videos
        directory (Path): The directory to save the video
        videoPath (Path): The path to the downloaded video
        youtubeGrabber (YoutubeGrabber): The YoutubeGrabber object
    """ 

    def __init__(self, youtubeGrabber: YoutubeGrabber, videoInfo: dict):
        self.videoInfo = videoInfo

        self.videoId = videoInfo["id"]["videoId"]
        self.title = videoInfo["snippet"]["title"]
        self.description = videoInfo["snippet"]["description"]
        self.channelId = videoInfo["snippet"]["channelId"]
        self.targetChannel = youtubeGrabber.targetChannel

        self.keywords: List[str] | None = None
        self.splitVideos: List[Path] | None = None

        self.directory = Path(f"data/{self.targetChannel}/videos/{self.title}")
        self.videoPath = self.directory.joinpath("main.mp4")

        self.youtubeGrabber = youtubeGrabber

    def download(self):
        """
        Downloads the video and saves the keywords
        Path -> data/{channelId}/videos/{title}/main.mp4

        Returns:
            Path: The path to the downloaded video

        """

        path, keywords = self.youtubeGrabber.downloadVideo(self.videoId)
        self.keywords = keywords

        return path

    def split(self):
        """
        Splits the video into 1 minute chunks
        Path -> data/{channelId}/videos/{title}/part-{i}.mp4

        Returns:
            List[Path]: The paths to the split videos

        """

        self.splitVideos = self.youtubeGrabber.splitVideo(self.title)
        return self.splitVideos
    
    def getVideoSplits(self) -> List[Path]:
        """
        Get the video splits from the directory
        """

        if self.directory.exists() == False:
            exit("Video not downloaded")


        return [
            file
            for file in self.directory.iterdir()
            if file.is_file() and "part" in file.name and file.suffix == ".mp4"
        ]
