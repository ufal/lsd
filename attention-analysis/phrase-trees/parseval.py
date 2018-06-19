import sys # For command line arguments

# Splits text into parts. Each part represent a single tree.
def partition(text, startTag, endTag):
   partitions = []
   i = 0
   level = 0
   for c in text:
       if c == startTag:
           if level == 0:
               start = i
           level = level + 1
       if c == endTag:
           level = level - 1
           if level == 0:
               partitions.append(text[start:(i+1)])
       i = i + 1
   return partitions

# Converts some nested text into tree.
def textToTree(text, startTag, endTag):
   node = ''
   children = []
   i = 0
   level = 0
   for c in text:

       if c == startTag:
           level = level + 1

           if level == 1:
               nodeStart = i+1

           if level == 2 and not node:
               node = text[nodeStart:i]
               childStart = i

       if c == endTag:
           level = level - 1

           if level == 1:
               childEnd = i + 1
               children.append(textToTree(text[childStart:childEnd], startTag, endTag))
               childStart = i+1

           if level == 0 and not node:
               node = text[nodeStart:i]

       i = i + 1
   if level != 0:
       return None # TODO: viska hoopis erind
   return node, children

# Returns the tag form a tag-word pair
def getTag(text):
   s = text.split()
   if s:
       return s[0].strip()
   return ''

# Returns the word form a tag-word pair
def getWord(text):
   s = text.split()
   if len(s) > 1:
       return s[1].strip()
   return ''

# Cleans a tree from spefic tags tags eg. NP-SBJ and -NONE-
def clean(node):
   i = 0
   cleanChildren = []
   for child in node[1]:
       cleanChild = clean(child)
       if cleanChild:
           cleanChildren.append(cleanChild)
   tag = getTag(node[0])
   if tag == '-NONE-':
       return None
   return (tag.split('-',1)[0] + ' ' + getWord(node[0]), cleanChildren)

"""
def getSentence(node, pos=0):
   s = str(pos) + ' '
   if node[1]:
       for c in node[1]:
           s = s + ' ' + getSentence(c,pos+1)
   else:
       s = getTag(node[0])
   return s
"""

# Returns a lis of tuples representing tags and their span.
# Tuples have form (tag start, tag end, tag name).
def getSegments(node, startPos):

   segments = []

   endPos = startPos

   for child in node[1]:
       childSegments = getSegments(child, endPos)
       endPos = childSegments[len(childSegments)-1][1]+1
       segments.extend(childSegments)

   if node[1]:
       endPos = endPos-1

   tag = getTag(node[0])
   segments.append((startPos, endPos, tag))

   return segments

# Prints a list to screen
def printList(list):
   for l in list:
       print l

# Prints disagreements to screen
def printDisagreements(disagreements):
   for d in disagreements:
       if d[1]:
           strings = []
           for s in d[1]:
               strings.append(str(s[2]))
           print str(d[0][2]) + ' <==> ' + ' & '.join(strings)
       else:
           print str(d[0][2]) + ' <==> ?'

# Checks if two segments are equal
def equal(segment1, segment2):
   if segment1[0] == segment2[0] and segment1[1] == segment2[1] and segment1[2] == segment2[2]:
       return True
   return False

# Checks if two segments cover the same words
def equalSpan(segment1, segment2):
   if segment1[0] == segment2[0] and segment1[1] == segment2[1]:
       return True
   return False


# Evaluates segments1 based on segments2
def evaluate(segments1, segments2):
   correct = 0
   crossings = 0
   errorCandidates = []
   errors = []
   for s2 in segments2:
       print s2
       for s1 in segments1:
           if equal(s1,s2):
               #print (s1, s2)
               correct = correct + 1
               break
   precision = float(correct)/len(segments1)
   recall = float(correct)/len(segments2)
   print (correct, len(segments1), len(segments2))

   # Find errors
   for s1 in segments1:
       candidates = []
       found = False
       foundCrossing = False
       for s2 in segments2:
           if equal(s1,s2):
               found = True
               break
           elif equalSpan(s1,s2):
               candidates.append(s2)
           # Check cross-brackets
           if ((s1[0] < s2[0] and (s2[0] < s1[1] and s1[1] < s2[1]))) or ((s2[0] < s1[0] and (s1[0] < s2[1] and s2[1] < s1[1]))):
               foundCrossing = True
       if not found:
           errors.append((s1,candidates))
       if foundCrossing:
           crossings = crossings + 1

       crossing = float(crossings)/len(segments1)

   return precision, recall, crossing, errors


"""
# Returns a list of text-tree-segments tuples taken from a file
def process(fileName, clean=False):
   data = []

   file = open(fileName, 'r')
   text = file.read()
   file.close()

   parts = partition(text, startTag, endTag)
   for part in parts:
       tree = textToTree(part, startTag, endTag)
       if clean:
           tree = clean(tree)
       segments = getSegments(tree, 1)
       data.append([part, tree, segments])

   return data
"""


########## Execution start here ##########

startTag = '('
endTag = ')'

doCleanup = False
showTrees = False
showSegments = False
showIndividualEval = False
showDisagreements = False
fileNames = []
data = [] # A List for holdin trees and segments

# Check command line arguments
for o in sys.argv[1:]:
   if o == '-c':
       doCleanup = True
   elif o == '-s':
       showSegments = True
   elif o == '-t':
       showTrees = True
   elif o == '-i':
       showIndividualEval = True
   elif o == '-d':
       showDisagreements = True
   else:
       fileNames.append(o)

# Check if there were enough arguments
if len(fileNames) < 2:
   # Print out some information
   print 'usage: parseval [file 1] [file 2] [options]'
   print 'example: parseval parse.txt gold.txt -c'
   print 'Precision, recall and cross-bracketing are given in tuples (prescision, recall, cross bracketing).'
   print '-c    remove unidentified words and additional labels eg. NP-SBJ --> NP'
   print '-s    display tags and their span'
   print '-t    display trees'
   print '-i    show evaluation results for every single tree'
   print '-d    show errors, prints "?" where constituent spans do not match'
   sys.exit()


# Process the first file

try:
   file1 = open(fileNames[0], 'r')
   text1 = file1.read()
   file1.close()
except:
   print 'Invalid file.'
   sys.exit()

trees1 = []
segments1 = []
parts1 = partition(text1, startTag, endTag)
for part in parts1:
   tree = textToTree(part, startTag, endTag)
   if doCleanup:
       tree = clean(tree)
   trees1.append(tree)
   segments1.append(getSegments(tree, 1))

# Process the second file

try:
   file2 = open(fileNames[1], 'r')
   text2 = file2.read()
   file2.close()
except:
   print 'Invalid file.'
   sys.exit()

trees2 = []
segments2 = []
parts2 = partition(text2, startTag, endTag)
for part in parts2:
   tree = textToTree(part, startTag, endTag)
   if doCleanup:
       tree = clean(tree)
   trees2.append(tree)
   segments2.append(getSegments(tree, 1))

# Evaluate and print the output

print ''
precision = recall = crossing = 0
for i in range(len(parts1)):
   if showTrees or showSegments or showIndividualEval or showDisagreements:
       print '########## ' + str(i) + ' ##########'
       print ''
   if showTrees:
       print parts1[i]
       print ''
       print parts2[i]
       print ''
   if showSegments:
       printList(segments1[i])
       print ''
       printList(segments2[i])
       print ''
   eval = evaluate(segments1[i], segments2[i])
   if showIndividualEval:
       print eval[:3]
       print ''
   if showDisagreements:
       printDisagreements(eval[3])
       print ''
   precision = precision + eval[0]
   recall = recall + eval[1]
   crossing = crossing + eval[2]

precision = precision/len(parts1)
recall = recall/len(parts1)
f1 = 2 / (1 / precision + 1 / recall)
crossing = crossing/len(parts1)

print '########## TOTAL ##########'
print ''
print 'Average precision, recall, F1, and cross brackets:'
print (precision, recall, f1, crossing)
#print(str(len(parts1)) + ' ' + str(len(parts2)))
