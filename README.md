env_installer
========
[![Support Python Version](https://img.shields.io/badge/Python-3-brightgreen.svg)](https://www.python.org/)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

[中文](https://github.com/yandenghong/env_installer/blob/master/README_CN.md)


env_installer is a tool for online packaging and offline installation of python projects.

## Introduction
* This tool is based on `pip` and `virtualenv`. so, your project must conform to the pip workflow, ie your project must have a file similar to `requirements.txt` to record dependencies.

* Only supports `python 3` and `linux` system.

## Quick start
First clone the env installer to the local (any path, preferably in your home directory).

Suppose this is the project you are about to deploy (located at /home/DemoProject)

```text
DemoProject
├──assets
├──library
├──local
├──settings
├──temp
└──requirements.txt
```

### pack
```text
usage: pack.py [-h] -b BASE_DIR -r REQ_DIR [-d DOWNLOAD_DIR] [-v]
               [-i INDEX_URL]

arguments:
  -b BASE_DIR, --base-dir BASE_DIR
                        absolute path of the project to be packaged.
  -r REQ_DIR, --req-dir REQ_DIR
                        absolute path of production environment dependency
                        file.
  -d DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
                        absolute path of package storage location.
  -v                    if need to download an additional `virtualenv`
                        package, use this param. default false.
  -i INDEX_URL, --index-url INDEX_URL
                        download package index url, equivalent to `pip install
                        -i`.

```

the absolute path of your project: 
```text
/home/DemoProject
```

the absolute path of dependent file: 
```text
/home/DemoProject/requirements.txt
```

If viutalenv is not already installed on the server, add the `-v` parameter and the env installer will download the installation package for you.

If the default pip source download is slow, you can replace it with `-i`, just like `pip install -i`.

now, our packaging command is complete:
```text
python3 pack.py -b /home/DemoProject -r /home/DemoProject/requirements.txt -v
```
This will generate a directory under your project that stores the installation package in the whl format of the dependencies listed in requirements.txt.

You don't have to care about the name of this directory, because env installer will handle everything!

result:
```text
Packaged successfully! Saved /home/DemoProject/ea385f6cb21d4097
```

### install
```text
usage: install.py [-h] -b BASE_DIR -r REQ_DIR [--venv-pip-path VENV_PIP_PATH]
                  [-p PYTHON]

arguments:
  -b BASE_DIR, --base-dir BASE_DIR
                        absolute path of the project to be deployed.
  -r REQ_DIR, --req-dir REQ_DIR
                        absolute path of production environment dependency
                        file.
  --venv-pip-path VENV_PIP_PATH
                        the pip absolute path of the virtual environment that
                        already exists on the server.
  -p PYTHON, --python PYTHON
                        python interpreter path on the server.equivalent to
                        `virtualenv -p`.

```

Now let's switch to the server, you have uploaded the packaged project to the server's `/deploy/Demo Project` and the python 3 is already installed on the server(`/usr/bin/python3`).

the absolute path of your project: 
```text
/deploy/DemoProject
```

the absolute path of dependent file: 
```text
/deploy/DemoProject/requirements.txt
```

if you use the `-v` parameter when packaging, env_installer thinks you want to install `virtualenv` on the server.
then ignore the `--venv-pip-path` parameter and give `-p`. The path to the python3 interpreter is used to create the virtual environment after installing `virtualenv`.
conversely, if you have a virtualenv on your server, you only need to give the pip path under the existing virtualenv, for example: `/deploy/ae0719f3_venv/bin/pip3`.


now, our installation command is complete:
```text
python3 install.py -b /deploy/DemoProject -r /deploy/DemoProject/requirements.txt -p /usr/bin/python3
```

result:
```text
installed successfully!now you can run:
 source /deploy/DemoProject/6195b07d_venv/bin/activate
to activate the virtualenv.

```

