# Twistair rendezvous notifications with Pushover

[twstr-rdv](https://github.com/jonathanmichel/twstr-rdv) is a Python script that parses the [Twistair](https://twistair.ch/ecole-parapente/62-rendez-vous) website page that indicates rendezvous for flying. If a new rendezvous is published, a notification is sent through [Pushover](https://pushover.net/).

![image](https://user-images.githubusercontent.com/24658882/164752869-ad16abd5-ff8c-4f15-8fac-2f19d7ac300c.png)

# Usage

1. Clone the repository
2. Call the [init.sh](./init.sh) script
4. Create an application on [Pushover](https://pushover.net/) and copy your user and api keys in a `credentials.json` file. *Note that pushover has a 30 days free trial, and then requires a unique buy per device.
3. Excecute [main.py](./main.py) frequently on your server

# Dependencies
Python and python-venv. 
Other dependencies are handled by poetry (in the init.sh script)

## Author

* **Jonathan Michel** - [jonathanmichel](https://github.com/jonathanmichel) 
