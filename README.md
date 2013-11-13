Joe Henke's 6.UAP Project
=========================

> A tool to visualize and understand semantic networks such as [ConceptNet](http://conceptnet5.media.mit.edu/).
>
> Powered by [Celestrium](https://github.com/jdhenke/celestrium).

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
```

## Interface Explanation

* **Add nodes** using the search box in the top right.
* **Select/Deselect nodes** by clicking them and using the hotkeys `Ctrl A` and `Esc`
* **Add related nodes** by selecting nodes and using the hotkey `+` which is really `Shift =`.
* **Remove nodes** by selecting them and using the hotkey `Delete`.

Play with the sliders in the top left to get a feel for what they do.

You can also drag the white bar on the link strength distribution chart.

## Visualizing Conceptnet

Run `foreman start` and go to [http://localhost:5000](http://localhost:5000) to visualize assertions found in Conceptnet.

**You should do this to compile the coffeescript files used in this project.**

## Visualizing Your Knowledgebase

You will need to create a pickled sparse matrix representing your knowledgebase. 

To easily do this, modify `getAssertions()` in `src/parse.py` to return a list or be a generator of assertions in your knowledgebase. It works out of the box with the simplest knowledgebase possible if you want to try using that first to get a feel for the process.

Running `python src/parse.py` from the root of this repo will create `./kb.pickle`.

Now to visualize the concepts in your knowledgebase based on sampling results at dimensionalities of 1, 2 and 3, run from the root of this repo:

```bash
python src/server.py ./kb.pickle 1,2,3 concepts src/www 5000
```

Again, go to [http://localhost:5000/](http://localhost:5000/).

Here's an explanation of the command line arguments:

* `./kb.pickle` is the path to the pickled sparse matrix file of your knowledgebase
* `25,50,100` is the comma delimited list of dimensions at which to sample the inference results.
* `concepts` is the node type, which indicates what nodes will be in the graph and must be either `concepts` or `assertions`.
* `src/www` is the path to the directory that will be served statically - should be where your `index.html` is.
* `5000` is the port that the visualization will be served on

## Recommended Reading

 - [License](./LICENSE)
 - [Deploying to Heroku](./HEROKU.md)
