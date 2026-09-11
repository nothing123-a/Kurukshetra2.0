import { useState, useCallback } from 'react'
import { WorkflowContext } from './WorkflowContext.js'

export const WorkflowProvider = ({ children }) => {
  const [currentStep, setCurrentStep] = useState(1)
  const [datasetId, setDatasetId] = useState(null)
  const [summary, setSummary] = useState(null)
  const [config, setConfig] = useState({
    imputation: { method: 'mean', columns: [], preserve_structure: false, generate_report: false },
    cleaning: { removeDuplicates: false, standardizeText: false, handleOutliers: false, dataValidation: false },
    outliers: { detection_method: 'iqr', handling_method: 'winsorize', columns: [], threshold: 2.0, replacement_value: '' },
    weights: { column: '', normalization: 'none' },
    estimation: { 
      confidence_level: 0.95, 
      bootstrap_samples: 1000, 
      finite_population_correction: false, 
      stratification: false 
    },
    advanced: {
      generate_variance_estimates: false,
      design_effects: false
    },
    estimate_columns: [],
    estimation_methods: ['mean'],
    confidence_level: 0.95,
    bootstrap_method: 'percentile',
    bootstrap_samples: 1000,
    quality_checks: {
      check_duplicates: false,
      validate_types: false,
      check_outliers: false,
      generate_report: false
    }
  })
  const [results, setResults] = useState(null)
  const [toasts, setToasts] = useState([])

  const notify = useCallback((type, message) => {
    const id = Math.random().toString(36).slice(2)
    setToasts((t) => [...t, { id, type, message }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3000)
  }, [])

  const nextStep = useCallback(() => {
    setCurrentStep(prev => Math.min(prev + 1, 6))
  }, [])

  const prevStep = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 1))
  }, [])

  const goToStep = useCallback((step) => {
    setCurrentStep(Math.max(1, Math.min(step, 6)))
  }, [])

  const resetWorkflow = useCallback(() => {
    setCurrentStep(1)
    setDatasetId(null)
    setSummary(null)
    setConfig({
      imputation: { method: 'mean', columns: [], preserve_structure: false, generate_report: false },
      cleaning: { removeDuplicates: false, standardizeText: false, handleOutliers: false, dataValidation: false },
      outliers: { detection_method: 'iqr', handling_method: 'winsorize', columns: [], threshold: 2.0, replacement_value: '' },
      weights: { column: '', normalization: 'none' },
      estimation: { 
        confidence_level: 0.95, 
        bootstrap_samples: 1000, 
        finite_population_correction: false, 
        stratification: false 
      },
      advanced: {
        generate_variance_estimates: false,
        design_effects: false
      },
      estimate_columns: [],
      estimation_methods: ['mean'],
      confidence_level: 0.95,
      bootstrap_method: 'percentile',
      bootstrap_samples: 1000,
      quality_checks: {
        check_duplicates: false,
        validate_types: false,
        check_outliers: false,
        generate_report: false
      }
    })
    setResults(null)
  }, [])

  const value = {
    currentStep,
    setCurrentStep,
    datasetId,
    setDatasetId,
    summary,
    setSummary,
    config,
    setConfig,
    results,
    setResults,
    toasts,
    notify,
    nextStep,
    prevStep,
    goToStep,
    resetWorkflow
  }

  return (
    <WorkflowContext.Provider value={value}>
      {children}
    </WorkflowContext.Provider>
  )
}
