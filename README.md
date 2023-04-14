SI 206 Final Project

Paul Chafetz and Brandon Monge

# Instructions

Set up your Python virtual environment:
```bash
$ python -m venv env
$ source env/bin/activate
```

Install the required packages:
```bash
$ pip install -r requirements.txt
```

Either use the Makefile, or run the database scripts directly:
```bash
$ make balldontlie
$ make stocks
# OR
$ python balldontlie.py
$ python stocks.py
# repeat as desired
```

Either use the Makefile, or run the visualization scripts directly:
```bash
$ make balldontlie_vis
$ make stocks_vis
# OR
$ python balldontlie_visualization.py
$ python stocks_visuals.py
```

To collect the 100+ items for each API as necessary, use the Makefile:
```bash
$ make prepare_balldontlie
$ make prepare_stocks
# OR
$ make prepare
```
