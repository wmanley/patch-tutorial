#!/usr/bin/env python

import markdown
import subprocess
import re

def prettify_diff(parent, diff_in):
    for line in iter(diff_in):
        if len(line) >= 4 and line[0:4] == "+++ ":
            file_container = markdown.etree.SubElement(parent, "div")
            file_container.set("class", "file_container")
            filename_container = markdown.etree.SubElement(file_container, "div")
            filename = line.split()[1]
            filename_container.text = "/".join(filename.split("/")[2:])
            filename_container.set('class', 'filename')
        elif len(line) >= 4 and line[0:4] == "--- ":
            pass
        elif len(line) >= 3 and line[0:3] == '@@ ':
            start_line = re.match('@@ -(\d+)(,\d+)? \+\d+(,\d+)? @@', line).group(1)
            hunk_header = markdown.etree.SubElement(file_container, "div")
            hunk_header.text = "line %s..." % start_line
            hunk_header.set('class', 'hunk_header')
            hunk_container = markdown.etree.SubElement(file_container, "pre")
            hunk_container.set("class", "diff")
            hunk_code = markdown.etree.SubElement(hunk_container, "code")
        else:
            c = { '-': 'diff_old',
                  '+': 'diff_new',
                  ' ': 'diff_unchanged' }.get(line[0])
            newelement = markdown.etree.SubElement(hunk_code, "div")
            newelement.set("class", c)
            newelement.text = markdown.AtomicString(line[1:])

def open_diff(old, new):
    dp = subprocess.Popen(["diff", "-u", old, new], stdout=subprocess.PIPE)
    return dp.stdout

class DiffBlockProcessor(markdown.blockprocessors.BlockProcessor):
    def __init__(self, configs):
        self.configs = configs
        self.srcdir = "."

    def test(self, parent, block):
        return block.startswith("@diff")

    def run(self, parent, blocks):
        block = blocks.pop(0)
        assert block.startswith("@diff")
        files = block[5:].split()
        for f in files:
            prettify_diff(parent, open_diff(self.srcdir + "/old/" + f, self.srcdir + "/new/" + f))

class ShowPatchExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add('diff',
                                      DiffBlockProcessor(md.parser),
                                      '_begin')

def makeExtension(configs=None) :
    return ShowPatchExtension(configs)

