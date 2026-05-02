export function HighlightedText({ text, phrases = [] }) {
  const realPhrases = phrases.filter((phrase) => text.toLowerCase().includes(phrase.toLowerCase()));
  if (!realPhrases.length) {
    return <p className="message-text">{text}</p>;
  }

  const pattern = new RegExp(`(${realPhrases.map(escapeRegex).join("|")})`, "gi");
  const parts = text.split(pattern);

  return (
    <p className="message-text">
      {parts.map((part, index) => {
        const suspicious = realPhrases.some((phrase) => phrase.toLowerCase() === part.toLowerCase());
        return suspicious ? <mark key={`${part}-${index}`}>{part}</mark> : <span key={`${part}-${index}`}>{part}</span>;
      })}
    </p>
  );
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
