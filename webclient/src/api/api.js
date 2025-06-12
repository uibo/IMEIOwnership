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
    if (!res.ok) throw new Error('조회 실패')
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

export async function store_trade_info(payload) {
    const res = await fetch('http://localhost:8000/tradeinfo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('판매 등록 실패')
    return await res.json()
}

export async function get_trades_by_buyer(payload) {
    const res = await fetch('http://localhost:8000/tradeinfo/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('진행중인 거래 불러오기 실패')
    return await res.json()
}

export async function match_buyerInfo(payload) {
    const res = await fetch('http://localhost:8000/buyerinfo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('거래 진행 실패')
    return await res.json()
}

export async function confirm_trade(payload) {
    const res = await fetch('http://localhost:8000/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('거래 확정 실패')
    return await res.json()
}
