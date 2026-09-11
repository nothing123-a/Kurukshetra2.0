import React, { useState, useEffect } from 'react';
import { FiDownload, FiFileText, FiUser, FiActivity } from 'react-icons/fi';

const PatientRecords = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/patients', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data.patients);
      }
    } catch (error) {
      console.error('Error fetching patients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/patients/export', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `patients_data_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to download CSV');
      }
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert('Failed to download CSV');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 p-4">
        <div className="flex items-center justify-center h-32">
          <div className="text-sm text-gray-600">Loading patient records...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 p-4">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FiFileText className="text-xl text-purple-600" />
            <h1 className="text-lg font-bold text-gray-800">Patient Records</h1>
          </div>
          <button
            onClick={handleDownloadCSV}
            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md flex items-center space-x-1 transition-colors text-sm"
          >
            <FiDownload className="text-sm" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div className="bg-white rounded-lg shadow-md p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-600">Total Patients</p>
              <p className="text-xl font-bold text-blue-600">{patients.length}</p>
            </div>
            <FiUser className="text-lg text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-600">Ongoing Checkups</p>
              <p className="text-xl font-bold text-green-600">
                {patients.filter(p => p.checkup_status === 'ongoing').length}
              </p>
            </div>
            <FiActivity className="text-lg text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-600">Completed Checkups</p>
              <p className="text-xl font-bold text-purple-600">
                {patients.filter(p => p.checkup_status === 'done').length}
              </p>
            </div>
            <FiFileText className="text-lg text-purple-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-600">No Checkups</p>
              <p className="text-xl font-bold text-gray-600">
                {patients.filter(p => p.checkup_status === 'none').length}
              </p>
            </div>
            <FiUser className="text-lg text-gray-500" />
          </div>
        </div>
      </div>

      {/* Patient Records Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-3 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">
            All Patient Records ({patients.length})
          </h2>
        </div>

        {patients.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <FiFileText className="text-3xl mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No patient records found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    ID
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Patient Name
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Age
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Gender
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Blood Group
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Weight
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Height
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Checkup Status
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Registration Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {patients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 whitespace-nowrap text-xs font-medium text-gray-900">
                      #{patient.id}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <div className="flex items-center">
                        <FiUser className="text-gray-400 mr-1 text-xs" />
                        <span className="text-xs font-medium text-gray-900">
                          {patient.patient_name}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {patient.age}y
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {patient.gender}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        {patient.blood_group}
                      </span>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {patient.weight}kg
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {patient.height}cm
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                        patient.checkup_status === 'ongoing' ? 'bg-yellow-100 text-yellow-800' :
                        patient.checkup_status === 'done' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {patient.checkup_status === 'none' ? 'No Checkup' : 
                         patient.checkup_status === 'ongoing' ? 'Ongoing' : 'Completed'}
                      </span>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                      {new Date(patient.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Download Info */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start space-x-2">
          <FiDownload className="text-blue-600 mt-0.5 text-sm" />
          <div>
            <h3 className="text-sm font-medium text-blue-800">CSV Export Information</h3>
            <p className="text-xs text-blue-700 mt-1">
              The CSV file includes all patient data with their basic information, checkup status, 
              and any associated medical records including oxygen levels, blood pressure, diseases, 
              medicines, dosages, and frequencies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientRecords;