import { useEffect, useState } from "react";

export default function Home() {
  const [emails, setEmails] = useState([]);

  async function fetchEmails() {
    const res = await fetch("http://localhost:8000/emails");
    setEmails(await res.json());
  }

  async function processEmails() {
    await fetch("http://localhost:8000/process_all", { method: "POST" });
    fetchEmails();
  }

  useEffect(() => {
    fetchEmails();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>AI Email Assistant Dashboard</h1>
      <button onClick={processEmails}>Process Emails</button>
      <ul>
        {emails.map((e) => (
          <li key={e.id}>
            <b>{e.subject}</b> ({e.priority}) → {e.sentiment}
            <p>{e.draft_reply}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
