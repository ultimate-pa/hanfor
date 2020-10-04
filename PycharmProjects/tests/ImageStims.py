from psychopy import visual
from Window import window

window = window()
win = window.win


class Images(object):
    imageHH = visual.ImageStim(win, image='images/HH.jpg', pos=[0, 0], units='pix', size=[226.768, 272.12])
    imageHS = visual.ImageStim(win, image='images/HS.jpg', pos=[0, 0], units='pix', size=[226.768, 272.12])
    imageSH = visual.ImageStim(win, image='images/SH.jpg', pos=[0, 0], units='pix', size=[226.768, 272.12])
    imageSS = visual.ImageStim(win, image='images/SS.jpg', pos=[0, 0], units='pix', size=[226.768, 272.12])
    imageStims = [imageHS, imageSH, imageHH, imageSS]

    globalFirstInstructionImage = visual.ImageStim(win, image='images/globalFirstInstruction.jpg', pos=[-75, 75],
                                                   units='pix',
                                                   size=[1200, 720])
    instructionImage2 = visual.ImageStim(win, image='images/instructionImage2.jpg', pos=[-75, 50], units='pix',
                                         size=[1200, 720])
    globalSecondInstructionImage = visual.ImageStim(win, image='images/globalSecondInstruction.jpg', pos=[-100, 50],
                                                  units='pix',
                                                  size=[1200, 720])
    localFirstInstructionImage = visual.ImageStim(win, image='images/localFirstInstruction.jpg', pos=[-50, 50],
                                                  units='pix',
                                                  size=[1200, 720])
    localSecondInstructionImage = visual.ImageStim(win, image='images/localSecondInstruction.jpg', pos=[-100, 50],
                                                   units='pix',
                                            size=[1200, 720])

    fixationPoint = visual.ImageStim(win, image='images/fixationPoint.png', pos=[-60, 75], units='pix', size=[300, 400])
    questionMark = visual.ImageStim(win, image='images/questionMark.png', pos=[-60, 75], units='pix', size=[140, 210])
    correct = visual.ImageStim(win, image='images/correct.png', pos=[-60, 75], units='pix', size=[80, 80])
    wrong = visual.ImageStim(win, image='images/wrong.png', pos=[-60, 75], units='pix', size=[80, 80])
    exitIcon = visual.ImageStim(win, image='Images/exitIcon.png', pos=(-726, -376), units='pix', size=(48, 48))





