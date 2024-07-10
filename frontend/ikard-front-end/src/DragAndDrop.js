import React, { useState } from 'react';
import './DragAndDrop.css';
import '@fortawesome/fontawesome-free/css/all.min.css'; // Importar Font Awesome

function DragAndDrop() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [file, setFile] = useState(null);
  const [responseImageData, setResponseImageData] = useState(null);
  const [responseAnonymImageData, setResponseAnonymImageData] = useState(null);
  const [responseJson, setResponseJson] = useState(null); // Estado para almacenar el JSON de respuesta
  const [responseAnonymJson, setResponseAnonymJson] = useState(null); // Estado para almacenar el JSON de respuesta
  const [isLoading, setIsLoading] = useState(false); // Estado de carga
  const [filename, setFilename] = useState('');

  const downloadFile = async () => {
    if (!filename) {
        alert('Please enter a filename');
        return;
    }
    const prefixedFilename = `anonymized_${filename}`;
    const response = await fetch('http://132.226.196.10:2053/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prefixedFilename })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = prefixedFilename;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } else {
        alert('File not found');
    }
  };
  
  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    handleFile(file);
    if (file){
      setFilename(file.name)
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleFileInput = (event) => {
    const file = event.target.files[0];
    handleFile(file);
    if (file){
      setFilename(file.name)
    }
  };

  const handleFile = (file) => {
    if (file) {
      setFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = () => {
    if (!file) return;

    setIsLoading(true); // Inicia la carga

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://132.226.196.10:2053/upload', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json()) // Recibe el texto como respuesta
    .then(data => {
      setResponseImageData(data.imageData); // Establece el texto de la imagen directamente
      setResponseAnonymImageData(data.anonymized_imageData);
      setResponseJson(data.original_data); // Almacena el JSON de respuesta
      setResponseAnonymJson(data.anonymized_data);

      setIsLoading(false); // Finaliza la carga
    })
    .catch((error) => {
      console.error('Error:', error);
      setIsLoading(false); // Finaliza la carga en caso de error
    });
  };

  return (
    <div className="drag-and-drop-container">
      <div className="box">
        <h3>Wybierz plik DICOM</h3>
        <div 
          className="drop-zone" 
          onDrop={handleDrop} 
          onDragOver={handleDragOver}
        >
          Przeciągnij i upuść swój plik DICOM tutaj
        </div>
        <input 
          type="file" 
          accept=".dcm" 
          onChange={handleFileInput}
        />
      </div>
      <div className="separator"></div>
      <div className="box">
        <h3>Original</h3>
        {selectedImage && (
          <>
          {responseImageData && (
             <>
            <img src={responseImageData} alt="Response" className="image-response" />
            
            </>
            )}
            <button onClick={handleUpload}>Upload Image</button>
            {isLoading ? (
          <br></br> 
        ) : (
          responseImageData && (
            <>

              <div className="info-text">Original information:</div>

                {responseJson && (
                  <div>

                    <table className="response-table">
                    <thead>
                      <tr>
                        <th>Key</th>
                        <th>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(responseJson).map(([key, value]) => (
                        <tr key={key}>
                          <td>{key}</td>
                          <td>{JSON.stringify(value)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

            </>
          )
        )}
          </>
        )}
      </div>
      <div className="separator"></div>
      <div className="box">
        <h3>Anonymized</h3>
        {isLoading ? (
          <i className="fas fa-spinner fa-spin"></i> // Icono de carga de Font Awesome
        ) : (
          responseImageData && (
            <>
              <img src={responseAnonymImageData} alt="Response" className="image-response" />
              <h3>Anonymized Data</h3>

                {responseAnonymJson && (
                  <div>

                    <table className="response-table">
                    <thead>
                      <tr>
                        <th>Key</th>
                        <th>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(responseAnonymJson).map(([key, value]) => (
                        <tr key={key}>
                          <td>{key}</td>
                          <td>{JSON.stringify(value)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            <br></br>
            <button onClick={downloadFile}>Download Anonymized File</button>
            </>
          )
        )}
      </div>
    </div>
  );
}

export default DragAndDrop;
