import numpy as np
import pandas as pd
from TradeTide import get_market_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from TradeTide import indicators

# Sample DataFrame loading
# Replace this with loading your forex market data
# For this example, assume 'close' is the closing price of a forex pair
market_data = get_market_data('eur', 'usd', year=2023, time_span='199day', spread=0)
# print(market_data)
market_data.drop(['volume', 'spread'], inplace=True, axis=1)


# Feature Engineering
indicator = indicators.MACD()
indicator.generate_signal(market_data)

# Calculate the target variable: 1 for "buy" signal, -1 for "sell" signal, based on future price movement
market_data['Future_Close'] = market_data['close'].shift(-1)
market_data['Signal'] = np.where(market_data['Future_Close'] > market_data['close'], 1, -1)

# Define features and target variable
X = indicator.get_features(drop_na=False)
y = market_data['Signal']

# Drop rows with NaN values created by rolling windows
nan_index = pd.isna(X).any(axis=1)

X.drop(X.index[nan_index], inplace=True)
y.drop(y.index[nan_index], inplace=True)
market_data.drop(market_data.index[nan_index], inplace=True)


# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize and train the logistic regression model
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Predict signals
y_pred = model.predict(X_test_scaled)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy}")

# Generate trading signals for the entire dataset (optional)
# This step is for applying the model to the dataset for actual trading or further analysis
X_scaled = scaler.transform(X)
market_data['Predicted_Signal'] = model.predict(X_scaled)

# Display the last few rows to verify the predicted signals
print(market_data[['close', 'Signal', 'Predicted_Signal']].tail())
