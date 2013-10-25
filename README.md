Joe Henke's 6.UAP Project
=========================

> A tool to visualize and understand [ConceptNet](http://conceptnet5.media.mit.edu/).
>
> Powered by [celestrium](https://github.com/jdhenke/celestrium).

## Setup

### Prerequisites

Install [virtualenv](https://pypi.python.org/pypi/virtualenv) and the [Heroku Toolbelt](https://toolbelt.heroku.com/).

### Installation

```bash
# clone this repo and its submodules
git clone --recursive https://github.com/jdhenke/uap.git && cd uap

# install node packages
npm install

# setup virtual environment
virtualenv env
source env/bin/activate

# install normal dependencies
pip install -r requirements.txt

# install these *special* dependencies
# this is a result of them depending on numpy in their setup.py's
pip install divisi2 csc-pysparse

# start local server
foreman start
```

View your [local instance](http://localhost:5000/).

## Recommended Reading

 - [License](./LICENSE)
 - [Deploying to Heroku](./HEROKU.md)
