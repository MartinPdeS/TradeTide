import numpy
import pandas
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import History
from TradeTide import get_market_data
from typing import Tuple


def preprocess_data(data: pandas.DataFrame, time_steps: int = 3) -> Tuple[numpy.ndarray, numpy.ndarray, MinMaxScaler]:
    """
    Scales the 'close' prices from the provided DataFrame and creates sequences for LSTM input.

    Args:
        - data (pd.DataFrame): DataFrame containing the 'close' column with closing prices.
        - time_steps (int): Number of time steps to be used for creating sequences.

    Returns:
        - Tuple[numpy.ndarray, numpy.ndarray, MinMaxScaler]: Tuple containing the input features `X`, target variable `y`,
                                                  and the scaler object used for inverse transformation.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['close']])

    X, y = [], []
    for i in range(len(scaled_data) - time_steps):
        X.append(scaled_data[i:i + time_steps])
        y.append(scaled_data[i + time_steps])

    return numpy.array(X), numpy.array(y), scaler


def build_lstm_model(input_shape: Tuple[int, int]) -> Sequential:
    """
    Constructs the LSTM model architecture.

    Args:
    input_shape (Tuple[int, int]): Shape of the input data, excluding the batch size.

    Returns:
    Sequential: Compiled LSTM model.
    """
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def train_model(
        model: Sequential,
        X_train: numpy.ndarray,
        y_train: numpy.ndarray,
        X_test: numpy.ndarray,
        y_test: numpy.ndarray,
        epochs: int = 100,
        batch_size: int = 64) -> History:
    """
    Trains the LSTM model on the provided training data and validates it using the test data.

    Args:
        - model (Sequential): The LSTM model to be trained.
        - X_train (numpy.ndarray): Training features.
        - y_train (numpy.ndarray): Training target variable.
        - X_test (numpy.ndarray): Testing features.
        - y_test (numpy.ndarray): Testing target variable.
        - epochs (int): Number of epochs for training.
        - batch_size (int): Batch size for training.

    Returns:
        - History: Object that contains the history of training/validation loss and accuracy for each epoch.
    """
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        verbose=1
    )

    return history


def forecast_next_day_price(model: Sequential, recent_data: numpy.ndarray, scaler: MinMaxScaler) -> float:
    """
    Predicts the next day's closing price based on recent data using the trained LSTM model.

    Args:
        - model (Sequential): Trained LSTM model.
        - recent_data (numpy.ndarray): Most recent data used for prediction.
        - scaler (MinMaxScaler): Scaler object for inverse transformation of the predicted value.

    Returns:
        - float: Predicted next day's closing price.
    """
    scaled_prediction = model.predict(numpy.array([recent_data]))
    return scaler.inverse_transform(scaled_prediction)[0][0]


def main() -> None:
    """
    Main function to execute the LSTM model training and prediction.
    """
    df = get_market_data('eur', 'usd', year=2023, time_span='2 days', spread=0)

    # Configure the sequence length
    time_steps = 3
    X, y, scaler = preprocess_data(df, time_steps=time_steps)

    # Split the dataset for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build and train the LSTM model
    model = build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
    train_model(model, X_train, y_train, X_test, y_test)

    # Forecast the next day's price
    next_day_price = forecast_next_day_price(model, X[-1], scaler)
    print(f"Predicted next day price: {next_day_price}")


if __name__ == "__main__":
    main()
