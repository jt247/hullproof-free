import { generateText, tool } from 'ai'
export async function run(prompt: string) {
  return generateText({ model, prompt, tools: { lookup: tool({ description: 'x', execute: async () => 1 }) } })
}
