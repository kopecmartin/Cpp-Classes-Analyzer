#!/usr/bin/env bash

TASK=cls
INTERPRETER=python3
EXTENSION=py

# paths for input and output files
LOCAL_IN_PATH="./" # (simple relative path)
LOCAL_IN_PATH2="" #Alternative 1 (primitive relative path)
LOCAL_IN_PATH3=`pwd`"/" #Alternative 2 (absolute path)
LOCAL_OUT_PATH="./" # (simple relative path)
LOCAL_OUT_PATH2="" #Alternative 1 (primitive relative path)
LOCAL_OUT_PATH3=`pwd`"/" #Alternative 2 (absolute path)

# path where error output will be saved
LOG_PATH="./"


# test01: print base class; Expected output: test01.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test01.in --output=${LOCAL_OUT_PATH}test01.out --details=C 2> ${LOG_PATH}test01.err
echo -n $? > test01.!!!

diff test01.\!\!\! ./ref-out/test01.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test01"
fi

java -jar ./jexamxml/jexamxml.jar test01.out ./ref-out/test01.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test01"
fi

echo "test01 complete"

# test02: inheritance tree; Expected output: test02.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test02.in > ${LOCAL_OUT_PATH}test02.out 2> ${LOG_PATH}test02.err
echo -n $? > test02.!!!

diff test02.\!\!\! ./ref-out/test02.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test02"
fi

java -jar ./jexamxml/jexamxml.jar test02.out ./ref-out/test02.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test02"
fi

echo "test02 complete"

# test03: print class which inherits from other one; Expected output: test03.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test03.in --output=${LOCAL_OUT_PATH}test03.out --details=D 2> ${LOG_PATH}test03.err
echo -n $? > test03.!!!

diff test03.\!\!\! ./ref-out/test03.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test03"
fi

java -jar ./jexamxml/jexamxml.jar test03.out ./ref-out/test03.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test03"
fi

echo "test03 complete"


# test04: overloading of pure virtual method; Expected output: test04.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION < ${LOCAL_IN_PATH3}test04.in > ${LOCAL_OUT_PATH}test04.out 2> ${LOG_PATH}test04.err
echo -n $? > test04.!!!

diff test04.\!\!\! ./ref-out/test04.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test04"
fi

java -jar ./jexamxml/jexamxml.jar test04.out ./ref-out/test04.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test04"
fi

echo "test04 complete"


# test05: pure virtual method inherited; Expected output: test05.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test05.in --output=${LOCAL_OUT_PATH}test05.out 2> ${LOG_PATH}test05.err
echo -n $? > test05.!!!

diff test05.\!\!\! ./ref-out/test05.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test05"
fi

java -jar ./jexamxml/jexamxml.jar test05.out ./ref-out/test05.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test05"
fi

echo "test05 complete"


# test06: diamond inheritance => conflict; Expected output: test06.out; Expected return code: 21
$INTERPRETER $TASK.$EXTENSION --output=${LOCAL_OUT_PATH3}test06.out < ${LOCAL_IN_PATH}test06.in --details=D 2> ${LOG_PATH}test06.err
echo -n $? > test06.!!!

diff test06.\!\!\! ./ref-out/test06.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test06"
fi

echo "test06 complete"


# test07: diamond inheritance => conflict solved by method overriding; Expected output: test07.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --details=D --input=${LOCAL_IN_PATH}test07.in --output=${LOCAL_OUT_PATH2}test07.out 2> ${LOG_PATH}test07.err
echo -n $? > test07.!!!

diff test07.\!\!\! ./ref-out/test07.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test07"
fi

java -jar ./jexamxml/jexamxml.jar test07.out ./ref-out/test07.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test07"
fi

echo "test07 complete"


# test08: print all details of all classes; Expected output: test08.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --details --input=${LOCAL_IN_PATH}test08.in --output=${LOCAL_OUT_PATH3}test08.out 2> ${LOG_PATH}test08.err
echo -n $? > test08.!!!

diff test08.\!\!\! ./ref-out/test08.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test08"
fi

java -jar ./jexamxml/jexamxml.jar test08.out ./ref-out/test08.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test08"
fi

echo "test08 complete"


# test09: more complicated inheritance tree; Expected output: test09.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH2}test09.in --output=${LOCAL_OUT_PATH}test09.out 2> ${LOG_PATH}test09.err
echo -n $? > test09.!!!

diff test09.\!\!\! ./ref-out/test09.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test09"
fi

java -jar ./jexamxml/jexamxml.jar test09.out ./ref-out/test09.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test09"
fi

echo "test09 complete"


# test10: conflict solved by using keyword; Expected output: test10.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}test10.in --output=${LOCAL_OUT_PATH}test10.out --details=C 2> ${LOG_PATH}test10.err
echo -n $? > test10.!!!

diff test10.\!\!\! ./ref-out/test10.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test10"
fi

java -jar ./jexamxml/jexamxml.jar test10.out ./ref-out/test10.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test10"
fi

echo "test10 complete"


# test11: XPATH search; Expected output: test11.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test11.in --output=${LOCAL_OUT_PATH2}test11.out --details --search="/model/class[*/attributes/attribute/@name='var']/@name" 2> ${LOG_PATH}test11.err
echo -n $? > test11.!!!

diff test11.\!\!\! ./ref-out/test11.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test11"
fi

java -jar ./jexamxml/jexamxml.jar test11.out ./ref-out/test11.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test11"
fi

echo "test11 complete"


# test12: print conflict members; Expected output: test12.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}test12.in --output=${LOCAL_OUT_PATH}test12.out --details=C --conflicts 2> ${LOG_PATH}test12.err
echo -n $? > test12.!!!

diff test12.\!\!\! ./ref-out/test12.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test12"
fi

java -jar ./jexamxml/jexamxml.jar test12.out ./ref-out/test12.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test12"
fi

echo "test12 complete"


# test13: do not print inherited private member; Expected output:  test13.out; Exptected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}test13.in --output=${LOCAL_OUT_PATH}test13.out --details=B 2> ${LOG_PATH}test13.err
echo -n $? > test13.!!!

diff test13.\!\!\! ./ref-out/test13.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test13"
fi

java -jar ./jexamxml/jexamxml.jar test13.out ./ref-out/test13.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test13"
fi

echo "test13 complete"


#Error tests
# test 14: two attributes with the same name, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr14.in 2> /dev/null

echo "test14 complete (retcode = 4 ?): $?"


# test 15: two methods with the same name, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr15.in 2> /dev/null

echo "test15 complete (retcode = 4 ?): $?"


# test 16: inheritance from undefined class, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr16.in 2> /dev/null

echo "test16 complete (retcode = 4 ?): $?"


# test 17: used "using" to undefined class, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr17.in 2> /dev/null

echo "test17 complete (retcode = 4 ?): $?"


# test 18: using two times with the same member from the same class, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr18.in 2> /dev/null

echo "test18 complete (retcode = 4 ?): $?"


# test 19: using unknown member from class, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr19.in 2> /dev/null


echo "test19 complete (retcode = 4 ?): $?"


# test 20: conflict in class H, expected return code: 21
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr20.in 

echo "test20 complete (conflict in H and retcode: 21 ?): $?"


# test 21: conflict in class H, expected return code: 21
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr21.in

echo "test21 complete (conflict in H and retcode: 21 ?): $?"


# test 22: redefinition of class, expected return code > 99
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr22.in 2> /dev/null

echo "test22 complete (retcode = 4 ?): $?"


# test 23: bad arguments, expected return code: 1
$INTERPRETER $TASK.$EXTENSION --input= 2> /dev/null

echo "test23 complete (retcode = 1 ?): $?"

# test 24: bad arguments, expected return code: 1
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr22.in --output 2> /dev/null

echo "test24 complete (retcode = 1 ?): $?"


# test 25: bad arguments, expected return code: 1
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}testErr22.in --pretty-xml=hello 2> /dev/null

echo "test25 complete (retcode = 1 ?): $?"


# test 26: unexisted file, expected return code: 2
$INTERPRETER $TASK.$EXTENSION --input=unexistedfile7799654123654786541254452.txt.in 2> /dev/null

echo "test26 complete (retcode = 2 ?): $?"




# test 27: pointers and ampersands test; expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test27.in --output=./test27.out --details
echo -n $? > test27.!!!

diff test27.\!\!\! ./ref-out/test27.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test27"
fi

java -jar ./jexamxml/jexamxml.jar test27.out ./ref-out/test27.out ./jexamxml/delta.xml ./jexamxml/cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test27"
fi

echo "test27 complete"