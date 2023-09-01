const audioInput = document.getElementById('audioInput');
const audioPlayer = document.getElementById('audioPlayer');
const uploadButton = document.getElementById('uploadButton');
const spectrogramImage = document.getElementById('spectrogramImage');
const predictionImage = document.getElementById('predictionImage');
const resultContainer = document.getElementById('resultContainer');
const chartCanvas = document.getElementById('chart');

audioInput.addEventListener('change', function() {
  const selectedFile = audioInput.files[0];
  if (selectedFile) {
    const objectURL = URL.createObjectURL(selectedFile);
    audioPlayer.src = objectURL;
  } else {
    audioPlayer.src = '';
  }
});

uploadButton.addEventListener('click', async function() {
  const selectedFile = audioInput.files[0];
  if (selectedFile) {
    const formData = new FormData();
    formData.append('audio', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();

        if (result.prediction) {
          // spectrogramImage.src = result.spectrogram;
          // predictionImage.src = result.prediction;
          resultContainer.style.display = 'block';
          console.log(response.data);
          prediction = result.prediction
          updateChart();
        } else {
          console.error('Incomplete response from the API.');
        }
      } else {
        console.error('Error uploading audio file.');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
});

function updateChart() {
  const ctx = chartCanvas.getContext('2d');

  // Destroy the existing chart (if it exists) before creating a new one
  if (window.myChart) {
    window.myChart.destroy();
  }


  const data = {
    labels: ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise'],
    datasets: [
      {
        label: 'Emotion Probability',
        data: [
          prediction.angry,
          prediction.disgust,
          prediction.fear,
          prediction.happy,
          prediction.neutral,
          prediction.sad,
          prediction.surprise
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(255, 159, 64, 0.2)',
          'rgba(255, 205, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(153, 102, 255, 0.2)',
          'rgba(201, 203, 207, 0.2)'
        ],
        borderColor: [
          'rgb(255, 99, 132)',
          'rgb(255, 159, 64)',
          'rgb(255, 205, 86)',
          'rgb(75, 192, 192)',
          'rgb(54, 162, 235)',
          'rgb(153, 102, 255)',
          'rgb(201, 203, 207)'
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        title: {
          color: 'black',
          display: true,
          text: 'Emotions'
        }
      },
      y: {
        title: {
          color: 'black',
          display: true,
          text: 'Probability'
        }
      },
    },
  };

  window.myChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: options,
  });
}