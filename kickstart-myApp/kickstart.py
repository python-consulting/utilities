# -*- coding: utf-8 -*-
import os
import subprocess
import argparse
import string

lastest_gitignore_url = "https://raw2.github.com/github/gitignore/master/Python.gitignore"
latest_buildout_url = "http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py"
basic_buildout_cfg = u"""
[buildout]
parts = python
develop = .
eggs = $app_name

[python]
recipe = zc.recipe.egg
interpreter = python
eggs = $${buildout:eggs}
"""

basic_setup_py = u"""
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "$app_name",
    version = "0.1",
    license = 'All rights reserved',
    description = "$app_name",
    author = 'modify_with_you_name',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
"""

basic_readme =""" Do not forget to source the virtualenv_activate_script script:
source virtualenv_activate_script
"""

def create_if_does_not_exist(in_dir):
    if not os.path.exists(in_dir):
        os.makedirs(in_dir)
    else:
        raise Exception('Unable to create %s. Aborting.' % in_dir)

def create_and_write_file(filename, data):
    fd = open(filename, "w")
    if not fd:
        raise Exception("Unable to create %s. Check for read-write permissions." % filename)
    fd.write(data)
    fd.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("application_name", help="Name of the application (e.g. myApp)")
    parser.add_argument("remote_git_repo", help="URL of a remote git repository. This will be used to push commits.",
        default = 'local', nargs='?')
    
    args = parser.parse_args()
    app_name = args.application_name
    
    working_dir = "%s/%s" % (os.getcwd(), app_name)
    create_if_does_not_exist(working_dir)

    if args.remote_git_repo == 'local':
        git_repo_dir = "%s/%s.git" % (os.getcwd(), app_name)
        create_if_does_not_exist(git_repo_dir)
        if subprocess.call(["git", "--bare", "init", git_repo_dir]):
            raise Exception("Unable to create git repository. Check for git installation or read-write permissions.")
    else:
        git_repo_dir = args.remote_git_repo

    if subprocess.call(["git", "clone", git_repo_dir, working_dir]):
        raise Exception("Unable to clone git repository. Check for read-write permissions.")
    
    if subprocess.call(["wget", lastest_gitignore_url, "-O", "%s/.gitignore" % working_dir]):
        raise Exception("Unable to get latest gitignore file from github. Check your internet connection.")

    if subprocess.call(["wget", latest_buildout_url, "-O", "%s/bootstrap.py" % working_dir]):
        raise Exception("Unable to get latest buildout bootstrap script from zope. Check your internet connection.")

    virtualenv_dir = "%s/virtualenv_%s" % (os.getcwd(), app_name)
    
    if subprocess.call(["virtualenv", virtualenv_dir]):
        raise Exception("Unable to create virtual environment. Check the virtualenv installation.")


    buildout_cfg = string.Template(basic_buildout_cfg)
    filename, data = working_dir+"/buildout.cfg", buildout_cfg.substitute(app_name=app_name)
    create_and_write_file(filename, data)

    setup_py = string.Template(basic_setup_py)
    filename, data = working_dir+"/setup.py", setup_py.substitute(app_name=app_name)
    create_and_write_file(filename, data)

    working_dir_src = "%s/%s/src" % (os.getcwd(), app_name)
    create_if_does_not_exist(working_dir_src)

    create_and_write_file("%s/README" % working_dir, basic_readme)

    virtualenv_python = "%s/virtualenv_%s/bin/python" % (os.getcwd(), app_name)
    os.chdir(working_dir)
    if subprocess.call([virtualenv_python, working_dir+"/bootstrap.py"]):
        raise Exception("Unable to launch buildout bootstrap.")

    virtualenv_activate_script = "../virtualenv_%s/bin/activate" % app_name
    if subprocess.call(["ln", "-s", virtualenv_activate_script, "./virtualenv_activate_script"]):
        raise Exception("Unable to create link from virtualenv activate script.")

    os.unlink('bootstrap.py')

    if subprocess.call(["touch", "src/README"]):
        raise Exception("Unable to create empty file")

    if subprocess.call(["git", "add", "src", "buildout.cfg", "setup.py", ".gitignore", "README"]):
        raise Exception("Unable to execute git commands.")

    if subprocess.call(["git", "commit", "-m", "Initial - automatic - commit"]):
        raise Exception("Unable to execute git commands.")

    if subprocess.call(["git", "push", "origin", "master"]):
        raise Exception("Unable to execute git commands.")

if __name__ == '__main__':
    main()