VENV = env
ENV = ./$(VENV)/bin
PYTHON = $(ENV)/python
PIP = $(ENV)/pip
TOX = $(ENV)/tox
PYTEST = $(ENV)/pytest
EGGLINK = $(VENV)/lib/python2.7/site-packages/pyconstring.egg-link


tests: $(VENV) $(EGGLINK)
	$(PYTEST)

$(EGGLINK): $(VENV)
	$(PIP) install -q -e .

tox: $(VENV)
	pyenv install -s 2.7.13
	pyenv install -s 3.4.6
	pyenv install -s 3.5.3
	pyenv install -s 3.6.2
	pyenv local 2.7.13 3.4.6 3.5.3 3.6.2
	$(TOX)

$(VENV): devtools.txt
	virtualenv -q $(VENV)
	$(PIP) install -q -r devtools.txt
