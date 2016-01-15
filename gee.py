#!/usr/bin/python3

# gee.py 
# Project 4: Types.

# Implemented by Cullen Rombach (cmromb)

import re, sys, string

debug = False
dict = { }
tokens = [ ]

class StatementList( object ):
	def __init__(self):
		self.statementList = []

	def addStatement(self, statement):
		self.statementList.append(statement)

	def __str__(self):
		printStr = ''
		for statement in self.statementList:
			printStr += str(statement)
		return printStr
	
	# Get the type of each statement in this statement list.
	def tipe(self, tm):
		for statement in self.statementList:
			statement.tipe(tm)


# === Statement class and subclasses
class Statement( object ):
	def __str__(self):
		return ""

class Assignment( Statement ):
	def __init__(self, identifier, expression):
		self.identifier = identifier
		self.expression = expression
		
	def __str__(self):
		return "= " + str(self.identifier) + " " + str(self.expression) + "\n"
	
	# Get the type of the variable to the left of this Assignment.
	def tipe(self, tm):
		# Store the type of this assignment's expression.
		exprType = self.expression.tipe(tm)
		
		# If there is no type, throw an error.
		if exprType == "":
			error("Type Error: Undefined expression!")
			
		# If this variable isn't in the type map, add it and print it out.
		if str(self.identifier) not in tm:
			tm[str(self.identifier)] = exprType
			print(str(self.identifier) + " " + exprType)
			
		# If this variable is already defined and its type does not match the
		# expression's type, throw an error.
		if tm[str(self.identifier)] != exprType:
			error("Type Error: " + tm[str(self.identifier)] + " = " + exprType + "!")

class WhileStatement( Statement ):
	def __init__(self, expression, block):
		self.expression = expression
		self.block = block

	def __str__(self):
		return "while " + str(self.expression) + "\n" + str(self.block) + "endwhile\n"
	
	# Get the type of this WhileStatement.
	def tipe(self, tm):
		# If this while statement doesn't have a boolean value as the
		# termination condition, throw an error.
		if self.expression.tipe(tm) != "boolean":
			error("Type Error: While expression is not a boolean.")
		# Otherwise, return the type of the while block.
		self.block.tipe(tm)


class IfStatement( Statement ):
	def __init__(self, expression, ifBlock, elseBlock):
		self.expression = expression
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock

	def __str__(self):
		return "if " + str(self.expression) + "\n" + str(self.ifBlock) + "else\n" + str(self.elseBlock) + "endif\n"
	
	# Get the type of this IfStatement.
	def tipe(self, tm):
		# If this if statement doesn't evaluate a boolean, throw an error.
		if self.expression.tipe(tm) != "boolean":
			error("Type Error: If expression is not a boolean.")
		# Otherwise, get the type of the if block.
		self.ifBlock.tipe(tm)
		# If there is an else block, gets its type as well.
		if self.elseBlock != "":
			self.elseBlock.tipe(tm)


# === Expression class and subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)
	
	# Get the type of this binary expression.
	def tipe(self, tm):
		# Store lists that hold all the numerical and boolean operations.
		numericalOps = ['+','-','*','/']
		booleanOps = ['and', 'or', '>','<','>=','<=','==','!=']
		
		# Store the type of the left and right arguments.
		leftTipe = self.left.tipe(tm)
		rightTipe = self.right.tipe(tm)
		
		# If there is a type error, print it out.
		if leftTipe != rightTipe:
			error("Type Error: " + str(leftTipe) + " " + str(self.op) + " " + str(rightTipe) + "!")
			
		# If the operation is numerical, return the string "number".
		if self.op in numericalOps and leftTipe == "number":
			return "number"
		
		# If the operation is boolean, return the string "boolean".
		if self.op in booleanOps:
			return "boolean"

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)
	
	# Get the type of this number.
	def tipe(self, tm):
		return "number"

class VarRef( Expression ):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)
	
	# Get the type of this VarRef.
	def tipe(self, tm):
		# If this variable hasn't been defined yet, throw an error.
		if str(self.value) not in tm:
			error("Type Error: " + self.value + " is referenced before being defined!")
		# Otherwise, return its type.
		else:
			return tm[str(self.value)]


class String( Expression ):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return str(self.value)
	
	# Get the type of this String.
	# Strings aren't handled in Gee's typing system, so throw an error.
	def tipe(self, tm):
		error("Type Error: Gee language doesn't handle string typing.")


# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	
	
	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.
# This is where the work is started after the tokens are loaded in correctly.

def parse( text ) :
	global tokens
	tokens = Lexer( text )
	stmtlist = parseStmtList( )
	# print (stmtlist)
	return stmtlist


def parseStmtList(  ):
	""" stmtList =  {  statement  } """

	tok = tokens.peek( )
	statementList = StatementList()

	while tok not in [None ,"~"]: #have to account for undent that signals an end of block

		statement = parseStatement()
		statementList.addStatement(statement)
		tok = tokens.peek()

	return statementList


def parseStatement():
	"""statement = ifStatement |  whileStatement  |  assignment"""

	tok = tokens.peek()
	if debug: print ("Statement: ", tok)

	if tok == "if":
		return parseIfStmt()

	elif tok == "while":
		return parseWhileStmt()

	elif re.match(Lexer.identifier, tok):
		return parseAssignment()

	error("error msg: statement")
	return


def parseAssignment():
	"""assign = ident "=" expression  eoln"""

	identifier = tokens.peek()
	if debug: print ("Assign statement: ", left)

	if tokens.next() != "=":
		error("error msg: assignment")

	tokens.next()
	exp = expression()

	tok = tokens.peek()
	if tok != ";":
		error("error msg: assignment")

	tokens.next()

	return Assignment(identifier, exp)
	


def parseIfStmt():
	"""ifStatement = "if" expression block   [ "else" block ] """

	tok = tokens.next()
	if debug: print ("If statement: ", tok)

	expr = expression()
	ifBlock = parseBlock()
	elseBlock = ''

	if tokens.peek() == "else":
		tok = tokens.next()
		if debug: print ("Else statement: ", tok)
		elseBlock = parseBlock()

	return IfStatement(expr, ifBlock, elseBlock)


def parseWhileStmt():
	"""whileStatement = "while"  expression  block"""

	tok = tokens.next()
	if debug: print ("While statement: ", tok)

	expr = expression()
	block = parseBlock()

	return WhileStatement(expr, block)


def parseBlock():
	"""block = ":" eoln indent stmtList undent"""

	tok = tokens.peek()
	if debug: print ("Block: ", tok)
	
	# Check to make sure each of the appropriate terminal tokens exist and are in the right place
	if tok != ":":
		error("error msg: block")

	tok = tokens.next()

	if tok != ";":
		error("error msg: block")

	tok = tokens.next()

	if tok != "@":
		error("error msg: block")

	tok = tokens.next()

	stmtList = parseStmtList()

	if tokens.peek() != "~":
		error("error msg: block")

	tokens.next()

	return stmtList


def expression():
	"""expression = andExpr { "or" andExpr }"""
	tok = tokens.peek( )
	if debug: print ("expression: ", tok)
	left = andExpr( )
	tok = tokens.peek( )
	while tok == "or":
		tokens.next()
		right = andExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def andExpr():
	"""andExpr    = relationalExpr { "and" relationalExpr }"""

	tok = tokens.peek( )
	if debug: print ("andExpr: ", tok)
	left = relationalExpr( )
	tok = tokens.peek( )
	while tok == "and":
		tokens.next()
		right = relationalExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def relationalExpr():
	"""relationalExpr = addExpr [ relation addExpr ]"""

	tok = tokens.peek( )
	if debug: print ("relationalExpr: ", tok)
	left = addExpr( )
	tok = tokens.peek( )
	while re.match(Lexer.relational, tok):
		tokens.next()
		right = addExpr( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def addExpr( ):
	""" addExpr    = term { ('+' | '-') term } """

	tok = tokens.peek( )
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left



def term( ):
	""" term    = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left


def factor( ):
	"""factor  = number | string | ident |  "(" expression ")" """

	tok = tokens.peek( )

	if debug: print ("Factor: ", tok)

	if re.match(Lexer.number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr

	elif re.match(Lexer.string, tok):
		expr = String(tok)
		tokens.next()
		return expr

	elif re.match(Lexer.identifier, tok):
		expr = VarRef(tok)
		tokens.next()
		return expr

	if tok == "(":
		tokens.next( )  # or match( tok )
		expr = expression( )
		tokens.peek( )
		tok = match(")")
		return expr

	error("error msg: factor()")
	return


def match(matchtok):
	tok = tokens.peek( )
	if (tok != matchtok): error("error msg: match()")
	tokens.next( )
	return tok

def error( msg ):
	print(msg)
	sys.exit()



def mklines(filename):

	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	for line in inn:
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
		elif indent < pos[-1]:
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		# print (ct, "\t", line)
		lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)

	return lines


def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct
		

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line



def main():

	global debug
	ct = 0
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
	if len(sys.argv) < 2+ct:
		print ("Usage:  %s filename" % sys.argv[0])
		return
	# Get the statement list from the parser.
	stmtlist = parse("".join(mklines(sys.argv[1+ct])))
	
	# Get and print the program's type map.
	tm = {}
	stmtlist.tipe(tm)
	
	return

main()
