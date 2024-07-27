# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import scikit-learn modules for model selection and preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score

# Import TensorFlow and Keras for neural network modeling
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Layer, Dense, BatchNormalization, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import backend as K

# Data Preprocessing
def load_cocomo_data():
    data = pd.read_csv("./cocomo81.csv")
    X = data.iloc[:, :-1].values  # Features
    y = data.iloc[:, -1].values  # Effort
    return X, y

totalX, totalY = load_cocomo_data()
X_train, X_test, y_train, y_test = train_test_split(totalX, totalY, test_size=0.25, random_state=42)

# Define the Morlet wavelet function as a custom layer
class MorletWavelet(Layer):
    def __init__(self, **kwargs):
        super(MorletWavelet, self).__init__(**kwargs)

    def call(self, inputs):
        sigma = 1.2  # Scale parameter
        return K.exp(-0.6 * K.square(inputs / sigma)) * K.cos(3.0 * inputs)

# Build the neural network model
def create_morlet_nn(input_dim):
    """
    Create a neural network model with Morlet wavelet layers.
    """
    model = Sequential()

    # Add a batch normalization layer to normalize inputs
    model.add(BatchNormalization(input_shape=input_dim))

    # Add a dense layer with Morlet wavelet activation
    model.add(Dense(50, input_dim=input_dim))
    model.add(MorletWavelet())

    # Add another dense layer with Morlet wavelet activation
    model.add(Dense(100))
    model.add(MorletWavelet())

    # Add a final dense layer with Morlet wavelet activation and flatten the output
    model.add(Dense(50))
    model.add(MorletWavelet())
    model.add(Flatten())

    # Output layer with a linear activation function
    model.add(Dense(1, activation='linear'))
    return model

# Initialize and compile the model
input_dim = X_train.shape[1:]  # Define input dimensions
model = create_morlet_nn(input_dim)  # Create the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')  # Compile the model

# Display the model summary
model.summary()

# Train the model
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1)

# Plot the training and validation loss
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('Training and Validation Loss')
plt.show()

# Make predictions on the test set
predicted_values = model.predict(X_test)

# Calculate R-squared score
r_squared = r2_score(y_test, predicted_values)
print("R-squared:", r_squared)

# Calculate Mean Magnitude of Relative Error (MMRE)
mmre = np.mean(np.abs((y_test - predicted_values) / y_test))
print("MMRE:", mmre)

# Calculate Magnitude of Relative Error (MRE) for each observation
mre = np.abs((y_test - predicted_values) / y_test)

# Calculate Median Magnitude of Relative Error (MdMRE)
mdmre = np.median(mre)
print("MdMRE:", mdmre)
