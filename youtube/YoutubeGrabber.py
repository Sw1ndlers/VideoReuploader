from pathlib import Path
from typing import Dict, List, Tuple
from googleapiclient.discovery import build
import json
from pytube import YouTube as PytubeDownloader
from pytube.cli import on_progress

from functions.Filesystem import createDirectory
from functions.utils import assertResponse
from processing.SplitVideo import splitVideoIntoChunks


class YoutubeGrabber:
    """
    A class to download and manage youtube videos

    Attributes:
        apiKey (str): The youtube api key
        targetChannel (str): The target channel to download videos from
        service (googleapiclient.discovery.Resource): The youtube api service
        channelId (str): The channel id of the target channel
        directory (Path): The directory to save the videos
    """

    def __init__(self, apiKey: str, targetChannel: str):
        self.apiKey = apiKey
        self.service = build("youtube", "v3", developerKey=apiKey)

        self.directory = Path(f"data/{targetChannel}")

        self.targetChannel = targetChannel
        self.channelId = self.getChannelID()

        createDirectory("data")
        createDirectory(self.directory)

    def getChannelID(self) -> str:
        """
        Fetches the channel id of the target channel
        Returns the channel id if it has been saved before

        Returns:
            str: The channel id of the target channel
        """
        channelIdSavedPath = self.directory.joinpath("channelId.json")

        if channelIdSavedPath.is_file():
            with open(channelIdSavedPath, "r") as f:
                return json.load(f)["channelId"]

        channelList = (
            self.service.search()
            .list(part="snippet", q=self.targetChannel, type="channel")
            .execute()
        )
        channel = channelList["items"][0]

        print(f"Found Channel: {channel['snippet']['title']}")

        with open(channelIdSavedPath, "w") as f:
            json.dump({"channelId": channel["id"]["channelId"]}, f, indent=4)

        return channel["id"]["channelId"]

    def getAllSavedVideos(self) -> Dict[str, dict]:
        jsonPath = self.directory.joinpath("fetchedVideos.json")

        if jsonPath.is_file():
            with open(jsonPath, "r") as f:
                return json.load(f)

        return {}

    def getChannelSavedVideos(self) -> dict:
        savedVideos = self.getAllSavedVideos()

        return (
            savedVideos[self.targetChannel] if self.targetChannel in savedVideos else {}
        )

    def saveVideos(self, videos: List[dict]):
        jsonPath = self.directory.joinpath("fetchedVideos.json")

        savedVideos = self.getAllSavedVideos()
        savedVideos[self.targetChannel] = videos

        with open(jsonPath, "w") as f:
            json.dump(savedVideos, f, indent=4)

    def getVideos(self) -> List[dict]:
        """
        Fetches all videos from the target channel

        Returns:
            list: A list of videos from the target channel
        """

        if self.targetChannel in self.getAllSavedVideos():
            return self.getChannelSavedVideos()

        nextPageToken = None
        videos = []

        while True:
            videosListResponse = (
                self.service.search()
                .list(
                    part="snippet",
                    channelId=self.channelId,
                    maxResults=50,
                    type="video",
                    pageToken=nextPageToken if nextPageToken else None,
                )
                .execute()
            )

            videos.extend(videosListResponse["items"])

            nextPageToken = videosListResponse.get("nextPageToken")

            if not nextPageToken:
                break

        print(f"Found {len(videos)} videos")

        self.saveVideos(videos)

        return videos

    def downloadVideo(self, videoId: str) -> Tuple[Path, List[str]]:
        """
        Downloads a video from youtube

        Args:
            videoId (str): The video id of the video to download

        Returns:
            Path: The path to the downloaded video
            Keywords: The keywords of the video

            -> Path, Keywords
        """

        video = PytubeDownloader(
            f"https://www.youtube.com/watch?v={videoId}",
            on_progress_callback=on_progress,
        )
        stream = video.streams.get_highest_resolution()

        videoDirectory = Path(f"data/{self.targetChannel}/videos/{video.title}")
        createDirectory(videoDirectory)

        print(f"Downloading {video.title}")

        path = stream.download(output_path=videoDirectory, filename="main.mp4")

        print(f"Downloaded {video.title}")

        return [path, video.keywords]

    def splitVideo(self, videoTitle: str) -> List[Path]:
        """
        Splits a video into 1 minute chunks
        Uses the downloaded video from the video title

        Args:
            videoTitle (str): The title of the video to split

        Returns:
            list: A list of paths to the split video chunks
        """

        videoDirectory = self.directory.joinpath(f"videos/{videoTitle}")
        assertResponse(
            videoDirectory.is_dir(),
            f"{videoDirectory} has not been created before splitting video",
        )

        videoPath = videoDirectory.joinpath("main.mp4")
        splitVideoIntoChunks(videoPath, videoDirectory)

        return [
            file
            for file in videoDirectory.iterdir()
            if file.is_file() and "part" in file.name and file.suffix == ".mp4"
        ]
