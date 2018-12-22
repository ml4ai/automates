Running the webapp locally
--------------------------

To run the webapp locally, you need to have [Delphi](https://github.com/ml4ai/delphi) on
your system and in your `PYTHONPATH`. Additional requirements are listed in
`requirements.txt` and can be installed by invoking

```
pip install -r requirements.txt
```

To run the webapp, invoke `source run.sh` and navigate to `localhost:5000` in
your web browser.


Setting up AWS EC2 (partial instructions)
-----------------------------------------

After setting up your instance, log in and do:

```bash
git clone https://github.com/ml4ai/automates
cd automates/demo
sudo sh setup_aws_ec2.sh
```

Then do:

```bash
sudo vi /etc/apache2/sites-enabled/000-default.conf
```

and add the following lines under line `DocumentRoot /var/www/html`

```
WSGIDaemonProcess automates_demo threads=5
WSGIScriptAlias / /var/www/html/automates_demo/app.wsgi

<Directory automates_demo>
	WSGIProcessGroup automates_demo
	WSGIApplicationGroup %{GLOBAL}
	Order deny,allow
	Allow from all
</Directory>
```

Then restart the server.

```
sudo apachectl restart
```
