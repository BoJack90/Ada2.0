import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.DOCKER_ENV === 'true' 
  ? 'http://web:8000' 
  : 'http://localhost:8090';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'PATCH');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  try {
    const path = pathSegments.join('/');
    const url = `${API_BASE_URL}/api/${path}`;
    
    // Get search params from the original request
    const searchParams = request.nextUrl.searchParams.toString();
    const fullUrl = searchParams ? `${url}?${searchParams}` : url;
    
    // Get headers from the original request
    const headers: HeadersInit = {};
    request.headers.forEach((value, key) => {
      // Skip host header to avoid conflicts
      if (key.toLowerCase() !== 'host') {
        headers[key] = value;
      }
    });
    
    // Get body for POST/PUT/PATCH requests
    let body: string | undefined;
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      body = await request.text();
    }
    
    console.log(`[API Proxy] ${method} ${fullUrl}`);
    console.log(`[API Proxy] Headers:`, headers);
    console.log(`[API Proxy] Body:`, body);
    
    const response = await fetch(fullUrl, {
      method,
      headers,
      body,
    });
    
    // Get response data
    const responseText = await response.text();
    console.log(`[API Proxy] Response status: ${response.status}`);
    console.log(`[API Proxy] Response text:`, responseText);
    
    // Return the response
    return new NextResponse(responseText, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error(`[API Proxy] Error:`, error);
    return NextResponse.json(
      { error: 'Internal Server Error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
