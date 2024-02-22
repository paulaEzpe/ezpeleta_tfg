import React, { useState } from 'react';
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
  const defaultLayoutPluginInstance = defaultLayoutPlugin(
);
  const [pdfFile, setPDFFile] = useState(null)
  const [viewPDF, setViewPDF] = useState(null)
  
  const fileType = ['application/pdf']
  const handleChange = (e) => {
    let selectedFile = e.target.files[0]
    if(selectedFile) {
      if(selectedFile && fileType.includes(selectedFile.type)) {
        let reader = new FileReader()
        reader.readAsDataURL(selectedFile)
        reader.onload = (e) => {
          setPDFFile(e.target.result)
        }
      }
      else {
        setPDFFile(null)
      }
    }
    else {
      console.log("please select")
    }


  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (pdfFile !== null) {
      try {
        setViewPDF(pdfFile);
        const loadingTask = pdfjsLib.getDocument(pdfFile);
        const pdf = await loadingTask.promise;
        let pdfText = '';
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          // Obtener la página actual
          const page = await pdf.getPage(pageNum);
    
          // Extraer el contenido de texto de la página
          const textContent = await page.getTextContent();
    
          // Concatenar el texto extraído de la página al texto total
          textContent.items.forEach((textItem) => {
            pdfText += textItem.str + ' ';
          });
        }
        const response = await fetch('/uploadText', {
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

    //     const formData = new FormData();
    //     formData.append('pdfFileName', pdfFile.name);
    //     console.log("nombre del pdf:",pdfFile.name)
    //     const response = await fetch('/upload', {
    //       method: 'POST',
    //       body: formData
    //     });
    //     if (response.ok) {
    //       console.log('PDF file sent to backend successfully.');
    //     } else {
    //       console.error('Failed to send PDF file to backend.');
    //     }
    //   } catch (error) {
    //     console.error('Error sending PDF file to backend:', error);
    //   }
    // } else {
    //   console.error('No PDF file selected.');
    // }

  
  

  
  
  return (
    <div className="container-fluid h-100">
      <div className="row h-100">
        <div className="col-3 px-1 bg-light position-fixed" id="sticky-sidebar">
          <div className="accordion accordion-flush" id="accordionFlushExample">
            <div className="accordion" id="accordionExample">
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button className="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                    Accordion Item #1
                  </button>
                </h2>
                <div id="collapseOne" className="accordion-collapse collapse show" data-bs-parent="#accordionExample">
                  <div className="accordion-body">
                    <strong>This is the first item's accordion body.</strong> It is shown by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
                  </div>
                </div>
              </div>
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                    Accordion Item #2
                  </button>
                </h2>
                <div id="collapseTwo" className="accordion-collapse collapse" data-bs-parent="#accordionExample">
                  <div className="accordion-body">
                    <strong>This is the second item's accordion body.</strong> It is hidden by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
                  </div>
                </div>
              </div>
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                    Accordion Item #3
                  </button>
                </h2>
                <div id="collapseThree" className="accordion-collapse collapse" data-bs-parent="#accordionExample">
                  <div className="accordion-body">
                    <strong>This is the second item's accordion body.</strong> It is hidden by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
                  </div>
                </div>
              </div>
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                    Accordion Item #4
                  </button>
                </h2>
                <div id="collapseFour" className="accordion-collapse collapse" data-bs-parent="#accordionExample">
                  <div className="accordion-body">
                    <strong>This is the third item's accordion body.</strong> It is hidden by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={`col-9 offset-3 h-100 main-area`} id="main">
          <form onSubmit={handleSubmit}>
            <input type="file" className='form-control' onChange={handleChange}/>
            <button type='submit' className='btn btn-success'>Click to view PDF</button>
          </form>
          <h2 className="text-view">View PDF</h2>
          <div className='pdf-container'>
            <Worker workerUrl="https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js">
              {viewPDF && <> 
                <Viewer fileUrl={viewPDF} plugins={[defaultLayoutPluginInstance]}/>
              </>}
              {!viewPDF && <> No PDF</>}
            </Worker>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
