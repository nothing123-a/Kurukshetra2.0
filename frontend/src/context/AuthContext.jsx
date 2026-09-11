import { createContext, useCallback, useEffect, useState } from 'react'
import { API_BASE_URL } from '../config.js'

// Create context outside component to avoid react-refresh issues
const AuthContext = createContext({ user:null, authenticated:false, refresh:()=>{}, login:async()=>{}, logout:async()=>{} })

export function AuthProvider({ children }){
	const [user, setUser] = useState(null)

	const refresh = useCallback(async ()=>{
		try{
const res = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials:'include' })
			const data = await res.json()
			if(res.ok && data.is_authenticated){ setUser(data.user) } else { setUser(null) }
		}catch{ setUser(null) }
	}, [])

	useEffect(()=>{ refresh() }, [refresh])

	const login = useCallback(async (username, password)=>{
		const res = await fetch(`${API_BASE_URL}/api/auth/login`, { method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'}, body: JSON.stringify({ username, password }), credentials:'include' })
		const contentType = res.headers.get('content-type') || ''
		if(contentType.includes('application/json')){
			const data = await res.json()
			if(!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`)
		} else if(!res.ok){
			const text = await res.text(); throw new Error(text || `HTTP ${res.status}`)
		}
		await refresh(); return true
	}, [refresh])

	const logout = useCallback(async ()=>{
		await fetch(`${API_BASE_URL}/api/auth/logout`, { method: 'POST', credentials:'include' }); await refresh()
	}, [refresh])

	return (
		<AuthContext.Provider value={{ user, authenticated: !!user, refresh, login, logout }}>
			{children}
		</AuthContext.Provider>
	)
}

export { AuthContext }
