import React from 'react';
import { Pie } from 'react-chartjs-2';
import './chart.css';
import 'chart.js/auto';
import { Chart } from 'react-chartjs-2';

const PieChartPolaridad = ({ polaridades }) => {
  const data = {
    labels: [
      'Positivo',
      'Negativo',
      'Neutro'
    ],
    datasets: [{
      data: polaridades,
      backgroundColor: [
        'rgba(0, 255, 0, 0.2)',
        'rgba(255, 0, 0, 0.2)',
        'rgba(128, 128, 128, 0.2)'
      ],
      borderColor: [
        'rgba(0, 255, 0, 1)',
        'rgba(255, 0, 0, 1)',
        'rgba(128, 128, 128, 1)'
      ],
      borderWidth: 1
    }]
  };

  const options = {
    plugins: {
      legend: {
        display: true
      }
    }
  };

  return (
    <div className="chart-wrapper">
      <div className="chart-container">
        <Pie data={data} options={options} />
      </div>
    </div>
  );
};

export default PieChartPolaridad;
