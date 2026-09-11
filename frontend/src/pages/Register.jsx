import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { API_BASE_URL } from '../config.js'
import { FiUserPlus, FiUser, FiMail, FiKey, FiArrowLeft, FiHome, FiHash, FiUsers } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Register() {
	const [formData, setFormData] = useState({
		username: '', email: '', password: '', confirmPassword: '',
		role: 'researcher', organization: '', organizationType: '', licenseNumber: '',
		hospitalId: '', hospitalName: '', hospitalEmail: '', country: ''
	})
	const [error, setError] = useState('')
	const [loading, setLoading] = useState(false)
	const navigate = useNavigate()

	useEffect(() => {
		fetch(`${API_BASE_URL}/api/auth/me`, { credentials: 'include' })
			.then(res => res.json())
			.then(data => data.is_authenticated && navigate('/'))
			.catch(() => {})
	}, [])

	const handleChange = (field, value) => setFormData(prev => ({ ...prev, [field]: value }))

	const onSubmit = async (e) => {
		e.preventDefault()
		setError('')
		setLoading(true)

		const { username, email, password, confirmPassword, organization, role, hospitalId, hospitalName, hospitalEmail } = formData
		
		// Role-specific validation
		let requiredFields = [password, confirmPassword]
		if (role === 'hospital') {
			requiredFields.push(hospitalId, hospitalName, hospitalEmail, formData.country)
		} else {
			requiredFields.push(username, organization, email)
		}
		
		const validationErrors = [
			requiredFields.some(field => !field?.trim()) ? 'Please fill in all required fields' : null,
			['@gmail.com', '@yahoo.com', '@hotmail.com'].some(domain => 
				(role === 'hospital' ? hospitalEmail : email).endsWith(domain)
			) ? 'Please use your professional/organizational email address' : null,
			password !== confirmPassword ? 'Passwords do not match' : null,
			password.length < 6 ? 'Password must be at least 6 characters long' : null
		].find(Boolean)

		if (validationErrors) {
			setError(validationErrors)
			setLoading(false)
			return
		}

		try {
			// Create separate payloads for different roles
			let payload = {
				role: role,
				password: password
			}

			if (role === 'hospital') {
				payload = {
					...payload,
					hospital_id: hospitalId,
					hospital_name: hospitalName,
					hospital_email: hospitalEmail,
					country: formData.country
				}
			} else {
				payload = {
					...payload,
					username: username,
					email: email,
					organization: organization,
					organization_type: formData.organizationType,
					license_number: formData.licenseNumber
				}
			}

			const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
				credentials: 'include'
			})

			const data = await response.json()
			if (response.ok && data.success) {
				navigate('/')
				window.location.reload()
			} else {
				setError(data.error || 'Registration failed')
			}
		} catch {
			setError('Cannot connect to server. Please make sure the backend is running.')
		} finally {
			setLoading(false)
		}
	}

	const containerStyle = { 
		display: 'flex', 
		alignItems: 'center', 
		justifyContent: 'center', 
		minHeight: '100vh',
		padding: '20px',
		position: 'fixed',
		top: 0,
		left: 0,
		width: '100%',
		background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
	}
	const cardStyle = { background: 'white', borderRadius: '20px', boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)', maxWidth: '500px', width: '100%', overflow: 'hidden' }
	const headerStyle = { background: 'var(--gradient-primary)', color: 'white', padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }
	const inputContainerStyle = { display: 'flex', alignItems: 'center', border: '2px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden', marginBottom: '20px' }
	const iconStyle = { padding: '12px 16px', background: '#f8fafc', borderRight: '2px solid #e2e8f0', color: 'var(--primary-600)' }
	const inputStyle = { flex: 1, padding: '12px 16px', border: 'none', outline: 'none', fontSize: '16px' }

	return (
		<div style={containerStyle}>
			<div style={cardStyle}>
				<div style={headerStyle}>
						<div style={{ position: 'absolute', top: '10px', right: '10px', opacity: 0.1, fontSize: '40px' }}>
							<HiSparkles />
						</div>
						<div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', fontSize: '1.2rem' }}>
							<FiUserPlus size={20} />
							Create Account
						</div>
					<button style={{ background: 'rgba(255, 255, 255, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', color: 'white', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }} onClick={() => navigate(-1)}>
							<FiArrowLeft size={16} />
							Back
						</button>
					</div>
					<div style={{ padding: '32px' }}>
					<p style={{ color: '#1f2937', marginBottom: '24px', textAlign: 'center', fontWeight: '500' }}>Join the clinical trial prediction revolution</p>
					{error && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', padding: '12px', borderRadius: '8px', marginBottom: '20px' }}>{error}</div>}
					<form onSubmit={onSubmit}>
						{/* Role Selection */}
						<div style={inputContainerStyle}>
							<div style={iconStyle}><FiUsers size={18} /></div>
							<select style={{ ...inputStyle, background: 'white' }} value={formData.role} onChange={(e) => handleChange('role', e.target.value)} required>
								<option value="researcher">Researcher</option>
								<option value="hospital">Hospital/Medical Center</option>
								<option value="sponsor">Pharmaceutical Sponsor</option>
							</select>
						</div>

						{/* Conditional Fields Based on Role */}
						{formData.role === 'hospital' ? (
							<>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiHash size={18} /></div>
									<input style={inputStyle} type="text" placeholder="Hospital ID" value={formData.hospitalId} onChange={(e) => handleChange('hospitalId', e.target.value)} required />
								</div>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiHome size={18} /></div>
									<input style={inputStyle} type="text" placeholder="Hospital Name" value={formData.hospitalName} onChange={(e) => handleChange('hospitalName', e.target.value)} required />
								</div>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiMail size={18} /></div>
									<input style={inputStyle} type="email" placeholder="Hospital Email" value={formData.hospitalEmail} onChange={(e) => handleChange('hospitalEmail', e.target.value)} required />
								</div>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiUsers size={18} /></div>
									<select style={{ ...inputStyle, background: 'white' }} value={formData.country} onChange={(e) => handleChange('country', e.target.value)} required>
										<option value="">Select Country</option>
										<option value="United States">United States</option>
										<option value="United Kingdom">United Kingdom</option>
										<option value="Canada">Canada</option>
										<option value="Australia">Australia</option>
										<option value="Germany">Germany</option>
										<option value="France">France</option>
										<option value="India">India</option>
										<option value="China">China</option>
										<option value="Japan">Japan</option>
										<option value="Brazil">Brazil</option>
										<option value="Mexico">Mexico</option>
										<option value="South Africa">South Africa</option>
										<option value="Singapore">Singapore</option>
										<option value="Switzerland">Switzerland</option>
										<option value="Netherlands">Netherlands</option>
										<option value="Sweden">Sweden</option>
										<option value="Spain">Spain</option>
										<option value="Italy">Italy</option>
										<option value="South Korea">South Korea</option>
										<option value="Other">Other</option>
									</select>
								</div>
							</>
						) : (
							<>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiUser size={18} /></div>
									<input style={inputStyle} type="text" placeholder="Username" value={formData.username} onChange={(e) => handleChange('username', e.target.value)} required />
								</div>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiHome size={18} /></div>
									<input style={inputStyle} type="text" placeholder="Organization Name" value={formData.organization} onChange={(e) => handleChange('organization', e.target.value)} required />
								</div>
								<div style={inputContainerStyle}>
									<div style={iconStyle}><FiMail size={18} /></div>
									<input style={inputStyle} type="email" placeholder="Professional Email" value={formData.email} onChange={(e) => handleChange('email', e.target.value)} required />
								</div>
							</>
						)}

						{/* Password Fields */}
						<div style={inputContainerStyle}>
							<div style={iconStyle}><FiKey size={18} /></div>
							<input style={inputStyle} type="password" placeholder="Password" value={formData.password} onChange={(e) => handleChange('password', e.target.value)} required />
						</div>
						<div style={inputContainerStyle}>
							<div style={iconStyle}><FiKey size={18} /></div>
							<input style={inputStyle} type="password" placeholder="Confirm Password" value={formData.confirmPassword} onChange={(e) => handleChange('confirmPassword', e.target.value)} required />
						</div>
						
						<button className="btn-primary" style={{ width: '100%', fontSize: '16px', opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }} type="submit" disabled={loading}>
							{loading ? 'Creating Account...' : 'Create Account'}
						</button>
						</form>
						<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e2e8f0' }}>
							<span style={{ color: '#6b7280', marginRight: '8px' }}>Already have an account?</span>
							<Link to="/login" style={{ color: 'var(--primary-600)', textDecoration: 'none', fontWeight: '500' }}>Sign In</Link>
						</div>
				</div>
			</div>
		</div>
	)
}