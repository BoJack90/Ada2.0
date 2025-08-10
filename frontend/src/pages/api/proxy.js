export default async function handler(req, res) {
  // In Docker environment, use the service name
  const baseUrl = 'http://web:8000';
  
  try {
    // Extract the path after /api/proxy
    const proxyPath = req.url.replace('/api/proxy', '') || '/';
    const targetUrl = `${baseUrl}${proxyPath}`;
    
    console.log(`[Proxy] ${req.method} ${req.url} -> ${targetUrl}`);
    
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        ...req.headers,
        host: 'web:8000',
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined,
    });

    const data = await response.text();
    
    res.status(response.status);
    
    // Copy headers from the backend response
    response.headers.forEach((value, key) => {
      res.setHeader(key, value);
    });
    
    res.send(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Proxy error', details: error.message });
  }
}
