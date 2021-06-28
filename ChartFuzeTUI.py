#Author: Vertrak

import tkinter
from tkinter import filedialog
from tkinter import messagebox

#Extract chart data from xml string
def getHeadData(hStr):
	head = []
	tags = ["mapID","path","barPerMin","timeOffset","leftRegion","rightRegion"]
	for i in tags:
		*garbage, data = hStr.split("<m_" + i + ">", 1)
		data, *garbage = data.split("</m_" + i + ">", 1)
		head.append(data)
	return head

#Remove sub notes for easier note handling
def removeSub(notes):
	#remove sub notes
	for i in range(len(notes)):
		#find all corresponding sub notes
		l = []
		for j in range(len(notes[i])):
			if notes[i][j][0] == "HOLD":
				l.append(int(notes[i][j][4]))
				notes[i][j][4] = notes[i][int(notes[i][j][4])]
		#remove sub notes
		while l:
			notes[i].pop(l.pop())
	return notes

#Extract note data from xml string
def getNoteData(nStr):
	garbage, *nData = nStr.split("<CMapNoteAsset>")
	tags = ["id","type","time","position","width","subId"]
	rawNotes = []
	for i in range(len(nData)):
		note = []
		for j in tags:
			*garbage, data = nData[i].split("<m_" + j + ">", 1)
			data, *garbage = data.split("</m_" + j + ">", 1)
			note.append(data)
		rawNotes.append(note)
	notes = []
	for i in range(len(rawNotes)):
		notes.insert(int(rawNotes[i][0]), rawNotes[i][1:])
	return notes

#Extract arguement data from xml string
def getArgData(aStr):
	garbage, *bpms = aStr.split("<CBpmchange>")
	args = []
	for i in bpms:
		*garbage, data = i.split("<m_time>", 1)
		time, data = data.split("</m_time>", 1)
		garbage, data = data.split("<m_value>", 1)
		value, *garbage = data.split("</m_value>", 1)
		args.append([time, value])
	return args
	
#Extract chart data from designated file
def readChart(fName):
	try:
		f = open(fName, "rt")
	except FileNotFoundError:
		print("File doesn't exist!")
		return None, None, None
	data = f.read()
	head, data = data.split("<m_notes>", 1)
	h = getHeadData(head)
	notesC, data = data.split("<m_notesLeft>", 1)
	c = getNoteData(notesC)
	notesL, data = data.split("<m_notesRight>", 1)
	l = getNoteData(notesL)
	notesR, *args = data.split("<m_argument>", 1)
	r = getNoteData(notesR)
	if args:
		a = getArgData(args[0])
	else:
		a = []
	n = [c, l, r]
	n = removeSub(n)
	return h, n, a

#Compile list of notes into a single list
def mergeNotes(nList):
	notes = [[],[],[]]
	for i in range(3):
		#Add notes, organized by time
		for j in range(len(nList[i])):
			add = True
			for k in range(len(notes[i])):
				if float(notes[i][k][1]) > float(nList[i][j][1]):
					notes[i].insert(k, nList[i][j])
					add = False
					break
			if add:
				notes[i].append(nList[i][j])				
	return notes

#Place sub notes in corresponding location
def addSub(notes):
	for i in range(len(notes)):
		j = 0
		while j < len(notes[i]):
			if notes[i][j][0] == "HOLD":
				add = True
				for k in range(len(notes[i])):
					if float(notes[i][k][1]) > float(notes[i][j][4][1]):
						notes[i].insert(k, notes[i][j][4])
						notes[i][j][4] = str(k)
						add = False
						break
				if add:
					notes[i].append(notes[i][j][4])
					notes[i][j][4] = str(len(notes[i]) - 1)
			j += 1
	return notes

#Get user input
def getAction(err, msg, ops):
	#Print error if passed in
	if err:
		print(err)
	#Prompt user until valid response
	ans = input(msg)
	while not ans.lower() in ops:
		print("Invalid response.")
		ans = input(msg)
	return ans

#Write merged chart to file specified
def writeNotes(head, notes, args, fName):
	#Add missing sub notes
	notes = addSub(notes)
	#Check for filename validity
	try:
		f = open(fName, "xt")
	except FileExistsError:
		#Ask if overwriting
		ops = ["y", "n"]
		err = "File already exists!"
		msg = "Would you like to overwrite?(y/n): "
		if getAction(err,msg,ops).lower() == "n":
			return
		f = open(fName, "wt")
	
	#Add the chart data to the file
	print('<?xml version="1.0" encoding="UTF-8" ?>', file = f)
	print("<CMap>", file = f)
	hTag = ["m_mapID", "m_path", "m_barPerMin", "m_timeOffset",
		"m_leftRegion", "m_rightRegion"]
	for i in range(6):
		print("<" + hTag[i] + ">" + head[i] + "</" + hTag[i] + ">",file = f)
	
	#Add the notes to the file
	nTag = ["m_type", "m_time", "m_position", "m_width", "m_subId"]
	for i in range(3):
		#Start section
		if i == 0:
			print("<m_notes>", file = f)
		elif i == 1:
			print("<m_notesLeft>", file = f)
		else:
			print("<m_notesRight>", file = f)
		print("<m_notes>", file = f)
		
		#Add section notes
		for j in range(len(notes[i])):
			print("<CMapNoteAsset>", file = f)
			print("<m_id>" + str(j)	+ "</m_id>",file = f)
			for k in range(5):
				print("<" + nTag[k] + ">" + notes[i][j][k]
						+ "</" + nTag[k] + ">",file = f)
			print("</CMapNoteAsset>", file = f)
		
		#End section
		print("</m_notes>", file = f)
		if i == 0:
			print("</m_notes>", file = f)
		elif i == 1:
			print("</m_notesLeft>", file = f)
		else:
			print("</m_notesRight>", file = f)
			
	#Add arguement data to the file
	print("<m_argument>", file = f)
	print("<m_bpmchange>", file = f)
	for i in args:
		print("<CBpmchange>", file = f)
		print("<m_time>" + str(i[0]) + "</m_time>", file = f)
		print("<m_value>" + str(i[1]) + "</m_value>", file = f)
		print("</CBpmchange>", file = f)
	print("</m_bpmchange>", file = f)
	print("</m_argument>", file = f)
	print("</CMap>",file = f)
	f.close()
	return

##Checks for base and section head and arguement data being equal 
def isCompatible(bHead, sHead, bArg, sArg):
	#Compare head data
	for i in range(6):
		if bHead[i] != sHead[i]:
			return False
	#Compare arguement length
	if abs(len(bArg) - len(sArg)) > 1:
		return False
	#Compare arguements
	if len(bArg) == len(sArg):
		for i in range(len(bArg)):
			if bArg[i] != sArg[i]:
				return False
	#Account for bpm set at 0 bars in bArg but not sArg and empty list
	elif len(bArg) > len(sArg):
		if bArg[0][0] != 0 or bArg[0][1] != sHead[2]:
			return False
		if len(bArg) > 1:
			for i in range(1, len(bArg)):
				if bArg[i] != sArg[i - 1]:	
					return False
	#Account for bpm set at 0 bars in sArg but not bArg and empty list
	else:
		if sArg[0][0] != 0 or sArg[0][1] != bHead[2]:
			return False
		if len(sArg) > 1:
			for i in range(1, len(sArg)):
				if sArg[i] != bArg[i - 1]:	
					return False
	return True
	
#Turn single line XML into readable XML
def makeReadable(data):
	i = 0
	while i < len(data) - 1:
		#Insert new line between butted tags
		if data[i] == ">" and data[i + 1] == "<":
			data = data[:i + 1] + "\n" + data[i + 1:]
		i += 1
	return data
	
##Check for xml file actually being a chart
def isChart(fName):
	print("Note: isChart() is experimental.")
	
	try:
		f = open(fName, "rt")
	except FileNotFoundError:
		print("File does not exist!")
		return False
	
	#All possible tags that appear in a valid map
	general = ["CMapNoteAsset","m_bpmchange",
			"m_notesRight","m_notesLeft",
			"CBpmchange","m_position","m_argument","m_value","m_notes",
			"m_subId","m_width","status","m_time","m_type","m_id"]
	
	unique = [	"Cmap",
				"m_mapID",
				"m_path",
				"m_barPerMin",
				"m_timeOffset",
				"m_leftRegion",
				"m_rightRegion",
				"m_notesLeft",
				"m_notesRight",
				"m_arguement",
				"m_bpmchange"	]
	
	#Check for tags not in list of tags
	data = f.read()
	data = data.replace('<?xml version="1.0" encoding="UTF-8" ?>', '', 1)
	for i in unique:
		data = data.replace('<' + i +'>','',1)
		data = data.replace('</' + i + '>','',1)
	
	data = f.read()
	if data.find("\n") == -1:
		data = makeReadable(data)
	data = data.split("\n")
	
	
	#Check for matching opening and closing tags
	
	#Check for proper nesting of tags
	
	f.close()
	return True
	
#Prompt user for single file
def getFile():
	while 1:
		#Read file name and check extension
		fName = input("Enter file name: ")
		ext = fName.rsplit(".", 1)[-1]
		if ext.lower() != "xml":
			print("Invalid file type!")
			continue
		#Check for file name presence. Print error if invalid.
		try:
			f = open(fName, "rt")
			f.close()
			break
		except FileNotFoundError:
			err = "File does not exist!"
			msg = "Would you like to try again?(y/n)"
			ops = ["y", "n"]
			if getAction(err, msg, ops).lower() == "n":
				break
	return fName
	
#Prompt user for multiple files
def getFiles(fNames):
	#Set up message, options,, response variable, and path separator
	cont = "y"
	msg1 = "Add another file?(y/n): "
	msg2 = "Would you like to see your selected files?(y/n): "
	ops = ["y", "n"]
	err = "File already in list."
	sep = "" if not fNames else "/" if "/" in fNames[0] else "\\"			
	while cont.lower() == "y":
		fName = getFile()
		#Check for duplicate before adding
		if not fName in fNames:
			fNames.append(fName)
			sep = "/" if "/" in fNames[0] else "\\"
		else:
			#Offer to display file list
			if getAction(err,msg2, ops).lower() == "y":
				for i in fNames:
					print(i.rsplit(sep, 1)[-1])
				print()
		cont = getAction("", msg1, ops)
	print("Exit function")
	return fNames

#Prompt user for filename
def getFilename(fName, fun):
	#Set up path separator, messages, options, and illegal characters
	sep = "/" if "/" in fName else "\\"
	msg2 = "Do you wish to save it by a different name?(y/n)"
	ops = ["y", "n"]
	illegal = ["/"]
	if sep != "/":
		illegal = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
	#Get file path and name
	path, name = fName.rsplit(sep, 1)
	nName = name.rsplit(".", 1)[0] + fun + ".xml"
	msg1 = "Default name for file will be:\n\t" + nName
	#Inform user of save location and prompt for filename
	print("File will be stored in the following folder:\n\t" + path)
	if getAction(msg1, msg2, ops).lower() == "y":
		#Inform user of illegal filename characters for OS
		print("The following are illegal charcter(s): ", end = "")
		for i in illegal:
			print(i, end = "")
		print()
		#Prompt user for new filename until valid entry
		while 1:
			nName = input("New file name: ")
			for i in illegal:
				if i in nName:
					print(i + " is an illegal character.")
					continue
			break
		#Terminate with xml extension if not already present
		if nName[-4:] != ".xml":
			nName += ".xml"
	return path + sep + nName

#Main menu
def main():
	menu = (
			"(1) Add files\n"
			"(2) Add basefile\n"
			"(3) Fix files\n"
			"(4) Check charts\n"
			"(5) Merge selection\n"
			"(6) Reset\n"
			"(e) Exit\n"
			)
	
	ops = ["1", "2", "3", "4", "5", "6", "e"]
	
	help = (
			"You noob!\n"
			"Note: When adding files just drag and drop file over terminal."
			"This will give the program the full filepath.\n"
			"Add files: add as many files as user wants to working list.\n"
			"Add basefile: include template file. Chart files not matching"
			"template's chart info and BPMs displayed and ignored at merge."
			"This is not required but it is recomended.\n"
			"Fix files: reformat all working files.\n"
			"Check charts: checks all files for valid charts.\n"
			"Reset: Clear all file selections.\n"
			"Exit: Exit the program.\n"
			)
	bFile = ""
	fNames = []
	
	choice = getAction("Menu:", menu, ops)
	
	while choice.lower() != "e":
		if choice == "1":	#Add files
			fNames = getFiles(fNames)
			if fNames:
				sep = "/" if "/" in fNames[0] else "\\"
		
		elif choice == "2":	#Add basefile
			bFile = getFile()
			if bFile:
				sep = "/" if "/" in bFile else "\\"
		
		elif choice == "3":	#Fix files
			if not fNames:
				print("No files have been selected yet.")
			else:
				for i in fNames:
					h, n, a = readChart(i)
		
		elif choice == "4":	#Check Charts
			if not fNames:
				print("No files have been selected yet.")
			else:
				for i in fNames:
					if not isChart(i):
						print(i.rsplit(sep, 1)[-1], "is not a valid chart.")
		
		elif choice == "5":	#Merge selected charts
			if not fNames:
				print("No files have been selected yet.")
			else:
				#Set up data lists
				heads = []
				notes = []
				args = []
				#Read all the file data
				for i in fNames:
					h, n, a = readChart(i)
					heads.append(h)
					notes.append(n)
					args.append(a)
				print(args)
				##Check all files are compatible with each other
				for i in range(len(fNames) - 1):
					for j in range(i + 1, len(fNames)):
						if not isCompatible(heads[i],heads[j],args[i],args[j]):
							print(fNames[i].rsplit(sep, 1)[-1],
									"is not compatible with",
									fNames[j].rsplit(sep, 1)[-1])
				#Complete the merge
				aNotes = [[],[],[]]
				for i in notes:
					for j in range(3):
						aNotes[j].extend(i[j])
				sNotes = mergeNotes(aNotes)
				nName = getFilename(fNames[0], "Merge")
				writeNotes(heads[0], sNotes, args[0], nName)
		
		elif choice == "6":	#Reset
			msg = "Are you sure you want to reset?(y/n): "
			ops = ["y", "n"]
			if getAction("", msg, ops).lower() == "y":
				bFile = ""
				fNames = []
			
		choice = getAction("Menu:", menu, ops)
	return

#Check if main file
if __name__ == "__main__":
	main()
else:
	Print("Wait, you're using ChartFuze as a module?")