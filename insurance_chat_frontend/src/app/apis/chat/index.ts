export const GET = async (query: string) => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat?query=${query}`, {
    headers: {
      Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      'Content-Type': 'text/event-stream',
    },
  });
  const data = await response.json();
  return data;
};
