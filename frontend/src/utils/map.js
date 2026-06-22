let bmapLoading = null

const BAIDU_MAP_AK = import.meta.env.VITE_BAIDU_MAP_AK || ''

export function hasBMapKey() {
  return !!BAIDU_MAP_AK && BAIDU_MAP_AK !== 'your_baidu_map_ak_here'
}

export function loadBMap() {
  if (typeof BMap !== 'undefined') return Promise.resolve(BMap)
  if (bmapLoading) return bmapLoading

  if (!hasBMapKey()) {
    return Promise.reject(new Error('Baidu Maps API key not configured. Set VITE_BAIDU_MAP_AK in .env'))
  }

  bmapLoading = new Promise((resolve, reject) => {
    const callbackName = '__baidu_map_callback_' + Date.now()
    window[callbackName] = () => {
      delete window[callbackName]
      resolve(BMap)
    }

    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=3.0&ak=${BAIDU_MAP_AK}&callback=${callbackName}`
    script.async = true
    script.onerror = () => {
      delete window[callbackName]
      bmapLoading = null
      reject(new Error('Baidu Maps JSAPI script failed to load'))
    }
    document.head.appendChild(script)
  })

  return bmapLoading
}

// Day colors for polylines
export const DAY_COLORS = {
  0: '#1677ff', // Day 1 - Blue
  1: '#fa8c16', // Day 2 - Orange
  2: '#722ed1', // Day 3 - Purple
  3: '#52c41a', // Day 4 - Green
  4: '#f5222d', // Day 5 - Red
}

// POI type icons
export const POI_ICONS = {
  scenic: '🏔️',
  restaurant: '🍽️',
  hotel: '🏨',
  gas_station: '⛽',
  parking: '🅿️',
  attraction: '🎯',
  default: '📍',
}

// POI marker colors
export const POI_COLORS = {
  scenic: '#52c41a',
  restaurant: '#fa8c16',
  hotel: '#1677ff',
  gas_station: '#f5222d',
  parking: '#722ed1',
  attraction: '#eb2f96',
  default: '#8c8c8c',
}

export function createMarkerContent(poi) {
  const color = POI_COLORS[poi.type] || POI_COLORS.default
  const icon = POI_ICONS[poi.type] || POI_ICONS.default
  return `<div class="custom-poi-marker" style="
    background: ${color};
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    border: 2px solid white;
    cursor: pointer;
  ">${icon}</div>`
}

export function createStartMarkerContent() {
  return `<div style="
    background: #52c41a;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    white-space: nowrap;
  ">🚩 起点</div>`
}

export function createEndMarkerContent() {
  return `<div style="
    background: #f5222d;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    white-space: nowrap;
  ">🏁 终点</div>`
}

export function createInfoWindowContent(poi) {
  const stars = '★'.repeat(Math.round(poi.rating || 0)) + '☆'.repeat(5 - Math.round(poi.rating || 0))
  return `
    <div style="min-width: 220px; max-width: 300px; padding: 0;">
      ${poi.image ? `<img src="${poi.image}" alt="${poi.name}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px 8px 0 0;" />` : ''}
      <div style="padding: 10px;">
        <h4 style="margin: 0 0 6px; font-size: 14px; font-weight: 600;">${poi.name}</h4>
        ${poi.rating ? `<div style="color: #fa8c16; font-size: 13px; margin-bottom: 4px;">${stars} ${poi.rating}</div>` : ''}
        ${poi.price ? `<div style="color: #f5222d; font-size: 13px; margin-bottom: 4px;">💰 ¥${poi.price}</div>` : ''}
        ${poi.duration ? `<div style="color: #8c8c8c; font-size: 12px; margin-bottom: 4px;">⏱ ${poi.duration}</div>` : ''}
        ${poi.description ? `<p style="margin: 6px 0 0; font-size: 12px; color: #666; line-height: 1.5;">${poi.description}</p>` : ''}
        ${poi.address ? `<div style="margin-top: 6px; font-size: 11px; color: #999;">📍 ${poi.address}</div>` : ''}
      </div>
    </div>
  `
}

// Decode coordinates from backend format — returns [lng, lat]
export function parseLngLat(coord) {
  if (!coord) return null
  if (Array.isArray(coord)) return coord
  if (typeof coord === 'object' && coord.lng !== undefined && coord.lat !== undefined) {
    return [coord.lng, coord.lat]
  }
  return null
}

// Helper to create a BMap.Point from [lng, lat]
export function toBPoint(lnglat) {
  if (!lnglat) return null
  if (Array.isArray(lnglat) && lnglat.length >= 2) {
    return new BMap.Point(lnglat[0], lnglat[1])
  }
  return null
}
