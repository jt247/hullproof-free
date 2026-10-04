export async function preview(url: string) { return fetch(url) }
export async function fixed() { return fetch('https://api.example.com/v1') }
export async function viaAxios(u: string) { return axios.get(u) }
