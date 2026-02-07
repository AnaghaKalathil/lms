import { useLocation, useNavigate } from "react-router-dom";


export default function TemplateCodePreview() {
const { state } = useLocation();
const navigate = useNavigate();


if (!state) return <p>No template data</p>;


const { mjml, html } = state;


return (
<div style={styles.page}>
<header style={styles.header}>
<h2>Template Code Preview</h2>
<button onClick={() => navigate(-1)} style={styles.back}>
← Back
</button>
</header>


<div style={styles.grid}>
<div style={styles.box}>
<h3>MJML</h3>
<pre style={styles.code}>{mjml}</pre>
</div>


<div style={styles.box}>
<h3>Responsive HTML</h3>
<pre style={styles.code}>{html}</pre>
</div>
</div>
</div>
);
}


const styles = {
page: {
minHeight: "100vh",
background: "#020617",
color: "#e5e7eb",
padding: 24,
},
header: {
display: "flex",
justifyContent: "space-between",
marginBottom: 16,
},
back: {
background: "#334155",
color: "white",
border: "none",
padding: "8px 12px",
borderRadius: 6,
cursor: "pointer",
},
grid: {
display: "grid",
gridTemplateColumns: "1fr 1fr",
gap: 16,
height: "calc(100vh - 100px)",
},
box: {
background: "#020617",
border: "1px solid #1e293b",
borderRadius: 8,
padding: 12,
display: "flex",
flexDirection: "column",
},
code: {
flex: 1,
background: "#020617",
color: "#38bdf8",
overflow: "auto",
fontSize: 13,
whiteSpace: "pre-wrap",
},
};