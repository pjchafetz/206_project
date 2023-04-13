database := database.db
bdl_py := balldontlie.py
bdl_vis := balldontlie_visualization.py
bdl := balldontlie
stocks_py := stocks_database_filler.py
stocks_vis := stocks_visualization.py

default: clean

all: scripts vis

bdl:
	@echo "Running Ball Don't Lie"
	@python3 $(bdl_py)

stocks:
	@echo "Running Stocks"
	@python3 $(stocks_py)

scripts: bdl stocks

bdl_vis:
	@echo "Running Ball Don't Lie Visualization"
	@python3 $(bdl_vis)

stocks_vis:
	@echo "Running Stocks Visualization"
	@python3 $(stocks_vis)

vis: bdl_vis stocks_vis

clean:
	@echo "Cleaning up..."
	rm -rf $(bdl) $(database)

.PHONY: clean
