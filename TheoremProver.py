#Imports
import shlex, re

#Data Structures
root_variables = {}
learned_variables = {}
facts = []
rules = []
output = []

#Classes
class Variable:
	def __init__(self, name, value, vtype):
		self.name = name
		self.value = value
		self.type = vtype

class rule:
	def __init__(self, postfix, infix, consequence):
		self.postfix = postfix
		self.infix = infix
		self.consequence = consequence

#Functions
def list():
	print("Root Variables:")
	for k,v in root_variables.items():
		print("\t" + k + " = " + "\"" + v + "\"")
	print("Learned Variables:")
	for k,v in learned_variables.items():
		print("\t" + k + " = " + "\"" + v + "\"")
	print("Facts:")
	for f in facts:
		print("\t" + f)
	print("Rules:")
	for r in rules:
		print("\t" + r.infix + " -> " + r.consequence)

def newVariable(name, value, vtype):
	if name in learned_variables.keys() or name in root_variables.keys():
		return#print("Error. A variable with that name already exists.")
	elif(vtype == "-L"):
		learned_variables[name] = value
	elif(vtype == "-R"):
		root_variables[name] = value
	else:
		return#print("Error. Invalid argument")

def updateRootVariable(name, value):
	if name in learned_variables:
		return#print("Error. User tried to set a learned variable directly.")
	elif name in root_variables:
		if name in facts and value == "false":
			facts.remove(name)
		elif name not in facts and value == "true":
			facts.append(name)
		for x in facts:
			if x in learned_variables:
				facts.remove(x)
	else:
		return#print("Error. No variable with that name exists.")

def newRule(expression, name):
	if name not in learned_variables:
		#print("Error. Variable must be a learned variable.")
		return
	postfix = toPostfix(expression)
	if(len(postfix) == 0):
		return#print("Error. Invalid expression.") 
	else:
		rules.append(rule(postfix, expression, name))

def toPostfix(infix):
	words = re.split('(\W)', infix)
	words = [w for w in words if w != '']
	queue = []
	stack = []
	for word in words:
		if word == "!":
			stack.append(word)
		elif word == "&":
			while len(stack) > 0 and stack[-1] == "!" and stack[-1] != "(":
				queue.append(stack.pop())
			stack.append(word)
		elif word == "|":
			while len(stack) > 0 and stack[-1] != "|" and stack[-1] != "(":
				queue.append(stack.pop())
			stack.append(word)
		elif word == "(":
			stack.append(word)
		elif word == ")":
			while len(stack) > 0 and stack[-1] != "(":
				queue.append(stack.pop())
			stack.pop()
		else:
			if word not in learned_variables and word not in root_variables:
				return []
			queue.append(word)
	while(len(stack) > 0):
		queue.append(stack.pop())
	return queue

def executeRule(rule, backwardchaining):
	if rule.consequence in facts:
		return True

	index = 0
	postfix = rule.postfix.copy()

	#Convert variables to boolean values
	for i in range(len(postfix)):
		if postfix[i] not in ['&', '!', '|']:
			if postfix[i] in facts:
				postfix[i] = True
			else:
				if backwardchaining:
					for rule in (x for x in rules if x.consequence == postfix[i]):
						if executeRule(rule, True):
							postfix[i] = True
							break
				if postfix[i] != True:
					postfix[i] = False


	#Apply operators to operands until one value remains
	while(len(postfix) > 1):
		if postfix[index] not in ['&', '!', '|']:
			index += 1
		else:
			if postfix[index] == '!':
				postfix.pop(index)
				postfix[index-1] = not postfix[index-1]
			elif postfix[index] == '&':
				postfix.pop(index)
				first = postfix.pop(index - 2)
				second = postfix.pop(index - 2)
				postfix.insert(index-2,first and second)
				index -= 1
			elif postfix[index] == '|':
				postfix.pop(index)
				first = postfix.pop(index - 2)
				second = postfix.pop(index - 2)
				postfix.insert(index-2,first or second)
				index -= 1
	if postfix[0] == True:
		return True
	return False


def learn():
	applied = 1
	remove = []
	rulescopy = rules.copy()
	while(applied > 0):
		applied = 0
		for rule in rulescopy:
			if executeRule(rule, False):
				remove.append(rule)
				if rule.consequence not in facts:
					facts.append(rule.consequence)
				applied += 1
		for i in remove:
			rulescopy.remove(i)
		remove.clear()

	

def query(expression):
	postfix = toPostfix(expression)
	if len(postfix) == 0:
		print("false")
		return
	r = rule(postfix, expression, "")
	if(executeRule(r, True)):
		print("true")
	else:
		print("false")
	del r
	return

def getValue(name):
	if name in learned_variables:
		return learned_variables[name]
	else:
		return root_variables[name]

def outputRule(rule, truth):
	"""
	for word in rule.postfix:
		if(word in facts):
			output.append("I KNOW THAT " + getValue(word))
	"""
	s = "BECAUSE "
	if not truth:
		s+="IT IS NOT TRUE THAT "
	for c in rule.infix:
		if c == "&":
			s+=" AND "
		elif c == "|":
			s+=" OR "
		elif c == "!":
			s+=" NOT "
		else:
			s+=getValue(c)
	s+=" I KNOW THAT " + getValue(rule.consequence)
	output.append(s)
	return

def outputConclusion(operator, value, expression):
	s = ""
	for c in expression:
		if c == "&":
			s+=" AND "
		elif c == "|":
			s+=" OR "
		elif c == "!":
			s+="NOT "
		else:
			s+=getValue(c)

	if value:
		output.append("I THUS KNOW THAT " + s)
	else:
		output.append("THUS I CANNOT PROVE " + s)

	return



def why(expression):
	global output
	global facts
	postfix = toPostfix(expression)
	postfixcopy = postfix.copy()
	index = 0
	factscopy = facts.copy()
	factscopy[:] = (x for x in factscopy if x in root_variables)

	if expression in factscopy:
		output.append("I KNOW THAT " + getValue(expression))
		return True
	elif expression in root_variables:
		output.append("I KNOW IT IS NOT TRUE THAT " + getValue(expression))
		return False
	else:
		for c in expression:
			if c not in ['&', '!', '|']:
				if c in root_variables:
					why(c)
				else:
					for rule in (x for x in rules if x.consequence == c):
						if why(rule.infix):
							outputRule(rule, True)

	#Convert variables to boolean values
	for i in range(len(postfix)):
		word = postfix[i]
		if word not in ['&', '!', '|']:
			if word in facts:
				postfix[i] = [word,True]
			else:
				for rule in (x for x in rules if x.consequence == word):
					if executeRule(rule, True):
						postfix[i] = [word,True]
						break
				if len(postfix[i]) == 1:
					postfix[i] = [word,False]

	#Apply operators to operands until one value remains
	while(len(postfix) > 1):
		if len(postfix[index]) > 1:
			index += 1
		else:
			if postfix[index] == '!':
				postfix.pop(index)
				postfix[index-1][1] = not postfix[index-1][1]
				postfix[index-1][0] = '!' + postfix[index-1][0]
				if postfix[index-1][1] == True:
					outputConclusion('!', True, postfix[index-1][0])
				else:
					outputConclusion('!', False, postfix[index-1][0])
			elif postfix[index] == '&':
				postfix.pop(index)
				first = postfix.pop(index - 2)
				second = postfix.pop(index - 2)
				postfix.insert(index-2,[first[0]+"&"+second[0],first[1] and second[1]])
				if first:
					if second:
						outputConclusion('&', True, postfix[index-2][0])
					else:
						outputConclusion('&', False, postfix[index-2][0])
				else:
					outputConclusion('&', False, postfix[index-2][0])
				index -= 1
			elif postfix[index] == '|':
				postfix.pop(index)
				first = postfix.pop(index - 2)
				second = postfix.pop(index - 2)
				postfix.insert(index-2,[first[0]+'|'+second[0],first[1] or second[1]])
				if not(first or second):
					outputConclusion('|', False, postfix[index-2][0])
				else:
					outputConclusion('|', True, postfix[index-2][0])
				index -= 1

	if postfix[0][1] == True:
		return True
	return

#Main Loop to read in user input, then call the appropriate function
while True:
	inp = shlex.split(input())
	size = len(inp)
	if size == 0:
		pass
	elif inp[0] == '0':
		exit()
	elif inp[0] == "Teach":
		if size == 5:
			newVariable(inp[2], inp[4], inp[1])
		elif inp[2] == "=":
			updateRootVariable(inp[1], inp[3])
		elif inp[2] == "->":
			newRule(inp[1], inp[3])
		pass
	elif inp[0] == "List":
		list()
		pass
	elif inp[0] == "Learn":
		learn()
		pass
	elif inp[0] == "Query":
		query(inp[1])
		pass
	elif inp[0] == "Why":
		output.clear()
		if why(inp[1]):
			print("true")
		else:
			print("false")
		for x in output:
			print(x)
		pass
	else:
		pass