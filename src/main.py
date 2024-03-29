import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from lib import simulate_trading, Trader, calculate_performance_score

STARTING_CAPITAL = 1000

stock_symbols = [
    "AAPL", "MSFT", "NVDA", "INTC", "AMD",  # Technology
    "JNJ", "PFE", "MRK", "BMY", "ABT",      # Healthcare
    "JPM", "GS", "BAC", "WFC", "C",         # Financials
    "AMZN", "TSLA", "DIS", "NKE", "F",      # Consumer Discretionary
    "XOM", "CVX", "COP", "SLB", "HAL",      # Energy
    "BA", "MMM", "CAT", "HON", "GE"         # Industrials
]


def fetch_stock_data(symbol, start_date, end_date, interval):
    data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    return data


def main():
    trader = Trader()
    pdf_path = 'stock_analysis_results.pdf'

    with PdfPages(pdf_path) as pdf:
        for symbol in stock_symbols:
            try:
                dataF = fetch_stock_data(symbol, "2024-3-19", "2024-3-22", "5m")
                trading_actions, final_profit_loss = simulate_trading(dataF, lambda prices: trader.decideRSI(prices, dataF['Volume']), STARTING_CAPITAL)

                buy_timestamps = [action[1] for action in trading_actions if action[0] == 'Buy']
                sell_timestamps = [action[1] for action in trading_actions if action[0] == 'Sell']
                
                total_change_in_price = dataF['Close'].iloc[-1] - dataF['Close'].iloc[0]

                performance_score = calculate_performance_score(final_profit_loss, dataF, STARTING_CAPITAL)

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                fig.subplots_adjust(hspace=1.0)
                
                # Plot the stock price and trades on ax1
                ax1.plot(dataF.index, dataF['Close'], label='Close Price')
                ax1.scatter(buy_timestamps, dataF.loc[buy_timestamps, 'Close'], color='green', label='Buy', marker='.', s=100)
                ax1.scatter(sell_timestamps, dataF.loc[sell_timestamps, 'Close'], color='red', label='Sell', marker='.', s=100)
                ax1.set_title(f'Stock Price for {symbol}')
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Price')
                ax1.legend()
                
                # Add the result text to ax2
                result_text = f"--- Results for {symbol} ---\n" + \
                                f"Buy Timestamps: {len(buy_timestamps)} buys\n" + \
                                f"Sell Timestamps: {len(sell_timestamps)} sells\n" + \
                                f"Total Change in Price: {total_change_in_price:.2f}\n" + \
                                f"Final Profit/Loss: {final_profit_loss:.2f}\n" + \
                                f"Performance Score: {performance_score:.2f}%"
                ax2.text(0.01, 0.5, result_text, fontsize=12, va='center', ha='left')
                ax2.axis('off')  # Hide the axis
                pdf.savefig(fig)  # Save the entire figure (both ax1 and ax2) into the pdf
                plt.close(fig)

            
            except Exception as e:
                print(f"Failed to process {symbol}: {e}")

    print(f"Analysis completed. Results saved to {pdf_path}.")


if __name__ == "__main__":
    main()