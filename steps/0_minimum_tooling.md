# 0. Minimum Tooling


### Table of Contents
1. [Brew](#install-brew)
2. [Pyenv](#pyenv)
3. [Pyenv install](#pyenv-install)
4. [virutalenv](#virtualenv)
5. [Install GIT](#install-git)



### Install Brew
Follow instructions to setup brew [here](https://docs.brew.sh/Installation)
But it's basically
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```


### Pyenv
[Pyenv installation instructions](https://github.com/pyenv/pyenv#installation)
```
$ brew install pyenv
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
$ echo 'export PATH="$PYENV_ROOT/shims:$PATH"' >> ~/.zshrc
```

### Pyenv install
For this guide we will work off of python version 3.12.2
But you can find and install a pyenv version using the below commands in your terminal
```
$ pyenv install --list
$ pyenv install 3.12.2
```

### virtualenv
[virtualenv](https://virtualenv.pypa.io/en/latest/installation.html#via-pip)
install by running
```
pip install virtualenv
```

## Install git
This guide will assume you are familiar with git and have it installed.
If not you can find the installation instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
