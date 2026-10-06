const API_BASE_URL = 'http://localhost:8000'

export async function askRepositoryQuestion({
  repositoryName,
  question,
  topK = 5,
}) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repository_name: repositoryName,
      question,
      top_k: topK,
    }),
  })

  let data

  try {
    data = await response.json()
  } catch {
    throw new Error('The backend returned an invalid response.')
  }

  if (!response.ok) {
    throw new Error(
      data?.detail || 'Unable to get an answer from CodeMind AI.',
    )
  }

  return data
}