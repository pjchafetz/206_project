import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "database.db"

def execute_query(query):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results

def calculate_roi(prices):
    roi = [(prices[i + 1] - prices[i]) / prices[i] for i in range(len(prices) - 1)]
    return roi

def output_to_file(data, file_name):
    with open(file_name, 'w') as f:
        for i, item in enumerate(data, start=1):
            f.write(f"Week {i}: {item}\n")

def output_average_prices_to_file(data, file_name):
    with open(file_name, 'w') as f:
        for month, sp500_avg, bitcoin_avg in data:
            f.write(f"Month {month}: S&P 500 Avg: {sp500_avg}, Bitcoin Avg: {bitcoin_avg}\n")

def plot_roi(sp500_roi, bitcoin_roi):
    plt.plot(sp500_roi, label="S&P 500")
    plt.plot(bitcoin_roi, label="Bitcoin")
    plt.xlabel("Week")
    plt.ylabel("ROI")
    plt.title("Weekly ROI in 2021")
    plt.legend()
    plt.show()


def plot_average_prices(data):
    months, sp500_prices, bitcoin_prices = zip(*data)
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    ax1.plot(months, sp500_prices, label="S&P 500", color="blue")
    ax2.plot(months, bitcoin_prices, label="Bitcoin", color="orange")
    
    ax1.set_xlabel('Month')
    ax1.set_ylabel('S&P 500 Average Price', color="blue")
    ax2.set_ylabel('Bitcoin Average Price', color="orange")
    
    ax1.tick_params(axis='y', colors='blue')
    ax2.tick_params(axis='y', colors='orange')
    
    plt.title('Average Price per Month in 2021')
    plt.show()


def main():
    #fetch data from the database
    sp500_data = execute_query("SELECT id, adjusted_close FROM sp500")
    bitcoin_data = execute_query("SELECT id, close FROM bitcoin")

    #calculate ROI
    sp500_roi = calculate_roi([x[1] for x in sp500_data])
    bitcoin_roi = calculate_roi([x[1] for x in bitcoin_data])

    #output data to files
    output_to_file(sp500_roi, 'sp500_roi.txt')
    output_to_file(bitcoin_roi, 'bitcoin_roi.txt')

    #plot ROI for each week in 2021
    plot_roi(sp500_roi, bitcoin_roi)

    #get the average price of S&P 500 and Bitcoin for each month
    join_query = '''
    SELECT sp500.month, AVG(sp500.adjusted_close), AVG(bitcoin.close)
    FROM sp500
    JOIN bitcoin ON sp500.month = bitcoin.month
    GROUP BY sp500.month
    ORDER BY sp500.month
    '''
    joined_data = execute_query(join_query)

    output_average_prices_to_file(joined_data, 'average_prices.txt')
    plot_average_prices(joined_data)

if __name__ == "__main__":
    main()