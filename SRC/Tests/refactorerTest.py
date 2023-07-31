import unittest
import clang.cindex
import sys
sys.path.append("..")
from Refactorer import Refactor

ref = Refactor("asdfkjasldkfj")

ref._convertHTMLtoCPP("DummyCode/FooClass.cpp.html", "DummyCode/blablabla.cpp")
ref.generateCppFile("DummyCode/blablabla.cpp", "DummyCode/FooClass.h", "DummyCode/final.cpp")