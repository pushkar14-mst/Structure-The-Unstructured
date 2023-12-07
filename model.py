import warnings
import librosa
import pandas as pd
from PIL import Image
import numpy as np
warnings.filterwarnings('ignore')
from flask import Flask, request, jsonify,send_from_directory
import os,io
from flask_cors import CORS, cross_origin
from preprocessing import preprocess_data

def extract_audio_features(audio_file):
    y, sr = librosa.load(io.BytesIO(audio_file.read()))
    loudness = librosa.feature.rms(y=y)[0].mean()
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    beats = len(librosa.onset.onset_detect(y=y, sr=sr))
    acoustiness = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1).tolist()
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr).mean()
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr).mean()
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y).mean()
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1).tolist()

    track_time = librosa.get_duration(y=y, sr=sr)

    features = {
        "loudness": loudness,
        "track_time": track_time,
        "tempo": tempo,
        "beats": beats,
        "acoustiness": acoustiness,
        "chroma_stft": chroma_stft,
        "spectral_bandwidth": spectral_bandwidth,
        "spectral_rolloff": spectral_rolloff,
        "zero_crossing_rate": zero_crossing_rate,
        "mfccs": mfccs
    }

    
    df=preprocess_data(pd.DataFrame([features]),['loudness', 'track_time', 'tempo', 'beats', 'acoustiness', 'spectral_bandwidth',
                   'spectral_rolloff', 'zero_crossing_rate'])
    return df

# audio_file_path = "100180.wav"
# audio_features_df = extract_audio_features(audio_file_path)

def extract_image_features(image_path):
    # Open the image using Pillow
    img = Image.open(io.BytesIO(image_path.read()))

    # Convert the image to grayscale and then to numpy array
    grayscale_img = img.convert('L')
    img_array = np.array(grayscale_img)

    # Extract image features
    mean_pixel_value = np.mean(img_array)
    min_pixel_value = np.min(img_array)
    max_pixel_value = np.max(img_array)
    image_shape = img_array.shape

    # Flatten the 2D array to a 1D array for histogram calculation
    flattened_img_array = img_array.flatten()

    sobel_edges = np.mean(np.abs(np.gradient(img_array, axis=(0, 1))))
    variance_pixel_values = np.var(img_array)
    edge_density = sobel_edges / (img_array.shape[0] * img_array.shape[1])
    aspect_ratio = img.width / img.height
    corner_pixels_mean = np.mean([img_array[0, 0], img_array[0, -1], img_array[-1, 0], img_array[-1, -1]])
    features = {
        "mean_pixel_value": mean_pixel_value,
        "min_pixel_value": min_pixel_value,
        "max_pixel_value": max_pixel_value,
        "image_shape": image_shape,
        "sobel_edges": sobel_edges,
        "variance_pixel_values": variance_pixel_values,
        "edge_density": edge_density,
        "aspect_ratio": aspect_ratio,
        "corner_pixels_mean": corner_pixels_mean

    }

    df1 = preprocess_data(pd.DataFrame([features]), ['mean_pixel_value', 'min_pixel_value', 'max_pixel_value',
                                                   'sobel_edges', 'variance_pixel_values', 'edge_density',
                                                   'aspect_ratio', 'corner_pixels_mean'])
    df=pd.DataFrame([features])
    print(df)
    return df1

# image_path = "test.png"
# image_features_df = extract_image_features(image_path)

def parse_network_log(log_file):
    timestamps = []
    threads = []
    types = []
    activities = []
    PIDs = []
    TTLs = []
    descriptions = []

    for line in log_file:
        line = line.decode('utf-8')  # Decode bytes to string if needed
        columns = line.strip().split()

        if len(columns) < 7:
            continue

        timestamp_str = ' '.join(columns[0:2])
        thread = columns[2]
        log_type = columns[3]
        activity = columns[4]

        timestamp_formats = ['%Y-%m-%d %H:%M:%S.%f+0000', '%Y-%m-%d %H:%M:%S+0000']
        timestamp = None
        for format_str in timestamp_formats:
            try:
                timestamp = pd.to_datetime(timestamp_str, format=format_str)
                break
            except ValueError:
                pass

        try:
            PID = int(columns[5])
            TTL = int(columns[6])
        except ValueError:
            PID = PID
            TTL = TTL

        description = ' '.join(columns[7:])

        timestamps.append(timestamp)
        threads.append(thread)
        types.append(log_type)
        activities.append(activity)
        PIDs.append(PID)
        TTLs.append(TTL)
        descriptions.append(description)

    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Thread': threads,
        'Type': types,
        'Activity': activities,
        'PID': PIDs,
        'TTL': TTLs,
        'Description': descriptions
    })

    return df

# log_file_path = 'network_logs.txt'
# network_log_df = parse_network_log(log_file_path)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@cross_origin()
@app.route('/process', methods=['POST'])
def process_files():

    if 'Files[]' not in request.files:
        return jsonify({'error': 'Missing files'})
    files = request.files.getlist('Files[]')
    format = request.form.getlist('Formats[]')[0]
    output_df = pd.DataFrame()
    print(format)
    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if format == 'Audio':
            audio_features_df = extract_audio_features(file)
            output_df = pd.concat([output_df, audio_features_df], ignore_index=True)
        elif format == 'Image':
            image_features_df = extract_image_features(file)
            output_df = pd.concat([output_df, image_features_df], ignore_index=True)
        elif format == 'Logs':
            network_log_df = parse_network_log(file)
            output_df = pd.concat([output_df, network_log_df], ignore_index=True)
        else:
            return jsonify({'error': 'Invalid format'})
   
    output_filename = 'combined_features.csv'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    output_df.to_csv(output_path, index=False)

    return jsonify({'success': True, 'output_filename': output_filename})
  

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)