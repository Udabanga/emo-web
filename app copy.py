from json import JSONEncoder
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tensorflow 
from keras.models import load_model
import soundfile as sf
import pandas as pd
import numpy as np
import librosa

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Prediction:
    def __init__(self, angry, disgust, fear, happy, neutral, sad, surprise):
        self.angry = angry.item()
        self.disgust= disgust.item()
        self.fear = fear.item()
        self.happy = happy.item()
        self.neutral = neutral.item()
        self.sad = sad.item()
        self.surprise = surprise.item()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(audio_file.filename)
        # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filename)

        # # Extract sample rate using soundfile
        # try:
        #     data, sample_rate = sf.read(filename)
        # except Exception as e:
        #     return jsonify({'error': 'Error reading audio file'}), 500

        data, sample_rate = librosa.load(filename, res_type='kaiser_best',duration=4,sr=44100)
        
        spectrogram = librosa.feature.melspectrogram(y=data, sr=sample_rate, n_mels=128,fmax=8000)
        db_spec = librosa.power_to_db(spectrogram)
        #temporally average spectrogram
        log_spectrogram = np.mean(db_spec, axis = 0)


        empty_df = pd.DataFrame(index=np.arange(1), columns=np.arange(345)) #259 #454
        df = pd.DataFrame(columns=['mel_spectrogram'])
        df.loc[0] = [log_spectrogram]
        df_combined = pd.concat([pd.DataFrame(df['mel_spectrogram'].values.tolist()), empty_df], ignore_index=True)
        df_combined = df_combined.fillna(0)

        prediction = get_prediction(df_combined)

        # Here you would call your machine learning model or process to generate spectrogram and prediction images
        # Replace the following lines with actual code that generates the images
        spectrogram_url = 'https://images.saymedia-content.com/.image/c_limit%2Ccs_srgb%2Cq_auto:eco%2Cw_760/MTk2NzY3MjA5ODc0MjY5ODI2/top-10-cutest-cat-photos-of-all-time.webp'
        prediction_url = 'https://images.twinkl.co.uk/tw1n/image/private/t_630/u/ux/graph-wiki_ver_1.png'

        return jsonify({
            'spectrogram': spectrogram_url,
            'prediction': JSONEncoder().encode(prediction)
        })
    else:
        return jsonify({'error': 'Invalid file format'}), 400
    
# def get_prediction(audio_data):
#     model = load_model('model_RAVDESS_TESS.h5')


#     audio_data_array = np.array(audio_data)
#     audio_data_3d_array = audio_data_array[:,:,np.newaxis]

#     m_predictions = model.predict(audio_data_3d_array[:1])

#     prediction = Prediction(
#         m_predictions[0][0],
#         m_predictions[0][1],
#         m_predictions[0][2],
#         m_predictions[0][3],
#         m_predictions[0][4],
#         m_predictions[0][5],
#         m_predictions[0][6]
#     )
    
#     return prediction
    




if __name__ == '__main__':
    app.run(debug=True)