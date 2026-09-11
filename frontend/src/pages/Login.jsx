import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'

import { API_BASE_URL } from '../config.js'
import { FiLock, FiUser, FiKey, FiArrowLeft, FiEye, FiEyeOff, FiUsers, FiHash } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Login(){
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [role, setRole] = useState('researcher')
	const [error, setError] = useState('')
	const [loading, setLoading] = useState(false)
	const [showPassword, setShowPassword] = useState(false)
	const navigate = useNavigate()

	// Check if already authenticated
	useEffect(() => {
		checkAuthStatus()
	}, [])

	const checkAuthStatus = async () => {
		try {
			const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
				credentials: 'include'
			})
			const data = await response.json()
			
			if (data.is_authenticated) {
				navigate('/')
			}
		} catch (error) {
			console.error('Auth check failed:', error)
		}
	}

	async function onSubmit(e) {
		e.preventDefault()
		setError('')
		setLoading(true)

		if (!username.trim() || !password) {
			setError('Please enter both username and password')
			setLoading(false)
			return
		}

		try {
			const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password, role }),
				credentials: 'include'
			})

			const data = await response.json()

			if (response.ok && data.success) {
				// Login successful, redirect based on role
				if (data.user.role === 'admin') {
					navigate('/admin')
				} else {
					navigate('/')
				}
				// Trigger navbar refresh by reloading
				window.location.reload()
			} else {
				setError(data.error || 'Login failed')
			}
		} catch (err) {
			setError('Cannot connect to server. Please make sure the backend is running.')
			console.error('Login error:', err)
		} finally {
			setLoading(false)
		}
	}

	return (
			<div style={{ 
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
			}}>
				<div style={{
					background: 'white',
					borderRadius: '20px',
					boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
					maxWidth: '460px',
					width: '100%',
					overflow: 'hidden'
				}}>
					<div style={{
						background: 'var(--gradient-primary)',
						color: 'white',
						padding: '24px',
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'space-between',
						position: 'relative'
					}}>
						<div style={{ position: 'absolute', top: '10px', right: '10px', opacity: 0.1, fontSize: '40px' }}>
							<HiSparkles />
						</div>
						<div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', fontSize: '1.2rem' }}>
							<FiLock size={20} />
							Sign In
						</div>
						<button 
							style={{
								background: 'rgba(255, 255, 255, 0.2)',
								border: '1px solid rgba(255, 255, 255, 0.3)',
								color: 'white',
								padding: '8px 16px',
								borderRadius: '8px',
								cursor: 'pointer',
								display: 'flex',
								alignItems: 'center',
								gap: '4px'
							}} 
							onClick={()=>navigate(-1)}
						>
							<FiArrowLeft size={16} />
							Back
						</button>
					</div>
					<div style={{ padding: '32px' }}>
						<p style={{ color: '#1f2937', marginBottom: '24px', textAlign: 'center', fontWeight: '500' }}>
							Access your AI data pipeline workspace
						</p>
						{error && (
							<div style={{
								background: '#fef2f2',
								border: '1px solid #fecaca',
								color: '#dc2626',
								padding: '12px',
								borderRadius: '8px',
								marginBottom: '20px'
							}}>
								{error}
							</div>
						)}
						<form onSubmit={onSubmit}>
							<div style={{ marginBottom: '20px' }}>
								<div style={{
									display: 'flex',
									alignItems: 'center',
									border: '2px solid #e2e8f0',
									borderRadius: '12px',
									overflow: 'hidden',
									transition: 'border-color 0.2s ease'
								}}>
									<div style={{
										padding: '12px 16px',
										background: '#f8fafc',
										borderRight: '2px solid #e2e8f0',
										color: 'var(--secondary-color)'
									}}>
										{role === 'hospital' ? <FiHash size={18} /> : <FiUser size={18} />}
									</div>
									<input 
										style={{
											flex: 1,
											padding: '12px 16px',
											border: 'none',
											outline: 'none',
											fontSize: '16px'
										}}
										placeholder={role === 'hospital' ? 'Hospital ID' : 'Username'} 
										value={username} 
										onChange={(e)=>setUsername(e.target.value)} 
										required 
									/>
								</div>
							</div>
							<div style={{ marginBottom: '24px' }}>
								<div style={{
									display: 'flex',
									alignItems: 'center',
									border: '2px solid #e2e8f0',
									borderRadius: '12px',
									overflow: 'hidden'
								}}>
									<div style={{
										padding: '12px 16px',
										background: '#f8fafc',
										borderRight: '2px solid #e2e8f0',
										color: 'var(--secondary-color)'
									}}>
										<FiKey size={18} />
									</div>
									<input 
										style={{
											flex: 1,
											padding: '12px 16px',
											border: 'none',
											outline: 'none',
											fontSize: '16px'
										}}
										type="password" 
										placeholder="Password" 
										value={password} 
										onChange={(e)=>setPassword(e.target.value)} 
										required 
									/>
								</div>
							</div>
							<div style={{ marginBottom: '20px' }}>
								<div style={{
									display: 'flex',
									alignItems: 'center',
									border: '2px solid #e2e8f0',
									borderRadius: '12px',
									overflow: 'hidden'
								}}>
									<div style={{
										padding: '12px 16px',
										background: '#f8fafc',
										borderRight: '2px solid #e2e8f0',
										color: 'var(--secondary-color)'
									}}>
										<FiUsers size={18} />
									</div>
									<select 
										style={{
											flex: 1,
											padding: '12px 16px',
											border: 'none',
											outline: 'none',
											fontSize: '16px',
											background: 'white'
										}}
										value={role} 
										onChange={(e)=>setRole(e.target.value)} 
										required
									>
										<option value="researcher">Researcher</option>
										<option value="hospital">Hospital</option>
										<option value="sponsor">Sponsor</option>
									</select>
								</div>
							</div>
							<button 
								className="btn-primary" 
								style={{ 
									width: '100%', 
									fontSize: '16px',
									opacity: loading ? 0.7 : 1,
									cursor: loading ? 'not-allowed' : 'pointer'
								}} 
								type="submit"
								disabled={loading}
							>
								{loading ? 'Signing In...' : 'Sign In'}
							</button>
						</form>
						<div style={{ 
							display: 'flex', 
							justifyContent: 'space-between', 
							alignItems: 'center', 
							marginTop: '24px',
							paddingTop: '24px',
							borderTop: '1px solid #e2e8f0'
						}}>
							<Link 
								to="/register" 
								style={{ 
									color: 'var(--secondary-color)', 
									textDecoration: 'none',
									fontWeight: '500'
								}}
							>
								Create account
							</Link>
							<Link 
								to="/admin" 
								style={{
									background: 'var(--warning-color)',
									color: 'white',
									padding: '8px 16px',
									borderRadius: '8px',
									textDecoration: 'none',
									fontWeight: '500',
									fontSize: '14px'
								}}
							>
								Admin
							</Link>
						</div>
					</div>
				</div>
			</div>
	)
}



