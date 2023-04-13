database := database.db
bdl_py := balldontlie.py
bdl_vis := balldontlie_visualization.py
stocks_py := stocks_database_filler.py
stocks_vis := stocks_visualization.py
PYTHON := python3

default: clean

all: scripts vis

bdl:
	@echo "Running Ball Don't Lie"
	@$(PYTHON) $(bdl_py)

stocks:
	@echo "Running Stocks"
	@$(PYTHON) $(stocks_py)

scripts: bdl stocks

bdl_vis:
	@echo "Running Ball Don't Lie Visualization"
	@$(PYTHON) $(bdl_vis)

stocks_vis:
	@echo "Running Stocks Visualization"
	@$(PYTHON) $(stocks_vis)

vis: bdl_vis stocks_vis

clean:
	@echo "Cleaning up database..."
	rm -f $(database)

.PHONY: clean
