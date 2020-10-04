from psychopy import core, event
import random
import xlsxwriter
import datetime
import os

from ImageStims import Images
from Window import window
from EndMessage import EndMessage


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
exitIcon = images.exitIcon

Headers = ['ImageFile', 'Congruency', 'Block', 'Trial', 'Key-Resp', 'Cor-Ans', 'Accuracy', 'R-time',
           'Trial-Start', 'Key-Resp-Start', 'Session', 'Experiment-Day', 'Stimulation-Site', 'Gender', 'Age',
           'Datetime']

Cells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

positions = [(166.75, 75), (-60, 301.77), (-286.77, 75), (-60, -151.77)]

event.globalKeys.clear()
event.globalKeys.add(key='q', func=os._exit, func_args=[1], func_kwargs=None)


class GGLL(object):
    def GGLLtask(self, subjectInfoList):

        workbook = xlsxwriter.Workbook(
            str(subjectInfoList[0] + subjectInfoList[1]) + '-' + 'S' + str(subjectInfoList[6])
            + '-' + 'D' + str(subjectInfoList[2]) + '.xlsx')
        worksheet = workbook.add_worksheet()

        HeaderFormat = workbook.add_format({
            'bold': True,
            'text_wrap': False,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1})

        for i in range(0, 16):
            worksheet.write(Cells[i] + '1', Headers[i], HeaderFormat)

        trialstart = 0
        generalTimer = core.getTime()

        for index1 in range(1, 3):

            # أGlobal Instruction
            globalFirstInstructionImage.draw()
            win.flip()
            flag = True
            while flag:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        globalFirstInstructionImage.autoDraw = False
                        instructionImage2.draw()
                        win.flip()
                        flag = False

            temp = True
            while temp:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        instructionImage2.autoDraw = False
                        win.flip()

                        c_counter = 0
                        i_counter = 0

                        # Global Practice
                        for j in range(1, 5):
                            rand1 = random.randrange(0, 3)
                            rand2 = 3 - rand1
                            print(rand1)
                            print(rand2)

                            instructionImage2.autoDraw = False
                            fixationPoint.draw()
                            win.flip()
                            core.wait(1)

                            fixationPoint.autoDraw = False

                            gtypeRandom = random.randint(0, 1)
                            # print('type is ' + str(typeRandom))
                            # print('i counter is ' + str(i_counter))
                            # print('c counter is ' + str(c_counter))

                            # 0 -> congruent
                            # 1 -> incongruent
                            if gtypeRandom == 0 and c_counter == 2:
                                gtypeRandom = 1

                            if gtypeRandom == 1 and i_counter == 2:
                                gtypeRandom = 0

                            if gtypeRandom == 0 and (rand1 == 2 or rand1 == 3):
                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()

                                win.flip()
                                core.wait(0.3)
                                c_counter += 1

                            if gtypeRandom == 0 and (rand1 == 0 or rand1 == 1):
                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()
                                core.wait(0.3)
                                c_counter += 1

                            if gtypeRandom == 1 and (rand1 == 0 or rand1 == 1):
                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()
                                win.flip()
                                core.wait(0.3)
                                i_counter += 1

                            if gtypeRandom == 1 and (rand1 == 2 or rand1 == 3):
                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()
                                core.wait(0.3)
                                i_counter += 1


                            imageStims[rand1].autoDraw = False
                            imageStims[rand2].autoDraw = False
                            questionMark.draw()
                            win.flip()

                            testTimer = core.CountdownTimer(4)
                            flag = True
                            while flag:
                                keys = event.getKeys(keyList=['end', 'down'])
                                if keys:

                                    if gtypeRandom == 0 and (rand1 == 1 or rand1 == 2):
                                        if keys[0] == 'end':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    if gtypeRandom == 0 and (rand1 == 0 or rand1 == 3):
                                        if keys[0] == 'down':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    if gtypeRandom == 1 and (rand1 == 0 or rand1 == 3):
                                        if keys[0] == 'end':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    if gtypeRandom == 1 and (rand1 == 1 or rand1 == 2):
                                        if keys[0] == 'down':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    flag = False
                                elif testTimer.getTime() <= 0:
                                    wrong.draw()
                                    win.flip()
                                    core.wait(2)
                                    flag = False

                        temp = False

            globalSecondInstructionImage.draw()
            win.flip()

            temp1 = True
            while temp1:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        globalSecondInstructionImage.autoDraw = False
                        win.flip()

                        main_i_counter = 0
                        main_c_counter = 0

                        # Global main task
                        for index in range(1, 5):
                            if index1 == 2:
                                index += 4
                            worksheet.write('D' + str(index + 1), str(index))
                            worksheet.write('C' + str(index + 1), '1')
                            worksheet.write('K' + str(index + 1), subjectInfoList[6])
                            worksheet.write('L' + str(index + 1), subjectInfoList[2])
                            worksheet.write('M' + str(index + 1), subjectInfoList[5])
                            worksheet.write('N' + str(index + 1), str(subjectInfoList[3]))
                            worksheet.write('O' + str(index + 1), str(subjectInfoList[4]))
                            worksheet.write('P' + str(index + 1), str(datetime.datetime.today()))

                            rand1 = random.randint(0, 3)
                            rand2 = 3 - rand1

                            globalSecondInstructionImage.autoDraw = False
                            fixationPoint.draw()
                            globalTimer = core.getTime()

                            win.flip()
                            core.wait(1)

                            fixationPoint.autoDraw = False

                            trialstart = globalTimer - generalTimer
                            worksheet.write('I' + str(index + 1), str(trialstart))

                            maintypeRandom = random.randint(0, 1)
                            # 0 -> congruent
                            # 1 -> incongruent

                            if maintypeRandom == 0 and main_c_counter == 2:
                                maintypeRandom = 1
                            if maintypeRandom == 1 and main_i_counter == 2:
                                maintypeRandom = 0

                            if maintypeRandom == 0 and (rand1 == 2 or rand1 == 3):
                                worksheet.write('B' + str(index + 1), '1')

                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()
                                win.flip()
                                core.wait(0.3)
                                main_c_counter += 1
                                if rand1 == 2:
                                    worksheet.write('A' + str(index + 1), 'ex1')
                                    worksheet.write('F' + str(index + 1), '1')
                                else:
                                    worksheet.write('A' + str(index + 1), 'ex4')
                                    worksheet.write('F' + str(index + 1), '2')

                            if maintypeRandom == 0 and (rand1 == 0 or rand1 == 1):
                                worksheet.write('B' + str(index + 1), '1')

                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()

                                core.wait(0.3)
                                main_c_counter += 1
                                if rand1 == 0:
                                    worksheet.write('A' + str(index + 1), 'ex4')
                                    worksheet.write('F' + str(index + 1), '2')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex1')
                                    worksheet.write('F' + str(index + 1), '1')

                            if maintypeRandom == 1 and (rand1 == 0 or rand1 == 1):
                                worksheet.write('B' + str(index + 1), '0')

                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()
                                win.flip()

                                core.wait(0.3)
                                main_i_counter += 1
                                if rand1 == 0:
                                    worksheet.write('A' + str(index + 1), 'ex3')
                                    worksheet.write('F' + str(index + 1), '1')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex2')
                                    worksheet.write('F' + str(index + 1), '2')

                            if maintypeRandom == 1 and (rand1 == 2 or rand1 == 3):
                                worksheet.write('B' + str(index + 1), '0')

                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()

                                core.wait(0.3)
                                main_i_counter += 1
                                if rand1 == 2:
                                    worksheet.write('A' + str(index + 1), 'ex2')
                                    worksheet.write('F' + str(index + 1), '1')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex3')
                                    worksheet.write('F' + str(index + 1), '2')

                            imageStims[rand1].autoDraw = False
                            imageStims[rand2].autoDraw = False

                            questionMark.draw()
                            win.flip()
                            counter = core.CountdownTimer(4)
                            flag = True
                            while flag:
                                keys = event.getKeys(keyList=['end', 'down'])
                                if keys:
                                    for key in keys:
                                        if key == 'end':
                                            worksheet.write('E' + str(index + 1), '1')
                                        if key == 'down':
                                            worksheet.write('E' + str(index + 1), '2')

                                        worksheet.write('G' + str(index + 1), '=IF(E' + str(index + 1) + '= F' +
                                                        str(index + 1) + ',1,0)')
                                        worksheet.write('H' + str(index + 1), str(4 - counter.getTime() + 0.3))
                                        worksheet.write('J' + str(index + 1),
                                                        str(4 - counter.getTime() + 0.3 + trialstart + 1))

                                        flag = False

                                elif counter.getTime() <= 0:
                                    worksheet.write('E' + str(index + 1), 'None')
                                    worksheet.write('H' + str(index + 1), 'None')
                                    worksheet.write('J' + str(index + 1), 'None')
                                    worksheet.write('G' + str(index + 1), 'None')
                                    flag = False

                            temp1 = False
            questionMark.autoDraw = False
            win.flip()

        for index2 in range(1, 3):

            localFirstInstructionImage.draw()
            win.flip()

            flag = True
            while flag:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        localFirstInstructionImage.autoDraw = False
                        instructionImage2.draw()
                        win.flip()
                        flag = False

            flag = True
            while flag:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        instructionImage2.autoDraw = False
                        win.flip()

                        i_counter = 0
                        c_counter = 0

                        # Local Practice
                        for index in range(1, 5):
                            rand1 = random.randint(0, 3)
                            rand2 = 3 - rand1

                            fixationPoint.draw()
                            win.flip()
                            core.wait(1)

                            fixationPoint.autoDraw = False
                            ltypeRandom = random.randint(0, 1)
                            # 0 -> congruent
                            # 1 -> incongruent

                            if ltypeRandom == 0 and c_counter == 2:
                                ltypeRandom = 1
                            if ltypeRandom == 1 and i_counter == 2:
                                ltypeRandom = 0

                            if ltypeRandom == 0 and (rand1 == 2 or rand1 == 3):
                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()
                                win.flip()
                                core.wait(0.3)
                                c_counter += 1

                            if ltypeRandom == 0 and (rand1 == 0 or rand1 == 1):
                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()
                                core.wait(0.3)
                                c_counter += 1

                            if ltypeRandom == 1 and (rand1 == 0 or rand1 == 1):
                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()
                                win.flip()
                                core.wait(0.3)
                                i_counter += 1

                            if ltypeRandom == 1 and (rand1 == 2 or rand1 == 3):
                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()
                                win.flip()
                                core.wait(0.3)
                                i_counter += 1

                            imageStims[rand1].autoDraw = False
                            imageStims[rand2].autoDraw = False
                            questionMark.draw()
                            testTimer1 = core.CountdownTimer(4)
                            win.flip()

                            flag = True
                            while flag:
                                keys = event.getKeys(keyList=['end', 'down'])
                                if keys:
                                    if ltypeRandom == 0 and (rand1 == 1 or rand1 == 2):
                                        if keys[0] == 'end':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()

                                            win.flip()
                                            core.wait(2)

                                    if ltypeRandom == 0 and (rand1 == 0 or rand1 == 3):
                                        if keys[0] == 'down':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    if ltypeRandom == 1 and (rand1 == 0 or rand1 == 3):
                                        if keys[0] == 'down':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)

                                    if ltypeRandom == 1 and (rand1 == 1 or rand1 == 2):
                                        if keys[0] == 'end':
                                            correct.draw()
                                            win.flip()
                                            core.wait(2)
                                        else:
                                            wrong.draw()
                                            win.flip()
                                            core.wait(2)
                                    flag = False
                                elif testTimer1.getTime() <= 0:
                                    wrong.draw()
                                    win.flip()
                                    core.wait(2)
                                    flag = False
                        flag = False

            localSecondInstructionImage.draw()
            win.flip()

            flag1 = True
            while flag1:
                keys = event.getKeys(keyList=['m'])
                for key in keys:
                    if key[0] == 'm':
                        localSecondInstructionImage.autoDraw = False
                        win.flip()

                        main_i_counter = 0
                        main_c_counter = 0

                        # Local Main task
                        for index in range(1, 5):
                            if index2 == 1:
                                index += 8
                            if index2 == 2:
                                index += 12
                            worksheet.write('D' + str(index + 1), str(index))
                            worksheet.write('C' + str(index + 1), '0')
                            worksheet.write('K' + str(index + 1), subjectInfoList[6])
                            worksheet.write('L' + str(index + 1), subjectInfoList[2])
                            worksheet.write('M' + str(index + 1), subjectInfoList[5])
                            worksheet.write('N' + str(index + 1), str(subjectInfoList[3]))
                            worksheet.write('O' + str(index + 1), str(subjectInfoList[4]))
                            worksheet.write('P' + str(index + 1), str(datetime.datetime.today()))

                            rand1 = random.randint(0, 3)
                            rand2 = 3 - rand1

                            globalSecondInstructionImage.autoDraw = False
                            fixationPoint.draw()
                            localTimer = core.getTime()

                            win.flip()
                            core.wait(1)

                            fixationPoint.autoDraw = False
                            trialstart = localTimer - generalTimer
                            worksheet.write('I' + str(index + 1), str(trialstart))

                            maintypeRandom = random.randint(0, 1)
                            # 0 -> congruent
                            # 1 -> incongruent
                            if maintypeRandom == 0 and main_c_counter == 2:
                                maintypeRandom = 1
                            if maintypeRandom == 1 and main_i_counter == 2:
                                maintypeRandom = 0

                            if maintypeRandom == 0 and (rand1 == 2 or rand1 == 3):
                                worksheet.write('B' + str(index + 1), '1')

                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()

                                win.flip()

                                core.wait(0.3)
                                main_c_counter += 1
                                if rand1 == 2:
                                    worksheet.write('A' + str(index + 1), 'ex1')
                                    worksheet.write('F' + str(index + 1), '1')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex4')
                                    worksheet.write('F' + str(index + 1), '2')

                            if maintypeRandom == 0 and (rand1 == 0 or rand1 == 1):
                                worksheet.write('B' + str(index + 1), '1')

                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()

                                win.flip()

                                core.wait(0.3)
                                main_c_counter += 1
                                if rand1 == 0:
                                    worksheet.write('A' + str(index + 1), 'ex4')
                                    worksheet.write('F' + str(index + 1), '2')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex1')
                                    worksheet.write('F' + str(index + 1), '1')

                            if maintypeRandom == 1 and (rand1 == 0 or rand1 == 1):
                                worksheet.write('B' + str(index + 1), '0')

                                imageStims[rand1].setPos(positions[rand1])
                                imageStims[rand1].draw()

                                win.flip()

                                core.wait(0.3)
                                main_i_counter += 1
                                if rand1 == 0:
                                    worksheet.write('A' + str(index + 1), 'ex3')
                                    worksheet.write('F' + str(index + 1), '1')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex2')
                                    worksheet.write('F' + str(index + 1), '1')

                            if maintypeRandom == 1 and (rand1 == 2 or rand1 == 3):
                                worksheet.write('B' + str(index + 1), '0')

                                imageStims[rand2].setPos(positions[rand1])
                                imageStims[rand2].draw()

                                win.flip()

                                core.wait(0.3)
                                main_i_counter += 1
                                if rand1 == 2:
                                    worksheet.write('A' + str(index + 1), 'ex2')
                                    worksheet.write('F' + str(index + 1), '2')

                                else:
                                    worksheet.write('A' + str(index + 1), 'ex3')
                                    worksheet.write('F' + str(index + 1), '2')

                            imageStims[rand1].autoDraw = False
                            imageStims[rand2].autoDraw = False
                            questionMark.draw()

                            win.flip()

                            counter = core.CountdownTimer(4)

                            flag = True
                            while flag:
                                keys = event.getKeys(keyList=['end', 'down'])
                                if keys:
                                    for key in keys:
                                        if key == 'end':
                                            worksheet.write('E' + str(index + 1), '1')
                                        if key == 'down':
                                            worksheet.write('E' + str(index + 1), '2')

                                        worksheet.write('G' + str(index + 1), '=IF(E' + str(index + 1) + '= F' +
                                                        str(index + 1) + ',1,0)')
                                        worksheet.write('H' + str(index + 1), str(4 - counter.getTime() + 0.3))
                                        worksheet.write('J' + str(index + 1),
                                                        str(4 - counter.getTime() + 0.3 + trialstart + 1))

                                        flag = False

                                elif counter.getTime() <= 0:
                                    worksheet.write('E' + str(index + 1), 'None')
                                    worksheet.write('H' + str(index + 1), 'None')
                                    worksheet.write('J' + str(index + 1), 'None')
                                    worksheet.write('G' + str(index + 1), 'None')
                                    flag = False
                        flag1 = False
            questionMark.autoDraw = False
            win.flip()

        EndMessage().displayEndMessage()
        workbook.close()
        core.quit()