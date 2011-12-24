#!/usr/bin/env python
# coding=UTF-8
###############################################################################
# Copyright (c) 2011 André D. Piske
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##############################################################################

import os
import io
import sys
import subprocess
import tempfile
import argparse
from lxml import etree

"""
The export tag:
<export
    file='file name'
    />
"""

input_file = ''
dom_tree = None
page_coords = None

def toikcoords(c):
    " Transform from SVG coordinates do Inkscape Coordinates "
    global dom_tree
    root = dom_tree.getroot()
    doc_width = float( root.get('width') )
    doc_height = float( root.get('height') )
    i = 0
    cn = dict()
    while True:
        xN = 'x' + str(i)
        yN = 'y' + str(i)
        if not xN in c:
            break
        x,y = float(c[xN]), float(c[yN])
        cn[xN] = str(x)
        cn[yN] = str(doc_height - y)
        i += 1
    return cn


def main():
    global dom_tree, p_args
    dom_tree = etree.parse(input_file)
    exports = dom_tree.findall('//export')

    exports_commands = []

    for expo in exports:
        parent = expo.getparent()
        export_file = expo.get('file')
        bounds = {
            'x0':  parent.get('x'),
            'y0': parent.get('y'),
        }
        bounds['x1'] = str( float(parent.get('width')) + float(bounds['x0']) )
        bounds['y1'] = str( float(parent.get('height')) + float(bounds['y0']) )

        bounds = toikcoords(bounds)
        
        args = ['inkscape', '-e', p_args.dir + '/' + export_file, '-a',
            '%(x0)s:%(y0)s:%(x1)s:%(y1)s' % bounds]

        exports_commands.append(args)

    for expo in exports:
        p = expo.getparent()
        p.getparent().remove(p)

    tmp_f = tempfile.mkstemp('.svg')[1]
    f = io.open(tmp_f, 'wb')
    dom_tree.write(f, encoding='UTF-8')
    f.close()

    try:
        for expo in exports_commands:
            args = expo + [tmp_f]
            print('Invoking ' + str(' '.join(args)))
            r = subprocess.Popen(args=args, executable='inkscape').wait()
            if r != 0:
                print('Something went wrong')
            else:
                print('ok')
    finally:
        os.remove(tmp_f)


if __name__ == '__main__':
    global p_args
    p = argparse.ArgumentParser(description='Export PNG from Inkscape SVG',
        prog='pngfromiksvg')
    p.add_argument('-C', '--directory', dest='dir', action='store', default='.',
            help='Destination directory')
    p.add_argument('-v', '--version', help='Show version', action='version',
        version='%(prog)s 0.1.1')
    p.add_argument('file')
    p_args = p.parse_args()
    input_file = p_args.file
    if p_args.dir[len(p_args.dir)-1] == '/':
        p_args.dir = p_args.dir[:len(p_args.dir)-1]
    main()



