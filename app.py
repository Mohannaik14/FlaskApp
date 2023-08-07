import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid GUI outside main thread warning
import matplotlib.pyplot as plt
import yfinance as yf
from flask import Flask, request, render_template

app = Flask(__name__)
# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Sample data for demonstration purposes
stocks = ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA", "NFLX", "NVDA", "AMD", "INTC"]

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/correlation_matrix', methods=['GET', 'POST'])
def correlation_matrix():
    selected_stocks = request.form.getlist('stocks')

    if request.method == 'POST' and selected_stocks:
        try:
            # Fetch data for selected stocks
            stock_data = yf.download(selected_stocks, start='2023-01-01', end='2023-06-30', progress=False)['Close']
            
            # Calculate the correlation matrix
            correlation_matrix = stock_data.corr()

            # Generate a heatmap plot of the correlation matrix with correlation values
            plt.figure(figsize=(10, 8))
            plt.title('Correlation Matrix')
            plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='none')
            plt.colorbar()

            for i in range(len(selected_stocks)):
                for j in range(len(selected_stocks)):
                    plt.text(i, j, f"{correlation_matrix.iloc[i, j]:.2f}", ha='center', va='center', color='black')

            plt.xticks(range(len(selected_stocks)), selected_stocks, rotation=45)
            plt.yticks(range(len(selected_stocks)), selected_stocks)
            plt.tight_layout()

            img_stream = io.BytesIO()
            plt.savefig(img_stream, format='png')
            img_stream.seek(0)
            plot_data = base64.b64encode(img_stream.read()).decode('utf-8')

            return render_template('correlation_matrix.html', stocks=stocks, selected_stocks=selected_stocks, plot_data=plot_data)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('correlation_matrix.html', stocks=stocks, error_message=error_message)

    return render_template('correlation_matrix.html', stocks=stocks)


# Route for the stock prices page
@app.route('/stock_prices', methods=['GET', 'POST'])
def stock_prices():
    if request.method == 'POST':
        selected_stock = request.form.get('stock')
        selected_date = request.form.get('date')

        try:
            if selected_stock and selected_date:
                stock_data = yf.download(selected_stock, start=selected_date)
                if not stock_data.empty:
                    selected_stock_data = stock_data['Close']

                    # Plot and convert the plot to a base64-encoded image
                    plt.figure(figsize=(8, 6))
                    plt.plot(selected_stock_data.index, selected_stock_data, label=selected_stock)
                    plt.xlabel('Date')
                    plt.ylabel('Price')
                    plt.title(f'Stock Prices for {selected_stock}')
                    plt.legend()
                    img_stream = io.BytesIO()
                    plt.savefig(img_stream, format='png')
                    img_stream.seek(0)
                    plot_data = base64.b64encode(img_stream.read()).decode('utf-8')

                    context = {
                        'stocks': stocks,
                        'selected_stock': selected_stock,
                        'plot_data': plot_data,
                    }
                    return render_template('stock_prices.html', **context)
                else:
                    error_message = f"No data available for {selected_stock} on {selected_date}"
                    return render_template('stock_prices.html', stocks=stocks, error_message=error_message)
            else:
                error_message = "Please select a stock and a date"
                return render_template('stock_prices.html', stocks=stocks, error_message=error_message)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('stock_prices.html', stocks=stocks, error_message=error_message)

    return render_template('stock_prices.html', stocks=stocks)

# Route for the beta analysis page
@app.route('/beta_analysis', methods=['GET', 'POST'])
def beta_analysis():
    selected_stock = request.form.get('stock')

    if selected_stock:
        stock_data = yf.download(selected_stock, period='1y')['Close']
        market_data = yf.download('^GSPC', period='1y')['Close']

        # Calculate beta value
        stock_returns = stock_data.pct_change().dropna()
        market_returns = market_data.pct_change().dropna()
        beta = stock_returns.cov(market_returns) / market_returns.var()

        return render_template('beta_analysis.html', stocks=stocks, selected_stock=selected_stock, beta=beta)

    return render_template('beta_analysis.html', stocks=stocks)

if __name__ == '__main__':
    app.run(debug=True)
