import React, { useState, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import Alert from 'react-bootstrap/Alert';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'pdfjs-dist/web/pdf_viewer.css';
import 'pdfjs-dist/build/pdf.worker.min';
import './App.css';
import { Button, Form, Modal } from 'react-bootstrap';

import { Viewer, Worker } from '@react-pdf-viewer/core'
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'
import '@react-pdf-viewer/core/lib/styles/index.css'
import '@react-pdf-viewer/default-layout/lib/styles/index.css'
import ListGroup from 'react-bootstrap/ListGroup'
import DoughnutChartSuscritos from "./components/DoughnutChartSuscritos";
import PieChartPolaridad from "./components/PieChartPolaridad";
import Spinner from 'react-bootstrap/Spinner';


function App() {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const [pdfFile, setPDFFile] = useState(null);
  const [viewPDF, setViewPDF] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [downloadedPDF, setDownloadedPDF] = useState(null);
  const [bibliographyText, setBibliographyText] = useState('');
  const [paragraphText, setParagraphText] = useState('');
  const [filteredCitations, setFilteredCitations] = useState([]);
  const [referenceJsonText, setReferenceJsonText] = useState('');
  const [showModalModeloCuerpo, setShowModalModeloCuerpo] = useState(false);
  const [showModalModeloAbstract, setShowModalModeloAbstract] = useState(false);
  const [showModalPolaridad, setShowModalPolaridad] = useState(false);
  const [similitud, setSimilitud] = useState(null);
  const modelNames = ['Fasttext model', 'Google model', 'Our model', 'BERT', 'sentence-transformers BERT model'];
  const [isAnalizarCitaEnabled, setIsAnalizarCitaEnabled] = useState(false);
  const [similitudAbstract, setSimilitudAbstract] = useState(null);
  const [paragraph, setParagraph] = useState("");
  const [polaridades, setPolaridades] = useState([]);
  const [selectedTextSent, setSelectedTextSent] = useState('');


  const customColorsAbstract = {
    backgroundColors: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)'
    ],
    borderColors: [
      'rgb(255, 99, 132)',
      'rgb(54, 162, 235)',
      'rgb(255, 206, 86)',
      'rgb(75, 192, 192)',
      'rgb(153, 102, 255)'
    ]
  };

  const customColorsBody = {
    backgroundColors: [
      'rgba(68, 108, 179, 0.2)', // Azul oscuro
      'rgba(146, 43, 33, 0.2)', // Rojo oscuro
      'rgba(41, 89, 69, 0.2)', // Verde oscuro
      'rgba(91, 42, 116, 0.2)', // Púrpura oscuro
      'rgba(119, 91, 91, 0.2)' // Marrón oscuro
    ],
    borderColors: [
      'rgb(68, 108, 179)', // Azul oscuro
      'rgb(146, 43, 33)', // Rojo oscuro
      'rgb(41, 89, 69)', // Verde oscuro
      'rgb(91, 42, 116)', // Púrpura oscuro
      'rgb(119, 91, 91)' // Marrón oscuro
    ]
  };



  useEffect(() => {
    // Desactivar el botón al principio
    setIsAnalizarCitaEnabled(false);
  }, []);

  /////////////////////////////////////////////////////////////////////////////////////////////////

  const handleShowModalModeloCuerpo = () => {
    setParagraph('');
    //borrar cita, parrafo del texto seleccionado y referencas???
    setShowModalModeloCuerpo(true);
    sendReferencedJsonBodyToBackend();
  };
  const handleShowModalModeloAbstract = () => {
    setParagraph('');
    //borrar cita, parrafo del texto seleccionado y referencas???
    setShowModalModeloAbstract(true);
    sendReferencedJsonAbstractToBackend();
  };

  //aqui habra que llamar a una funcion que mande la cita al backend para que calcule la polaridad, 
  // y me devuelva la polaridad
  const handleShowModalPolaridad = () => {
    setShowModalPolaridad(true);
    sendCitationForPolarityToBackend();
  };

  const handleCloseModalModeloCuerpo = () => setShowModalModeloCuerpo(false);
  const handleCloseModalModeloAbstract = () => setShowModalModeloAbstract(false);
  const handleCloseModalPolaridad = () => setShowModalPolaridad(false);

  const sendCitationForPolarityToBackend = async () => {
    setPolaridades([]);
    const toastIdPolaridad = toast.loading('Calculando polaridad de la cita...');
    try {
      console.log("he entrado y la cita es: ", selectedTextSent);
      const response = await fetch('/sendCitationForPolarityToBackend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ selectedTextSent })
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Respuesta del backend:', responseData);

        // Procesar las polaridades recibidas
        if (responseData.polaridades_list && responseData.polaridades_list.length > 0) {
          setPolaridades(responseData.polaridades_list);
          console.log('Polaridades recibidas en el frontend:', polaridades);
          // Aquí puedes actualizar el estado, UI, etc. con las polaridades
          // Por ejemplo, si usas React, podrías actualizar el estado con las polaridades
          // setPolaridades(polaridades);
          toast.update(toastIdPolaridad, {
            render: 'Polaridad obtenida!',
            type: 'success',
            autoClose: 3000,
            isLoading: false
          });
        } else {
          console.error('La respuesta no contiene polaridades.');
          toast.update(toastIdPolaridad, {
            render: 'No se ha podido calcular la polaridad.',
            type: 'error',
            autoClose: 3000,
            isLoading: false
          });
        }
      } else {
        console.error('Error al enviar la cita al backend.');
        toast.update(toastIdPolaridad, {
          render: 'No se ha podido calcular la polaridad.',
          type: 'error',
          autoClose: 3000,
          isLoading: false
        });
      }
    } catch (error) {
      console.error('Error al enviar la cita al backend:', error);
      toast.update(toastIdPolaridad, {
        render: 'No se ha podido calcular la polaridad.',
        type: 'error',
        autoClose: 3000,
        isLoading: false
      });
    }
  };

  const sendReferencedJsonBodyToBackend = async () => {
    setSimilitud('');
    const toastIdBody = toast.loading('Calculando similitud entre la cita y los párrafos del cuerpo...');
    try {
      // Encontrar el índice donde comienza el cuerpo del texto
      const cuerpoDelTextoIndex = referenceJsonText.indexOf("Texto del Cuerpo:");

      // Si "texto cuerpo:" se encuentra en referenceJsonText, extraerlo
      let cuerpoDelTexto = referenceJsonText;
      if (cuerpoDelTextoIndex !== -1) {
        // Extraer el texto que sigue después de "texto cuerpo:"
        cuerpoDelTexto = referenceJsonText.substring(cuerpoDelTextoIndex + "Texto del Cuerpo:".length).trim();
        console.log('Cuerpo del texto:', cuerpoDelTexto);
      } else {
        console.error('No se encontró "texto cuerpo:" en el texto de la referencia.');
        return;
      }

      // Enviar solo el cuerpo del texto al backend
      const response = await fetch('/sendReferencedJsonBodyToBackend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ referencedjsonbodytextandselectedtext: cuerpoDelTexto, selectedTextSent })
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Respuesta del backend:', responseData);

        if (responseData.similitudes && responseData.similitudes.length > 0) {
          // Actualizar el estado con las similitudes recibidas y el párrafo correspondiente
          setSimilitud(responseData.similitudes);
          setParagraph(responseData.paragraph);
          console.log('Similitudes recibidas:', responseData.similitudes);
          console.log('Párrafo con las similitudes más altas:', responseData.paragraph);
          toast.update(toastIdBody, {
            render: 'Párrafo con mayor similitud con la cita encontrado!',
            type: 'success',
            autoClose: 4000,
            isLoading: false
          });
        } else {
          console.error('El backend no devolvió las similitudes esperadas.');
          toast.update(toastIdBody, {
            render: 'Párrafo con mayor similitud con la cita no encontrado',
            type: 'error',
            autoClose: 4000,
            isLoading: false
          });
        }
      } else {
        console.error('Error al enviar el texto al backend.');
        toast.update(toastIdBody, {
          render: 'Párrafo con mayor similitud con la cita no encontrado',
          type: 'error',
          autoClose: 4000,
          isLoading: false
        });
      }
    } catch (error) {
      console.error('Error al enviar el texto al backend:', error);
      toast.update(toastIdBody, {
        render: 'Párrafo con mayor similitud con la cita no encontrado',
        type: 'error',
        autoClose: 4000,
        isLoading: false
      });
    }
  };


  const sendReferencedJsonAbstractToBackend = async () => {
    const toastIdAbstract = toast.loading('Calculando similitud entre cita y abstract...');
    try {
      // Encontrar el índice donde comienza el abstract
      const abstractIndex = referenceJsonText.indexOf("Abstract:");

      // Encontrar el índice donde comienza el cuerpo del texto
      const cuerpoDelTextoIndex = referenceJsonText.indexOf("Texto del Cuerpo:");

      // Si "Abstract:" y "Texto del Cuerpo:" se encuentran en referenceJsonText, extraer el texto entre ellos
      if (abstractIndex !== -1 && cuerpoDelTextoIndex !== -1) {
        // Extraer el texto entre "Abstract:" y "Texto del Cuerpo:" (excluyendo ambas etiquetas)
        const textoEntreAbstractYCuerpo = referenceJsonText.substring(abstractIndex + "Abstract:".length, cuerpoDelTextoIndex).trim();
        console.log('Texto entre Abstract y Texto del Cuerpo:', textoEntreAbstractYCuerpo);

        // Enviar solo el texto entre Abstract y Texto del Cuerpo al backend
        const response = await fetch('/sendReferencedJsonAbstractToBackend', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ referencedjsonabstracttextandselectedtext: textoEntreAbstractYCuerpo, selectedTextSent })
        });

        if (response.ok) {
          const responseData = await response.json();
          console.log('Respuesta del backend:', responseData);

          if (responseData.similitudes && responseData.similitudes.length > 0) {
            // Actualizar el estado con las similitudes recibidas
            setSimilitudAbstract(responseData.similitudes);
            console.log('Similitudes recibidas:', responseData.similitudes);
            toast.update(toastIdAbstract, {
              render: 'Similitud calculada!',
              type: 'success',
              autoClose: 3000,
              isLoading: false
            });
          } else {
            console.error('El backend no devolvió las similitudes esperadas.');
            toast.update(toastIdAbstract, {
              render: 'No se ha podido calcular la similitud entre la cita y el abstract',
              type: 'error',
              autoClose: 3000,
              isLoading: false
            });
          }
        } else {
          console.error('Error al enviar la cita al backend.');
          toast.update(toastIdAbstract, {
            render: 'No se ha podido calcular la similitud entre la cita y el abstract',
            type: 'error',
            autoClose: 3000,
            isLoading: false
          });
        }
      } else {
        console.error('No se encontró "Abstract:" o "Texto del Cuerpo:" en el texto de la referencia.');
        toast.update(toastIdAbstract, {
          render: 'No se ha podido calcular la similitud entre la cita y el abstract',
          type: 'error',
          autoClose: 3000,
          isLoading: false
        });
        return;
      }
    } catch (error) {
      console.error('Error al enviar la cita al backend:', error);
    }
  };


  /////////////////////////////////////////////////////////////////////////////////////////////////





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



  const sendSelectedTextToBackend = async () => {
    // Comprobar si el texto seleccionado no es una cadena vacía
    if (!selectedText.trim()) {
      toast.warn('No hay texto seleccionado');
      console.warn('El texto seleccionado está vacío, no se enviará al backend.');
      // almacenar la cita que se ha mandado al backend
      return;
    }
    setSelectedTextSent(selectedText);
    console.log("Ahora la cita es: ", selectedTextSent);
    const toastId = toast.loading('Buscando párrafo correspondiente...');

    try {
      console.log('He entrado');
      // prueba
      setBibliographyText('');
      setTextInput('');
      setParagraphText('');
      setFilteredCitations([]);
      setReferenceJsonText('');

      const response = await fetch('/uploadSelectedText', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedText })
      });

      if (response.ok) {
        console.log('Texto seleccionado enviado al backend exitosamente.');

        await fetchBibliographyFromBackend();
        await fetchParagraphFromBackend();

        toast.update(toastId, {
          render: 'Párrafo encontrado!',
          type: 'success',
          autoClose: 3000,
          isLoading: false
        });
      } else {
        console.error('Error al enviar el texto seleccionado al backend.');
        toast.update(toastId, {
          render: 'Error al enviar el texto seleccionado',
          type: 'error',
          autoClose: 5000,
          isLoading: false
        });
      }
    } catch (error) {
      console.error('Error al enviar el texto seleccionado al backend:', error);
      toast.update(toastId, {
        render: 'Error al buscar párrafo',
        type: 'error',
        autoClose: 5000,
        isLoading: false
      });
    }
  };

  //  para recibir del backend la bibliografía correspondiente al parrafo al que pertenece el texto seleccionado por el usuario
  async function fetchBibliographyFromBackend() {
    try {
      const response = await fetch('/getBibliography');
      if (response.ok) {
        const bibliographyText = await response.text();
        console.log('Longitud de bibliografía:', bibliographyText.length); // Verificar la longitud del texto recibido
        console.log(bibliographyText); // Aquí puedes manejar el string recibido
        setBibliographyText(bibliographyText);
        const citations = bibliographyText.split("Cita {cite:");
        let index = 1; // Inicializar el índice en 1
        // Filtrar las citas para eliminar las cadenas vacías
        const filteredCitations = citations.filter(citation => citation.trim() !== '').map(citation => {
          // Dividir la cita en dos partes: identificador y bibliografía
          const parts = citation.split("}");
          // Tomar la segunda parte, que es la bibliografía, y eliminar espacios adicionales
          //const citationContent = parts.slice(1).map(part => part + "}").join("");
          const citationContent = parts.slice(1).map((part, index, array) => {
            if (index === array.length - 1) {
              return part;
            } else {
              return part + "}";
            }
          }).join("");
          // Construir la cita con el índice delante
          const indexedCitation = `[${index++}] ${citationContent}`;
          return indexedCitation;
        }).filter(citation => citation !== ''); // Filtrar citas vacías

        console.log(filteredCitations); // Mostrar las citas divididas en la consola
        setFilteredCitations(filteredCitations);
      } else {
        console.error('Error al obtener la bibliografía del backend.');
      }
    } catch (error) {
      console.error('Error al obtener la bibliografía del backend:', error);
    }
  }

  // const handleClick = async (citationContent) => {
  //   // Imprimir el contenido por terminal
  //   console.log('Contenido de la cita:', citationContent);

  //   try {
  //       // Enviar el contenido al backend
  //       const response = await fetch('/sendCitationToBackend', {
  //           method: 'POST',
  //           headers: {
  //               'Content-Type': 'application/json'
  //           },
  //           body: JSON.stringify({ citation: citationContent })
  //       });
  //       if (response.ok) {
  //           console.log('Cita enviada al backend con éxito.');
  //       } else {
  //           console.error('Error al enviar la cita al backend.');
  //       }
  //   } catch (error) {
  //       console.error('Error al enviar la cita al backend:', error);
  //   }
  // }

  const handleClick = async (citationContent) => {
    console.log('Contenido de la cita:', citationContent);

    // En caso de que la cita seleccionada no contenga "arxiv:", no se envía al backend
    if (!citationContent.includes("arXiv:")) {
      toast.warn('La cita seleccionada no pertenece a arXiv. Seleccione una que sí.');
      console.warn('La cita seleccionada no pertenece a arXiv.');
      return;
    }
    // poner vacio el textarea
    setReferenceJsonText('');
    const toastIdCita = toast.loading('Obteniendo artículo de la referencia clickada...');
    try {
      const response = await fetch('/sendCitationToBackend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ citation: citationContent })
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Cuerpo del JSON recibido en el frontend:', responseData);

        // Formatear el texto recibido para mostrar en el textarea
        const formattedText = `Abstract: ${responseData.abstract}\n\nTexto del Cuerpo:\n${responseData.texto_del_cuerpo}`;

        // Guardar el texto recibido en la variable de estado
        setReferenceJsonText(formattedText);
        toast.update(toastIdCita, {
          render: 'Artículo encontrado correctamente!',
          type: 'success',
          autoClose: 3000,
          isLoading: false});
      } else {
        console.error('Error al enviar la cita al backend.');
        toast.update(toastIdCita, {
          render: 'Error al buscar el artículo referenciado',
          type: 'error',
          autoClose: 5000,
          isLoading: false
        });
      }
    } catch (error) {
      console.error('Error al enviar la cita al backend:', error);
      toast.update(toastIdCita, {
        render: 'Error al buscar el artículo referenciado',
        type: 'error',
        autoClose: 5000,
        isLoading: false
      });
    }
  };

  const isTextPresent = referenceJsonText.length > 0;

  // async function fetchParagraphFromBackend() {
  //   try {
  //       const response = await fetch('/getTextParagraphSelection');
  //       if (response.ok) {
  //           const paragraphText = await response.text();
  //           console.log(paragraphText); // Aquí puedes manejar el string recibido
  //           setParagraphText(paragraphText);
  //       } else {
  //           console.error('Error al obtener el parrafo del backend.');
  //       }
  //   } catch (error) {
  //       console.error('Error al obtener el parrafo del backend:', error);
  //   }
  // }

  async function fetchParagraphFromBackend() {
    try {
      const response = await fetch('/getTextParagraphSelection');
      if (response.ok) {
        const paragraphText = await response.text();
        console.log(paragraphText); // Aquí puedes manejar el string recibido
        const citationMap = {};
        let nextIndex = 1;
        // Reemplazar cada cita con un número de referencia
        const updatedText = paragraphText.replace(/\{\{cite:(.*?)\}\}/g, (_, id) => {
          if (!citationMap[id]) {
            citationMap[id] = nextIndex++;
          }
          return `[${citationMap[id]}]`;
        });
        setParagraphText(updatedText);
      } else {
        console.error('Error al obtener el parrafo del backend.');
      }
    } catch (error) {
      console.error('Error al obtener el parrafo del backend:', error);
    }
  }

  async function fetchParagraphFromBackend() {
    try {
      const response = await fetch('/getTextParagraphSelection');
      if (response.ok) {
        const paragraphText = await response.text();
        console.log(paragraphText); // Aquí puedes manejar el string recibido
        const citationMap = {};
        let nextIndex = 1;
        // Reemplazar cada cita con un número de referencia
        const updatedText = paragraphText.replace(/\{\{cite:(.*?)\}\}/g, (_, id) => {
          if (!citationMap[id]) {
            citationMap[id] = nextIndex++;
          }
          return `[${citationMap[id]}]`;
        });
        setParagraphText(updatedText);
      } else {
        console.error('Error al obtener el parrafo del backend.');
      }
    } catch (error) {
      console.error('Error al obtener el parrafo del backend:', error);
    }
  }





  const fileType = ['application/pdf'];

  const handleChange = (e) => {
    //prueba 
    setBibliographyText('');
    setPDFFile(null);
    let selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile && fileType.includes(selectedFile.type)) {
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
    document.getElementById('analizar-cita-btn').disabled = true;
    // prueba
    setTextInput('');
    setSelectedText('');
    setBibliographyText('');
    setViewPDF(null)
    e.preventDefault();
    setParagraphText('');
    setFilteredCitations([]);
    setReferenceJsonText('');
    if (pdfFile !== null) {
      try {
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
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pdfText })
        });
        console.log('Texto extraído del PDF:', pdfText);
        if (response.ok) {
          const { pdfUrl, tituloEncontrado, error } = await response.json();
          if (pdfUrl) {
            setDownloadedPDF(pdfUrl);
            console.log('PDF descargado desde el backend:', pdfUrl);
            // Activar el botón de "Analizar cita" solo si se encontró el título en la base de datos
            if (tituloEncontrado) {
              setIsAnalizarCitaEnabled(true);
            }
            else {
              toast.error('El artículo no se encuentra en la base de datos. No podrá analizar citas ni referencias.');
              console.log('Error al encontrar el título:', error);
            }
          } else {
            // Si no se encuentra el documento, mostrar mensaje y mantener botón desactivado

          }
        } else {
          console.error('Error al enviar el Input Text al backend:', response.statusText);
        }
      } catch (error) {
        console.error('Error extracting text from PDF:', error);
        throw error;
      }
    }
  };

  const handleInputSubmit = async () => {
    if (!textInput.trim()) {
      toast.warn('No se ha introducido ningún identificador de paper');
      console.warn('El texto seleccionado está vacío, no se enviará al backend.');
      return;
    }
    try {
      setIsAnalizarCitaEnabled(false);
      setBibliographyText('');
      setSelectedText('');
      setParagraphText('');
      setFilteredCitations([]);
      setReferenceJsonText('');
      // icono de carga
      // Desactivar el botón de "Analizar cita" antes de enviar la solicitud
      document.getElementById('analizar-cita-btn').disabled = true;

      const response = await fetch('/uploadInputPdfId', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputText: textInput })
      });
      if (response.ok) {
        const { pdfUrl, tituloEncontrado, error } = await response.json();
        if (pdfUrl) {
          setDownloadedPDF(pdfUrl);
          console.log('PDF descargado desde el backend:', pdfUrl);
          // Activar el botón de "Analizar cita" solo si se encontró el título en la base de datos
          if (tituloEncontrado) {
            setIsAnalizarCitaEnabled(true);
          }
          else {
            toast.error('El artículo no se encuentra en la base de datos. No podrá analizar citas ni referencias.');
            console.log('Error al encontrar el título:', error);
          }
        } else {
          // Si no se encuentra el documento, mostrar mensaje y mantener botón desactivado

        }
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
      <ToastContainer />
      <div className="row h-100">
        <div className="col-3 px-1 bg-light position-fixed" id="sticky-sidebar" style={{
          overflow: 'auto', scrollbarWidth: 'none', /* For Firefox */
          msOverflowStyle: 'none' /* For Internet Explorer and Edge */
        }}>
          <div className="accordion accordion-flush" id="accordionFlushExample">
            <div className="accordion" id="accordionExample">
              <div className="accordion-item" >
                <h2 className="accordion-header">
                  <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                    Use tool to analyze citations and references
                  </button>
                </h2>
                <div className="container_accordion" style={{
                  maxHeight: '100%', overflowY: 'auto', scrollbarWidth: 'none', /* For Firefox */
                  msOverflowStyle: 'none' /* For Internet Explorer and Edge */
                }}>
                  <div id="collapseFour" className="accordion-collapse collapse" data-bs-parent="#accordionExample" style={{ maxHeight: '100%', overflowY: 'auto' }}>
                    <div className="accordion-body" style={{ maxHeight: '100%', overflowY: 'auto' }}>
                      <div className="input-container">
                        <input type="text" className="form-control" placeholder="Enter the paper ID on arXiv" value={textInput} onChange={handleTextInputChange} />
                        <button type="button" className="btn btn-primary" onClick={() => handleInputSubmit()}>Submit paper</button>
                      </div>
                      <div className="input-container2">
                        <h4>Selected text</h4>
                        {/* Cuadro de entrada de texto de solo lectura */}
                        <textarea className="form-control mt-2 w-100" style={{
                          height: '300px', maxWidth: '100%', resize: 'none', overflow: 'auto', scrollbarWidth: 'none', /* For FFirefox */
                          msOverflowStyle: 'none' /* For Internet Explorer and Edge */
                        }} value={selectedText} readOnly
                        />
                        <button id="analizar-cita-btn" type="button" className="btn btn-primary" onClick={() => sendSelectedTextToBackend()} disabled={!selectedText || !isAnalizarCitaEnabled}>Analyze citation</button>
                      </div>
                      <div className="input-container3">
                        <h6>Paragraph of the selected text</h6>
                        {/* Cuadro de entrada de texto de solo lectura */}
                        <textarea className="form-control mt-2 w-100" style={{
                          height: '300px', maxWidth: '100%', resize: 'none', overflow: 'auto', scrollbarWidth: 'none', /* For Firefox */
                          msOverflowStyle: 'none' /* For Internet Explorer and Edge */
                        }} value={paragraphText}
                          onChange={handleTextInputChange} readOnly
                        />
                      </div>
                      <div style={{
                        maxHeight: '300px', overflowY: 'auto', scrollbarWidth: 'none', /* For Firefox */
                        msOverflowStyle: 'none' /* For Internet Explorer and Edge */
                      }}>
                        <h6>Paragraph references</h6>
                        {/* <ListGroup as="ol" numbered>
                          {filteredCitations.map((citation, index) => (
                            <ListGroup.Item key={index} as="li">{citation}</ListGroup.Item>
                          ))}
                        </ListGroup> */}
                        <ListGroup>
                          {filteredCitations.map((citation, index) => (
                            <ListGroup.Item key={index} as="li" onClick={() => handleClick(citation)}>
                              {citation}
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={`col-9 offset-3 h-100 main-area`} id="main" style={{ marginBottom: '40px' }}>
          <form onSubmit={handlePDFSubmit}>
            <input type="file" className='form-control' onChange={handleChange} />
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
          <h3 className="text-view">Article corresponding to the selected reference</h3>
          <textarea className="form-control mt-2 w-100" style={{
            height: '300px', maxWidth: '90%', resize: 'none', overflow: 'auto', scrollbarWidth: 'none', /* For Firefox */
            msOverflowStyle: 'none' /* For Internet Explorer and Edge */
          }} value={referenceJsonText}
            onChange={handleTextInputChange} readOnly
          />
          <Button variant="outline-success" disabled={!isTextPresent} onClick={handleShowModalModeloCuerpo}>
            Obtain similarity with body
          </Button>
          <Modal show={showModalModeloCuerpo} onHide={handleCloseModalModeloCuerpo} centered>
            <Modal.Header closeButton>
              <Modal.Title>Similarity between cite and referenced paper body</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <DoughnutChartSuscritos similitudes={similitud} colors={customColorsBody} />
              <h5 className="text-view">Paragraph with highest similarity:</h5>
              {paragraph}
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseModalModeloCuerpo}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
          <Button variant="outline-dark" disabled={!isTextPresent} onClick={handleShowModalModeloAbstract}>
            Obtain similarity with abstract
          </Button>
          <Modal show={showModalModeloAbstract} onHide={handleCloseModalModeloAbstract} centered>
            <Modal.Header closeButton>
              <Modal.Title>Similarity between cite and referenced paper abstract</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <DoughnutChartSuscritos similitudes={similitudAbstract} colors={customColorsAbstract} />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseModalModeloAbstract}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
          <Button variant="outline-secondary" disabled={!isTextPresent} onClick={handleShowModalPolaridad}>
            Obtain polarity of the cite
          </Button>
          <Modal show={showModalPolaridad} onHide={handleCloseModalPolaridad} centered>
            <Modal.Header closeButton>
              <Modal.Title>Polarity of the cite</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <PieChartPolaridad polaridades={polaridades} />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseModalPolaridad}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
      </div>
    </div>
  );
}

export default App;
