#C++ Classes Analyzer

##About
Script was implemented in Python3 as a school project. The script analyzes inheritance of classes written in simplified syntax for valid header files of C++11.
The script creates inheritance tree or prints details about all members of a specified class.


##Input format
C++ header file where classes are written in simplified syntax according these rules:
- in file only declaration/definition of classes and theirs members is allowed (including redefinitions and overloading class members)
- definition of a class is indicated by curly braces ({})
- class definition inside class is not allowed
- no command of preprocesor are occured in file, so definition of macros and includes of libraries is not possible
- declaration/definition of namespaces, templates or definitions of friend classes are not allowed
- no definitions of own operators are allowed in file
- files do not contain comments
- as data types are used only:
  - primitive data types
  - defined classes
  - pointers/referencies to these data types


##Output format
Output of the script is XML file describing
- inheritance tree
- description all members (including inherited ones) of specified class


##Parameters
- --help 
- --input=filename - input file, if this parameter is missing, input file is expected in standard input
- --output=filename - output file, if this parameter is missing, script output is printed to standard output
- --pretty-xml=k - indentation of output XML will be k spaces, if this parameter is missing, k=4
- --details=class - instead of inheritance tree, details about the class (all class when class is not specified) will be printed out 
- --search=XPATH - result of XPATH search in original output will be printed out
- --conflicts - has to be used with --details, if a conflict turned out, script will not end with error code, conflict members will be printed in \<conflicts> tag


##Returns
- 1 (wrong format of the parameters)
- 2 (input file does not exist or an error occured during openning an input file for reading)
- 3 (script can't open a file for writing, f.e. because of limited permissions)
- 4 (wrong format of an input file)
- 21 (conflict member found)


##Tests
Tests are located in test directory. Tests check basic functionality. Jexamxml used for comparing two xml files is needed to download.