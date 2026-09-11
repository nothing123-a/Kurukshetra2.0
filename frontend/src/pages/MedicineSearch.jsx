import React, { useState } from 'react';
import { FiSearch, FiPackage, FiInfo } from 'react-icons/fi';

const MedicineSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [medicineData, setMedicineData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError('');
    setMedicineData(null);

    try {
      const response = await fetch(`http://localhost:8000/api/medicine/search?name=${encodeURIComponent(searchTerm)}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setMedicineData(data);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Medicine not found');
      }
    } catch (err) {
      setError('Failed to search medicine. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-4">
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center space-x-2">
          <FiPackage className="text-xl text-purple-600" />
          <h1 className="text-lg font-bold text-gray-800">Medicine Search</h1>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter medicine name (e.g., Aspirin, Paracetamol)"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
            {error}
          </div>
        )}

        {medicineData && (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
              <h2 className="text-xl font-bold text-gray-800 mb-2">{medicineData.name}</h2>
              {medicineData.generic_name && (
                <p className="text-sm text-gray-600">Generic Name: <span className="font-semibold">{medicineData.generic_name}</span></p>
              )}
            </div>

            {medicineData.composition && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiInfo className="text-purple-600" />
                  Chemical Composition
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-purple-50">
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700">Property</th>
                        <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50">Composition</td>
                        <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700 break-words">{medicineData.composition.length > 300 ? medicineData.composition.substring(0, 300) : medicineData.composition}</td>
                      </tr>
                      {medicineData.molecular_formula && (
                        <tr>
                          <td className="border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50">Molecular Formula</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700 font-mono">{medicineData.molecular_formula}</td>
                        </tr>
                      )}
                      {medicineData.molecular_weight && (
                        <tr>
                          <td className="border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50">Molecular Weight</td>
                          <td className="border border-gray-300 px-4 py-2 text-sm text-gray-700">{medicineData.molecular_weight}</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {medicineData.description && medicineData.description.length < 400 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Description</h3>
                <p className="text-gray-700">{medicineData.description}</p>
              </div>
            )}

            {medicineData.uses && medicineData.uses.length < 400 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Uses</h3>
                <p className="text-gray-700">{medicineData.uses}</p>
              </div>
            )}

            {medicineData.side_effects && medicineData.side_effects.length < 400 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Side Effects</h3>
                <p className="text-gray-700">{medicineData.side_effects}</p>
              </div>
            )}
          </div>
        )}

        {!medicineData && !loading && !error && (
          <div className="text-center py-12">
            <FiPackage className="text-6xl text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Search for a medicine to view its chemical composition and details</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MedicineSearch;
