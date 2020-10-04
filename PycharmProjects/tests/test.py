from ImageStims import Images
from Window import window
from DialogueBox import dialoguebox

from GLLG import GLLG
from LGLG import LGLG
from LLGG import LLGG
from LGGL import LGGL
from GGLL import GGLL
from GLGL import GLGL

window = window()
win = window.win

images = Images()
imageHH = images.imageHH
imageHS = images.imageHS
imageSH = images.imageSH
imageSS = images.imageSS
imageStims = [imageHS, imageSH, imageHH, imageSS]

globalFirstInstructionImage = images.globalFirstInstructionImage
instructionImage2 = images.instructionImage2
globalSecondInstructionImage = images.globalSecondInstructionImage
localFirstInstructionImage = images.localFirstInstructionImage
localSecondInstructionImage = images.localSecondInstructionImage
fixationPoint = images.fixationPoint
questionMark = images.questionMark
correct = images.correct
wrong = images.wrong

subjectInfo = dialoguebox().showDialogBox()

if int(subjectInfo[1]) % 6 == 0:
    task = GLGL()
    task.GLGLtask(subjectInfo)

if int(subjectInfo[1]) % 6 == 1:
    task = GLLG()
    task.GLLGtask(subjectInfo)

if int(subjectInfo[1]) % 6 == 2:
    task = LGGL()
    task.LGGLtask(subjectInfo)

if int(subjectInfo[1]) % 6 == 3:
    task = LLGG()
    task.LLGGtask(subjectInfo)

if int(subjectInfo[1]) % 6 == 4:
    task = GGLL()
    task.GGLLtask(subjectInfo)

if int(subjectInfo[1]) % 6 == 5:
    task = LGLG()
    task.LGLGtask(subjectInfo)



