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
import sys
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

def generate_html(output, patches):
    for comment, patch in get_list_of_commits(patches):
        output.write(markdown.markdown(comment))
        output.write("\n")

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-o", "--output", dest="filename",
                      help="write output to FILE rather than STDOUT", metavar="FILE")

    (options, patches) = parser.parse_args(argv[1:])
    abspatches = [os.path.abspath(patch) for patch in patches]

    if options.filename == None:
        output = sys.stdout
    else:
        output = open(options.filename, 'w')

    generate_html(output, abspatches)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

