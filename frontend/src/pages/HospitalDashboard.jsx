import { useState, useEffect } from 'react'
import { 
  FiUsers, FiActivity, FiCalendar, FiHeart, FiClipboard,
  FiFileText, FiBarChart, FiShield, FiTrendingUp, 
  FiCheckCircle, FiClock, FiAlertCircle, FiPlus
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

const hospitalStats = [
  { 
    title: 'Active Patients', 
    value: '1,247', 
    change: '+12%', 
    icon: FiUsers, 
    color: '#3B82F6',
    trend: 'up'
  },
  { 
    title: 'Ongoing Trials', 
    value: '23', 
    change: '+3', 
    icon: FiActivity, 
    color: '#10B981',
    trend: 'up'
  },
  { 
    title: 'Enrollment Rate', 
    value: '87.3%', 
    change: '+5.2%', 
    icon: FiTrendingUp, 
    color: '#8B5CF6',
    trend: 'up'
  },
  { 
    title: 'Appointments Today', 
    value: '34', 
    change: 'Scheduled', 
    icon: FiCalendar, 
    color: '#F59E0B',
    trend: 'up'
  }
]

const recentActivity = [
  {
    type: 'patient_enrollment',
    title: 'New patient enrolled in Trial #NCT-2024-001',
    description: 'Patient ID: P-2024-0847 - Phase III Oncology Trial',
    timestamp: '30 minutes ago',
    status: 'completed',
    icon: FiClipboard
  },
  {
    type: 'appointment',
    title: 'Follow-up appointment completed',
    description: 'Patient monitoring visit - Trial #NCT-2024-003',
    timestamp: '1 hour ago',
    status: 'completed',
    icon: FiCalendar
  },
  {
    type: 'medical_record',
    title: 'Medical records updated',
    description: 'Lab results and vitals recorded for 5 patients',
    timestamp: '2 hours ago',
    status: 'completed',
    icon: FiFileText
  },
  {
    type: 'treatment',
    title: 'Treatment protocol administered',
    description: 'Chemotherapy cycle 3 - Patient P-2024-0823',
    timestamp: '3 hours ago',
    status: 'completed',
    icon: FiHeart
  }
]

const trialStatus = [
  { name: 'Phase III Trials', count: 8, percentage: 35, color: '#3B82F6', status: 'active' },
  { name: 'Phase II Trials', count: 9, percentage: 39, color: '#10B981', status: 'active' },
  { name: 'Phase I Trials', count: 4, percentage: 17, color: '#8B5CF6', status: 'active' },
  { name: 'Observational', count: 2, percentage: 9, color: '#F59E0B', status: 'active' }
]

function getStatusColor(status) {
  switch (status) {
    case 'completed': return '#10B981'
    case 'active': return '#3B82F6'
    case 'pending': return '#F59E0B'
    case 'cancelled': return '#EF4444'
    default: return '#6B7280'
  }
}

export default function HospitalDashboard() {
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 p-3">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-lg p-4 mb-4 text-white relative overflow-hidden">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <FiUsers className="text-xl" />
                <h1 className="text-xl font-bold">
                  Hospital Dashboard
                </h1>
              </div>
              <p className="text-sm opacity-90">
                Manage clinical trials and patient enrollment
              </p>
            </div>
            
            <div className="flex gap-2">
              <button className="flex items-center gap-1 px-3 py-2 bg-white/20 hover:bg-white/30 border border-white/30 rounded-md transition-all duration-200 backdrop-blur-sm text-sm">
                <FiPlus className="text-sm" />
                New Patient
              </button>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          {hospitalStats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg p-3 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <div className="p-2 rounded-md" style={{ backgroundColor: `${stat.color}20` }}>
                  <stat.icon className="text-lg" style={{ color: stat.color }} />
                </div>
                <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${
                  stat.trend === 'up' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {stat.change}
                </span>
              </div>
              <div className="text-xl font-bold text-gray-900 mb-1">
                {stat.value}
              </div>
              <div className="text-gray-600 font-medium text-xs">{stat.title}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-100">
            <div className="p-3 border-b border-gray-100">
              <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                <FiActivity className="text-blue-600 text-sm" />
                Recent Activity
              </h3>
            </div>
            <div className="p-0">
              {recentActivity.slice(0, 3).map((activity, index) => (
                <div key={index} className="flex items-center gap-3 p-3 hover:bg-gray-50 transition-colors duration-200 border-b border-gray-100 last:border-b-0">
                  <div className="p-2 rounded-md" style={{ backgroundColor: `${getStatusColor(activity.status)}20` }}>
                    <activity.icon className="text-sm" style={{ color: getStatusColor(activity.status) }} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1 text-sm">
                      {activity.title}
                    </h4>
                    <p className="text-gray-600 text-xs mb-1">
                      {activity.description}
                    </p>
                    <span className="text-gray-500 text-xs">
                      {activity.timestamp}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trial Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-100">
            <div className="p-3 border-b border-gray-100">
              <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                <FiBarChart className="text-blue-600 text-sm" />
                Active Trials
              </h3>
            </div>
            <div className="p-3">
              {trialStatus.map((trial, index) => (
                <div key={index} className="mb-3 last:mb-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-gray-900 text-sm">
                      {trial.name}
                    </span>
                    <span className="text-gray-600 text-xs">
                      {trial.count}
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{
                      width: `${trial.percentage}%`,
                      backgroundColor: trial.color
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Hospital Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-100">
          <div className="p-3 border-b border-gray-100">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
              <FiClipboard className="text-blue-600 text-sm" />
              Hospital Management
            </h3>
          </div>
          <div className="p-3">
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { icon: FiUsers, title: 'Patient Management', description: 'Manage patient records', color: '#3B82F6', path: '/patient-management' },
                { icon: FiClipboard, title: 'Trial Enrollment', description: 'Enroll patients in trials', color: '#10B981', path: '/trial-enrollment' },
                { icon: FiFileText, title: 'Medical Records', description: 'Access medical records', color: '#8B5CF6', path: '/medical-records' },
                { icon: FiHeart, title: 'Treatment Protocols', description: 'Manage protocols', color: '#F59E0B', path: '/treatment-protocols' },
                { icon: FiCalendar, title: 'Appointments', description: 'Schedule appointments', color: '#EF4444', path: '/appointment-scheduling' },
                { icon: FiShield, title: 'Data Security', description: 'Secure data management', color: '#6B7280', path: '/data-security' }
              ].map((action, index) => (
                <a key={index} href={action.path} className="group flex flex-col items-center gap-2 p-3 bg-gray-50 hover:bg-white border border-gray-200 hover:border-blue-300 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md text-decoration-none">
                  <div className="p-2 rounded-lg transition-all duration-200" style={{ backgroundColor: `${action.color}20` }}>
                    <action.icon className="text-lg" style={{ color: action.color }} />
                  </div>
                  <div className="text-center">
                    <h4 className="font-semibold text-gray-900 mb-1 text-sm">
                      {action.title}
                    </h4>
                    <p className="text-gray-600 text-xs leading-relaxed">
                      {action.description}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Hospital Features */}
        <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-8 border border-green-200">
          <div className="text-center mb-8">
            <FiHeart className="text-4xl text-green-600 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              🏥 Hospital Management Features
            </h3>
            <p className="text-gray-600 max-w-3xl mx-auto">
              Comprehensive hospital management system for clinical trials, patient care, and medical record management.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: FiUsers,
                title: 'Patient Management',
                description: 'Complete patient lifecycle management with enrollment tracking and medical history',
                color: '#3B82F6',
                features: ['Patient Enrollment', 'Medical History', 'Contact Management']
              },
              {
                icon: FiActivity,
                title: 'Clinical Trials',
                description: 'Manage active clinical trials with patient monitoring and protocol compliance',
                color: '#10B981',
                features: ['Trial Management', 'Protocol Compliance', 'Patient Monitoring']
              },
              {
                icon: FiCalendar,
                title: 'Appointment System',
                description: 'Advanced scheduling system for patient appointments and follow-up visits',
                color: '#8B5CF6',
                features: ['Smart Scheduling', 'Automated Reminders', 'Resource Management']
              },
              {
                icon: FiFileText,
                title: 'Medical Records',
                description: 'Secure electronic medical records with HIPAA compliance and audit trails',
                color: '#F59E0B',
                features: ['EMR System', 'HIPAA Compliance', 'Audit Trails']
              },
              {
                icon: FiHeart,
                title: 'Treatment Protocols',
                description: 'Standardized treatment protocols with dosing guidelines and safety monitoring',
                color: '#EF4444',
                features: ['Protocol Management', 'Dosing Guidelines', 'Safety Monitoring']
              },
              {
                icon: FiShield,
                title: 'Data Security',
                description: 'Enterprise-grade security for patient data with encryption and access controls',
                color: '#6B7280',
                features: ['Data Encryption', 'Access Controls', 'Security Monitoring']
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 rounded-lg" style={{ backgroundColor: `${feature.color}20` }}>
                    <feature.icon className="text-2xl" style={{ color: feature.color }} />
                  </div>
                  <h4 className="font-semibold text-gray-900">{feature.title}</h4>
                </div>
                <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                  {feature.description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {feature.features.map((feat, idx) => (
                    <span key={idx} className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                      {feat}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
    </div>
  )
}