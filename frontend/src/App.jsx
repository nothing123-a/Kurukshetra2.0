import './App.css'
import { Routes, Route, Navigate } from 'react-router-dom'
import { WorkflowProvider } from './context/WorkflowContext.jsx'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import DataCleaning from './pages/DataCleaning.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Profile from './pages/Profile.jsx'
import Admin from './pages/Admin.jsx'
import Upload from './pages/Upload.jsx'
import Summary from './pages/Summary.jsx'
import Configuration from './pages/Configuration.jsx'
import DataAugmentation from './pages/DataAugmentation.jsx'
import PrivacySecurity from './pages/PrivacySecurity.jsx'
import Outliers from './pages/Outliers.jsx'
import Weights from './pages/Weights.jsx'
import Results from './pages/Results.jsx'
import TypoCorrection from './pages/TypoCorrection.jsx'
import Augmentation from './pages/Augmentation.jsx'
import Analytics from './pages/Analytics.jsx'
import DataEncryption from './pages/DataEncryption.jsx'
import History from './pages/History.jsx'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import AdvancedCleaning from './pages/AdvancedCleaning.jsx'
import SyntheticData from './pages/SyntheticData.jsx'
import PrivacyProtection from './pages/PrivacyProtection.jsx'
import AIDataAssistant from './pages/AIDataAssistant.jsx'
import NarayanChatbot from './components/NarayanChatbot.jsx'

function App() {
  return (
    <WorkflowProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ai-assistant" element={<AIDataAssistant />} />
          <Route path="/data-cleaning" element={<DataCleaning />} />
          <Route path="/trial-data" element={<DataCleaning />} />
          <Route path="/dataset" element={<Upload />} />

          <Route path="/analytics" element={<Analytics />} />
          <Route path="/data-encryption" element={<DataEncryption />} />
          <Route path="/history" element={<History />} />
          <Route path="/advanced-cleaning" element={<AdvancedCleaning />} />
          <Route path="/synthetic-data" element={<SyntheticData />} />
          <Route path="/privacy-protection" element={<PrivacyProtection />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/admin" element={<Admin />} />
          
          {/* Workflow Routes */}
          <Route path="/upload" element={<Upload />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/configuration" element={<Configuration />} />
          <Route path="/data-augmentation" element={<DataAugmentation />} />
          <Route path="/privacy-security" element={<PrivacySecurity />} />
          <Route path="/outliers" element={<Outliers />} />
          <Route path="/weights" element={<Weights />} />
          <Route path="/results" element={<Results />} />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
      <NarayanChatbot />
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </WorkflowProvider>
  )
}

export default App
