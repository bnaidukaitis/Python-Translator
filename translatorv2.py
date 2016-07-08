# FRIES/MITRE/Pitt Translator
# Created by Bryce Aidukaitis
# June 14th, 2016

import os
from os import listdir
import json
import csv
from pprint import pprint
from tkinter import *
from urllib.request import urlopen

# sumStrings converts a list of string into a comma-separated combined string
def sumStrings(listOfStrings):
    if isinstance(listOfStrings, list):
        allStrings = listOfStrings[0]
        for index in range(1, len(listOfStrings)):
                           allStrings += ', ' + listOfStrings[index]
        return allStrings
    else:
        return listOfStrings
# end sumStrings
    
# declareColumnHeaders Creates an array of column headers for our model file 
def declareColumnHeaders():
    columnHeaders = ['#',                           # 0
                      'Full Element Name',          # 1
                      'Importance',                 # 2
                      None,                         # 3
                      'Element name',               # 4
                      'Element type',               # 5
                      'Database ID',                # 6
                      'Element ID',                 # 7
                      'Cell line',                  # 8
                      'Cell type',                  # 9
                      'Organism',                   # 10
                      'Tissue type',                # 11
                      'Location',                   # 12
                      'Location identifier',        # 13
                      'NOTES',                      # 14
                      None,                         # 15
                      'Variable name',              # 16
                      'Model Input (I) Output (O)', # 17
                      'Spontaneously Restores (R) Degrades (D)',    # 18
                      'Type of value: Activity (A) Amount (C) Process (P)', #19
                      'Begin',                      # 20
                      'End',                        # 21
                      'Sim End',                    # 22
                      'Begin',                      # 23
                      'End',                        # 24
                      'Sim End',                    # 25
                      'Begin',                      # 26
                      'End',                        # 27
                      'Sim End',                    # 28
                      'NOTES',                      # 29
                      None,                         # 30
                      'No. of reg.',                # 31
                      'Positive',                   # 32
                      'Negative',                   # 33
                      'Interaction Direct (D) Indirect (I)',    # 34
                      'Mechanism type for direct (D)',          # 35
                      'NOTES',                                  # 36
                      None,                                     # 37
                      'Unique ID (text)',                       # 38
                      'Element kind',                           # 39
                      'Element sub-type',                       # 40
                      None,                                     # 41
                      'References for model connections'        # 42
                    # 'FRIES Context ID',                       # 43
                    # 'FRIESEntity-mention ID',                 # 44                          # 44
        ]            
    return columnHeaders
# end declareColumnHeaders

# removeRowsWithEmptyColumns removes rows from an array "modelData" that do
# not contain a value other than "nullValue" in the column "columnToCheck"
def removeRowsWithEmptyColumns(array, columnToCheck, nullValue):
    # Make a list of the row indices for later removal
    badRows = []
    # Search for rows to remove
    for i in range(len(array)):
        if array[i][columnToCheck] == nullValue:
            # Make a list of the index for later removal
            badRows.append(i)
    if len(badRows) == 0:
        # There were no rows to delete--return the original array
        return array
    else:
        # Recreate the list without rows with numbers listed in badRows
        newArray = [None] * (len(array) - len(badRows))
        badIndex = 0
        for i in range(len(array)):
            if i in badRows:
                badIndex += 1
            else:
                newArray[i - badIndex] = array[i]
        return newArray
# end removeRowsWithEmptyColumns       

# writeToCSV writes the data in modelData with column header defined by
# columnHeaders to a file fileName
def writeToCSV(modelData, columnHeaders, fileName):
    try:
        with open(fileName, 'w') as csvfile:
            modelfile = csv.writer(csvfile, dialect = 'excel', delimiter=',',
                                   lineterminator = '\n'
                                   #quotechar='|',
                                   #quoting=csv.QUOTE_MINIMAL
                                   )
            modelfile.writerow(columnHeaders)
            modelfile.writerows(modelData)
    except PermissionError:
        print("Please close the file " + fileName + " and try again.")
# end writeToCSV

# translateMITRE translates a single MITRE file at the path filePath
# and returns the data
def translateMITRE(filePath):
    modelData = [None] * 46

    # Import JSON file
    with open(filePath) as MITREData:
        data = json.load(MITREData)

    # Extract reference article    
    modelData[42] = data["pmc_id"]
    # For convenience, limit data to interaction data
    data = data["interaction"]

    try:
        data["participant_b"]["entities"]
    except KeyError:
        # participant_b is the element under study - set its name
        modelData[4] = sumStrings(data["participant_b"]["entity_text"])
        # Set its type
        modelData[5] = data["participant_b"]["entity_type"]
        # Set its database type
        try:
            modelData[6] = data["participant_b"]["identifier"][:data["participant_b"]["identifier"].index(':')]
            # Set its database value (number)
            modelData[7] = data["participant_b"]["identifier"][data["participant_b"]["identifier"].index(':')+1:]
        except ValueError:
            modelData[6] = data["participant_b"]["identifier"] # Works in the case that the identifier is "ungrounded"
            modelData[7] = data["participant_b"]["identifier"]
    else:
        data["participant_b"]["entities"][0]["entity_text"] = sumStrings(data["participant_b"]["entities"][0]["entity_text"])
        modelData[4] = data["participant_b"]["entities"][0]["entity_text"]
        for j in range(1, len(data["participant_b"]["entities"])):
            data["participant_b"]["entities"][j]["entity_text"] = sumStrings(data["participant_b"]["entities"][j]["entity_text"])
            modelData[4] += ', ' + data["participant_b"]["entities"][j]["entity_text"]

        modelData[5] = data["participant_b"]["entities"][0]["entity_type"]
        for j in range(1, len(data["participant_b"]["entities"])):
            modelData[5] += ', ' + data["participant_b"]["entities"][j]["entity_type"]

        try:
            modelData[6] = data["participant_b"]["entities"][0]["identifier"][:data["participant_b"]["entities"][0]["identifier"].index(':')]
            for j in range(1, len(data["participant_b"]["entities"])):
                modelData[6] += ', ' + data["participant_b"]["entities"][j]["identifier"][:data["participant_b"]["entities"][j]["identifier"].index(':')]

            modelData[7] = data["participant_b"]["entities"][0]["identifier"][data["participant_b"]["entities"][0]["identifier"].index(':')+1:]
            for j in range(1, len(data["participant_b"]["entities"])):
                modelData[7] += ', ' + data["participant_b"]["entities"][j]["identifier"][data["participant_b"]["entities"][j]["identifier"].index(':')+1:]
        except ValueError:
            modelData[6] = data["participant_b"]["entities"][0]["identifier"]
            for j in range(1, len(data["participant_b"]["entities"])):
                modelData[6] += ', ' + data["participant_b"]["entities"][j]["identifier"]

            modelData[7] = data["participant_b"]["entities"][0]["identifier"]
            for j in range(1, len(data["participant_b"]["entities"])):
                modelData[7] += ', ' + data["participant_b"]["entities"][j]["identifier"]
    # Determine what regulators exist and populate the appropriate fields
    if data["interaction_type"] == "increases":
        # participant_a is a positive regulator of participant_b
        modelData[32] = sumStrings(data["participant_a"]["entity_text"])
    elif data["interaction_type"] == "decreases":
        # participant_a is a negative regulator of participant_b
        modelData[33] = sumStrings(data["participant_a"]["entity_text"])

    # Return the translated data
    modelData = [modelData]
    return modelData
# end translateMITRE

def translateMultipleMITRE(JSONFolderPath):
    # Make a list of files in the current directory
    os.chdir(JSONFolderPath)
    fileList = listdir()
    
    # Create an empty array in which to store the Pitt model data as we translate
    modelData = [None] * len(fileList)

    for i in range(len(fileList)):
        modelData[i] = translateMITRE(fileList[i])[0]
        
    # Return the translated data
    return modelData
# end translateMultipleMITRE

# loadEntities loads a JSON file at a specified path filePath and directory.
# If the file does not exist at that path and directory, a warning is printed.
def loadEntities(filePath):
    import json
    try:
        with open(str(filePath)) as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("The file " + filePath + " does not exist.")
# end loadEntities

# translateFRIES translates the JSON data in FRIES format at the path filePath
# and returns it.
def translateFRIES(filePath):
    with open(filePath) as FRIESData:
        data = json.load(FRIESData)

    # For simplicity, limit data to frames and not meta information
    data = data["frames"]
    # Create an empty array in which to store the Pitt model data as we translate
    modelData = [None] *len(data)

    for i in range(len(data)):
        modelData[i] = [None] * 46

    for i in range(len(data)):
        if len(data[i]["arguments"]) == 1:
            # Make this the element under study
            try:
                modelData[i][4] = data[i]["arguments"][0]["text"]
            except KeyError:
                continue
            # Name the event taking place (e.g. "phosphorylation")
            try:
                modelData[i][35] = data[i]["subtype"]
                # Extract "entity-mention" ID for later analysis
                modelData[i][44] = data[i]["arguments"][0]["arg"]
            except KeyError:
                pass
        else:
            try:
                for j in range(len(data[i]["arguments"])):
                    if data[i]["arguments"][j]["type"] == "controlled":
                        # Make this the element under study
                        modelData[i][4] = data[i]["arguments"][j]["text"]
                        if "arg" in data[i]["arguments"][j]:
                            modelData[i][44] = data[i]["arguments"][j]["arg"]
                    elif data[i]["arguments"][j]["type"] == "controller":
                        # Make this the regulator, depending on event type/subtype
                        if data[i]["subtype"] == "positive-activation" or data[i]["subtype"] == "positive-regulation":
                            modelData[i][32] = data[i]["arguments"][j]["text"]
                            modelData[i][35] = "positive activation"
                        elif data[i]["subtype"] == "negative-activation" or data[i]["subtype"] == "negative-regulation":
                            modelData[i][33] = data[i]["arguments"][j]["text"]
                            modelData[i][35] = "negative activation"
                        else:
                            modelData[i][32] = data[i]["arguments"][j]["text"]
                            modelData[i][35] = data[i]["subtype"]
                        # Extract the "entity-mention" ID of this regulator for later analysis
                        if "arg" in data[i]["arguments"][j]:
                            modelData[i][44] = data[i]["arguments"][j]["arg"]
            except KeyError:
                pass
        try:
            # Extract PubMed reference
            modelData[i][42] = data[i]["frame-id"][data[i]["frame-id"].index("PMC"):data[i]["frame-id"][data[i]["frame-id"].index("PMC"):].index("-") + data[i]["frame-id"].index("PMC")]
            # Extract "context" ID for later analysis
            modelData[i][43] = data[i]["context"]
        except KeyError:
            pass
    # return the translated data
    return modelData
# end translateFRIES

# addContextAndEntityInformation adds linked context and entity data to that
# contained in modelData from the file contextFilePath
def addContextAndEntityInfo(modelData, contextFilePath):
    # Compare with entity and context information
    ent = loadEntities(contextFilePath)
    try:
        frames = ent["frames"]
    except KeyError:
        print("No frame information availabe in selected entity file.")
        return

    frameTypes = [None] * len(frames)
    typeListing = {}
    for i in range(len(frames)):
        frameTypes[i] = frames[i]["frame-type"]
        if frameTypes[i] not in typeListing:
            typeListing[frameTypes[i]] = 1
        else:
            typeListing[frameTypes[i]] += 1

    contexts = [None] * typeListing["context"]
    entities = [None] * typeListing["entity-mention"]

    j = 0
    k = 0
    for i in range(len(frames)):
        if frames[i]["frame-type"] == "context":
            contexts[j] = frames[i]
            j += 1
        elif frames[i]["frame-type"] == "entity-mention":
            entities[k] = frames[i]
            k += 1

    contextIndices = {}
    for i in range(len(contexts)):
        contextIndices[contexts[i]["frame-id"]] = i
    entityIndices = {}
    for i in range(len(entities)):
        entityIndices[entities[i]["frame-id"]] = i

    yesno = {"yes":0, "no":0}
    for i in range(len(modelData)):
        try:
            if modelData[i][43][0] in contextIndices:
                yesno["yes"] += 1
            else:
                yesno["no"] += 1
        except TypeError:
            # There is no context information available for this entity. 
            pass
    #print("Contexts available:")
    #pprint(yesno)

    yesno = {"yes":0, "no":0}
    for i in range(len(modelData)):    
        if modelData[i][44] in entityIndices:
            yesno["yes"] += 1
        else:
            yesno["no"] += 1
    #print("Entities available:")
    #pprint(yesno)

    # Place context and entity information into model
    for i in range(len(modelData)):
        # Begin by placing entity information into the model
        if modelData[i][44] in entityIndices:
            thisEntity = entities[entityIndices[modelData[i][44]]]
            # Extract element type
            modelData[i][5] = thisEntity["type"]

            # Extract other useful information about the element
            modelData[i][6] = thisEntity["xrefs"][0]["namespace"]
            modelData[i][7] = thisEntity["xrefs"][0]["id"]
                
            # Use the entity's context ID if event context is unavailable
            contextAvailable = False
            availableContextIndex = 0
            try:
                for j in range(len(modelData[i][43])):
                    if modelData[i][43][j] in contextIndices:
                        contextAvailable = True
                        availableContextIndex = j
            except TypeError:
                # No context information available for this element.
                pass
            if not contextAvailable and "context" in thisEntity:
                modelData[i][43] = thisEntity["context"]

        # Place context information into model
        try:
            if modelData[i][43][availableContextIndex] in contextIndices:
                thisContext = contexts[contextIndices[modelData[i][43][availableContextIndex]]]
                # Set cell line and remove superfluous characters
                if "cell-line" in thisContext["facets"]:
                    modelData[i][8] = thisContext["facets"]["cell-line"][0]
                    if modelData[i][8].count(":") > 1:
                        modelData[i][8] = modelData[i][8][modelData[i][8].index(":") + 1:]
                # Set cell type and remove superfluous characters
                if "cell-type" in thisContext["facets"]:
                    modelData[i][9] = thisContext["facets"]["cell-type"][0]
                    if modelData[i][9].count(":") > 1:
                        modelData[i][9] = modelData[i][9][modelData[i][9].index(":") + 1:]
                # Set organism and remove superfluous characters
                if "organism" in thisContext["facets"]:
                    modelData[i][10] = thisContext["facets"]["organism"][0]
                    if modelData[i][10].count(":") > 1:
                        modelData[i][10] = modelData[i][10][modelData[i][10].index(":") + 1:]
                # Set tissue type and remove superfluous characters
                if "tissue-type" in thisContext["facets"]:
                    modelData[i][11] = thisContext["facets"]["tissue-type"][0]
                    if modelData[i][11].count(":") > 1:
                        modelData[i][11] = modelData[i][11][modelData[i][11].index(":") + 1:]
        except TypeError:
            # No context info available for this element.
            pass
    # return the enhanced data
    return modelData
# end addContextAndEntityInfo

# consolidateDuplicates analyzes what rows involve the same element and fills
# in blank entries in that row that are not blank in "duplicate" rows
def consolidateDuplicates(modelData):
    # Compare entries for the same element
    duplicateRows = []

    for i in range(len(modelData)):
        if i in duplicateRows:
            continue
        duplicates = 0
        duplicateIndex = []
        for j in range(len(modelData)):
            if i == j:
                continue
            elif modelData[i][4] == modelData[j][4]:
                duplicates += 1
                duplicateIndex.append(j)
                duplicateRows.append(j)
        if duplicates == 0:
            continue
        else:
            # Consolidate information
            for j in range(duplicates):
                # If an element is in one row and not the other, add it
                for k in range(43):
                    if k == 32 or k == 33:
                         # Compare positive and negative regulators, make a list...
                        if modelData[i][k] == None and modelData[duplicateIndex[j]][k] == None:
                            continue
                        elif modelData[i][k] == None and modelData[duplicateIndex[j]][k] != None:
                            modelData[i][k] = modelData[duplicateIndex[j]][k]
                        elif modelData[i][k] != None and modelData[duplicateIndex[j]][k] != None:
                            if modelData[duplicateIndex[j]][k] not in modelData[i][k]:
                                modelData[i][k] += ', ' + modelData[duplicateIndex[j]][k]
                    else:
                        if modelData[i][k] == None and modelData[duplicateIndex[j]][k] == None:
                            continue
                        elif modelData[i][k] == None and modelData[duplicateIndex[j]][k] != None:
                            modelData[i][k] = modelData[duplicateIndex[j]][k]
        ##                elif modelData[i][k] != None and modelData[duplicateIndex[j]][k] != None and modelData[i][k] != modelData[duplicateIndex[j]][k]:
        ##                    modelData[i][k] += ", " + modelData[duplicateIndex[j]][k]
                if modelData[i][32] != None and modelData[i][33] != None:
                            modelData[i][35] = "Multiple"
                    
    if len(duplicateRows) > 0:
        newArray = [None] * (len(modelData) - len(duplicateRows))
        badIndex = 0
        for i in range(len(modelData)):
            if i in duplicateRows:
                badIndex += 1
            else:
                newArray[i - badIndex] = modelData[i]
        modelData = newArray

    # return the consolidated data
    return modelData
# end consolidateDuplicates

# pittify returns an array that does not contain information not used in the
# PITT formalism (i.e. columns 43+ that contain FRIES entity/context info
def pittify(modelData):
    printableData = [None] * len(modelData)
    for i in range(len(modelData)):
        printableData [i] = modelData[i][0:43]

    # return the pittified data
    return printableData
# end pittify

# linkDB uses external databases from database identifiers to complete
# missing fields for an element. 
def linkDB(modelData):
    if modelData[12] == None:
        # Get location information from database ID
        if modelData[6] == "Uniprot":
            try:
                url = 'http://www.uniprot.org/uniprot/' + modelData[7]
                body = str(urlopen(url).read())
                index = body.index('<ul class="noNumbering cellular_component">')
                end = index + body[index:].index("</a>")
                subcellLoc = body[index:end]
                beginGo = subcellLoc[subcellLoc.index("GO:"):]
                idGO = beginGo[:beginGo.index('"')]
                rev = rev = subcellLoc[::-1].index(">")
                location = subcellLoc[len(subcellLoc)-rev:]
                modelData[12] = location
                modelData[13] = idGO
            except ValueError:
                pass
    return modelData
# end linkDB





# The main loop of the program

origType = None
incorrectAttempts = 0
root = Tk()
##root.withdraw()

textBoxText = "Welcome to the translator!\nPlease select an original file type to translate to the Pitt formalism."
modelData = []

class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
    def createWidgets(self):
        # Text box
        self.title = LabelFrame(self, text="FRIES/MITRE/Pitt Translator")
        self.title.pack(fill="both", expand=1)
        self.left = Label(self.title, text=textBoxText)
        self.left["justify"] = "left"
        self.left["width"] = 50
        self.left.pack(fill="both", expand=1)

        # FRIES select button
        self.fries = Button(self)
        self.fries["text"] = "FRIES"
        self.fries["command"] = self.selectFRIES
        self.fries["width"] = 10
        self.fries["height"] = 3
        self.fries["border"] = 3
        self.fries["font"] = ["calibri", 24, "bold"]
        self.fries["anchor"] = "center"
        self.fries.pack(side="left", padx=30, pady=30, fill="both")

        # MITRE select button
        self.mitre = Button(self)
        self.mitre["text"] = "MITRE"
        self.mitre["command"] = self.selectMITRE
        self.mitre["width"] = 10
        self.mitre["height"] = 3
        self.mitre["border"] = 3
        self.mitre["font"] = ["calibri", 24, "bold"]
        self.mitre["anchor"] = "center"
        self.mitre.pack(side = "right", padx=30, pady=30, fill="both")

    def selectFRIES(self):
        # Delete the selection buttons and update text box
        self.fries.destroy()
        self.mitre.destroy()
        self.left["text"] = "Select a FRIES file for translation.\n"
        
        # Ask for a file to read
        filePath = filedialog.askopenfilename()
        
        # Translate from FRIES to Pitt
        global modelData
        modelData = translateFRIES(filePath)

        # Ask if done or if user wants to link context and entity information
        # from an entity JSON file in FRIES format.
        self.left["text"] = "Translation from FRIES to Pitt successful.\n"
        self.left["text"] += "Would you like to add context and entity information?\n"
        self.addEntities = Button(self, text="Link Entity File",
                                  command=self.addEntityInfo, width=13, height=3,
                                  border=3, font=["calibri",24,"bold"])
        self.addEntities.pack(side="right", padx=30, pady=30, fill="both", expand=1)

        self.save = Button(self, text="Save Output",
                           command=self.saveOutput, width=10, height=3,
                           border=3, font=["calibri",24,"bold"])
        self.save.pack(side="left", padx=30, pady=30, fill="both", expand=1)

    def addEntityInfo(self):
        self.left["text"] = "Select matching entity file, if any.\n"
        
        options = {}
        options["title"] = "Select matching entity file, if any\n"
        options["filetypes"] = [("JSON",".json"), ("Text files", ".txt"), ("All files", ".*")]
        entityFilePath = filedialog.askopenfilename(**options)
        global modelData
        
        try:
            addContextAndEntityInfo(modelData, entityFilePath)
            self.addEntities.destroy()
            self.left["text"] = "Entities linked successfully.\n"
        except KeyError:
            self.left["text"] = "KeyError... No context or entity information added.\n"

    def selectMITRE(self):
        self.fries.destroy()
        self.mitre.destroy()

        self.left["text"] = "You can translate a single MITRE file or a folder "
        self.left["text"] += "containing many MITRE files.\n"
        
        self.singleMitre = Button(self, text="Single file",
                                  command=self.mitreFile, width=10, height=3,
                                  border=3, font=["calibri",24,"bold"])
        self.singleMitre.pack(side="left", padx=30, pady=30, fill="both", expand=1)
        
        self.folderMitre = Button(self, text="Folder",
                                  command=self.mitreFolder, width=10, height=3,
                                  border=3, font=["calibri",24,"bold"])
        self.folderMitre.pack(side="left", padx=30, pady=30, fill="both", expand=1)

    def mitreFile(self):
        self.singleMitre.destroy()
        self.folderMitre.destroy()
        
        self.left["text"] = "Select a MITRE file to translate.\n"
        path = filedialog.askopenfilename()
        global modelData

        # Translate a single file from MITRE to Pitt
        modelData = translateMITRE(path)
        self.left["text"] = "Translation from MITRE to Pitt successful.\n"
        self.left["text"] += "Save output as .csv?\n"

        self.save = Button(self, text="Save Output",
                           command=self.saveOutput, width=10, height=3,
                           border=3, font=["calibri",24,"bold"])
        self.save.pack(side="left", padx=30, pady=30, fill="both", expand=1)

        
    def mitreFolder(self):
        self.folderMitre.destroy()
        self.singleMitre.destroy()
        
        self.left["text"] = "Select a folder containing MITRE files.\n"
        self.left["text"] += "Output will be a multi-row spreadsheet.\n"
        path = filedialog.askdirectory()
        global modelData

        # Translate multiple files from a folder.
        # folderPath = filedialog.askdirectory(**options)
        modelData = translateMultipleMITRE(path)
        self.left["text"] = "Translation from MITRE to Pitt successful.\n"
        self.left["text"] += "Save output to .csv?\n"

        self.save = Button(self, text="Save Output",
                           command=self.saveOutput, width=10, height=3,
                           border=3, font=["calibri",24,"bold"])
        self.save.pack(side="left", padx=30, pady=30, fill="both", expand=1)

    def saveOutput(self):
        self.save.destroy()
        try:
            self.addEntities.destroy()
        except:
            pass
        
        self.left["text"] = "Preparing data..."
        global modelData
        # Remove empty rows, handle duplicate rows, and remove columns 43+
        modelData = removeRowsWithEmptyColumns(modelData, 4, None)
        modelData = pittify(modelData)
        modelData = consolidateDuplicates(modelData)

        #for i in range(len(modelData)):
            #self.left["text"] = "Preparing data...\nFetching info from external databases: " + str(i) + "/" + str(len(modelData))
            #modelData[i] = linkDB(modelData[i])
        self.left["text"] = "Data is ready to save.\nPlease name the output file.\n"
        
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV (Comma delimited)', '.csv'),('All files', '.*')]
        options['title'] = 'Save Output'
        #options['initialdir'] = os.getcwd()
        outputPath = filedialog.asksaveasfilename(**options)

        # Write to CSV
        writeToCSV(modelData, declareColumnHeaders(), outputPath)

        self.left["text"] = "Save successful.\n"
        self.left["text"] += "Would you like to translate another file, or are you done?"

        self.again = Button(self, text="Translate\n additional files",
                            command=self.doAgain, width=16, height=3,
                            border=3, font=["calibri",24,"bold"])
        self.again.pack(side="left", padx=30, pady=30, fill="both", expand=1)
        
        self.quit = Button(self, text="Quit",
                           command=root.destroy, width=10, height=3,
                           border=3, font=["calibri",24,"bold"])
        self.quit.pack(side="right", padx=30, pady=30, fill="both", expand=1)

    def doAgain(self):
        try:
            self.again.destroy()
        except:
            pass
        try:
            self.quit.destroy()
        except:
            pass
        try:
            self.title.destroy()
        except:
            pass
        try:
            self.left.destroy()
        except:
            pass
        
        self.createWidgets()

# create the application
myapp = App(master=root)

myapp.master.title("Translator")
myapp.master.minsize(640, 320)

myapp.mainloop()        
