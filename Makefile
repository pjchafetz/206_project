PYTHON := python
database := database.db
bdl_py := balldontlie.py
stocks_py := stocks.py
bdl_vis := balldontlie_visualization.py
stocks_vis := stocks_visualization.py


default: clean


prepare: clean prepare_balldontlie prepare_stocks
	@echo "Done! $(database) should be ready."


prepare_balldontlie:
	@echo "Collecting 100 items from Ball Don't Lie..."
	@$(PYTHON) $(bdl_py)
	@$(PYTHON) $(bdl_py)
	@$(PYTHON) $(bdl_py)
	@$(PYTHON) $(bdl_py)
	@$(PYTHON) $(bdl_py)


prepare_stocks:
	@echo "Collecting 100 items from Stocks..."
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)
	@$(PYTHON) $(stocks_py)


balldontlie:
	@echo "Running Ball Don't Lie"
	@$(PYTHON) $(bdl_py)


balldontlie_vis:
	@echo "Running Ball Don't Lie Visualization"
	@$(PYTHON) $(bdl_vis)


stocks:
	@echo "Running Stocks"
	@$(PYTHON) $(stocks_py)


stocks_vis:
	@echo "Running Stocks Visualization"
	@$(PYTHON) $(stocks_vis)

clean:
	@echo "Cleaning up database..."
	rm -f $(database)


.PHONY: clean bdl bdl_vis stocks stocks_vis
