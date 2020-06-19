# OrderBook

A simplified simulator for SETSmm iceberg order functionality as specified in the document “SETSmm and 
Iceberg Orders Service & Technical Description”.

## Getting started
```shell script
pipenv install
pipenv run python3 -m orderbook
```

## Features
* Extremely robust input reader. You may even set up buffer size to avoid running out of memory due to non-controlled input.
* Error tolerance and exact adherence to specifications. You cannot enter an order that does not correspond to the documentation, but you will certainly know what is wrong with it.
* Detailed logging will allow you to restore events even without access to script output.
* Compliance with `isort`, `black`, `flake8`, `mypy`, `pytest`


If you want to setup pre-commit and pre-push checks you may consider setting up corresponding hooks:
```shell script
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
