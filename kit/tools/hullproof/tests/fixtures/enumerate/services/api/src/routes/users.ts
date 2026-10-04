import { Router } from 'express'
const router = Router()
router.get('/', list)
router.post('/', create)
router.delete('/:id', remove)
router.route('/:id').put(update)
const cache = new Map(); cache.get('a'); headers.get('x-id')
export default router
