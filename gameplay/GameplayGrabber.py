from pathlib import Path
from typing import List
from pytube import YouTube as PytubeDownloader
from pytube.cli import on_progress
from functions.Filesystem import createDirectory
from processing.SplitVideo import splitVideoIntoChunks


class GameplayGrabber:
    """
    A class to download and manage gameplay videos

    Attributes:
        link (str): The link to the gameplay video
        pytube (PytubeDownloader): The PytubeDownloader object
        videoDirectory (Path): The directory to save the video
        alreadyDownloaded (bool): Whether the video has already been downloaded
    """

    def __init__(self, link: str):
        self.link = link
        self.pytube = PytubeDownloader(link, on_progress_callback=on_progress)
        self.videoDirectory = Path(f"data/Gameplay/{self.pytube.title}")

        self.alreadyDownloaded = self.videoDirectory.exists()

        createDirectory(self.videoDirectory)

    def getGameplayClips(self) -> List[Path]:
        """
        Get the gameplay clips from the directory
        """

        if self.alreadyDownloaded:
            return [
                file
                for file in self.videoDirectory.iterdir()
                if file.is_file() and "part" in file.name and file.suffix == ".mp4"
            ]
        else:
            exit("Gameplay not downloaded")

    def getGameplayClip(self, index: int) -> Path:
        """
        Get a specific gameplay clip from the directory
        """

        return self.videoDirectory.joinpath(f"part-{index}.mp4")

    def download(self) -> List[Path]:
        """
        Download the gameplay video
        """

        if self.alreadyDownloaded:
            print(f"{self.pytube.title} already exists")
            return self.getGameplayClips()

        stream = self.pytube.streams.get_highest_resolution()
        videoPath = stream.download(
            output_path=self.videoDirectory, filename="main.mp4"
        )

        self.alreadyDownloaded = True

        splitVideoIntoChunks(videoPath, self.videoDirectory)

        return self.getGameplayClips()
