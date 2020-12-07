# README

A basic script to pull all of the transactions out of the accounts in your RBS open banking sandbox app and save them to CSV.

You can reconfigure the `APP_ID` and other query data by changing the variables at the top of `rbs-get-transactions.py`.

To set up and run, create a virtualenv with something like:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

For authentication with your sandbox app you need to set up your client id and secret in your `.bashrc` or `.zshrc` like this:

```
export RBS_CLIENT_ID="ljAIOSDJLajdioAJSDiAJD"
export RBS_CLIENT_SECRET="sadfASdasjioDJASOdjasoF"
```

You'll also need to make sure the `APP_ID` in the script is updated to match your app.

Then just run the script with `python rbs-get-transactions.py`.

## API reference material

- https://developer.sandbox.rbs.co.uk
- https://www.bankofapis.com/products/natwest-group-open-banking/accounts/documentation/rbs/3.1.4
- https://www.bankofapis.com/api/dynamic-content/v1.0/products/371967cf-41fc-46a8-9759-393194375814/native-loans/nwb/1.0.0/sandbox-swagger.json
- https://sgerogia.github.io/OpenBanking-Part2
