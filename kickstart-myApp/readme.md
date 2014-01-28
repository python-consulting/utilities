# Introduction #

A suivre ici, une série d'articles visant à simplifier, automatiser et bien architecturer un projet d'application web.

# L'inception #

Une idée germe, un besoin émerge : vous savez que vous allez développer une solution à base d'application(s) web (ici on utilisera Django). A force de réinventer la roue tous les quatre matins, ça n'avance jamais assez vite. Et puis, il y a toujours l'espèce de découragement qui vous guette une fois un certain temps passé sur les tâches les moins intéressantes. Donc cette fois, on va faire en sorte d'aller le plus rapidement possible au développement de votre application mais en bâtissant une structure de travail la plus robuste et la plus fonctionnelle possible. Cette fois, on va bien faire les choses !

# Le cycle de vie d'une application web #

Sans rentrer dans des considérations métaphysiques, le cycle de vie objectif d'une application web devrait ressembler à ça:

1. Définition claire et concise de l'objectif
2. Chasse aux modules existant sur le web afin de minimiser le temps de développement
3. Phase d'intégration / évaluation des modules
4. Développement des modules propres à votre application (Tests intégrés)
5. Déploiement
6. Gestion des évolutions en reprenant à la phase 2

Dans cet article, nous allons voir comment bien traiter les étapes 2 à 6 en étant le plus efficace possible.

# Une trousse à outils #

L'objectif étant d'être efficace, de bons outils sont indispensables. Ci-dessous la liste absolument minimale :
* Git
* Buildout
* Virtualenv

# Bootstrap(ons) ! #

On veut (doit) bien faire les choses, donc ça suppose quelques opérations assez rébarbatives, donc on va bootstraper(c) tout ça... Notons que les étapes qui suivent sont décrites à titre informatif et que celles-ci feront l'objet d'une automatisation complète.

## Les préliminaires, l'indispensable en fait ##

Bon ce paragraphe récapitulel 'absolu nécessaire, mais qu'il faut rappeler, et puis c'est pratique...par contre ça marche pour debian, les autres repassez plus tard.

```Shell
apt-get install -y git build-essential python-pip
```

## Gestion de version - Qui a dit GIT ? ##
### Etape 1 : Création d'un dépôt GIT ###

On crée un dépôt GIT dans un répertoire bien au chaud :

```Shell
#~/repo-git/: mkdir myApp.git
#~/repo-git/: cd myApp.git
#~/repo-git/: git --bare init
```

### Etape 2 : On définit un espace de travail ###

Ici, on va dupliquer (cloner) notre dépôt pour y travailler:

```Shell
#~/work-dir/: git clone ~/repo-git/myApp.git
Cloning into 'myApp'...
done.
```

On récupère le fichier de configuration *.gitignore* dédié aux applications python. Celui de Github est celui qu'il vous faut.

```Shell
#~/work-dir/myApp/: wget https://raw2.github.com/github/gitignore/master/Python.gitignore
#~/work-dir/myApp/: mv Python.gitignore .gitignore
```

On peut commencer à bosser maintenant ... ah.. non pas encore, il nous faut un virtualenv, sinon on va perdre notre temps sur des ...

## Virtualenv, le bac à sable ##

L'installation est assez simple :

```Shell
#~/work-dir/: pip install virtualenv
```

Et on crée un environnement pour nos travaux, je ne rentrerai pas dans le détail de l'utilisation de virtualenv pour la gestion des différentes versions des paquets.

```Shell
#~/work-dir/: mkdir virtualEnvDir ; cd virtualEnvDir
#~/work-dir/virtualEnvDir/: virtualenv myAppVirtEnv
```

Et donc, pour pouvoir travailler dans ce bac à sable (et y installer tout plein de librairies qui ne pourriront pas notre machine), il suffit de :

```Shell
#~/work-dir/virtualEnvDir/: source myAppVirtEnv/bin/activate
```

On a un environnement de travail assez propre, continuons en intégrant buildout.

## Buildout, la base ##
### En très bref ###

En très bref, Buildout est un outil de construction, d'assemblage et de déploiement d'applications à partir de tout type de source (non exclusivement du python). En construisant une configuration donnée, Buildout permet de reproduire l'application dans les mêmes conditions.

### Le script d'installation ###

On va récupérer le script d'installation de buildout et préparer notre arborescence :

```Shell
#~/work-dir/myApp/: wget http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py
```

On dispose à ce moment d'une structure basique mais quasi-complète pour commencer à travailler sérieusement.

### La configuration buildout ###

La configuration de buildout est en fait la configuration de notre projet d'application. On doit spécifier la structure et les dépendances de notre application. Nous allons voir ça dans les articles suivants.

# A suivre... #

Au menu des articles suivants :

* La structure du projet d'application
* Aspects spécifiques Python/Django
* Apache et django
* Template HTML5 et tout le *boilerplate*
* ...


# Bonus #
Le script qui automatise les étapes vues précédemment (hors installation git, pip et virtualenv) est disponible sur github :
https://github.com/python-consulting/utilities/tree/master/kickstart-myApp

Le script réalise les opérations suivantes :
* Création d'un dépôt git
* Clone du dépôt git
* Récupération du *.gitignore*
* Récupération du script de buildout
* Création du virtualenv
* Création des fichiers de configuration basiques
* Commit initial et push vers le dépôt git

Il est également possible d'initialiser le dépôt git à partir d'un dépôt existant (mais vide). Par exemple en créant un dépôt sur github, par exemple https://github.com/mon-login/myApp il suffit de noter l'url en 2e argument du script. Cela permet tout de même d'avoir une configuration idéale en environ 20 secondes ;)

Il ne reste plus qu'à *sourcer* le fichier virtualenv_activate_script et le développement peut démarrer.

Le script fonctionne comme décrit ci-dessous.

```Shell
#~/: python kickstart.py -h
usage: kickstart.py [-h] application_name [remote_git_repo]

positional arguments:
  application_name  Name of the application (e.g. myApp)
  remote_git_repo   URL of a remote git repository. This will be used to push
                    commits.

optional arguments:
  -h, --help        show this help message and exit

#~/: python kickstart.py myApp
...
#~/: ls
myApp  myApp.git  virtualenv_myApp
#~/: ls myApp
bin  buildout.cfg  develop-eggs  eggs  parts  README  setup.py  src  virtualenv_activate_script
```

Et avec un dépôt distant vierge :

```Shell
#~/: python kickstart.py myApp https://github.com/mon-login/myApp
...
#~/: ls
myApp  myApp.git  virtualenv_myApp
#~/: ls myApp
bin  buildout.cfg  develop-eggs  eggs  parts  README  setup.py  src  virtualenv_activate_script
```
