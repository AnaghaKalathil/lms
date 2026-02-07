import { useState } from "react";
import CreateContentEditor from "./CreateContentEditor";

export default function CreateCampaignPage() {
  const [step, setStep] = useState("setup"); // setup | content | review

  const [campaign, setCampaign] = useState({
    name: "",
    subject: "",
    emailGroup: "",
    content: [], // block-based content
  });

  const updateField = (e) => {
    setCampaign({ ...campaign, [e.target.name]: e.target.value });
  };

  /* ---------------- SETUP STEP ---------------- */
  if (step === "setup") {
    return (
      <div style={styles.page}>
        <div style={styles.card}>
          <h2>Create Campaign</h2>

          <label>Campaign Name</label>
          <input
            name="name"
            value={campaign.name}
            onChange={updateField}
            placeholder="Spring Sale Campaign"
            style={styles.input}
          />

          <label>Email Subject</label>
          <input
            name="subject"
            value={campaign.subject}
            onChange={updateField}
            placeholder="Big discounts inside"
            style={styles.input}
          />

          <label>Email Group</label>
          <input
            name="emailGroup"
            value={campaign.emailGroup}
            onChange={updateField}
            placeholder="Newsletter Subscribers"
            style={styles.input}
          />

          <div style={styles.actionsRight}>
            <button
              style={styles.primary}
              disabled={!campaign.name || !campaign.subject}
              onClick={() => setStep("content")}
            >
              Save & Create Content
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ---------------- CONTENT STEP ---------------- */
  if (step === "content") {
    return (
      <div style={styles.page}>
        <div style={styles.cardWide}>
          {/* <h2>Create Email Content</h2>

          {campaign.content.length === 0 ? (
            <div style={styles.emptyState}>
              <h3>No content added yet</h3>
              <p>Add text or images to build your email</p>
              <button
                style={styles.primary}
                onClick={() => setCampaign({ ...campaign, content: [] })}
              >
                Create Content
              </button>
            </div>
          ) : null} */}

          <CreateContentEditor
            value={campaign.content}
            onChange={(blocks) =>
              setCampaign({ ...campaign, content: blocks })
            }
          />

          <div style={styles.actionsBetween}>
            <button
              style={styles.secondary}
              onClick={() => setStep("setup")}
            >
              Back
            </button>
            <button
              style={styles.primary}
              disabled={campaign.content.length === 0}
              onClick={() => setStep("review")}
            >
              Review Campaign
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ---------------- REVIEW STEP ---------------- */
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h2>Review Campaign</h2>

        <p><strong>Name:</strong> {campaign.name}</p>
        <p><strong>Subject:</strong> {campaign.subject}</p>
        <p><strong>Email Group:</strong> {campaign.emailGroup}</p>

        <h4>Content Blocks</h4>
        <pre style={styles.preview}>
          {JSON.stringify(campaign.content, null, 2)}
        </pre>

        <div style={styles.actionsBetween}>
          <button
            style={styles.secondary}
            onClick={() => setStep("content")}
          >
            Back
          </button>
          <button
            style={styles.primary}
            onClick={() => {
              console.log("FINAL CAMPAIGN PAYLOAD", campaign);
              alert("Campaign created (check console)");
            }}
          >
            Create Campaign
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------------- STYLES ---------------- */

const styles = {
  page: {
  minHeight: "100vh",
  background: "#f1f5f9",
  display: "flex",
  flexDirection: "column",
},

card: {
  background: "white",
  width: "100%",
  maxWidth: "900px",
  margin: "40px auto",
  padding: 32,
  borderRadius: 14,
  boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
},

cardWide: {
  background: "white",
  width: "100%",
  height: "100%",
  padding: 0,
  borderRadius: 0,
  boxShadow: "none",
},

  input: {
    width: "100%",
    padding: 10,
    marginBottom: 16,
    borderRadius: 6,
    border: "1px solid #ccc",
  },
  emptyState: {
    border: "1px dashed #cbd5f5",
    padding: 40,
    textAlign: "center",
    borderRadius: 10,
    background: "#f8fafc",
    marginBottom: 20,
  },
  actionsRight: {
    display: "flex",
    justifyContent: "flex-end",
    marginTop: 20,
  },
  actionsBetween: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: 24,
  },
  primary: {
    background: "#2563eb",
    color: "white",
    border: "none",
    padding: "10px 16px",
    borderRadius: 8,
    cursor: "pointer",
  },
  secondary: {
    background: "#e5e7eb",
    border: "none",
    padding: "10px 16px",
    borderRadius: 8,
    cursor: "pointer",
  },
  preview: {
    background: "#f3f4f6",
    padding: 12,
    borderRadius: 6,
    maxHeight: 200,
    overflow: "auto",
    fontSize: 12,
  },
};
