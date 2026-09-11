import { useEffect, useMemo, useState, useCallback } from 'react'
import Navbar from '../components/Navbar.jsx'
import { API_BASE_URL } from '../config.js'

export default function Admin(){
	console.log('Admin component rendering...') // Debug log
	
	const [summary, setSummary] = useState(null)
	const [error, setError] = useState('')
	const [success, setSuccess] = useState('')
	const [filter, setFilter] = useState('')
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		console.log('Admin component mounted') // Debug log
	}, [])

	const fmt = (iso)=>{
		try{
			const d = new Date(iso)
			const pad=(n)=> String(n).padStart(2,'0')
			return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
		}catch{return iso}
	}

	const fetchDashboardData = useCallback(async () => {
		console.log('Fetching admin dashboard data...') // Debug log
		setLoading(true)
		setError('')
		try {
			const res = await fetch(`${API_BASE_URL}/api/admin/dashboard`, { credentials:'include' })
			console.log('Admin response status:', res.status) // Debug log
			console.log('Admin response headers:', res.headers) // Debug log
			
			const contentType = res.headers.get('content-type') || ''
			console.log('Content type:', contentType) // Debug log
			
			if(!contentType.includes('application/json')){
				const text = await res.text(); 
				console.log('Non-JSON response:', text) // Debug log
				throw new Error(text || `HTTP ${res.status}`)
			}
			const data = await res.json();
			console.log('Admin dashboard data:', data) // Debug log
			if(!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
			setSummary(data)
		} catch (e) {
			console.error('Admin dashboard error:', e) // Debug log
			if (e.message.includes('403') || e.message.includes('Admin access required')) {
				setError('Access denied. You need admin privileges to view this page.')
			} else {
				setError(e.message)
			}
		} finally {
			setLoading(false)
		}
	}, [])

	useEffect(() => {
		fetchDashboardData()
	}, [fetchDashboardData])

	const updateUserRole = useCallback(async (userId, newRole) => {
		try {
			const res = await fetch(`${API_BASE_URL}/admin/user/${userId}/role`, { 
				method:'POST', 
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ role: newRole }),
				credentials:'include' 
			})
			const data = await res.json()
			if(!res.ok){ throw new Error(data.error || `HTTP ${res.status}`) }
			
			// Update the user list with the new role
			setSummary(s => !s ? s : { ...s, all_users: s.all_users.map(u => u.id === userId ? { ...u, role: newRole } : u) })
			setSuccess(data.message || `Role updated successfully for user ${userId}`)
			setError('')
			
			// Refresh the dashboard data to ensure consistency
			setTimeout(() => {
				fetchDashboardData()
			}, 1000)
		} catch (error) {
			console.error('Role update error:', error)
			setError(`Failed to update role: ${error.message}`)
			setSuccess('')
		}
	}, [fetchDashboardData])

	const filteredRuns = useMemo(()=>{
		if(!summary) return []
		return (summary.recent_runs || []).filter(r => (r.dataset_id || '—').toString().toLowerCase().includes(filter.toLowerCase()))
	}, [summary, filter])

	return (
		<div>
			<Navbar />
			<div className="container py-3">
			<h3 className="mb-3 d-flex align-items-center justify-content-between">
				Admin dashboard 
				<div>
					<button className="btn btn-outline-primary btn-sm me-2" onClick={fetchDashboardData} disabled={loading}>
						<i className="fas fa-sync-alt"></i> Refresh
					</button>
					<button className="btn btn-outline-secondary btn-sm" onClick={()=>window.history.back()}>Back</button>
				</div>
			</h3>
			{error && <div className="alert alert-danger">{error}</div>}
			{success && <div className="alert alert-success">{success}</div>}
			{loading && <div className="text-center py-5"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div>}
			{!loading && summary && (
				<>
					<div className="row g-3">
						<div className="col-md-3">
							<div className="card p-3 kpi d-flex align-items-center gap-3">
								<div className="icon" style={{width:40,height:40,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:10,background:'#eef2ff',color:'#2563eb'}}><i className="fas fa-users"></i></div>
								<div><div className="text-muted">Users</div><div className="h4 mb-0">{summary.users || 0}</div></div>
							</div>
						</div>
						<div className="col-md-3">
							<div className="card p-3 kpi d-flex align-items-center gap-3">
								<div className="icon" style={{width:40,height:40,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:10,background:'#eef2ff',color:'#2563eb'}}><i className="fas fa-database"></i></div>
								<div><div className="text-muted">Datasets</div><div className="h4 mb-0">{summary.datasets || 0}</div></div>
							</div>
						</div>
						<div className="col-md-3">
							<div className="card p-3 kpi d-flex align-items-center gap-3">
								<div className="icon" style={{width:40,height:40,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:10,background:'#eef2ff',color:'#2563eb'}}><i className="fas fa-cog"></i></div>
								<div><div className="text-muted">Runs</div><div className="h4 mb-0">{summary.runs || 0}</div></div>
							</div>
						</div>
						<div className="col-md-3">
							<div className="card p-3 kpi d-flex align-items-center gap-3">
								<div className="icon" style={{width:40,height:40,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:10,background:'#eef2ff',color:'#2563eb'}}><i className="fas fa-file-pdf"></i></div>
								<div><div className="text-muted">Reports</div><div className="h4 mb-0">{summary.reports || 0}</div></div>
							</div>
						</div>
					</div>

					<div className="row g-3 mt-1">
						<div className="col-lg-6">
							<div className="card p-3">
								<h5 className="mb-3">Latest uploads</h5>
								<div className="table-responsive">
									<table className="table table-striped table-hover align-middle">
										<thead>
											<tr><th>File</th><th>Rows</th><th>Cols</th><th>Owner</th><th>Uploaded</th></tr>
										</thead>
										<tbody>
											{(summary.latest_datasets||[]).map((d)=>(
												<tr key={d.id}>
													<td>{d.filename}</td>
													<td>{d.rows || '—'}</td>
													<td>{d.columns || '—'}</td>
													<td>
														<span className="text-muted">{d.owner || '—'}</span>
													</td>
													<td><span className="badge bg-light text-dark">{fmt(d.uploaded_at)}</span></td>
												</tr>
											))}
										</tbody>
									</table>
								</div>
							</div>
						</div>
						<div className="col-lg-6">
							<div className="card p-3">
								<div className="d-flex justify-content-between align-items-center mb-3">
									<h5 className="mb-0">Recent runs</h5>
									<input className="form-control form-control-sm" style={{maxWidth:220}} placeholder="Filter by dataset" value={filter} onChange={(e)=>setFilter(e.target.value)} />
								</div>
								<div className="table-responsive">
									<table className="table table-striped table-hover align-middle">
										<thead>
											<tr><th>Dataset</th><th>User</th><th>Success</th><th>Plots</th><th>Time</th></tr>
										</thead>
										<tbody>
											{filteredRuns.map((r)=>(
												<tr key={r.id}>
													<td>Dataset #{r.dataset_id || '—'}</td>
													<td>
														<span className="text-muted">User #{r.user_id || '—'}</span>
													</td>
													<td><span className={`badge ${r.success ? 'bg-success':'bg-danger'}`}>{r.success ? 'ok' : 'fail'}</span></td>
													<td>{r.plots_count || 0}</td>
													<td><span className="badge bg-light text-dark">{fmt(r.created_at)}</span></td>
												</tr>
											))}
										</tbody>
									</table>
								</div>
							</div>
						</div>
					</div>

					<div className="card p-3 mt-3">
						<h5 className="mb-2">User management</h5>
						<div className="table-responsive">
							<table className="table table-striped table-hover align-middle">
								<thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Action</th></tr></thead>
								<tbody>
									{(summary.all_users || []).map(u => (
										<tr key={u.id}>
											<td>{u.username}</td>
											<td>{u.email || '—'}</td>
											<td><span className={`badge ${u.role==='admin' ? 'bg-warning text-dark' : 'bg-secondary'}`}>{u.role}</span></td>
											<td>
												<div className="d-flex gap-2">
													<select className="form-select form-select-sm" style={{maxWidth:140}} value={u.role} onChange={(e)=> updateUserRole(u.id, e.target.value)}>
														<option value="user">user</option>
														<option value="admin">admin</option>
													</select>
												</div>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</div>
				</>
			)}
			</div>
		</div>
	)
}



