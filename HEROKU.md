Deploying to Heroku
===================

## Instructions

### **Step 0**

Ensure your [local setup](./README.md#setup) is working.

### **Step 1**

```bash
git checkout -b prod
heroku create --buildpack https://github.com/jdhenke/heroku-buildpack-python-extras
git push -u heroku prod:master
```

### **Step 2**

Uncomment the bottom three lines of `requirements.txt`.

### **Step 3**

```bash
git add requirements.txt
git commit -m 'add second wave of requirements'
git push heroku prod:master
heroku open
```

## Explanation

Some `pip` packages require `numpy` during their installation.
Unfortunately, packages do not have access to other packages that are installed in the same round as each other.
Therefore, the first wave installs `numpy` and everything that doesn't require `numpy` during installation.
The second wave then installs the packages that do require `numpy` during installation.
