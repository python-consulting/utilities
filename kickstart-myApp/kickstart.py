# -*- coding: utf-8 -*-
import os
import subprocess
import argparse
import string

lastest_gitignore_url = "https://raw2.github.com/github/gitignore/master/Python.gitignore"
latest_buildout_url = "http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py"
basic_buildout_cfg = u"""[buildout]
parts = python
develop = .
eggs = $app_name

[python]
recipe = zc.recipe.egg
interpreter = python
eggs = $${buildout:eggs}
"""

basic_setup_py = u"""# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="$app_name",
    version="0.1",
    license='All rights reserved',
    description="$app_name",
    author='modify_with_you_name',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
)
"""

basic_readme =""" Do not forget to source the *activate* script:
source activate
"""

def suppress_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pass
    return wrapper

def mkdir(in_dir):
    if not os.path.exists(in_dir):
        os.makedirs(in_dir)
    else:
        raise Exception('Directory %s already exists. Will not overwrite. Aborting.' % in_dir)

@suppress_errors
def try_mkdir(in_dir):
    return mkdir(in_dir)

def touch_and_write(filename, data):
    if not os.path.exists(filename):
        fd = open(filename, "w")
        if not fd:
            raise Exception("Unable to create %s. Check for read-write permissions." % filename)
        fd.write(data)
        fd.close()
    else:
        raise Exception('File %s already exists. Will not overwrite. Aborting.' % filename)

@suppress_errors
def try_touch_and_write(filename, data):
    return touch_and_write(filename, data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("application_name", help="Name of the application (e.g. myApp)")
    parser.add_argument("remote_git_repo", help="URL of a remote git repository. This will be used to push commits.",
        default = 'local', nargs='?')
    
    args = parser.parse_args()
    app_name = args.application_name
    
    working_dir = "%s/%s" % (os.getcwd(), app_name)
    mkdir(working_dir)

    if args.remote_git_repo == 'local':
        git_repo_dir = "%s/%s.git" % (os.getcwd(), app_name)
        mkdir(git_repo_dir)
        if subprocess.call(["git", "--bare", "init", git_repo_dir]):
            raise Exception("Unable to create git repository. Check for git installation or read-write permissions.")
        fn_touch_and_write = touch_and_write
        fn_mkdir = mkdir
    else:
        git_repo_dir = args.remote_git_repo
        fn_touch_and_write = try_touch_and_write
        fn_mkdir = try_mkdir

    if subprocess.call(["git", "clone", git_repo_dir, working_dir]):
        raise Exception("Unable to clone git repository. Check for read-write permissions.")
    
    if subprocess.call(["wget", "--no-check-certificate", lastest_gitignore_url, "-O", "%s/.gitignore" % working_dir]):
        raise Exception("Unable to get latest gitignore file from github. Check your internet connection.")

    if subprocess.call(["wget", "--no-check-certificate", latest_buildout_url, "-O", "%s/bootstrap.py" % working_dir]):
        raise Exception("Unable to get latest buildout bootstrap script from zope. Check your internet connection.")

    virtualenv_dir = "%s/virtualenv_%s" % (os.getcwd(), app_name)
    
    if subprocess.call(["virtualenv", virtualenv_dir]):
        raise Exception("Unable to create virtual environment. Check the virtualenv installation.")


    buildout_cfg = string.Template(basic_buildout_cfg)
    filename, data = working_dir+"/buildout.cfg", buildout_cfg.substitute(app_name=app_name)
    fn_touch_and_write(filename, data)
    
    setup_py = string.Template(basic_setup_py)
    filename, data = working_dir+"/setup.py", setup_py.substitute(app_name=app_name)
    fn_touch_and_write(filename, data)

    working_dir_src = "%s/%s/src" % (os.getcwd(), app_name)
    fn_mkdir(working_dir_src)

    fn_touch_and_write("%s/README" % working_dir, basic_readme)

    # Upgrate setuptools
    virtualenv_ezi = "%s/virtualenv_%s/bin/easy_install" % (os.getcwd(), app_name)
    if subprocess.call([virtualenv_ezi, "--upgrade", "setuptools"]):
        raise Exception("Unable to upgrade setuptools")

    virtualenv_python = "%s/virtualenv_%s/bin/python" % (os.getcwd(), app_name)
    os.chdir(working_dir)

    if subprocess.call([virtualenv_python, working_dir+"/bootstrap.py"]):
        raise Exception("Unable to launch buildout bootstrap.")

    os.unlink('bootstrap.py')

    if args.remote_git_repo == 'local':
        virtualenv_activate_script = "../virtualenv_%s/bin/activate" % app_name
        if subprocess.call(["ln", "-s", virtualenv_activate_script, "./activate"]):
            raise Exception("Unable to create link from virtualenv activate script.")

        if subprocess.call(["touch", "src/README"]):
            raise Exception("src folder does not exits or unable to create file README")

        if subprocess.call(["git", "add", "src", "buildout.cfg", "setup.py", ".gitignore", "README"]):
            raise Exception("Unable to execute git commands.")

        if subprocess.call(["git", "commit", "-m", "Initial - automatic - commit"]):
            raise Exception("Unable to execute git commands.")

        if subprocess.call(["git", "push", "origin", "master"]):
            raise Exception("Unable to execute git commands.")

if __name__ == '__main__':
    main()
