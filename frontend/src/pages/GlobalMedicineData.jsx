import React, { useState, useEffect } from 'react';
import { FiGlobe, FiDownload, FiFilter } from 'react-icons/fi';

const GlobalMedicineData = () => {
  const [countries, setCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCountries();
  }, []);

  const fetchCountries = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/global/countries', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCountries(data.countries);
      }
    } catch (error) {
      console.error('Error fetching countries:', error);
    }
  };

  const handleDownload = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/global/download?country=${selectedCountry}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `global_medicine_data_${selectedCountry}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to download data');
      }
    } catch (error) {
      console.error('Error downloading:', error);
      alert('Failed to download data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center space-x-2">
          <FiGlobe className="text-xl text-blue-600" />
          <h1 className="text-lg font-bold text-gray-800">Global Medicine Data</h1>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Download Patient & Medicine Data</h2>
          <p className="text-sm text-gray-600 mb-4">
            Select a country to download patient and checkup data from hospitals in that region.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FiFilter className="inline mr-2" />
              Filter by Country
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Countries</option>
              {countries.map((country) => (
                <option key={country} value={country}>
                  {country}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleDownload}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <FiDownload />
              {loading ? 'Downloading...' : 'Download CSV'}
            </button>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">Data Includes:</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Patient Information (ID, Name, Age, Gender, Blood Group, etc.)</li>
            <li>• Checkup Records (Blood Pressure, Oxygen Level, Disease)</li>
            <li>• Medicine Prescriptions (Medicine Name, Dosage, Frequency)</li>
            <li>• Hospital Information (Hospital Name, Country)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GlobalMedicineData;
