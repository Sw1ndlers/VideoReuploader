import json
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    TextClip,
    ColorClip,
    TextClip,
    vfx
)

from functions.Filesystem import createDirectory
from functions.utils import softWrapText
from youtube.YoutubeVideo import YoutubeVideo

class ClipVideoBuilder:
    def __init__(
        self,
        videoData: YoutubeVideo,
        videoOutputDirectory: Path,
        videoClipPath: Path,
        gameplayClipPath: Path,
        currentPart: int,
        totalParts: int,
    ):
        self.videoData = videoData

        self.videoClipPath = videoClipPath
        self.gameplayClipPath = gameplayClipPath

        self.width, self.height = 720, 1280
        self.topOffset = 80

        self.outputDirectory = videoOutputDirectory.joinpath(f"part-{currentPart}")
        self.outputPath = self.outputDirectory.joinpath("output.mp4")
        self.metadataPath = self.outputDirectory.joinpath("metadata.json")

        self.wrappedLines = 1
        self.videoDuration = None

        self.currentPart = currentPart
        self.totalParts = totalParts

        createDirectory(self.outputDirectory)
        self.createMetadata()

    def createMetadata(self):
        with open(self.metadataPath, "w") as metadataFile:
            metadata = {
                "title": self.videoData.title,
                "tags": self.videoData.keywords,
            }
            json.dump(metadata, metadataFile)

    def createTextClipTitle(self):
        videoTitle, wrappedLines = softWrapText(
            self.videoData.title,
            fontSize=40,
            letterSpacing=1,
            maxWidth=self.width * 0.8,
        )

        textClipTitle = TextClip(
            videoTitle,
            fontsize=40,
            font="Arial-Bold",
            color="white",
            align="Center",
            size=(self.width, 50 * wrappedLines),
        )

        textClipTitle = textClipTitle.set_position(
            ("center", 50 + self.topOffset)
        ).set_duration(self.videoDuration)

        self.wrappedLines = wrappedLines

        return textClipTitle

    def createTextClipCaption(self):
        videoCaption = f"Part {self.currentPart + 1} of {self.totalParts}"

        textClipCaption = TextClip(
            videoCaption,
            fontsize=40,
            font="Arial",
            color="white",
            align="Center",
            size=(self.width, 50),
        )

        textClipCaption = textClipCaption.set_position(
            ("center", 60 + (50 * self.wrappedLines) + self.topOffset)
        )
        textClipCaption = textClipCaption.set_duration(self.videoDuration)

        return textClipCaption

    def buildVideo(self):
        width, height = self.width, self.height
        topOffset = self.topOffset

        videoClip: VideoFileClip = VideoFileClip(str(self.videoClipPath))
        videoClip = videoClip.resize(width=width)

        gameplayClip: VideoFileClip = VideoFileClip(str(self.gameplayClipPath))
        gameplayClip = gameplayClip.resize(width=width)
        gameplayClip = gameplayClip.without_audio()

        videoDuration = max(videoClip.duration, gameplayClip.duration)
        self.videoDuration = videoDuration

        background = ColorClip(size=(width, height), color=(0, 0, 0))
        background = background.set_duration(videoDuration)

        centerY = height // 2
        videoClipHeight = videoClip.size[1]

        videoClip = videoClip.set_position(
            ("center", centerY - videoClipHeight + topOffset)
        )
        gameplayClip = gameplayClip.set_position(("center", centerY + topOffset))

        textClipTitle = self.createTextClipTitle()
        textClipCaption = self.createTextClipCaption()

        finalClip = CompositeVideoClip(
            [
                background,
                textClipTitle,
                textClipCaption,
                videoClip,
                gameplayClip,
            ]
        )

        finalClip.write_videofile(str(self.outputPath), fps=24, threads=4)

    def buildVideo(self):
        width, height = self.width, self.height
        topOffset = self.topOffset

        videoClip: VideoFileClip = VideoFileClip(str(self.videoClipPath))
        videoClip = videoClip.resize(width=width)

        videoDuration  =videoClip.duration
        self.videoDuration = videoDuration

        background = ColorClip(size=(width, height), color=(0, 0, 0))
        background = background.set_duration(videoDuration)

        centerY = height // 2
        videoClipHeight = videoClip.size[1]

        videoClip = videoClip.set_position(
            ("center", centerY - (videoClipHeight // 2) + topOffset)
        )

        textClipTitle = self.createTextClipTitle()
        textClipCaption = self.createTextClipCaption()

        finalClip = CompositeVideoClip(
            [
                background,
                textClipTitle,
                textClipCaption,
                videoClip,
            ]
        )

        finalClip.write_videofile(str(self.outputPath), fps=24, threads=4)
