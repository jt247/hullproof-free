export default function handler(req, res) { switch (req.method) { case 'GET': return res.end('a'); case 'DELETE': return res.end('b') } }
