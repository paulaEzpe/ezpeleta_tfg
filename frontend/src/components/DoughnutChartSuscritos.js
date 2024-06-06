/*
  Autor: Paula Ezpeleta
  Fecha de creación: Marzo/Abril/Mayo 2023
  Descripción: fichero de la aplicacion ZgzInfo
*/
import React from 'react';
import { Bar } from 'react-chartjs-2';
import './chart.css';
import 'chart.js/auto';
import { Chart } from 'react-chartjs-2';

const DoughnutChartSuscritos = ({ similitudes }) => {
  const data = {
    labels: [
      'Fasttext model',
      'Google model',
      'Our model',
      'BERT',
      'sentence-transformers BERT model'
    ],
    datasets: [{
      data: similitudes, // Usar similitudes directamente
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)', // Color para Google model
        'rgba(54, 162, 235, 0.2)', // Color para sentences-transformers BERT model
        'rgba(255, 206, 86, 0.2)', // Color para Fasttext model
        'rgba(75, 192, 192, 0.2)', // Color para bert
        'rgba(153, 102, 255, 0.2)' // Color para sentence bert
      ],
      borderColor: [
        'rgb(255, 99, 132)', // Color para Google model
        'rgb(54, 162, 235)', // Color para sentences-transformers BERT model
        'rgb(255, 206, 86)', // Color para Fasttext model
        'rgb(75, 192, 192)', // Color para bert
        'rgb(153, 102, 255)' // Color para sentence bert
      ],
      borderWidth: 1
    }]
  };

  const options = {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  return (
    <div className="chart-container">
      <Bar data={data} options={options} />
    </div>
  );
};
export default DoughnutChartSuscritos;
