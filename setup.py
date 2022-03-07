from setuptools import setup, find_packages

PACKAGES = find_packages()

CLASSIFIERS = ["Environment :: Console",
               "Intended Audience :: Science/Research",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Wikipedia API"]

NAME = "wikipedia-api"
DESCRIPTION = "A library enhance wikipedia RESTful API functionality"
URL = "https://github.com/IvyLinGit/wikipedia_api"
AUTHOR = "Weiqing (Ivy) Lin"
AUTHOR_EMAIL = "ivylin@uw.edu"
PLATFORMS = "Linux, Windows and MacOS"
VERSION = 1.0
REQUIRES = ["numpy", "pandas", "requests"]

opts = dict(name=NAME,
            description=DESCRIPTION,
            url=URL,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            version=VERSION,
            packages=PACKAGES,
            install_requires=REQUIRES,
            requires=REQUIRES)


if __name__ == '__main__':
    setup(**opts)