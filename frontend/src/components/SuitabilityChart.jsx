import React from 'react';
import { Radar } from 'react-chartjs-2';

const SuitabilityChart = ({ data, title = "Suitability Analysis" }) => {
  const chartData = {
    labels: ['Data Quality', 'Sample Size', 'Compliance', 'Risk Level'],
    datasets: [
      {
        label: title,
        data: [
          data?.data_quality || 0,
          data?.sample_adequacy || 0,
          data?.compliance || 0,
          data?.risk_level || 0
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20
        }
      }
    }
  };

  return (
    <div className="w-full h-64">
      <Radar data={chartData} options={options} />
    </div>
  );
};

export default SuitabilityChart;