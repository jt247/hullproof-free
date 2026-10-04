// server actions for items
'use server'
import { db } from './db'
export async function createItem(form: FormData) { return db.insert(form) }
export const removeItem = async (id: string) => db.delete(id)
export async function renameItem(id: string, name: string) { return db.update(id, name) }
