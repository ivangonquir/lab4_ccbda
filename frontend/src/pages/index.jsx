import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL;

const emptyForm = {
  name: "",
  email: "",
};

function Home() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  const totalCount = items.length;
  const latest = useMemo(() => {
    if (items.length === 0) return null;
    return items[items.length - 1];
  }, [items]);

  async function loadItems() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/`);
      if (!response.ok) {
        throw new Error(`Fetch failed with ${response.status}`);
      }
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError("Unable to load items. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadItems();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("");
    setError("");

    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
    };

    if (!payload.name || !payload.email) {
      setError("Name and email are required.");
      return;
    }

    try {
      const response = await fetch(
        editingId ? `${API_BASE}/${editingId}` : `${API_BASE}/`,
        {
          method: editingId ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        const message = detail?.detail || `Request failed with ${response.status}`;
        throw new Error(message);
      }

      setStatus(editingId ? "Item updated." : "Item created.");
      setForm(emptyForm);
      setEditingId(null);
      await loadItems();
    } catch (err) {
      setError(err.message || "Save failed.");
    }
  }

  async function handleDelete(itemId) {
    setStatus("");
    setError("");
    try {
      const response = await fetch(`${API_BASE}/${itemId}`, {
        method: "DELETE",
      });
      if (!response.ok && response.status !== 204) {
        throw new Error(`Delete failed with ${response.status}`);
      }
      setStatus("Item deleted.");
      if (editingId === itemId) {
        setEditingId(null);
        setForm(emptyForm);
      }
      await loadItems();
    } catch (err) {
      setError(err.message || "Delete failed.");
    }
  }

  function handleEdit(item) {
    setEditingId(item.id);
    setForm({ name: item.name, email: item.email });
    setStatus("");
    setError("");
  }

  function handleCancel() {
    setEditingId(null);
    setForm(emptyForm);
    setStatus("");
    setError("");
  }

  return (
    <div className="app">
      <div className="background">
        <div className="orb orb-one" />
        <div className="orb orb-two" />
        <div className="grid" />
      </div>

      <header className="hero">
        <p className="eyebrow">FastAPI + Next.js</p>
        <h1>CCBDA CRUD Console</h1>
        <p className="subtitle">
          A workspace for managing names and emails.
        </p>
        <div className="hero-meta">
          <div>
            <span className="meta-label">API</span>
            <span className="meta-value">{API_BASE}</span>
          </div>
          <div>
            <span className="meta-label">Total Items</span>
            <span className="meta-value">{totalCount}</span>
          </div>
          <div>
            <span className="meta-label">Latest Entry</span>
            <span className="meta-value">
              {latest ? latest.name : "No entries yet"}
            </span>
          </div>
        </div>
      </header>

      <main className="content">
        <section className="panel form-panel">
          <h2>{editingId ? "Edit item" : "Create item"}</h2>
          <p className="panel-note">
            {editingId
              ? "Update the details and save to the API."
              : "Fill the form to create a new record."}
          </p>
          <form onSubmit={handleSubmit} className="form">
            <label>
              Name
              <input
                type="text"
                placeholder="Jane Doe"
                value={form.name}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, name: event.target.value }))
                }
              />
            </label>
            <label>
              Email
              <input
                type="email"
                placeholder="jane@example.com"
                value={form.email}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, email: event.target.value }))
                }
              />
            </label>
            <div className="form-actions">
              <button type="submit" className="primary">
                {editingId ? "Save changes" : "Create"}
              </button>
              {editingId ? (
                <button type="button" className="ghost" onClick={handleCancel}>
                  Cancel
                </button>
              ) : null}
            </div>
          </form>
          {status ? <div className="status success">{status}</div> : null}
          {error ? <div className="status error">{error}</div> : null}
        </section>

        <section className="panel list-panel">
          <div className="panel-header">
            <h2>Items</h2>
            <button className="ghost" onClick={loadItems} disabled={loading}>
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
          <div className="list">
            {loading ? (
              <div className="empty">Loading items...</div>
            ) : items.length === 0 ? (
              <div className="empty">No items yet. Create your first one.</div>
            ) : (
              items.map((item) => (
                <article key={item.id} className="list-item">
                  <div>
                    <p className="item-title">{item.name}</p>
                    <p className="item-sub">{item.email}</p>
                  </div>
                  <div className="item-actions">
                    <button className="ghost" onClick={() => handleEdit(item)}>
                      Edit
                    </button>
                    <button
                      className="danger"
                      onClick={() => handleDelete(item.id)}
                    >
                      Delete
                    </button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>
          Frontend powered by Next.js. Backend powered by FastAPI.
        </p>
      </footer>
    </div>
  );
}

export default dynamic(() => Promise.resolve(Home), { ssr: false });
