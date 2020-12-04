# README

A basic script to pull all of the transactions out of the accounts in your app.

You can reconfigure this by changing the credentials at the top of `rbs-get-transactions.py`.

To set up and run, create a virtualenv with something like:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

Then just run the script with `python rbs-get-transactions.py`.

You need to set up your client id and secret in your `.bashrc` or `.zshrc` like this:

```
export RBS_CLIENT_ID="ljAIOSDJLajdioAJSDiAJD"
export RBS_CLIENT_SECRET="sadfASdasjioDJASOdjasoF"
```
