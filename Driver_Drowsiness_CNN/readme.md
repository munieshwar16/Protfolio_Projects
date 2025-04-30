
# 💤 Driver Drowsiness Detection System

An end-to-end deep learning-based system to detect driver fatigue in real-time using computer vision and CNN architectures. This project aims to reduce road accidents caused by drowsy driving by providing timely alerts based on eye state monitoring.

## 🧠 Overview

This project leverages image processing and deep learning to monitor eye state and trigger alerts when drowsiness is detected. It replicates and extends upon the academic research paper, "**Driver Drowsiness Alert System Using Deep Learning**", implementing it in a real-time prototype using OpenCV, TensorFlow, and CNN.

## 📌 Key Features

- Real-time eye monitoring via webcam
- CNN-based binary eye classification (open vs. closed)
- Alarm sound to wake up drowsy drivers
- Transfer learning applied to pre-trained models
- Augmented dataset with open/closed eyes for robust training

## 📂 Project Structure

```
Driver_Drowsiness_CNN/
├── alarm.wav                # Alert sound for drowsy detection
├── dataset/                 # Custom or external datasets
├── haarcascade_eye.xml      # Eye detector Haar cascade
├── haarcascade_frontalface_default.xml
├── model/                   # Trained CNN models (e.g., cnnCat2.h5)
├── main.py                  # Main script for running detection
├── utils.py                 # Utility functions (preprocessing, etc.)
└── README.md                # Project documentation
```

## 🛠️ Technologies Used

- Python 3.8+
- OpenCV for face and eye detection
- TensorFlow/Keras for CNN-based eye classification
- NumPy, Matplotlib for data handling and plotting

## 🧪 Methodology

- Extract eye region from face frames using Haar cascades
- Preprocess and normalize images (grayscale, resize to 24x24)
- Train CNN model with binary classification (open vs closed)
- Set a frame-based drowsiness threshold to trigger alarm

## 🧬 Model Architecture

- 4 Convolution layers with ReLU activation
- 2 MaxPooling layers
- 1 Fully Connected layer with sigmoid output
- Trained on over 7000 labeled eye images

## 📈 Results & Analysis

- Achieved high accuracy in both bright and dim light conditions
- System works with glasses, minor occlusions
- Alert triggered when eyes are closed > threshold duration

## 📄 Reference Paper

This project is inspired by the research paper:
> "Driver Drowsiness Alert System Using Deep Learning"  
> [PDF Attached]  

## 🚀 Future Scope

- Integrate with vehicle telemetry and external sensors
- Include yawning detection for more robust fatigue detection
- Export as a standalone desktop or mobile app

---

**Contributors**:  
- Muni Eshwar Evakattu  
- Venkata Sai Prakash Y  


📬 For questions or collaborations, reach out via GitHub or email.
