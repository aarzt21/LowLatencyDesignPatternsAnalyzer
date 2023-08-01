import unittest
import clang.cindex
import sys
sys.path.append("..")
from Refactorer import Refactor

ref = Refactor()

ref._convertHTMLtoCPP("/home/alex/Desktop/Test/HTML_OUT/BarClass.cpp.html", "/home/alex/Desktop/Test/HTML_OUT/BarClass.cpp")
ref.generateCppFile("/home/alex/Desktop/Test/HTML_OUT/BarClass.cpp", "/home/alex/Desktop/Test/HTML_OUT/BarClass.h", "/home/alex/Desktop/Test/HTML_OUT/BarClass.cpp")

