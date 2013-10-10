Joe Henke's 6.UAP Project
=========================

> A tool to visualize and understand [ConceptNet](http://conceptnet5.media.mit.edu/).
>
> Check out the hopefully functioning and probably not current [public instance](http://conceptnet.herokuapp.com/).
>
> Powered by [celestrium](https://github.com/jdhenke/celestrium).
>
> 

## Setup && Running Locally

Install [virtualenv](https://pypi.python.org/pypi/virtualenv) and the [Heroku Toolbelt](https://toolbelt.heroku.com/).

```bash
git clone --recursive https://github.com/jdhenke/uap.git && cd uap

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

View your local version at [http://localhost:5000/](http://localhost:5000/).

## Deploying to [Heroku](https://www.heroku.com/)

This must be done in two stages because some packages require numpy to be fully installed before even starting to install these packages.

### Stage 1

```bash
# do all these changes on a different branch
git checkout -b prod

# create a new heroku app
heroku create

# push current branch to heroku
git push heroku prod:master
```

> This push to heroku should successfully intall the dependencies but fail to launch the app, as all the dependencies have not been installed.
> You can see the dependency installation as output to the push but to see the failed launch you'll need to check the logs with `heroku logs --tail`.

### Stage 2

Edit `requirements.txt` to uncomment the bottom list of packages, then run:

```bash
git add requirements.txt
git commit -m 'add second wave of requirements'
git push heroku prod:master && (heroku logs --tail; heroku open)
```

> The last line is a convenience and a one line script I saved as `deploy.sh` on my prod branch.
> First, push to heroku, stopping if it fails for some reason.
> If all seems well, view the logs so you can watch for a successful startup of your app on heroku or see what fails.
> Lastly, hit CTRL-C to stop viewing the log and your instance will be opened in your browser.

## License

See [LICENSE](./LICENSE)
