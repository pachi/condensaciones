#!/usr/bin/env python
#encoding: iso-8859-15

def stringify(list, prec):
    format = '%%.%if' % prec
    return "[" + ", ".join([format % item for item in list]) + "]"

