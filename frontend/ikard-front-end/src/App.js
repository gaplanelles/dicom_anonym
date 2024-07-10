import oracleConsulting from './static/Oracle_Consulting_rgb.png';
import ikardIcon from './static/ikard-icon.png';
import './App.css';
import React, {useState} from 'react';
import DragAndDrop from './DragAndDrop';



function App() {

  const [responseStatus, setResponseStatus] = useState(null);
  const callEndpoint = async () => {
    try {
      const response = await fetch('http://132.226.196.10:2053/batch_conversion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },

      });

      setResponseStatus(response.status);
    } catch (error) {
      console.error('Error:', error);

      setResponseStatus('Error ');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
      <div className="image-container">
          <img src={oracleConsulting} className="header-image" alt="Oracle Consulting" />
          <div className="separator"></div>
          <img src={ikardIcon} className="header-image" alt="Ikard Icon" />
        </div>
        
        <p>
        Możemy uruchomić konwersję wsadową klikając tutaj:
        </p>
        <div>
          <button onClick={callEndpoint}>Uruchom wsadową anonimizację</button>

          {responseStatus === 200 && (
            <div>
              <h3>Sprawdź folder TRG_DICOM w swoim wiadrze OC</h3>

            </div>
          )}
          {/* Mostrar un mensaje de error genérico si el código de estado no es 200 */}
          {responseStatus !== 200 && (
            <div>


            </div>
          )}
        </div>

        <p>Wgraj obraz DICOM, aby zanonimizować go. 
        </p>

        
        
        <DragAndDrop />
        
      </header>


    </div>
  );
}

export default App;


