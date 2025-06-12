export async function register_imei(payload) {
    const res = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('등록 실패')
    return await res.json()
}

export async function get_imei_owner(payload) {
    const res = await fetch('http://localhost:8000/get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('조회 실패패')
    return await res.json()
}

export async function transfer_imei(payload) {
    const res = await fetch('http://localhost:8000/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('전송 실패')
    return await res.json()
}