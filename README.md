SI 206 Final Project

Paul Chafetz and Brandon Monge

# Instructions

Set up your Python virtual environment:
```bash
$ python3 -m venv env
$ source env/bin/activate
```

Install the required packages:
```bash
$ pip install -r requirements.txt
```

Either use the Makefile, or run the database scripts directly:
```bash
$ make bdl
$ make stocks
$ make scripts # does both
# OR
$ python3 balldontlie.py
$ python3 stocks_database_filler.py
# repeat as desired
```

Either use the Makefile, or run the visualization scripts directly:
```bash
$ make bdl_vis
$ make stocks_vis
$ make vis # does both
# OR
$ python3 balldontlie_visualization.py
$ python3 stocks_visuals.py
```
