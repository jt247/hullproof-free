import express from 'express'
import users from './routes/users'
const app = express()
app.use('/users', users)
app.get('/health', (_req, res) => res.send('ok'))
app.listen(3000)
