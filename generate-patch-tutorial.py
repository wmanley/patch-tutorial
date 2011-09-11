#!/usr/bin/env python

#
#  generate-patch-tutorial - Patch series to HTML tutorial converter
#
#  Copyright (C) 2011 William Manley <will@williammanley.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import StringIO
import optparse
import os.path
import os
import tempfile
import shutil
import sys
import subprocess
import markdown
import re

class commit_iterator:
    """
    Presents an iterator interface to patch lists.  The input format should
    be same as expected by "git am".  See man git-am for a description of the
    format.
    """
    def __init__(self, lineiter):
        self.lineiter = lineiter

    def __iter__(self):
        return self

    def next(self):
        comment = ""
        patch = ""

        subjectline = re.compile(r'Subject: (\[PATCH[^\]]*\] )?(.*)')
        patchbegin = re.compile(r'(---\n$|diff -|Index:)')

        match = None
        while not match:
            line = self.lineiter.next()
            match = subjectline.match(line)
        comment = match.group(2) + "\n"
        line = ""
        while not (patchbegin.match(line)):
            comment += line
            line = self.lineiter.next()

        line = ""
        while not (line == "-- \n"):
            patch += line
            line = self.lineiter.next()

        return (comment, patch)

def test_commit_iterator_without_patch():
    test_input_file=StringIO.StringIO("""
Some header stuff
To be ignored
Subject: This is the first line

and here is another one
---
Here is the patch
and it ends with a line like:
-- 
Stuff for ignoring
Heres an example with Subject
Subject: [PATCH 3/4] This is another first line

And a second body with a blank line next

and the end
---
The second patch contents
-- 
bye!
""")
    ci = list(commit_iterator(iter(test_input_file)))
    assert ("""This is the first line

and here is another one
""", """Here is the patch
and it ends with a line like:
""") == ci[0]
    assert ("""This is another first line

And a second body with a blank line next

and the end
""", """The second patch contents
""") == ci[1]

def get_list_of_commits(patch_list):
    lst = []
    for i in patch_list:
        f = open(i, 'r')
        lst.extend(list(commit_iterator(iter(f))))
        f.close()
    return lst

def apply_patch(path, patch):
    os.chdir(path)
    pp = subprocess.Popen(["patch", "-p1"], stdin=subprocess.PIPE, stdout=open("/dev/null", "w"))
    pp.stdin.write(patch)
    pp.stdin.close()
    if pp.wait() != 0:
        raise CalledProcessError()

header_html = """
<html>
    <head>
        <style>
            .diff_old {
                background-color: #FFCCCC;
                text-decoration: line-through;
            }
            .diff_new {
                background-color: #CCFFCC;
                font-weight:bold; }
            .filename {
                text-align: center;
                padding: 0.3em;
                margin: 0;
                border-bottom: solid thin black;
                font-family: sans-serif;
                font-size: small;
            }
            .show {
                margin: 0;
            }
            .diff {
                margin: 0;
            }
            .file_container {
                margin: 1em 3em 1em 3em;
            }
            .hunk_header {
                font-family: sans-serif;
                font-size: x-small;
                padding: 0 0 0 3em;
                background-color: #F0F0F0;
            }
        </style>
    </head>
    <body>
"""

footer_html = """
    </body>
</html>
"""

def generate_html(output, patches, decorate):
    tmpdir = tempfile.mkdtemp()
    assert tmpdir[0:5] == "/tmp/"
    os.mkdir(tmpdir + "/old")
    os.mkdir(tmpdir + "/new")
    if decorate:
        output.write(header_html)
    for comment, patch in get_list_of_commits(patches):
        apply_patch(tmpdir + "/new", patch)
        os.chdir(tmpdir)

        output.write(markdown.markdown(comment, ["showpatch"]))
        output.write("\n")

        apply_patch(tmpdir + "/old", patch)
    if decorate:
        output.write(footer_html)
    shutil.rmtree(tmpdir)

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-o", "--output", dest="filename",
                      help="write output to FILE rather than STDOUT", metavar="FILE")
    parser.add_option("-s", "--suppress-decoration", action="store_false", dest="decorate",
                      default=True, help="Don't write out header/footer")

    (options, patches) = parser.parse_args(argv[1:])
    abspatches = [os.path.abspath(patch) for patch in patches]

    if options.filename == None:
        output = sys.stdout
    else:
        output = open(options.filename, 'w')

    generate_html(output, abspatches, options.decorate)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

