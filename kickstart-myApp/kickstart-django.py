# -*- coding: utf-8 -*-
import os
import subprocess
import argparse
import string

lastest_gitignore_url = "https://raw2.github.com/github/gitignore/master/Python.gitignore"
latest_buildout_url = "http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py"
basic_buildout_cfg = u"""[buildout]
parts = python django node web-components
develop = .
eggs = $app_name

[python]
recipe = zc.recipe.egg
interpreter = python
eggs = $${buildout:eggs}

[versions]
django = 1.6.5

[paths]
downloads = downloads

[django]
recipe = djangorecipe
settings = development
eggs = $${buildout:eggs}
project = project

[node]
recipe = gp.recipe.node
npms = bower
scripts = bower

[web-components]
recipe = bowerrecipe
packages = jquery#2.1.0 bootstrap#3.1.1 underscore#1.5.2 backbone#1.1.0 jquery-file-upload#9.5.7
executable = $${buildout:bin-directory}/bower
base-directory = $${paths:downloads}
downloads = web-components
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
    install_requires=['setuptools', 'django-extensions'],
)
"""

basic_readme = """ Do not forget to source the *activate* script:
source activate
"""

development_py = u"""# -*- coding: utf-8 -*-
from project.settings import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin', 'root@localhost'),
)

HOSTNAME = 'localhost'

MANAGERS = ADMINS

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__)) + '/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_ROOT + 'database.sqlite',
    }
}

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'

TEMPLATE_DIRS += (
    os.path.join(PROJECT_ROOT, 'templates/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
MEDIA_URL = 'http://%s:8000/media/' % HOSTNAME

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/')
STATIC_URL = 'http://%s:8000/static/' % HOSTNAME

INSTALLED_APPS += (
    'django.contrib.admin',
    'django_extensions',
)
"""

urls_py = u"""# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
"""

t_kickstart_stage2_sh = u"""#!/bin/bash
activate () {
    . ${virtualenv_dir}/bin/activate
}
activate
./bin/buildout
exit 0
"""

t_kickstart_stage3_sh = u"""#!/bin/bash
activate () {
    . ${virtualenv_dir}/bin/activate
}

activate
mkdir -p ./project/static
bin/django syncdb --noinput
bin/django collectstatic --noinput --link

echo "from django.contrib.auth.models import User;User.objects.create_superuser('django', 'admin@e.com', 'django')" | bin/django shell

echo "All work is done here !"
echo "Don't forget to source activate script : source activate"
exit 0
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
    parser.add_argument(
        "remote_git_repo",
        help="URL of a remote git repository. This will be used to push commits.",
        default='local',
        nargs='?'
    )

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

    kickstart_stage2_sh = string.Template(t_kickstart_stage2_sh)
    filename, data = working_dir+"/kickstart_stage2.sh", kickstart_stage2_sh.substitute(virtualenv_dir=virtualenv_dir)
    fn_touch_and_write(filename, data)

    kickstart_stage3_sh = string.Template(t_kickstart_stage3_sh)
    filename, data = working_dir+"/kickstart_stage3.sh", kickstart_stage3_sh.substitute(virtualenv_dir=virtualenv_dir)
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

        if subprocess.call(["bash", working_dir+"/kickstart_stage2.sh"]):
            raise Exception("Unable to execute kickstart_stage2.sh")

        os.unlink(working_dir+"/project/development.py")
        os.unlink(working_dir+"/project/urls.py")
        filename, data = working_dir+"/project/development.py", development_py
        fn_touch_and_write(filename, data)
        filename, data = working_dir+"/project/urls.py", urls_py
        fn_touch_and_write(filename, data)

        if subprocess.call(["bash", working_dir+"/kickstart_stage3.sh"]):
            raise Exception("Unable to execute kickstart_stage3.sh")

        os.unlink(working_dir+"/kickstart_stage2.sh")
        os.unlink(working_dir+"/kickstart_stage3.sh")

if __name__ == '__main__':
    main()
