import { useState } from "react";
import { getCSRFToken } from "./utils/csrf";

/* ================= TEXT TOOLBAR ================= */

function TextToolbar({ visible }) {
  if (!visible) return null;

  const cmd = (c, v = null) => document.execCommand(c, false, v);

  return (
    <div style={styles.textToolbar}>
      <button onMouseDown={() => cmd("bold")}>B</button>
      <button onMouseDown={() => cmd("italic")}>I</button>
      <button onMouseDown={() => cmd("underline")}>U</button>

      <select onChange={(e) => cmd("fontSize", e.target.value)}>
        <option>Size</option>
        <option value="2">Small</option>
        <option value="3">Normal</option>
        <option value="5">Large</option>
        <option value="7">XL</option>
      </select>

      <input type="color" onChange={(e) => cmd("foreColor", e.target.value)} />

      <button onMouseDown={() => cmd("justifyLeft")}>L</button>
      <button onMouseDown={() => cmd("justifyCenter")}>C</button>
      <button onMouseDown={() => cmd("justifyRight")}>R</button>
    </div>
  );
}

/* ================= MAIN EDITOR ================= */

export default function CreateContentEditor({ value = [], onChange }) {
  const [rows, setRows] = useState(value);
  const [dragItem, setDragItem] = useState(null);
  const [activeText, setActiveText] = useState(false);
  const [view, setView] = useState("split");

  const [codeView, setCodeView] = useState(null);
  const [generatedMJML, setGeneratedMJML] = useState("");
  const [generatedHTML, setGeneratedHTML] = useState("");

  const update = (next) => {
    setRows(next);
    onChange?.(next);
  };

  /* ================= DRAG ================= */

  const dragFromPalette = (type, meta) => setDragItem({ type, meta });

  const dropOnCanvas = (r = null, c = null) => {
    if (!dragItem) return;
    const copy = structuredClone(rows);

    if (dragItem.type === "row") {
      copy.push({
        id: Date.now(),
        columns: Array.from({ length: dragItem.meta }).map(() => ({
          id: Math.random(),
          blocks: [],
        })),
      });
    }

    if (dragItem.type === "text") {
      copy[r].columns[c].blocks.push({
        id: Math.random(),
        type: "text",
        html: "<p>Edit text</p>",
      });
    }

    if (dragItem.type === "image") {
      copy[r].columns[c].blocks.push({
        id: Math.random(),
        type: "image",
        src: "",
        width: 100,
      });
    }

    setDragItem(null);
    update(copy);
  };

  /* ================= DELETE ================= */

  const deleteRow = (r) => {
    const copy = structuredClone(rows);
    copy.splice(r, 1);
    update(copy);
  };

  const deleteColumn = (r, c) => {
    const copy = structuredClone(rows);
    copy[r].columns.splice(c, 1);
    update(copy);
  };

  const deleteBlock = (r, c, b) => {
    const copy = structuredClone(rows);
    copy[r].columns[c].blocks.splice(b, 1);
    update(copy);
  };

  /* ================= IMAGE ================= */

  const uploadImage = (r, c, b, file) => {
    const reader = new FileReader();
    reader.onload = () => {
      const copy = structuredClone(rows);
      copy[r].columns[c].blocks[b].src = reader.result;
      update(copy);
    };
    reader.readAsDataURL(file);
  };
/*==================Save as template============*/
// Helper: read CSRF token from cookies
// function getCsrfToken() {
//   const match = document.cookie.match(/(^| )csrftoken=([^;]+)/);
//   return match ? match[2] : "";
// }



const handleSaveTemplate = async () => {
  const templateName = prompt("Enter Template Name");
  if (!templateName) {
    alert("Template name is required");
    return;
  }

  if (!generatedHTML) {
    alert("Please generate HTML first");
    return;
  }

  let htmlSource = generatedHTML;
const csrfToken = await getCSRFToken();
  if (!csrfToken) {
    alert("Please login to Frappe first");
    return;
  }
  try {
    // 1️⃣ Upload all base64 images to Frappe
    const base64Regex = /<img[^>]+src="(data:image\/[^"]+)"/g;
    let match;

    while ((match = base64Regex.exec(htmlSource)) !== null) {
      const base64Image = match[1];

      // Prepare FormData for upload
      const formData = new FormData();
      formData.append("file", base64Image.split(",")[1]); // remove "data:image/png;base64,"
      formData.append("file_name", `email_image_${Date.now()}.png`);
      formData.append("doctype", "Email Template");
      formData.append("docname", templateName);
      formData.append("decode", "true"); // tell Frappe to decode base64

      const res = await fetch("http://development.localhost:8000/api/method/upload_file", {
        method: "POST",
        body: formData,
        credentials: "include", // send cookies for authentication
        headers: {
          "Content-Type": "application/json",
    "X-Frappe-CSRF-Token": csrfToken
          // "X-Frappe-CSRF-Token": getCsrfToken(),
        },
      });

      const data = await res.json();

      if (!data.message || !data.message.file_url) {
        alert("Image upload failed");
        return;
      }

      const fileUrl = data.message.file_url;

      // Replace base64 in HTML with hosted URL
      htmlSource = htmlSource.replace(base64Image, fileUrl);
    }

    // 2️⃣ Save Email Template (HTML ONLY)
    const saveRes = await fetch(
      "http://development.localhost:8000/api/method/legal_management.email_template_front_end.create_from_frontend",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
    "X-Frappe-CSRF-Token": csrfToken
          // "Content-Type": "application/json",
          // "X-Frappe-CSRF-Token": getCsrfToken(),
        },
        body: JSON.stringify({
          template_name: templateName,
          html: htmlSource, // 🔥 Only HTML
        }),
        credentials: "include",
      }
    );

    const saveData = await saveRes.json();

    if (saveData.message) {
      alert(`Email Template "${templateName}" created successfully!`);
    } else {
      alert("Failed to create template");
      console.error(saveData);
    }
  } catch (err) {
    console.error(err);
    alert("Server error while saving template");
  }
};


function base64ToBlob(base64) {
  const [meta, data] = base64.split(",");
  const mime = meta.match(/:(.*?);/)[1];
  const bytes = atob(data);
  const arr = new Uint8Array(bytes.length);

  for (let i = 0; i < bytes.length; i++) {
    arr[i] = bytes.charCodeAt(i);
  }

  return new Blob([arr], { type: mime });
}



  /* ================= MJML ================= */

  const generateMJMLFromRows = () => {
    return `
<mjml>
  <mj-body background-color="#ffffff">
    ${rows
      .map(
        (row) => `
      <mj-section>
        ${row.columns
          .map(
            (col) => `
          <mj-column>
            ${col.blocks
              .map((b) =>
                b.type === "text"
                  ? `<mj-text>${b.html}</mj-text>`
                  : `<mj-image src="${b.src}" width="${b.width}%" />`
              )
              .join("")}
          </mj-column>
        `
          )
          .join("")}
      </mj-section>
    `
      )
      .join("")}
  </mj-body>
</mjml>
`.trim();
  };

  const handleGenerateMJML = () => {
    setGeneratedMJML(generateMJMLFromRows());
    setCodeView("mjml");
  };

  const handleGenerateHTML = () => {
    setGeneratedHTML(`
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0">
${rows
  .map((row) =>
    row.columns
      .map((col) =>
        col.blocks
          .map((b) =>
            b.type === "text"
              ? b.html
              : `<img src="${b.src}" style="width:${b.width}%;" />`
          )
          .join("")
      )
      .join("")
  )
  .join("")}
</body>
</html>
`.trim());
    setCodeView("html");
  };

  /* ================= RENDER ================= */

  return (
    <div style={styles.wrapper}>
      <header style={styles.topbar}>
        <strong>Email Content Builder</strong>
        <div style={styles.topActions}>
          <button onClick={() => setView("design")}>Design</button>
          <button onClick={() => setView("preview")}>Preview</button>
          <button onClick={() => setView("split")}>Split</button>
          <button onClick={handleGenerateMJML}>Generate MJML</button>
          <button onClick={handleGenerateHTML}>Generate HTML</button>
          <button onClick={handleSaveTemplate} style={styles.genBtn}>Save as Email Template</button>
        </div>
      </header>

      <div style={styles.editor}>
        {view !== "preview" && (
          <aside style={styles.sidebar}>
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                draggable
                onDragStart={() => dragFromPalette("row", n)}
                style={styles.paletteItem}
              >
                ➕ {n} Column Row
              </div>
            ))}
            <hr />
            <div draggable onDragStart={() => dragFromPalette("text")} style={styles.paletteItem}>
              📝 Text
            </div>
            <div draggable onDragStart={() => dragFromPalette("image")} style={styles.paletteItem}>
              🖼 Image
            </div>
          </aside>
        )}

        {view !== "preview" && (
          <main
            style={styles.canvas}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => dropOnCanvas()}
          >
            <TextToolbar visible={activeText} />

            {rows.map((row, r) => (
              <div key={row.id} style={styles.row}>
                <div style={styles.rowHeader}>
                  <span>Row</span>
                  <button onClick={() => deleteRow(r)}>🗑 Row</button>
                </div>

                <div style={styles.columns}>
                  {row.columns.map((col, c) => (
                    <div
                      key={col.id}
                      style={styles.column}
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={() => dropOnCanvas(r, c)}
                    >
                      <div style={styles.columnHeader}>
                        <span>Column</span>
                        <button onClick={() => deleteColumn(r, c)}>🗑</button>
                      </div>

                      {col.blocks.map((block, b) => (
                        <div key={block.id} style={styles.block}>
                          <button
                            style={styles.blockDelete}
                            onClick={() => deleteBlock(r, c, b)}
                          >
                            ✕
                          </button>

                          {block.type === "text" && (
                            <div
                              contentEditable
                              dangerouslySetInnerHTML={{ __html: block.html }}
                              onFocus={() => setActiveText(true)}
                              onBlur={(e) => {
                                setActiveText(false);
                                const copy = structuredClone(rows);
                                copy[r].columns[c].blocks[b].html =
                                  e.target.innerHTML;
                                update(copy);
                              }}
                            />
                          )}

                          {block.type === "image" && (
  <>
    {block.src ? (
      <>
        <img
          src={block.src || null} // <-- pass null if empty
          alt=""
          style={{ ...styles.image, width: `${block.width}%` }}
        />
        <input
          type="range"
          min="20"
          max="100"
          value={block.width}
          onChange={(e) => {
            block.width = e.target.value;
            update([...rows]);
          }}
        />
      </>
    ) : (
      <input
        type="file"
        accept="image/*"
        onChange={(e) =>
          uploadImage(r, c, b, e.target.files[0])
        }
      />
    )}
  </>
)}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </main>
        )}

        {view !== "design" && (
          <aside style={styles.preview}>
            <div style={styles.email}>
              {rows.map((row) =>
                row.columns.map((col) =>
                  col.blocks.map((b) =>
                    b.type === "text" ? (
                      <div dangerouslySetInnerHTML={{ __html: b.html }} />
                    ) : (
                      <img src={b.src} style={{ width: `${b.width}%` }} />
                    )
                  )
                )
              )}
            </div>
          </aside>
        )}
      </div>

      {codeView && (
        <div style={styles.codePanel}>
          <pre>{codeView === "mjml" ? generatedMJML : generatedHTML}</pre>
          <button onClick={() => setCodeView(null)}>Close</button>
        </div>
      )}
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  wrapper: { height: "100vh", display: "flex", flexDirection: "column" },
  topbar: { background: "#fff", padding: 12, display: "flex", justifyContent: "space-between" },
  topActions: { display: "flex", gap: 8 },
  editor: { flex: 1, display: "flex", background: "#f1f5f9" },
  sidebar: { width: 220, padding: 12, background: "#fff" },
  paletteItem: { padding: 10, border: "1px dashed #cbd5f5", marginBottom: 8, cursor: "grab" },
  canvas: { flex: 1, padding: 30 },
  row: { background: "#fff", padding: 12, marginBottom: 20 },
  rowHeader: { display: "flex", justifyContent: "space-between", marginBottom: 8 },
  columns: { display: "flex", gap: 12 },
  column: { flex: 1, background: "#f8fafc", padding: 10 },
  columnHeader: { display: "flex", justifyContent: "space-between", marginBottom: 6 },
  block: { background: "#fff", padding: 10, marginBottom: 8, position: "relative" },
  blockDelete: { position: "absolute", top: 4, right: 4 },
  preview: { width: "40%", padding: 20, background: "#e5e7eb" },
  email: { background: "#fff", padding: 20 },
  codePanel: { background: "#000", color: "#0f0", padding: 20, height: 300, overflow: "auto" },
  textToolbar: { background: "#fff", padding: 6, marginBottom: 10 },
};
