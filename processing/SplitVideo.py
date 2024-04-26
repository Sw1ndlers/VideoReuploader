from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import math
import subprocess
from concurrent.futures import ThreadPoolExecutor


def getVideoDuration(inputVideo: Path) -> int:
    """
    Get the duration of a video in seconds
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(inputVideo),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    duration = float(result.stdout)
    return int(duration)


@dataclass
class Timestamp:
    start: int
    end: int


def splitVideoChunk(inputVideo: Path, outputFileName: Path, start: int, end: int):
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel","error",
            "-y",
            "-i", str(inputVideo),
            "-ss", str(start),
            "-to", str(end),
            str(outputFileName),
        ]
    )

def splitVideoIntoChunks(inputVideo: Path, outputDir) -> List[Path]:
    """
    Split a video into 1-minute chunks and save them to the output directory

    Args:
        inputVideo (Path): The path to the input video
        outputDir (Path): The path to the output directory

    Returns:
        List[Path]: The paths to the output video chunks
    """

    timeStamps: List[Tuple[Timestamp]] = []

    # Get the duration of the video
    duration = getVideoDuration(inputVideo)

    # Calculate the number of chunks
    numChunks = math.ceil(duration / 60)

    # Split the video into chunks
    for i in range(numChunks):
        startTime = i * 60
        endTime = min((i + 1) * 60, duration)
        timeStamps.append((Timestamp(startTime, endTime)))

    # Combine the last part with the preceding one if less than a minute
    if len(timeStamps) > 1 and timeStamps[-1].end - timeStamps[-1].start < 60:
        lastChunk = timeStamps.pop()
        lastChunkIndex = len(timeStamps) - 1
        timeStamps[lastChunkIndex] = Timestamp(
            timeStamps[lastChunkIndex].start, lastChunk.end
        )

    videoPaths = []

    for i, timestamp in enumerate(timeStamps):
        outputFileName = outputDir / f"part-{i}.mp4"
        videoPaths.append(Path(outputFileName))

        subprocess.run([
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(inputVideo),
            "-ss", str(timestamp.start),
            "-to", str(timestamp.end),
            str(outputFileName)
        ])

        print(f"Split {i} of {numChunks}", end="\r")
    
    return videoPaths

# from concurrent.futures import ThreadPoolExecutor

# def splitVideoChunkThreaded(inputVideo: Path, outputFileName: Path, start: int, end: int):
#     subprocess.run([
#         "ffmpeg",
#         "-hide_banner",
#         "-loglevel", "error",
#         "-y",
#         "-i", str(inputVideo),
#         "-ss", str(start),
#         "-to", str(end),
#         str(outputFileName)
#     ])

# def splitVideoIntoChunks(inputVideo: Path, outputDir: Path) -> List[Path]:
#     """
#     Split a video into 1-minute chunks and save them to the output directory using threading

#     Args:
#         inputVideo (Path): The path to the input video
#         outputDir (Path): The path to the output directory

#     Returns:
#         List[Path]: The paths to the output video chunks
#     """

#     # Get the duration of the video
#     duration = getVideoDuration(inputVideo)

#     # Calculate the number of chunks
#     numChunks = math.ceil(duration / 60)

#     # Create a ThreadPoolExecutor
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         futures = []
        
#         # Split the video into chunks
#         for i in range(numChunks):
#             startTime = i * 60
#             endTime = min((i + 1) * 60, duration)

#             outputFileName = outputDir / f"part-{i}.mp4"

#             # Submit the task to the executor
#             future = executor.submit(
#                 splitVideoChunkThreaded, inputVideo, outputFileName, startTime, endTime
#             )
#             futures.append(future)

#         # Wait for all tasks to complete
#         for future in futures:
#             future.result()

#     # Return the paths to the output video chunks
#     return [outputDir / f"part-{i}.mp4" for i in range(numChunks)]
