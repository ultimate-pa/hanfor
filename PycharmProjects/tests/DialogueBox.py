from psychopy import gui

class dialoguebox(object):
    def showDialogBox(self):
        Dlg = gui.Dlg(title="Navon Task", pos=(525, 250))
        Dlg.addField('Subject Name')
        Dlg.addField('Subject Number')
        Dlg.addField('Experiment Day', choices=['1', '2', '3'])
        Dlg.addField('Gender', choices=['Male', 'Female'])
        Dlg.addField('Age')
        Dlg.addField('Stimulation Site', choices=['R-PPC', 'L-PPC', 'CZ'])
        Dlg.addField('Session', choices=['1', '2'])
        ok_data = Dlg.show()

        subjectName = ok_data[0]
        subjectNumber = ok_data[1]
        dayNumber = ok_data[2]
        subjectGender = ok_data[3]
        subjectAge = ok_data[4]
        stimSite = ok_data[5]
        sessionNumber = ok_data[6]

        subjectInfo = [subjectName, subjectNumber, dayNumber, subjectGender, subjectAge,  stimSite, sessionNumber]
        return subjectInfo

