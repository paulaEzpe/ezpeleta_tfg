import React from 'react';
import { Bar } from 'react-chartjs-2';
import './chart.css';
import 'chart.js/auto';
import { Chart } from 'react-chartjs-2';

const DoughnutChartSuscritos = ({ similitudes, colors }) => {
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
      backgroundColor: colors.backgroundColors,
      borderColor: colors.borderColors,
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
    <div className="chart-wrapper">
      <div className="chart-container">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default DoughnutChartSuscritos;
