import { createMcpHandler } from 'mcp-handler'
export const POST = async (req: Request) => { const body = await req.json(); if (body.method === 'tools/call') return new Response('x'); return new Response('y') }
