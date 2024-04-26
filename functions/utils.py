import textwrap
from PIL import ImageFont

def assertResponse(value: any, message: str):
    if not value:
        print(message)
        exit(1)

def softWrapText(
    text: str,
    fontSize: int,
    letterSpacing: int,
    maxWidth: int,
):
    imageFont = ImageFont.load_default(fontSize)

    textWidth = imageFont.getlength(text) + (len(text) - 1) * letterSpacing
    letterWidth = textWidth / len(text)

    if textWidth < maxWidth:
        return text, 1

    maxChars = maxWidth / letterWidth
    wrappedText = textwrap.fill(text, width=maxChars)
    return wrappedText, wrappedText.count("\n") + 1

