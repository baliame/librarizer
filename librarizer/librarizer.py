from __future__ import print_function
import click
from .context import Context, verbosity_quiet, verbosity_normal, verbosity_loud
from .getch import getch
from shutil import copyfile
import os
import re
import time
from os.path import join as pathjoin

import sys


context = Context()


@click.command()
@click.argument('source_root')
@click.argument('destination_root')
@click.option("-s", "--quiet", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-t", "--trace", is_flag=True)
@click.option("-d", "--delete", is_flag=True, help='If set, delete the original files. Mutually exclusive with --link-only.')
@click.option("-l", "--link-only", is_flag=True, help='If set, symbolic link the original files instead of copying them. Mutually exclusive with --delete. Requires elevated privileges under Windows.')
@click.option("-m", "--max-depth", type=int, default=3, help='Maximum depth to traverse into the directory structure.')
@click.option("-e", "--include-extension", type=str, multiple=True, help='Additional extensions to include in the search. By default, we look for avi, mp4 and mkv. You may specify this option multiple times.')
@click.option("--no-year-detection", is_flag=True, help='If set, librarizer will not ask for confirmation about numbers that could be construed as years, and consider them part of the title instead.')
@click.option("--auto-year-after", type=int, default=0, help='If set, librarizer will not ask for confirmation about numbers that could be construed as years. All numbers at the end of the title between the value of this option and the current year is considered and year and will be parenthesized. The default value of 0 indicates this option is turned off. Has no effect is --no-year-detection is set.')
@click.option("-y", "--yes", is_flag=True, help='Shorthand for --auto-year-after=1900.')
def cli(**kwargs):
    if kwargs["quiet"] and kwargs["verbose"]:
        raise ValueError("Confusing arguments: both --quiet and --verbose provided.")
    if kwargs["link_only"] and kwargs["delete"]:
        raise ValueError("Confusing arguments: both --delete and --link-only provided.")
    dr = kwargs["destination_root"]
    try:
        os.stat(dr)
    except Exception:
        os.mkdir(dr)
    context.click = click
    context.merge(kwargs, exclude=["source_root", "destination_root", "quiet", "verbose", "include_extension"])
    if context["yes"]:
        context["auto-year-after"] = 1900
    context.verbose = verbosity_quiet if kwargs["quiet"] else verbosity_loud if kwargs["verbose"] else verbosity_normal
    if context["trace"]:
        sys.settrace(tracefunc)
    exts = ["avi", "mp4", "mkv"]
    exts.extend([s.lstrip('. ') for s in kwargs['include_extension']])
    context.storage["regex"] = re.compile(r'(?P<title>.+)\.S(?P<season>[0-9]+)E(?P<episode>[0-9]+).+?(?:-(?P<group>.+?)(?:\[.+?\])?)?\.(?P<extension>{0})'.format('|'.join(exts)))
    files = rectrav(kwargs["source_root"])
    context.log("Traversing complete!", min_verbosity=verbosity_loud)
    year = int(time.strftime("%Y"))
    for path, data in files.items():
        context.log("Processing {0}".format(path), min_verbosity=verbosity_loud)
        rn = context(data["title"])
        if rn is not None:
            title = rn
        else:
            title = data["title"]
            p = title.split(' ')
            idx = len(p) - 1
            if (p[idx].isdigit()):
                py = int(p[idx])
                if py <= year and not context["no-year-detection"] and ((context["auto-year-after"] != 0 and py >= context["auto-year-after"]) or py >= 1900):
                    if context["auto-year-after"] != 0:
                        p[idx] = '({0})'.format(p[idx])
                        nt = ' '.join(p)
                        context.rename(title, nt)
                        title = nt
                    else:
                        print("Found series titled '{0}' - is {1} the year it was released? (Y)es/(n)o  ".format(title, py), end='')
                        sys.stdout.flush()
                        inp = ''
                        while inp not in ['y', 'Y', 'n', 'N', '']:
                            inp = getch()
                            if inp not in ['y', 'Y', 'n', 'N', '']:
                                print('Please answer with (Y)es/(n)o.  ', end='')
                        if inp in ['y', 'Y', '\n']:
                            p[idx] = '({0})'.format(p[idx])
                            nt = ' '.join(p)
                            context.rename(title, nt)
                            title = nt
        context.log("Title: {0}".format(path), min_verbosity=verbosity_loud)
        destdir = pathjoin(dr, title)
        try:
            os.stat(destdir)
        except Exception:
            os.mkdir(destdir)
        dfn = "{0} - S{1}E{2} [{3}].{4}".format(title, data["season"], data["episode"], data["group"], data["extension"])
        if context["link-only"]:
            context.log("Linking {0} to {1}.".format(path, pathjoin(destdir, dfn)))
            os.symlink(path, pathjoin(destdir, dfn))
        else:
            context.log("Copying {0} to {1}.".format(path, pathjoin(destdir, dfn)))
            copyfile(path, pathjoin(destdir, dfn))
            if context["delete"]:
                context.log("Deleting {0}.".format(path, pathjoin(destdir, dfn)))
                os.remove(path)
    #    print("== Found TV episode at {0} ==".format(path))
    #    print("Title: {0}".format(data["title"]))
    #    print("Season: {0}".format(data["season"]))
    #    print("Episode: {0}".format(data["episode"]))
    #    print("Release group: {0}".format(data["group"]))
    #    print("Extension: {0}".format(data["extension"]))


def tracefunc(frame, event, args):
    if event == 'call':
        context.log('{0}:{1} -> {2}:{3} {4}'.format(frame.f_back.f_code.co_filename, frame.f_back.f_lineno, frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name), min_verbosity=verbosity_quiet)


def rectrav(path, depth=0):
    ret = {}
    context.log("Traversing {0}".format(path))
    for elem in os.scandir(path):
        if elem.is_file(follow_symlinks=False):
            mo = context.storage["regex"].match(elem.name)
            if mo is not None:
                ret[pathjoin(path, elem.name)] = {
                    "title": mo.group('title').replace('.', ' '),
                    "season": int(mo.group('season')),
                    "episode": int(mo.group('episode')),
                    "group": mo.group("group"),
                    "extension": mo.group("extension")
                }
        elif elem.is_dir(follow_symlinks=True) and depth < context["max-depth"]:
            ret.update(rectrav(pathjoin(path, elem.name), depth + 1))
    return ret
