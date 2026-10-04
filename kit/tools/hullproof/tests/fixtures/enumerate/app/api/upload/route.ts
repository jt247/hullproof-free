export async function POST(req: Request) { const form = await req.formData(); return Response.json({ n: [...form.keys()].length }) }
