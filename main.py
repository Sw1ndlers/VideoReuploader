from pathlib import Path
from dotenv import dotenv_values
import concurrent.futures

from functions.Filesystem import createDirectory
from gameplay.GameplayGrabber import GameplayGrabber
from processing.ClipVideoBuilder import ClipVideoBuilder
from youtube.YoutubeGrabber import YoutubeGrabber
from youtube.YoutubeVideo import YoutubeVideo

dotenv = dotenv_values(".env")
apiKey = dotenv["GOOGLE_API_KEY"]

targetChannel = "SamONellaAcademy"
gameplayLinks = ["https://www.youtube.com/watch?v=n_Dv4JMiwK8"]

youtubeGrabber = YoutubeGrabber(apiKey, targetChannel)
videoDataList = youtubeGrabber.getVideos()

gameplayGrabber = GameplayGrabber(gameplayLinks[0])
gameplayIndex = 1

outputDirectory = Path("output")
createDirectory(outputDirectory)


for videoData in videoDataList:
    video = YoutubeVideo(youtubeGrabber, videoData)
    videoOutputDirectory = outputDirectory.joinpath(video.title)

    if videoOutputDirectory.exists():
        print(f"Video {video.title} already exists, skipping")
        continue

    video.download()
    video.split()

    splits = video.getVideoSplits()

    createDirectory(videoOutputDirectory)

    for i, splitPath in enumerate(splits):
        gameplayClipPath = gameplayGrabber.getGameplayClip(gameplayIndex)

        videoBuilder = ClipVideoBuilder(
            videoData=video,
            videoOutputDirectory=videoOutputDirectory,
            videoClipPath=splitPath,
            gameplayClipPath=gameplayClipPath,
            currentPart=i,
            totalParts=len(splits)
        )

        videoBuilder.buildVideo()


    break


