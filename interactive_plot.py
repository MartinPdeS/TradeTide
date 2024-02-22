import tkinter as tk
from tkinter import ttk, messagebox
import inspect
from TradeTide.backtester import BackTester
from TradeTide.strategy import Strategy
from TradeTide.tools import get_dataframe
from TradeTide.plottings import plot_trading_strategy

def get_strategy_classes():
    """Retrieve all subclasses of the Strategy class."""
    return Strategy.__subclasses__()

def get_init_parameters(strategy_class):
    """Retrieve the __init__ parameters and their default values of a strategy class, excluding 'self'."""
    init_signature = inspect.signature(strategy_class.__init__)
    parameters = {
        k: v.default for k, v in init_signature.parameters.items() if k != 'self' and v.default is not inspect.Parameter.empty
    }
    return parameters

def get_backtest_parameters():
    """Retrieve the __init__ parameters of the back_test method, excluding 'self'."""
    backtest_signature = inspect.signature(BackTester.back_test)
    parameters = {
        k: v.default for k, v in backtest_signature.parameters.items() if k != 'self' and v.default is not inspect.Parameter.empty
    }
    return parameters

def get_dataframe_parameters():
    """Retrieve the parameters of the get_dataframe function, excluding 'self'."""
    dataframe_signature = inspect.signature(get_dataframe)
    parameters = {
        k: v.default for k, v in dataframe_signature.parameters.items() if v.default is not inspect.Parameter.empty
    }
    return parameters

def update_parameter_fields(*args):
    for widget in parameter_frame.winfo_children():
        widget.destroy()
    
    parameter_entries.clear()  # Clear the dictionary for new entries

    # Strategy Parameters
    selected_strategy = strategy_var.get()
    strategy_class = strategies[selected_strategy]
    strategy_parameters = get_init_parameters(strategy_class)

    # Display Strategy Parameters
    row_index = 0
    ttk.Label(parameter_frame, text="Strategy Parameters:", font=('Helvetica', 15, 'bold')).grid(row=row_index, column=0, sticky="w")
    row_index += 1
    for param, default in strategy_parameters.items():
        ttk.Label(parameter_frame, text=f"{param} (default={default}):").grid(row=row_index, column=1, sticky="w")
        entry = ttk.Entry(parameter_frame)
        entry.insert(0, str(default))
        entry.grid(row=row_index, column=0, sticky="ew")
        parameter_entries[param] = (entry, type(default))
        row_index += 1

    # Display Backtest Parameters
    row_index += 2
    ttk.Label(parameter_frame, text="Backtest Parameters:", font=('Helvetica', 15, 'bold')).grid(row=row_index, column=0, sticky="w")
    row_index += 1
    for param, default in backtest_parameters.items():
        ttk.Label(parameter_frame, text=f"{param} (default={default}):").grid(row=row_index, column=1, sticky="w")
        entry = ttk.Entry(parameter_frame)
        entry.insert(0, str(default))
        entry.grid(row=row_index, column=0, sticky="ew")
        parameter_entries[param] = (entry, type(default))
        row_index += 1

    # Display Dataframe Parameters
    row_index += 2
    ttk.Label(parameter_frame, text="Data Parameters:", font=('Helvetica', 15, 'bold')).grid(row=row_index, column=0, sticky="w")
    row_index += 1
    for param, default in dataframe_parameters.items():
        ttk.Label(parameter_frame, text=f"{param} (default={default}):").grid(row=row_index, column=1, sticky="w")
        entry = ttk.Entry(parameter_frame)
        entry.insert(0, str(default))
        entry.grid(row=row_index, column=0, sticky="ew")
        parameter_entries[param] = (entry, type(default))
        row_index += 1


def run_backtest():
    try:
        dataframe_kwargs = {}
        strategy_kwargs = {}
        backtest_kwargs = {}

        # Fetch and separate all parameters from parameter_entries
        for param, (entry, expected_type) in parameter_entries.items():
            value_str = entry.get()
            try:
                value = expected_type(value_str)
                if param in dataframe_parameters:
                    dataframe_kwargs[param] = value
                elif param in backtest_parameters:
                    backtest_kwargs[param] = value
                else:
                    strategy_kwargs[param] = value
            except ValueError:
                messagebox.showerror("Type Error", f"Parameter '{param}' expects a value of type {expected_type.__name__}")
                return

        # Load market data using the entered dataframe parameters
        dataframe = get_dataframe(**dataframe_kwargs)
        market = dataframe[:100_000]

        # Instantiate the selected strategy with its parameters
        selected_strategy = strategy_var.get()
        strategy_class = strategies[selected_strategy]
        strategy = strategy_class(**strategy_kwargs)

        # Generate signals with the strategy
        strategy.generate_signal(market)

        # Initialize the BackTester and run the backtest with backtest parameters
        backtester = BackTester(market=market, strategy=strategy)
        portfolio, metadata = backtester.back_test(**backtest_kwargs)
        
        # plot figures
        plot_trading_strategy(
            market=market,
            portfolio=portfolio,
            strategy=strategy,
        )
    
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Populate with the parameters from the back_test function
backtest_parameters = get_backtest_parameters()

# Populate with the parameters from the get_dataframe function
dataframe_parameters = get_dataframe_parameters()

# Setting up the Tkinter window
window = tk.Tk()
window.title("Trading Strategy Simulation")

# Strategy selection
strategy_var = tk.StringVar()
strategy_var.trace('w', update_parameter_fields)
strategies = {cls.__name__: cls for cls in get_strategy_classes()}
strategy_label = ttk.Label(window, text="Select Strategy:", font=('Helvetica', 20, 'bold'))
strategy_label.grid(row=0, column=0, sticky="w")
strategy_dropdown = ttk.Combobox(window, textvariable=strategy_var, values=list(strategies.keys()))
strategy_dropdown.grid(row=0, column=1, sticky="ew")

# Parameter input frame
parameter_frame = ttk.Frame(window)
parameter_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
parameter_entries = {}

# Run button
run_button = ttk.Button(window, text="Run Simulation", command=run_backtest)
run_button.grid(row=2, column=1, sticky="ew")

window.mainloop()