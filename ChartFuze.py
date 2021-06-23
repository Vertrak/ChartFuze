'''
Author: Vertrak
'''
import tkinter
from tkinter import filedialog
from tkinter import messagebox

##Extract chart data from xml string
def getHeadData(hStr):
	head = []
	tags = ["mapID","path","barPerMin","timeOffset","leftRegion","rightRegion"]
	for i in tags:
		*garbage, data = hStr.split("<m_" + i + ">", 1)
		data, *garbage = data.split("</m_" + i + ">", 1)
		head.append(data)
	return head

##Remove sub notes for easier note handling
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

##Extract note data from xml string
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

##Extract arguement data from xml string
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
	
##Extract chart data from designated file
def readChart(fName):
	try:
		f = open(fName, "rt")
	except FileNotFoundError:
		ti = "Error"
		msg = "File does not exist!"
		messagebox.showerror(title = ti, message = msg)
		return None
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
	return h, [c, l, r], a

##Compile list of notes into a single list
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

##Place sub notes in corresponding location
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

##Write merged chart to file specified
def writeNotes(head, notes, args, fName):
	##Check for filename validity
	try:
		f = open(fName, "xt")
	except FileExistsError:
		##Ask if overwriting
		ti = "Warning"
		msg = "File already exists. Do you wish to overwrite it?"
		ico = "warning"
		cont = messagebox.askyesno(title = ti, message = msg, icon = ico)
		if not cont:
			return
		f = open(fName, "wt")
	
	##Add the chart data to the file
	print('<?xml version="1.0" encoding="UTF-8" ?>', file = f)
	print("<CMap>", file = f)
	hTag = ["m_mapID", "m_path", "m_barPerMin", "m_timeOffset",
		"m_leftRegion", "m_rightRegion"]
	for i in range(6):
		print("<" + hTag[i] + ">" + head[i] + "</" + hTag[i] + ">",file = f)
	
	##Add the notes to the file
	nTag = ["m_type", "m_time", "m_position", "m_width", "m_subId"]
	for i in range(3):
		##Start section
		if i == 0:
			print("<m_notes>", file = f)
		elif i == 1:
			print("<m_notesLeft>", file = f)
		else:
			print("<m_notesRight>", file = f)
		print("<m_notes>", file = f)
		
		##Add section notes
		for j in range(len(notes[i])):
			print("<CMapNoteAsset>", file = f)
			print("<m_id>" + str(j)	+ "</m_id>",file = f)
			for k in range(5):
				print("<" + nTag[k] + ">" + notes[i][j][k]
						+ "</" + nTag[k] + ">",file = f)
			print("</CMapNoteAsset>", file = f)
		
		##End section
		print("</m_notes>", file = f)
		if i == 0:
			print("</m_notes>", file = f)
		elif i == 1:
			print("</m_notesLeft>", file = f)
		else:
			print("</m_notesRight>", file = f)
			
	##Add arguement data to the file
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
def compatible(bHead, sHead, bArg, sArg):
	##Compare head data
	for i in range(6):
		if bHead[i] != sHead[i]:
			return False
	##Compare arguement length
	if len(bArg) != len(sArg):
		return False
	##Compare arguements
	for i in range(len(bArg)):
		if bArg[i] != sArg[i]:
			return False
	return True
	
##Turn single line XML into readable XML
def makeReadable(data):
	i = 0
	while i < len(data) - 1:
		##Insert new line between butted tags
		if data[i] == ">" and data[i + 1] == "<":
			data = data[:i + 1] + "\n" + data[i + 1:]
		i += 1
	return data
	
##Check for xml file actually being a proper chart
def isChart(fName):
	try:
		f = open(fName, "rt")
	except FileNotFoundError:
		ti = "Error"
		msg = "File does not exist!"
		messagebox.showerror(title = ti, message = msg)
		return False
	
	##All possible tags that appear in a valid map
	tags = ["CMap","m_mapID","m_path","m_barPerMin","m_timeOffset","status",
			"m_leftRegion","m_rightRegion","m_notes","CMapNoteAsset","m_id",
			"m_type","m_time","m_position","m_width","m_subId","m_notesLeft",
			"m_notesRight","m_argument","m_bpmchange","CBpmchange","m_value"]
	data = f.read()
	if data.find("\n") == -1:
		data = makeReadable(data)
	data = data.split("\n")
	
	
	
	f.close()
	return True
	

def getBase():
	fTypes = (("eXtensible Markup Language", "*.xml"),("All Types", "*.*"))
	return filedialog.askopenfilename(filetypes = fTypes)
	
def getFiles():
	fTypes = (("eXtensible Markup Language", "*.xml"),("All Types", "*.*"))
	return filedialog.askopenfilenames(filetypes = fTypes)

##Main function
if __name__ == "__main__":
	'''
	root = tkinter.Tk()
	root.title("Dynamix Chart Merger")
	root.geometry("768x480")
	#frame = tkinter.Frame(root)
	fNames = tkinter.Entry(root, font = 12)
	fNames.pack()
	bTxt = "Select Base File"
	bButton = tkinter.Button(root, text = bTxt, command = getBase)
	bButton.pack()
	fTxt = "Add Sections"
	fButton = tkinter.Button(root, text = fTxt, command = getFiles)
	fButton.pack()
	print("files:")
	print(fList)
	root.mainloop()
	'''
	fName = input("Enter filename: ")
	print(isChart(fName))
	'''
	head, notes, args = readChart(fName)
	print("args", args)
	notes = removeSub(notes)
	notes = mergeNotes(notes)
	notes = addSub(notes)
	name, ext = fName.rsplit(".", 1)
	name += "Test." + ext
	writeNotes(head, notes, args, name)
	'''
