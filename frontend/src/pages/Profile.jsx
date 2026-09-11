import { useEffect, useState } from 'react'

import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { API_BASE_URL } from '../config.js'
import { FiUser, FiMail, FiLock, FiCamera, FiArrowLeft, FiShield, FiPhone, FiMapPin, FiBriefcase, FiCalendar } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Profile(){
	const [username, setUsername] = useState('')
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [phone, setPhone] = useState('')
	const [address, setAddress] = useState('')
	const [company, setCompany] = useState('')
	const [role, setRole] = useState('user')
	const [joinDate, setJoinDate] = useState('')
	const [avatarFile, setAvatarFile] = useState(null)
	const [avatarUrl, setAvatarUrl] = useState('')
	const [error, setError] = useState('')
	const [success, setSuccess] = useState('')
    const navigate = useNavigate()
    const { refresh } = useAuth()

    // Load current user to prefill
    useEffect(()=>{
        (async ()=>{
            try{
                const res = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials:'include' })
                const data = await res.json()
                if(!res.ok || !data.is_authenticated){
                    navigate('/login')
                    return
                }
                setUsername(data.user.username || '')
                setEmail(data.user.email || '')
                setPhone(data.user.phone || '')
                setAddress(data.user.address || '')
                setCompany(data.user.company || '')
                setRole(data.user.role || 'user')
                setJoinDate(data.user.created_at || '')
                setAvatarUrl(data.user.profile_image || '')
            }catch{
                setError('Failed to load profile')
            }
        })()
    }, [navigate])

	async function onSubmit(e){
		e.preventDefault()
		setError(''); setSuccess('')
		try{
			// Handle avatar upload separately if needed
			if(avatarFile) {
				const avatarForm = new FormData()
				avatarForm.append('avatar', avatarFile)
				const avatarRes = await fetch(`${API_BASE_URL}/api/auth/avatar`, { method:'POST', body: avatarForm, credentials:'include' })
				if(!avatarRes.ok){
					const text = await avatarRes.text(); throw new Error(text || `HTTP ${avatarRes.status}`)
				}
			}
			
			// Update profile data
			const res = await fetch(`${API_BASE_URL}/api/auth/profile`, { 
				method:'POST', 
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, email, password, phone, address, company }),
				credentials:'include' 
			})
			const data = await res.json()
			if(!res.ok){
				throw new Error(data.error || `HTTP ${res.status}`)
			}
			setSuccess('Profile updated')
			setPassword('')
            try{
                await refresh()
                const resMe = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials:'include' })
                const dataMe = await resMe.json()
                if(resMe.ok && dataMe.is_authenticated){
                    setUsername(dataMe.user.username || '')
                    setEmail(dataMe.user.email || '')
                    setPhone(dataMe.user.phone || '')
                    setAddress(dataMe.user.address || '')
                    setCompany(dataMe.user.company || '')
                    setRole(dataMe.user.role || 'user')
                    setAvatarUrl(dataMe.user.profile_image || '')
                }
            }catch{
                // Continue if refresh fails
            }
		}catch(err){ setError(err.message) }
	}

	return (
		<div className="page-container">
			<div className="fade-in-up">
				<div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
					<div className="main-container">
						{/* Header */}
						<div style={{
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'space-between',
							marginBottom: '32px',
							padding: '24px',
							background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
							color: 'white',
							borderRadius: '16px',
							position: 'relative',
							overflow: 'hidden'
						}}>
							<div style={{ position: 'absolute', top: '10px', right: '10px', opacity: 0.1, fontSize: '60px' }}>
								<HiSparkles />
							</div>
							<div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
								<FiUser size={24} />
								<h2 style={{ margin: 0, fontSize: '1.8rem', fontWeight: '700' }}>Edit Profile</h2>
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
								onClick={()=>window.history.back()}
							>
								<FiArrowLeft size={16} />
								Back
							</button>
						</div>

						{/* Alerts */}
						{error && (
							<div style={{
								background: '#fef2f2',
								border: '1px solid #fecaca',
								color: '#dc2626',
								padding: '16px',
								borderRadius: '12px',
								marginBottom: '24px'
							}}>
								{error}
							</div>
						)}
						{success && (
							<div style={{
								background: '#f0fdf4',
								border: '1px solid #bbf7d0',
								color: '#166534',
								padding: '16px',
								borderRadius: '12px',
								marginBottom: '24px'
							}}>
								{success}
							</div>
						)}

						{/* User Role Display */}
						<div className="card" style={{ marginBottom: '24px', background: role === 'admin' ? 'linear-gradient(135deg, #dc2626, #ef4444)' : 'linear-gradient(135deg, #3b82f6, #06b6d4)', color: 'white' }}>
							<div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
								<FiShield size={24} />
								<div>
									<h3 style={{ margin: 0, fontSize: '1.2rem' }}>Account Role: {role.toUpperCase()}</h3>
									<p style={{ margin: '4px 0 0 0', opacity: 0.9 }}>Member since: {new Date(joinDate).toLocaleDateString()}</p>
								</div>
							</div>
						</div>

						{/* Form */}
						<form onSubmit={onSubmit}>
							{/* Profile Picture */}
							<div className="card" style={{ marginBottom: '20px' }}>
								<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
									<FiCamera style={{ color: '#3b82f6', fontSize: '20px' }} />
									<h4 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '600' }}>Profile Picture</h4>
								</div>
								<div style={{ textAlign: 'center', marginBottom: '16px' }}>
									<div style={{ width: '120px', height: '120px', margin: '0 auto', position: 'relative' }}>
										{avatarUrl ? (
											<img src={avatarUrl} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%', border: '4px solid #3b82f6' }} />
										) : (
											<div style={{ width: '100%', height: '100%', borderRadius: '50%', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid #3b82f6' }}>
												<FiUser size={40} color="#6b7280" />
											</div>
										)}
									</div>
								</div>
								<input type="file" accept="image/*" onChange={(e)=> setAvatarFile(e.target.files?.[0] || null)} className="form-input" />
							</div>

							<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
								{/* Username */}
								<div className="card">
									<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
										<FiUser style={{ color: '#3b82f6', fontSize: '20px' }} />
										<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>Username</label>
									</div>
									<input value={username} onChange={(e)=>setUsername(e.target.value)} required className="form-input" />
								</div>

								{/* Email */}
								<div className="card">
									<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
										<FiMail style={{ color: '#3b82f6', fontSize: '20px' }} />
										<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>Email</label>
									</div>
									<input type="email" value={email} onChange={(e)=>setEmail(e.target.value)} className="form-input" />
								</div>

								{/* Phone */}
								<div className="card">
									<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
										<FiPhone style={{ color: '#3b82f6', fontSize: '20px' }} />
										<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>Phone</label>
									</div>
									<input type="tel" value={phone} onChange={(e)=>setPhone(e.target.value)} className="form-input" placeholder="+1 (555) 123-4567" />
								</div>

								{/* Company */}
								<div className="card">
									<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
										<FiBriefcase style={{ color: '#3b82f6', fontSize: '20px' }} />
										<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>Company</label>
									</div>
									<input value={company} onChange={(e)=>setCompany(e.target.value)} className="form-input" placeholder="Your Company" />
								</div>

								{/* Password */}
								<div className="card">
									<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
										<FiLock style={{ color: '#3b82f6', fontSize: '20px' }} />
										<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>New Password</label>
									</div>
									<input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} className="form-input" placeholder="Leave blank to keep current" />
								</div>
							</div>

							{/* Address */}
							<div className="card" style={{ marginTop: '20px' }}>
								<div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
									<FiMapPin style={{ color: '#3b82f6', fontSize: '20px' }} />
									<label style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>Address</label>
								</div>
								<textarea value={address} onChange={(e)=>setAddress(e.target.value)} className="form-input" rows="3" placeholder="Your full address" style={{ resize: 'vertical', minHeight: '80px' }} />
							</div>

							{/* Submit Button */}
							<div style={{ textAlign: 'center', marginTop: '32px' }}>
								<button className="btn btn-primary btn-lg" style={{ padding: '16px 48px', fontSize: '1.1rem', fontWeight: '600' }}>
									<FiUser size={20} style={{ marginRight: '8px' }} />
									Save Profile Changes
								</button>
							</div>
						</form>
					</div>
				</div>
			</div>

			<style jsx="true">{`
				.form-input {
					width: 100%;
					padding: 12px 16px;
					border: 2px solid #e2e8f0;
					border-radius: 8px;
					outline: none;
					font-size: 16px;
					transition: all 0.3s ease;
					box-sizing: border-box;
				}
				.form-input:focus {
					border-color: #3b82f6;
					box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
				}
				.card {
					background: white;
					border-radius: 12px;
					padding: 24px;
					box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
					border: 1px solid #e5e7eb;
					transition: all 0.3s ease;
				}
				.card:hover {
					transform: translateY(-2px);
					box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
				}
			`}</style>
		</div>
	)
}



