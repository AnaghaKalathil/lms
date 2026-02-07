export function generateMJML(blocks, options = {}) {
return `
<mjml>
<mj-head>
<mj-preview>${options.previewText || "Email preview"}</mj-preview>
<mj-attributes>
<mj-text font-family="Arial" />
</mj-attributes>
</mj-head>


<mj-body background-color="#ffffff">
${blocks.map(blockToMJML).join("\n")}
</mj-body>
</mjml>`;
}


function blockToMJML(block) {
if (block.type === "text") {
return `
<mj-section>
<mj-column>
<mj-text font-size="16px">${block.value}</mj-text>
</mj-column>
</mj-section>`;
}


if (block.type === "image") {
return `
<mj-section>
<mj-column>
<mj-image src="${block.src}" />
</mj-column>
</mj-section>`;
}


return "";
}