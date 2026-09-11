import React, { useState, useEffect } from 'react';
import { FiUser, FiHeart, FiActivity, FiCheck, FiPlus, FiX } from 'react-icons/fi';

const PatientCheckup = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showCheckupForm, setShowCheckupForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    oxygen_level: '',
    blood_pressure: '',
    disease: ''
  });
  const [medicines, setMedicines] = useState([{ medicine: '', dosage: '', frequency: '' }]);

  useEffect(() => {
    fetchOngoingCheckups();
  }, []);

  const fetchOngoingCheckups = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/checkups', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data.patients);
      }
    } catch (error) {
      console.error('Error fetching checkups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCheckupData = async (patient) => {
    setSelectedPatient(patient);
    
    // Fetch existing checkup data
    try {
      const response = await fetch(`http://localhost:8000/api/patients/${patient.id}/checkup-data`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setFormData({
          oxygen_level: data.oxygen_level || '',
          blood_pressure: data.blood_pressure || '',
          disease: data.disease || ''
        });
        setMedicines(data.medicines || [{ medicine: '', dosage: '', frequency: '' }]);
      }
    } catch (error) {
      console.error('Error fetching checkup data:', error);
    }
    
    setShowCheckupForm(true);
  };

  const handleSubmitCheckup = async (e) => {
    e.preventDefault();
    
    try {
      // Delete existing checkups first to avoid duplicates
      await fetch(`http://localhost:8000/api/patients/${selectedPatient.id}/checkup-data`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      // Add new checkup data
      const response = await fetch('http://localhost:8000/api/checkups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...formData,
          medicines: medicines,
          patient_id: selectedPatient.id
        })
      });

      if (response.ok) {
        alert('Checkup data saved successfully!');
        resetForm();
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to save checkup data');
      }
    } catch (error) {
      console.error('Error saving checkup data:', error);
      alert('Failed to save checkup data');
    }
  };

  const addMedicine = () => {
    setMedicines([...medicines, { medicine: '', dosage: '', frequency: '' }]);
  };

  const removeMedicine = (index) => {
    setMedicines(medicines.filter((_, i) => i !== index));
  };

  const updateMedicine = (index, field, value) => {
    const updated = [...medicines];
    updated[index][field] = value;
    setMedicines(updated);
  };

  const handleCompleteCheckup = async (patientId) => {
    if (!confirm('Are you sure you want to complete this checkup?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/patients/${patientId}/checkup/complete`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        fetchOngoingCheckups();
        alert('Checkup completed successfully!');
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to complete checkup');
      }
    } catch (error) {
      console.error('Error completing checkup:', error);
      alert('Failed to complete checkup');
    }
  };

  const resetForm = () => {
    setFormData({
      oxygen_level: '',
      blood_pressure: '',
      disease: ''
    });
    setMedicines([{ medicine: '', dosage: '', frequency: '' }]);
    setShowCheckupForm(false);
    setSelectedPatient(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 p-4">
        <div className="flex items-center justify-center h-32">
          <div className="text-sm text-gray-600">Loading checkups...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 p-4">
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center space-x-2">
          <FiHeart className="text-xl text-green-600" />
          <h1 className="text-lg font-bold text-gray-800">Patient Checkup</h1>
        </div>
      </div>

      {showCheckupForm && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            Checkup for {selectedPatient?.patient_name}
          </h2>
          <form onSubmit={handleSubmitCheckup} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Oxygen Level (%) *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.oxygen_level}
                  onChange={(e) => setFormData({...formData, oxygen_level: e.target.value})}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Blood Pressure *
                </label>
                <input
                  type="text"
                  required
                  placeholder="120/80"
                  value={formData.blood_pressure}
                  onChange={(e) => setFormData({...formData, blood_pressure: e.target.value})}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Disease/Condition *
                </label>
                <input
                  type="text"
                  required
                  value={formData.disease}
                  onChange={(e) => setFormData({...formData, disease: e.target.value})}
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-green-500"
                />
              </div>
            </div>

            <div className="border-t pt-3">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-sm font-semibold text-gray-700">Medicines</h3>
                <button
                  type="button"
                  onClick={addMedicine}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs flex items-center gap-1"
                >
                  <FiPlus /> Add Medicine
                </button>
              </div>
              {medicines.map((med, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2 p-2 bg-gray-50 rounded">
                  <input
                    type="text"
                    required
                    placeholder="Medicine name"
                    value={med.medicine}
                    onChange={(e) => updateMedicine(index, 'medicine', e.target.value)}
                    className="px-2 py-1.5 text-sm border border-gray-300 rounded-md"
                  />
                  <input
                    type="text"
                    required
                    placeholder="Dosage (e.g., 500mg)"
                    value={med.dosage}
                    onChange={(e) => updateMedicine(index, 'dosage', e.target.value)}
                    className="px-2 py-1.5 text-sm border border-gray-300 rounded-md"
                  />
                  <select
                    required
                    value={med.frequency}
                    onChange={(e) => updateMedicine(index, 'frequency', e.target.value)}
                    className="px-2 py-1.5 text-sm border border-gray-300 rounded-md"
                  >
                    <option value="">Frequency</option>
                    <option value="Once daily">Once daily</option>
                    <option value="Twice daily">Twice daily</option>
                    <option value="Three times daily">Three times daily</option>
                    <option value="Four times daily">Four times daily</option>
                    <option value="As needed">As needed</option>
                  </select>
                  {medicines.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMedicine(index)}
                      className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-xs flex items-center justify-center gap-1"
                    >
                      <FiX /> Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="flex space-x-2">
              <button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-1.5 rounded-md transition-colors text-sm"
              >
                Add Checkup Data
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-1.5 rounded-md transition-colors text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-3 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">
            Ongoing Checkups ({patients.length})
          </h2>
        </div>

        {patients.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <FiHeart className="text-3xl mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No ongoing checkups found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Patient Name</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Age</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Gender</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Blood Group</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {patients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 whitespace-nowrap text-xs font-medium text-gray-900">#{patient.id}</td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <div className="flex items-center">
                        <FiUser className="text-gray-400 mr-1 text-xs" />
                        <span className="text-xs font-medium text-gray-900">{patient.patient_name}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">{patient.age}y</td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">{patient.gender}</td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        {patient.blood_group}
                      </span>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs font-medium">
                      <div className="flex space-x-1">
                        <button
                          onClick={() => handleAddCheckupData(patient)}
                          className="text-blue-600 hover:text-blue-900 p-1 rounded text-xs"
                          title="Add Checkup Data"
                        >
                          <FiActivity />
                        </button>
                        <button
                          onClick={() => handleCompleteCheckup(patient.id)}
                          className="text-green-600 hover:text-green-900 p-1 rounded text-xs"
                          title="Complete Checkup"
                        >
                          <FiCheck />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientCheckup;
