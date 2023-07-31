import unittest
import clang.cindex
import sys
sys.path.append("..")
from Refactorer import Refactor

ref = Refactor("asdfkjasldkfj")

ref._convertHTMLtoCPP("DummyCode/FooClass.cpp.html", "DummyCode/blablabla.cpp")
ref.generateCppFile("DummyCode/blablabla.cpp", "DummyCode/FooClass.h", "DummyCode/final.cpp")
print(ref.send_prompt_to_cgpt("DummyCode/final.cpp"))

