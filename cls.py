#!/usr/bin/python3

#CLS:xkopec42

###
# Project: CLS - C++ Classes
# Author: Martin Kopec
# Login: xkopec42
# Date: 17.04.2016
################################### 
import sys
import re

from lxml import etree as ET
from lxml.etree import ElementTree
from xml.dom.minidom import Document
from xml.dom import minidom 

inputSrc = None     #string
outputSrc = None    #file or STDOUT
indentation = 2     #spaces, default 2
details = False     #true if print details about classes
specificClassName = ""  #specific class name to print details about or "" if print all 
search = False      #true if XPATH to search given
XPATH = ""          #XPATH to be searched
conflicts = False   #true if ignored conflicts


class Model:
    """
    Class Model - defines model of c++ header file 
                - implements methods over it 
    """

    existedM = []    #temp global list for recursive printing methods and determine inherited methods
    existedAtt = []  #temp global list for recursive printing attributes and determine inherited attributes
    
    existedAttC = [] #list of lists=> [ att_name, [parents of att]; ...] for conflict analysis 
                     #if conflict exists, existedAttC is not empty after conflict detect function
    existedMC = []   #list of lists=> [ [method_name, [method arguments type] ], [parents of method]; ...]
    conflictExists = False  #true if conflict found
   
    class CClass:
        """
        Class CClass - one instance = one c++ class
                     - contains all needed information about the class
        """

        def __init__(self, name, inheritance):
            self.name = name
            self.kind = "concrete"  # concrete/abstract
            self.inheritance = inheritance   # dictionary => class_name : access_specifier
            self.using = []
            self.usingAtt = []     #list of lists => [[access_mode, class_name, attribute],...]:after setKind: class_name = class_object
            self.usingMethod = []  #list of lists => [[access_mode, class_name, method],...]   :after setKind: class_name = class_object
            #-- 
            self.methods = []
            self.attributes = []
            self.constructors = []
            #-- a litle bit redundant, but faster when printing class-details
            self.publicAtt = []
            self.publicMet = []
            self.protectedAtt = []
            self.protectedMet = []
            self.privateAtt = []
            self.privateMet = []

        def addMethod(self, name, datatype, privacy, scope, pure, argsType, argsName):
            """ Creates instance of method, fills it by data and append instance to method list"""

            if self.findAttribute(name):
                raise NameError("Duplicate declaration : "+name+" in class: "+self.name)
            
            for instance in self.findAllMethods(name, self.methods):
                if instance != None and instance.argumentType == argsType:
                    raise NameError("Duplicate declaration : "+name+" in class: "+self.name)

            if datatype != "":  #classic method
                member = Model().Method(name, datatype, privacy, scope, pure, argsType, argsName)
                self.methods.append(member)
                self.__sortMemberByAccess(member, privacy)           

            else:               #it's constructor or destructor
                if name.replace("~","") != self.name:   #name has to be the same as class name
                    raise NameError("WRONG constructor/destructor declaration, name does not match parent's class")
                
                if name.find("~") != -1:    #it's desctructor
                    if len(self.findAllMethods(name, self.constructors)) != 0:  
                        raise NameError("A destructor already exists in "+self.name)
                    if len(argsType) != 0 or len(argsName) != 0:
                        raise Exception("Destructor can't have arguments")
                    datatype = "void"

                else:       #it's constructor
                    datatype = self.name
                    for instance in self.findAllMethods(name, self.constructors):       #check overloading
                        if instance != None and instance.argumentType == argsType:
                            raise NameError("Duplicate declaration of constructor: "+name+" in class: "+self.name)

                constructor = Model().Method(name, datatype, privacy, scope, pure, argsType, argsName)
                self.constructors.append(constructor)

        def __sortMemberByAccess(self, member, privacy):
            """Adds member to list according to privacy"""

            if privacy == "public":
                self.publicAtt.append(member) if member.__class__.__name__ == "Attribute" else self.publicMet.append(member)

            elif privacy == "private":
                self.privateAtt.append(member) if member.__class__.__name__ == "Attribute" else self.privateMet.append(member)

            else:   #protected
                self.protectedAtt.append(member) if member.__class__.__name__ == "Attribute" else self.protectedMet.append(member)

        def findMethod(self, name):
            """Returns method object specified by name, if not found, returns None"""

            for m in self.methods:
                if m.name == name:
                    return m
            return None

        def findAllMethods(self, name, where):
            """Returns list of methods with given 'name' in 'where' list"""

            result = []
            for m in where:
                if m.name == name:
                    result.append(m)
            return result

        def addAttribute(self, name, dataType, privacy, scope): 
            """Creates instance of Attribute class, fills it by given data and append it to list of attributes"""

            if self.findAttribute(name) or self.findMethod(name):
                raise NameError("Duplicate declaration : "+name+" in class: "+self.name)
           
            else: 
                attribute = Model().Attribute(name, dataType, privacy, scope)
                self.attributes.append(attribute)
                self.__sortMemberByAccess(attribute, privacy)

        def findAttribute(self, name):
            """Returns attribute object specified by name, if not found returns False"""

            for att in self.attributes:
                if att.name == name:
                    return att
            return False

        def parseIdentifier(self, mode, identifier):
            """Parses information about attribute (data type, scope, name,..)
               mode = access mode
               identifier = string containing attribute declaration"""

            #delete spaces around =.. and delete spaces between *           
            identifier = re.sub("\s*=(?:\w*\s*)+|(?<=\*)\s*(?=\*)", "", identifier)  
            identifier = identifier.replace(";","")
            identifier = identifier.split(",")
    
            temp = identifier[0].split(" ")    #contains type and first var
            dataType = " ".join(temp[:-1])     #omit last part which contains variable

            identifiers = [temp[-1]] + identifier[1:] #the rest is/are variable/s

            #determine scope
            scope = "instance"
            if dataType.find("static ") != -1:
                dataType = dataType.replace("static ","", 1)    #max first one replaced
                scope = "static"
            if dataType.find("virtual ") != -1:
                raise Exception("Attribute can't be virtual in class: "+self.name)

            # int*a would be not divided !!!
            
            #create instances of Attribute and deal with pointers (move them from var's name to dataType)
            for var in identifiers:

                lst = re.findall("\*+|&+", var)
                if len(lst) != 0:
                    dataType = dataType + lst[0]
                    var = var.replace(lst[0], "")

                self.addAttribute(var, dataType, mode, scope)                
                dataType = re.sub("\*+|&+", "", dataType)
        
        def parseMethod(self, mode, method):
            """Parses information about method (virtuality, arguments..)
                mode = access mode
                method = string containing just method declaration"""
          
            method = re.sub("(?<=\*)\s*(?=\*)|(?<=,)\s*(?=\w)|(?<=\w)\s*(?=,)", "", method) #remove spaces between * and around ,
            pure = None
            
            #determine virtuality
            if method.find("virtual ") != -1:
                method = method.replace("virtual ", "", 1)   #max first one replaced
                pure = "no"
                
            if re.search("\s*=\s*0\s*", method) != None:
                if pure != "no":
                    raise Exception("Pure virtual syntax can be applied only on virtual member, class: "+self.name)
                pure = "yes"
                self.kind = "abstract"
                

            #determine name and data type
            temp = method.split("(", 1)
            temp = list(filter(lambda x: len(x) > 0, temp[0].split(" ")))
            name = temp[-1]
            dataType = " ".join(temp[:-1])

            lst = re.findall("\*+|&+", name)
            if len(lst) != 0:
                dataType = dataType + lst[0]
                name = name.replace(lst[0], "")
            
            #determine scope
            scope = "instance"
            if dataType.find("static ") != -1:
                dataType = dataType.replace("static ","", 1)
                scope = "static"
                if pure != None:
                    raise Exception("Virtual method can't be static, method: "+name+" in class: "+self.name)

            #parse arguments of method
            argumentName = []
            argumentType = []
            args = method.split("(")
            args = args[1].split(")")
            if len(args[0]) != 0 and re.search("^\s+$|^\s*void\s*$", args[0]) == None:
                            
                args = args[0].split(",")
               
                for a in args:
                    a = list(filter(lambda x: len(x) > 0, a.split(" ")))
                    aType = " ".join(a[:-1])
                    lst = re.findall("\*+|&+", a[-1])
                    
                    if len(lst) != 0:
                        aType = aType + lst[0]

                    argumentType.append(aType)
                    argumentName.append(re.sub("\*+|&+","",a[-1]))
          
            self.addMethod(name, dataType, mode, scope, pure, argumentType, argumentName)

        def parseBody(self, text):
            """Parses body of c++ class, finds methods/attributes declarations
                 text = string of class body
            """

            body = text.split("{", 1)
            body = re.sub("\s*}\s*;\s*$", "", body[1]) #cut out the }; which belongs to class, so only body left

            if len(body) == 0: return

            #parse access specifiers
            specifiers = re.findall("\w+:(?!:)", body)
            accessRanges = []
            offset = 0
            temp = body

            for specifier in specifiers:
                
                index = temp.find(specifier)
                offset = offset + len(specifier)
                spec = specifier.replace(":", "")
                if Model().isAccessValid(spec):
                    accessRanges.append(index+offset)
                    accessRanges.append(spec)
                else:
                    raise NameError("Unknown access specifier2")
                temp = temp[:index]+temp[index+len(specifier):]
            
            #parse using
            using = re.findall("using[^;]*;", body)
            nextParseBody = body   
            for u in using:
                u2 = u.split("::")
                member = u2[1].replace(";","")
                namespace = u2[0].split(" ")
                namespace = namespace[1]
                
                mode = Model().determineAccess(accessRanges, body.find(u))
                self.using.append([mode, namespace, member]) #for now contains attributes and methods as well

                nextParseBody = body.replace(u, "")

            variables = []
            methods = []
            nextParseBody = re.sub("\w+:","", nextParseBody) #delete access modifiers if present
            
            #split through ; and do not consider empty list          
            for part in filter( lambda x: len(x) > 1, nextParseBody.split(";") ):                
                
                for member in filter( lambda x: len(x) > 1, re.split("\s*{\s*}\s*", part) ):
                    member = re.sub("^\s*|\s*$", "", member)
                    if len(member) > 0:
                        if "(" in member:
                            methods.append(member)
                        else:
                            variables.append(member)
                   
            for var in variables:
                self.parseIdentifier(Model().determineAccess(accessRanges, body.find(var)), var)
           
            for m in methods:
                self.parseMethod(Model().determineAccess(accessRanges, body.find(m)), m)

        def getPrivatePureVirtualMList(self, origin):
            """Returns list of pure virtual methods"""

            lst = []
            for m in self.methods:
                if m.privacy == "private" and m.virtualPure == "yes":
                    temp = origin.findMethod(m.name)
                    if temp != None and temp.argumentType == m.argumentType:
                        continue
                    lst.append(m)
            return lst


    class Method:
        """
        Class Method - one instance = one c++ method
                     - contains all needed information about the method
        """

        def __init__(self, name, dataType, privacy, scope, pure, argsType, argsName):
            self.name = name
            self.dataType = dataType
            self.privacy = privacy      # access mode
            self.scope = scope          # instance/static
            self.virtualPure = pure     # None/yes/no
            self.argumentType = argsType     # list of arguments types
            self.argumentName = argsName     # list of arguments names 

    class Attribute:
        """
        Class Attribute - one instance = one c++ attribute
                        - contains all needed information about the attribute
        """

        def __init__(self, name, dataType, privacy, scope):
            self.name = name
            self.dataType = dataType
            self.privacy = privacy  # access mode
            self.scope = scope      # instance/static


    def __init__(self):
        self.classInstances = []    #list of instances of CClass
        self.classNames = []        #for checking if the same name exist and for inheritance controll

    def __findName(self, name):
        """Returns boolean if class with 'name' was found or not"""

        if name in self.classNames:
            return True
        else:
            self.classNames.append(name)        
        return False

    def addClass(self, name, inheritance):
        """Creates instance of CClass and append it to list of CClass objects"""

        if self.__findName(name) == True:
            raise NameError("Class redefinition: "+name)

        self.classInstances.append(self.CClass(name, inheritance))
        return self.classInstances[-1]  #return the last instance

    def findClass(self, name):
        """Returns class specified by 'name' or None if not found"""

        for i in self.classInstances:
            if i.name == name:
                return i
        return None

    def setKind(self):
        """Sets kind of class and check if inheritance + using is correct"""

        for cl in self.classInstances:
            for u in cl.using:
               
                parent = self.findClass(u[1])
                if parent == None:
                    raise NameError("Using from undefined class")
                #forbid using from self
                else:
                    member = parent.findAttribute(u[2])
                    if not member:
                        member = parent.findMethod(u[2])
                        if not member:
                            raise NameError("Using includes undeclared member")
                   
                    if member.privacy == "private" or (member.privacy == "protected" and parent.name not in cl.inheritance):
                        raise Exception("Can't using member: "+member.name+" from: "+parent.name)

                    #substitute name of class by the object of the class and sort 
                    if member.__class__.__name__ == "Method":
                        cl.usingMethod.append([u[0], parent, u[2]])
                    else:
                        cl.usingAtt.append([u[0], parent, u[2]])
                
            
            #sets kind of class 
            for parent in cl.inheritance.keys():
                if parent == cl.name:
                    raise NameError("self inheritance forbidden")
                parent = self.findClass(parent)
                if parent == None:
                    raise NameError(cl.name+" inherits from undefined class")

                #examine methods to set kind of class
                if cl.kind == "concrete":
                    if not self.__isAbstract(cl) == []:
                        cl.kind = "abstract"
    
    def __isAbstract(self, classInst):
        """Recursively checks all ancestors of classInst and if found pure virtual method
           which is not implemented in classInst, it's append to the list which is returned"""

        pureM = []
        for parent in classInst.inheritance.keys():
            pureM = pureM + self.__isAbstract(self.findClass(parent))

        for m in classInst.methods:
            if [m.name, m.argumentType] in pureM:
                pureM.remove([m.name, m.argumentType])
        for m in classInst.methods:
            if m.virtualPure == "yes":
                pureM.append([m.name, m.argumentType])

        return pureM

    @staticmethod
    def getName(text):
        """Parses and returns name of class from text"""

        result = re.findall("(?<=^)\s*\w+\s*(?=:|{)", text)
        return re.sub("\s*", "", result[0])

    @staticmethod
    def isAccessValid(access):
        """Returns boolean if 'access' is valid access specifier"""

        if access in ["public", "private", "protected"]:
            return True
        return False        #probably redundant

    @staticmethod
    def determineAccess(accessRanges, index):
        """Returns access specifier which is valid in index
            accessRanges = dictionary => {index:specifier, ...}"""

        mode = "private"
        for i in range(0,len(accessRanges),2):
            if accessRanges[i] < index:
                mode = accessRanges[i+1]
            else:
                break
        return mode

    @staticmethod
    def inheritance(text):
        """Parses inheritance of a class
            text = string defining whole class"""

        inh = text.split("{")
        inh = inh[0].split(":")
        if len(inh) == 2:
            inh = inh[1].split(",")
            inheritance = {}

            for upClass in inh:
                upClass = list(filter(lambda x: len(x) > 0, upClass.split(" ")))
                if len(upClass) == 2 and upClass[1] in inheritance or upClass[0] in inheritance:
                    raise NameError("WRONG inheritance, cannot inherit from class twice")
                if len(upClass) == 2:         #access modifier present
                    if Model().isAccessValid(upClass[0]):
                        inheritance[upClass[1]] = upClass[0]
                    else:
                        raise NameError("Unknown access specifier")
                else:
                    inheritance[upClass[0]] = "private"

            return inheritance
        return {}

    def __findInheritanceRecursive(self, parentName):
        """Returns minidom structure - whole structure of ancestors of class specified by parentName"""

        rootLst = []
        #ask if anybody inherit from parentName, if so, create subentry
        for child in filter(lambda x: len(x.inheritance) > 0 ,self.classInstances):
            if parentName in child.inheritance:
                subEntry = Document().createElement("class")
                subEntry.setAttribute("name", child.name)
                subEntry.setAttribute("kind", child.kind)
                
                children = self.__findInheritanceRecursive(child.name)
                if len(children) != 0:
                    for ch in children:
                        subEntry.appendChild(ch)
                #else:
                #    subEntry.appendChild(Document().createTextNode("")) #insert empty node, to prevent having self closing node

                rootLst.append(subEntry)

        return rootLst

    def printInherTree(self): 
        """Creates and print out minidom structure => inheritance tree of whole Model"""

        #create minidom-document
        doc = Document()

        # create model element
        model = doc.createElement("model")
        doc.appendChild(model)

        #loop through all parent/base classes
        for cl in self.classInstances:
            if len(cl.inheritance) == 0:
                entry = doc.createElement("class")
                entry.setAttribute("name", cl.name)
                entry.setAttribute("kind", cl.kind)
                model.appendChild(entry)

                children = self.__findInheritanceRecursive(cl.name)
                if len(children) != 0:
                    for ch in children:
                        entry.appendChild(ch)
                #else:
                #    entry.appendChild(Document().createTextNode(""))  #insert empty node, to prevent having self closing node         

            elif len(cl.inheritance) > 1:   #check if conflict in the cl is possible
                if self.detectConflict(cl, cl):
                    #print("conflict")
                    raise Exception("Conflict in class: "+cl.name)

        doc.writexml(outputSrc,"", " "*indentation,"\n", encoding="utf-8")

    def __getNonOneParentMembers(self):
        """Filters global list of items to contain only items with more than one parent"""

        att = []
        nonDuplicateParents = []
        for i in range(1, len(self.existedAttC),2):
            if len(self.existedAttC[i]) > 1:
                att.append(self.existedAttC[i-1])
            
                [nonDuplicateParents.append(item) for item in self.existedAttC[i] if item not in nonDuplicateParents]
                att.append(nonDuplicateParents)

        self.existedAttC = att

    def detectConflict(self, origin, parent):
        """Sets global list, starts recursive search for conflict and returns boolean if origin has conflict or not"""

        self.detectConflictsRecursive(origin, parent, [])    
       
        #merge lists
        for i in range(1, len(self.existedMC), 2):
            if self.existedMC[i-1][0] not in list(map(lambda x: x[2],origin.usingMethod)):
                try:
                    j = self.existedAttC.index(self.existedMC[i-1][0])
                   
                except:     #method name does not exist in att list
                    self.existedAttC.append(self.existedMC[i-1][0])   #method's name
                    self.existedAttC.append(self.existedMC[i])        #method's parents
                else:       #method name exists in att list
                    self.existedAttC[j+1] = self.existedAttC[j+1] + self.existedMC[i]       #add methods parents

        self.__getNonOneParentMembers()
       
        if self.existedAttC != []:
            return True
        return False

    def detectConflictsRecursive(self, origin, parent, path):
        """Recursively search conflicts in origin class"""

        path.append(parent.name)
       
        for parent in parent.inheritance.keys():
            parent = self.findClass(parent)
            
            #iterate through names of attributes in attribute's list and usingAtt list
            for att in list(map(lambda x: x.name, parent.attributes)) + list(map(lambda x: x[2], parent.usingAtt) ):
                # !!!! names contains spaces !!! remove them !!!
                # if attribute name in list and name of this class is not in path of the attribute in list, append new parent and path
                if att in self.existedAttC[::3]:
                    i = self.existedAttC.index(att)
                    if len(set(self.existedAttC[i+1]) & set(path)) == 0:    #no parent of att is in path  
                        self.existedAttC[i+1].append(parent.name)           #add one more parent
                else:
                    if att not in list(map(lambda x: x.name, origin.attributes)) and att not in list(map(lambda x: x[2], origin.usingAtt)):                        
                        self.existedAttC.append(att)
                        self.existedAttC.append([parent.name])
                       
            #iterate through objects of methods in method's list and usingMethod list
            for m in parent.methods + list(map(lambda x: x[1].findMethod(x[2]), parent.usingMethod)):
                
                if [m.name, m.argumentType] in self.existedMC[::2]:
                    i = self.existedMC.index([m.name, m.argumentType])
                    if len(set(self.existedMC[i+1]) & set(path)) == 0:
                        self.existedMC[i+1].append(parent.name)
                else:
                    temp = origin.findMethod(m.name)
                    if temp == None or m.argumentType != temp.argumentType:
                        self.existedMC.append([m.name, m.argumentType])
                        self.existedMC.append([parent.name])
                                       
            self.detectConflictsRecursive(origin, parent, path)
            path = []

    def canExcludeMember(self, isAtt, parentName, cmpID):
        """Returns boolean, if attribute should be excluded because it's conflict member"""

        retVal = False
        zipLst = zip(self.existedAttC[0::2], self.existedAttC[1::2]) if isAtt else zip(self.existedMC[0::2], self.existedMC[1::2])
        
        for ID, parents in zipLst:
            if parentName in parents and cmpID == ID:
                retVal = True
                break
        return retVal 

    def createAttNodes(self, ancestor, attList, parentName):
        """Returns minidom structure of attributes"""

        global conflicts
        attNodes = []
        
        for att in attList:
            #print(self.existedAttC)
            if conflicts and self.conflictExists:
                if self.canExcludeMember(True, parentName, att.name):
                    continue
            if att.name not in self.existedAtt:
                self.existedAtt.append(att.name)
                aTag = Document().createElement("attribute")
                aTag.setAttribute("name", att.name)
                aTag.setAttribute("type", att.dataType)
                aTag.setAttribute("scope", att.scope)
                if ancestor:
                    fr = Document().createElement("from")
                    fr.setAttribute("name", parentName)
                    aTag.appendChild(fr)
                attNodes.append(aTag)

        return attNodes

    def createAttNodeStructRecursive(self, classInst, accessGroup, ancestor, inherMode):
        """Recursively finds all inherited attributes and returns minidom structure of attributes"""

        attNodes = []
        permission = True
        attList = getattr(classInst, accessGroup)
        if ancestor:
            if Model().isAccessLoEqThan(inherMode, accessGroup):    #inherMode <= accessGroup ? 
                if inherMode == "public" and "private" not in accessGroup:
                    attList = getattr(classInst, accessGroup) if "public" in accessGroup else getattr(classInst, accessGroup)
    
                elif (inherMode == "protected" and "protected" in accessGroup) or (inherMode == "private" and "private" in accessGroup):
                    attList = getattr(classInst, "publicAtt") + getattr(classInst, "protectedAtt")
                else:
                   permission = False
            else:
                permission = False

        if permission:
            if not ancestor:        #add attributes inherited by using
                for u in classInst.usingAtt:
                    if u[0] in accessGroup:
                        attNodes = self.createAttNodes(False if u[1].name == classInst.name else True, [u[1].findAttribute(u[2])], u[1].name)
            
            attNodes = attNodes + self.createAttNodes(ancestor, attList, classInst.name)

        for parent in classInst.inheritance.keys():
            attNodes = attNodes + self.createAttNodeStructRecursive(self.findClass(parent), accessGroup, True, classInst.inheritance[parent])

        return attNodes
   
    def createAttNodeStruct(self, classInst, accessGroup):
        """Returns minidom structure of attributes under access specified by accessGroup"""

        attrTag = None
        nodes = self.createAttNodeStructRecursive(classInst, accessGroup, False, "")

        if not nodes == []:
            attrTag = Document().createElement("attributes")            
            for node in nodes: 
                attrTag.appendChild(node)

        return attrTag

    @staticmethod
    def isAccessLoEqThan(a, b):
        """Compare two access specifiers and returns boolean if second is greater than first"""

        modes = ["public", "protected", "private"]
        a = modes.index(a)
        for i in range(len(modes)):
            if modes[i] in b:
                b = i
                break
        return a <= b

    def createMethodNodes(self, ancestor, mList, classInst):
        """Returns minidom structure of methods"""

        mNodes = []
             
        for m in mList:
            if conflicts and self.conflictExists:
                if self.canExcludeMember(False, classInst.name, [m.name, m.argumentType]):
                    continue

            if [m.name, m.argumentType] not in self.existedM:
                self.existedM.append([m.name, m.argumentType])
                mTag = Document().createElement("method")
                mTag.setAttribute("name", m.name)
                mTag.setAttribute("type", m.dataType)
                mTag.setAttribute("scope", m.scope)

                if m.virtualPure != None:
                    virtual = Document().createElement("virtual")
                    virtual.setAttribute("pure", m.virtualPure)
                    mTag.appendChild(virtual)

                if ancestor:
                    fr = Document().createElement("from")
                    fr.setAttribute("name", classInst.name)
                    mTag.appendChild(fr)

                argTag = Document().createElement("arguments")
                for i in range(len(m.argumentType)):
                    arg = Document().createElement("argument")
                    arg.setAttribute("name", m.argumentName[i])
                    arg.setAttribute("type", m.argumentType[i])
                    argTag.appendChild(arg)
                mTag.appendChild(argTag)

                mNodes.append(mTag)

        return mNodes

    def createMethodNodeStructRecursive(self, classInst, accessGroup, ancestor, inherMode, origin):
        """Recusively search for inherited members and returns minidom structure of methods"""

        methodNodes = []
        permission = True
        
        mList = getattr(classInst, accessGroup)
        if ancestor:
            if Model().isAccessLoEqThan(inherMode, accessGroup):    #inherMode <= accessGroup ? 
                if inherMode == "public":
                    if "private" not in accessGroup:
                        mList = getattr(classInst, accessGroup) if "public" in accessGroup else getattr(classInst, accessGroup)
                    
                    elif "private" in accessGroup:  #class inherit from private members only pure virtual methods
                        mList = classInst.getPrivatePureVirtualMList(origin)
                   
                elif (inherMode == "protected" and "protected" in accessGroup) or (inherMode == "private" and "private" in accessGroup):
                    mList = getattr(classInst, "publicMet") + getattr(classInst, "protectedMet") + classInst.getPrivatePureVirtualMList(origin)
                
                elif inherMode == "protected" and "private" in accessGroup:
                    mList = classInst.getPrivatePureVirtualMList(origin)  #class inherit from private members only pure virtual methods
                else:
                   permission = False
            else:
                permission = False
       
        
        if not ancestor and len(classInst.constructors) > 0:        #add constructors and desctructors
            methodNodes = self.createMethodNodes(ancestor, list(filter(lambda x: x.privacy in accessGroup,classInst.constructors)), classInst)

        if permission:  
            if not ancestor:
                for u in classInst.usingMethod:
                    if u[0] in accessGroup:
                        methodNodes = methodNodes + self.createMethodNodes(False if u[1].name == classInst.name else True, [u[1].findMethod(u[2])], u[1])
                
            methodNodes = methodNodes + self.createMethodNodes(ancestor, mList, classInst)

        for parent in classInst.inheritance.keys():
            methodNodes = methodNodes + self.createMethodNodeStructRecursive(self.findClass(parent), accessGroup, True, classInst.inheritance[parent], origin)

        return methodNodes

    def createMethodNodeStruct(self, classInst, accessGroup):
        """Returns minidom structure of methods under access specified by accessGroup"""

        metTag = None
        nodes = self.createMethodNodeStructRecursive(classInst, accessGroup, False, "", classInst)

        if not nodes == []:
            metTag = Document().createElement("methods")        
            for node in nodes: 
                metTag.appendChild(node)

        return metTag

    def printConflictMembers(self):
        """Returns minidom structure of conflict members"""

        conflictTag = Document().createElement("conflicts")

        for member in self.existedAttC[0::2]:
            memTag = Document().createElement("member")
            memTag.setAttribute("name", member)
            for className in self.existedAttC[self.existedAttC.index(member)+1]:
                clTag = Document().createElement("class")
                clTag.setAttribute("name", className)
                cl = self.findClass(className)
                
                CMember = cl.findAttribute(member)
                if CMember: #it's attribute
                    att = Document().createElement("attribute")
                else: #it's method
                    CMember = cl.findMethod(member)
                    att = Document().createElement("method")
                    
                    if CMember.virtualPure != None:
                        virtual = Document().createElement("virtual")
                        virtual.setAttribute("pure", CMember.virtualPure)
                        att.appendChild(virtual)
                   
                    args = Document().createElement("arguments")
                    for i in range(len(CMember.argumentType)):
                        arg = Document().createElement("argument")
                        arg.setAttribute("name", CMember.argumentName[i])
                        arg.setAttribute("type", CMember.argumentType[i])
                        args.appendChild(arg)
                    att.appendChild(args)

                accessTag = Document().createElement(CMember.privacy)
                att.setAttribute("name", CMember.name)
                att.setAttribute("type", CMember.dataType)
                att.setAttribute("scope", CMember.scope)
                accessTag.appendChild(att)
                clTag.appendChild(accessTag)
                memTag.appendChild(clTag)

            conflictTag.appendChild(memTag)

        return conflictTag

    def printClassMembers(self, className):
        """Creates and print minidom structure of details of class / classes (depands on script's --details attribute)"""

        global conflicts

        doc = Document()
       
        root = None
        if len(className) > 0 :         #specific class name given 
            classes = [self.findClass(className)]
            root = doc
            if not className in self.classNames:    #class does not exist => print just xml header
                doc.writexml(outputSrc,"", " "*indentation,"\n", encoding="utf-8")
                return            
        else:
            classes = self.classInstances    #iterate through all classes
            root = doc.createElement("model")
            doc.appendChild(root)

        for cl in classes:
            classTag = doc.createElement("class")
            classTag.setAttribute("name", cl.name)
            classTag.setAttribute("kind", cl.kind)
            root.appendChild(classTag)

            if len(cl.inheritance) > 0:
                inheritance = doc.createElement("inheritance")
                for parent in cl.inheritance.keys():                        
                    fr = doc.createElement("from")
                    fr.setAttribute("name", parent)
                    fr.setAttribute("privacy", cl.inheritance[parent])
                    inheritance.appendChild(fr)

                classTag.appendChild(inheritance)

            #detect conflicts, if conflicts argument True, print conflicts members, if False, terminate with 21
            self.existedMC = []
            self.existedAttC = []
            if self.detectConflict(cl, cl):
                if not conflicts:
                    raise Exception("Conflict in class "+cl.name)
                self.conflictExists = True
                classTag.appendChild(self.printConflictMembers())

            lst = ["privateAtt", "privateMet", "protectedAtt", "protectedMet", "publicAtt", "publicMet",]
            acc = ["private", "protected", "public"]
            self.existedM = [] #clean 
            self.existedAtt = []
            for i in range(len(acc)):  
                j=i*2  
                attNode = self.createAttNodeStruct(cl, lst[j])
                metNode = self.createMethodNodeStruct(cl, lst[j+1])

                if not attNode == None or not metNode == None: 
                    tag = doc.createElement(acc[i])                
                    if not attNode == None: tag.appendChild(attNode)
                    if not metNode == None: tag.appendChild(metNode)

                    classTag.appendChild(tag)

        if search:
            parseXMLbyXPATH(doc.toprettyxml(), XPATH)
        else:
            doc.writexml(outputSrc,"", " "*indentation,"\n", encoding="utf-8")

def printHelp():
    print ("\nCLS - C++ Classes:")
    print("./cls.py [--input=<file>] [--output=<file>] [--pretty-xml=k] [--details=class] [--search=XPATH] [--conflicts]")
    print("  <file> = path to file")
    print("  k      = new child of tag will have indent k greater")
    print("  class  = print information about the class, otherwise about all classes")
    print("  XPATH  = print result of XPATH searching")
    print("  --conflicts = print conflicts members\n")

def handleArguments():
    global inputSrc, outputSrc, indentation, specificClassName, details, search, XPATH, conflicts
    okArgv = ["--help", "--input", "--output", "--pretty-xml", "--details", "--search", "--conflicts"]
    counter = 0
    args = {}

    for arg in sys.argv[1:]:

        arg = arg.split("=", 1) #split through first equal sign found
        args[arg[0]] = arg[1] if len(arg) == 2 else None
    
        if (arg[0] in okArgv):                 
            counter += 1     
    
    seen = []
    if (len(sys.argv) - 1) != counter or len([x for x in sys.argv[1:] if x not in seen and not seen.append(x)]) != len(sys.argv)-1:
        sys.stderr.write("Wrong arguments\n")
        exit(1)

    
    ###--- Examine arguments ---###
    if("--help" in args):
        if(len(args) == 1 and args["--help"] == None):
           printHelp();
           exit(0)
        else:
            sys.stderr.write("With help no value or other arguments allowed\n")
            exit(1)

    #-----------------------------------------------
    if("--input" in args):  #if exists, try open it
        if(args["--input"] == None or len(args["--input"]) == 0):
            sys.stderr.write("Wrong arguments\n")
            exit(1)
        else:
            try:
                myFile = open(args["--input"], 'r')
                inputSrc = myFile.read()
                myFile.close()
            except:
                sys.stderr.write("Can't open file\n")
                exit(2)
    else:                   #if not exists, read from STDIN
        inputSrc = sys.stdin.read()

    #-----------------------------------------------
    if("--output" in args): #if exists, try open it
        
        if args["--output"] == None or len(args["--output"]) == 0:
            sys.stderr.write("Wrong arguments\n")
            exit(1)
        else:
            try:
                outputSrc = open(args["--output"], 'w')
            except:
                sys.stderr.write("Can't open/create file\n")
                exit(3)            
    else:
        outputSrc = sys.stdout  #if argument does not exist, write to STDOUT

    #-----------------------------------------------
    if("--pretty-xml" in args):
        if args["--pretty-xml"] == None: 
            indentation = 4
        elif len(args["--pretty-xml"]) == 0:
            sys.exit.write("Wrong argumetns\n")
            exit(1)
        else:
            try:
                indentation = int(args["--pretty-xml"])
            except ValueError:
                sys.stderr.write("--pretty-xml excpects number\n")
                exit(1)   

    #-----------------------------------------------
    if("--details" in args):            #make --details= error??
        details = True
        if args["--details"] == None : #print info about all classes
            pass
        elif len(args["--details"]) == 0:
            sys.exit.write("Wrong argumetns\n")
            exit(1)
        else:           #print info about specific class
            specificClassName = args["--details"]

    #-----------------------------------------------
    if("--search" in args):
        if args["--search"] == None or len(args["--search"]) == 0:
            sys.stderr.write("WRONG XPATH given\n")
            exit(1)
        else:
            search = True
            XPATH = args["--search"]
    #-----------------------------------------------
    if "--conflicts" in args:
        if args["--conflicts"] == None and details == True:
            conflicts = True
        else:
            sys.stderr.write("Argument --conflicts is accepted only when --details argument is present\n")
            exit(1)

def parseXMLbyXPATH(xml, xpath):
    """ Parses xml by lxml, finds xpath matches and prints them as new xml"""

    result = ET.Element("result")
    parser = ET.XMLParser(remove_blank_text=True)

    root = ET.XML(xml, parser)
    find = ET.XPath(xpath)

    names = "\n"
    for f in find(root):
        try:
            result.append(f)
        except:
            names = names+f+"\n"
    
    if len(names) > 1:
        result.text = names

    rough_string = ET.tostring(result)
    
    x = minidom.parseString(rough_string)

    x.writexml(outputSrc,"", " "*indentation,"\n", encoding="utf-8")

# ----------------------------------MAIN------ #
if __name__ == "__main__":

    handleArguments()

    myModel = Model()
    classes = re.split("(?<=;|\}|\s)class\s|(?<=^)class\s",inputSrc.replace("\n",""))
    
    for cl in filter(lambda x: len(x) > 1, classes):    #loop through each class

        if len(re.findall("^\s*\w+\s*;$",cl)):      #ignore if just class declaration
            continue
        
        try:
            current = myModel.addClass(Model().getName(cl), Model().inheritance(cl))  
            current.parseBody(cl)
        except:
            sys.stderr.write(str(sys.exc_info()[1])+"\n")
            sys.exit(4)

    try:
        myModel.setKind()
    except:
        sys.stderr.write(str(sys.exc_info()[1])+"\n")
        exit(4)

    try:
        if details:
            myModel.printClassMembers(specificClassName)
        else:
            myModel.printInherTree()
    except:
        sys.stderr.write(str(sys.exc_info()[1])+"\n")
        exit(21)
    
    sys.exit(0)
