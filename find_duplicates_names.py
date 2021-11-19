import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import collections
    
class FindDupes():
    def __init__(self, app):
        self.app = app
        self.ui = self.app.userInterface        
        self.duplicates = []
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def log_dupes(self, things, path = ''):
        thing_names =  [d.name for d in things]
        
        for item, count in collections.Counter(thing_names).items():
            if count > 1:
                self.duplicates.append("detected multiple \"{}\" named \"{} / {}\"".format(things.__class__.__name__, path, item))
                

    def _traverse_folders(self, folder, path):
        self.log_dupes(folder.dataFiles, path)
    
        for sub_folder in folder.dataFolders:
            self._traverse_folders(sub_folder, path + ' / ' + sub_folder.name)

        
    def run(self):
        self.progressDialog = self.ui.createProgressDialog()
        self.progressDialog.cancelButtonText = 'Cancel'
        self.progressDialog.isBackgroundTranslucent = False
        self.progressDialog.isCancelButtonShown = True
        self.progressDialog.show("Scanning", "Analysing project %v of %m", 0, len(self.app.data.activeHub.dataProjects))

        self.log_dupes(self.app.data.activeHub.dataProjects)
        
        for project in self.app.data.activeHub.dataProjects:
            if self.progressDialog.wasCancelled:
                raise Exception("Scan aborted")

            self.progressDialog.title = project.name
            self.progressDialog.progressValue += 1
            adsk.doEvents()
            
            root_folder = project.rootFolder
            self._traverse_folders(root_folder, project.name)

        self.ui.messageBox('Duplicates:\n{}'.format('\n'.join(self.duplicates)))


def run(context):
    try:
        app = adsk.core.Application.get()
        with FindDupes(app) as fd:
            fd.run()

    except:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
