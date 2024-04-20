import React, { useState, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'pdfjs-dist/web/pdf_viewer.css';
import 'pdfjs-dist/build/pdf.worker.min';
import './App.css';


import {Viewer, Worker} from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'


function App() {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const [pdfFile, setPDFFile] = useState(null);
  const [viewPDF, setViewPDF] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [downloadedPDF, setDownloadedPDF] = useState(null);
  const [bibliographyText, setBibliographyText] = useState('');


  // Función para finalizar la selección de texto en el pdf una vez el 
  // usuario ha dejado de hacer "click"
  useEffect(() => {
    let selectedText = '';

    const handleSelectionChange = () => {
      const selection = window.getSelection();
      selectedText = selection.toString();
    };

    const handleMouseUp = () => {
      if (selectedText.length > 0) {
        setSelectedText(selectedText);
        setBibliographyText('');
        // Enviar texto seleccionado al servidor
        //mostrar el texto en el recuadro
      }
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);



  async function sendSelectedTextToBackend() {
      try {
          // prueba
          setBibliographyText('');
          setTextInput('');
          const response = await fetch('/uploadSelectedText', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ selectedText })
          });
          if (response.ok) {
              console.log('Texto seleccionado enviado al backend exitosamente.');
          } else {
              console.error('Error al enviar el texto seleccionado al backend.');
          }
          await fetchBibliographyFromBackend();
      } catch (error) {
          console.error('Error al enviar el texto seleccionado al backend:', error);
      }
  }

  // para recibir del backend la bibliografía correspondiente al parrafo al que pertenece el texto seleccionado por el usuario
  async function fetchBibliographyFromBackend() {
    try {
        const response = await fetch('/getBibliography');
        if (response.ok) {
            const bibliographyText = await response.text();
            console.log(bibliographyText); // Aquí puedes manejar el string recibido
            setBibliographyText(bibliographyText);
        } else {
            console.error('Error al obtener la bibliografía del backend.');
        }
    } catch (error) {
        console.error('Error al obtener la bibliografía del backend:', error);
    }
  }

  const fileType = ['application/pdf'];

  const handleChange = (e) => {
    //prueba 
    setBibliographyText('');
    setPDFFile(null);
    let selectedFile = e.target.files[0];
    if(selectedFile) {
      if(selectedFile && fileType.includes(selectedFile.type)) {
        let reader = new FileReader();
        reader.readAsDataURL(selectedFile);
        reader.onload = (e) => {
          setPDFFile(e.target.result);
        };
      }
      else {
        setPDFFile(null);
      }
    }
    else {
      console.log("please select");
    }
  };

  const handleTextInputChange = (e) => {
    setTextInput(e.target.value);
  };

  const handlePDFSubmit = async (e) => {
    // prueba
    setTextInput('');
    setSelectedText('');
    setBibliographyText('');
    setViewPDF(null)
    e.preventDefault();
    if (pdfFile !== null) {
      try {
        setViewPDF(pdfFile);
        const loadingTask = pdfjsLib.getDocument(pdfFile);
        const pdf = await loadingTask.promise;
        let pdfText = '';
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          textContent.items.forEach((textItem) => {
            pdfText += textItem.str + ' ';
          });
        }
        const response = await fetch('/uploadPDFText', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ pdfText })
        });
        console.log('Texto extraído del PDF:', pdfText);
      } catch (error) {
        console.error('Error extracting text from PDF:', error);
        throw error;
      }
    }
  };


  const handleInputSubmit = async () => {
    try {
      //ultimo
      setBibliographyText('');
      setSelectedText('');
      const response = await fetch('/uploadInputPdfId', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ inputText: textInput })
      });
      if (response.ok) {
        // Obtener la URL del PDF descargado desde el backend
        const { pdfUrl } = await response.json();
        // Establecer el PDF descargado en el estado
        setDownloadedPDF(pdfUrl);
        console.log('PDF descargado desde el backend:', pdfUrl);
      } else {
        console.error('Error al enviar el Input Text al backend:', response.statusText);
      }
    } catch (error) {
      console.error('Error al enviar el Input Text al backend:', error);
      throw error;
    }
  };
  

  const handleDownloadedPDF = (downloadedPDFUrl) => {
    setDownloadedPDF(downloadedPDFUrl);
  };

  return (
    <div className="container-fluid h-100">
      <div className="row h-100">
        <div className="col-3 px-1 bg-light position-fixed" id="sticky-sidebar">
          <div className="accordion accordion-flush" id="accordionFlushExample">
            <div className="accordion" id="accordionExample">
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                    Accordion Item #4
                  </button>
                </h2>
                <div id="collapseFour" className="accordion-collapse collapse" data-bs-parent="#accordionExample">
                  <div className="accordion-body">
                    <div className="input-container">
                      <input type="text" className="form-control" placeholder="Introduzca ID del paper en Arxiv" value={textInput} onChange={handleTextInputChange} />
                      <button type="button" className="btn btn-primary" onClick={ () => handleInputSubmit()}>Submit paper</button>
                    </div>
                    <div className="input-container2">
                      <h4>Texto seleccionado</h4>
                      {/* Cuadro de entrada de texto de solo lectura */}
                      <textarea className="form-control mt-2 w-100" style={{ 
                        height: '300px', maxWidth: '100%', resize: 'none',overflow: 'auto',scrollbarWidth: 'none', /* For Firefox */
                        msOverflowStyle: 'none' /* For Internet Explorer and Edge */}}  value={selectedText} readOnly 
                      />
                      <button type="button" className="btn btn-primary" onClick={() => sendSelectedTextToBackend()}>Analizar cita</button>
                    </div>
                    <div className="input-container3">
                      <h6>Referencias bibliográficas encontradas en el párrafo del texto seleccionado</h6>
                      {/* Cuadro de entrada de texto de solo lectura */}
                      <textarea className="form-control mt-2 w-100" style={{ 
                        height: '200px', maxWidth: '100%', resize: 'none',overflow: 'auto',scrollbarWidth: 'none', /* For Firefox */
                        msOverflowStyle: 'none' /* For Internet Explorer and Edge */}} value={bibliographyText}
                        onChange={handleTextInputChange} readOnly 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={`col-9 offset-3 h-100 main-area`} id="main">
          <form onSubmit={handlePDFSubmit}>
            <input type="file" className='form-control' onChange={handleChange}/>
            <button type='submit' className='btn btn-success'>Click to view PDF</button>
          </form>
          <h2 className="text-view">View PDF</h2>
          <div className='pdf-container'>
            <Worker workerUrl="https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js">
              {downloadedPDF && (
                <Viewer fileUrl={downloadedPDF} plugins={[defaultLayoutPluginInstance]} />
              )}
              {!downloadedPDF && viewPDF && (
                <Viewer fileUrl={viewPDF} plugins={[defaultLayoutPluginInstance]} />
              )}
              {!downloadedPDF && !viewPDF && <>No PDF</>}
            </Worker>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
