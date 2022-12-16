## Team and Player Stats Application
**_(In development)_**

The web application displays the latest news, team, and players stats.
Development was performed primarily using Python3 and Flask. Using Docker,
the application has been containerized.

The application has been tested on Chrome/Chromium.

_Note: The application is currently in a development phase and is not suitable
for production deployment. As such, there may be bugs in the application or
browser-specific errors._

### Starting the application
Please first clone / download the repository to your machine.

```git clone https://github.com/kaitj/tbj-statsapp.git```

Once cloned, there are **2** possible ways to start the application.

**Docker**

The simplest is to use Docker and Docker-compose. To do so, the following
pre-requisites must first be installed (click on each for installation
instructions):

1. [Docker](https://docs.docker.com/get-docker/)
2. [Docker Compose](https://docs.docker.com/compose/install/)

Once installed, navigate to the location of where the repository was cloned.
Once there, run the following command from a terminal:

```docker compose up -d```

To check if the web application has started successfully, enter the following
command:

```docker ps```

Under the `STATUS` column, a message similar to "Up N seconds" should be
displayed.

From here, open up your web browser (e.g. Chrome, Safari, Firefox, etc.) and
type the following URL in the address bar: https://0.0.0.0:5000

Once you have finished, the web application can be shutdown by typing the
following command in the terminal:

```docker compose down```

**Poetry**

If you wish to run it locally instead of using Docker, the project uses Poetry
to manage dependencies. See the installation instructions
[here](https://python-poetry.org/docs/). Once Poetry has been installed,
navigate to the cloned / downloaded repository and run the following command:

```poetry install```

After the dependencies have been installed, the web application can be started
with the following command:

```poetry run flask run --host=0.0.0.0```

From here, open up your web browser (e.g. Chrome, Safari, Firefox, etc.) and
type the following URL in the address bar: https://0.0.0.0:5000

Once you have finished, you can shutdown the web application by hitting `CTRL+C`
in the terminal window.
