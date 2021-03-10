webblocker
==========

A simple website list blocker for time periods based on hosts 

Add a list of websites to hosts file to redirect them to loopback
for a period of time defined by the use

The rules are define in the `rules.json`. See `rules.json.sample` to
understand how to use it. Basically it's a JSON with `lists` where you
defined any number of named lists using the key as the identificator and
the value as a list of string with the websites. The other important key
in this JSON is `periods` where you define a list of objects, which object
define a period with the attributes `start_time`, `end_time` and
`website_list`. This last attribute is a string that match a list defined
in the `lists` key previously. The time format is a string like `HH:MM:`.

    cp rules.json.sample rules.json

Then just run the script with privileges.

    sudo python webblocker.py
