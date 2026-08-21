import { app } from "../../scripts/app.js";

const NODE_NAME = "PadImageForOutpaintingColor";
const HEX_WIDGET = "color";

function normalizeHex(v) {
    let s = String(v ?? "").trim().replace(/^#/, "");
    if (/^[0-9a-f]{3}$/i.test(s)) s = s.split("").map((c) => c + c).join("");
    if (!/^[0-9a-f]{6}$/i.test(s)) return null;
    return "#" + s.toUpperCase();
}

app.registerExtension({
    name: "Comfy.PadImageForOutpaintingColor.ColorPicker",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const ret = onNodeCreated?.apply(this, arguments);

            const hexWidget = this.widgets?.find((w) => w.name === HEX_WIDGET);
            if (!hexWidget) return ret;

            // --- DOM element: native color input + live hex label ---
            const wrap = document.createElement("div");
            Object.assign(wrap.style, {
                display: "flex",
                alignItems: "center",
                gap: "8px",
                width: "100%",
                height: "100%",
                boxSizing: "border-box",
                padding: "2px 6px",
            });

            const input = document.createElement("input");
            input.type = "color";
            Object.assign(input.style, {
                flex: "0 0 auto",
                width: "44px",
                height: "22px",
                padding: "0",
                border: "1px solid #555",
                borderRadius: "4px",
                background: "transparent",
                cursor: "pointer",
            });

            const label = document.createElement("span");
            Object.assign(label.style, {
                fontFamily: "monospace",
                fontSize: "12px",
                color: "#ddd",
                userSelect: "text",
            });

            wrap.appendChild(input);
            wrap.appendChild(label);

            const syncFromHex = () => {
                const n = normalizeHex(hexWidget.value);
                if (n) {
                    input.value = n;
                    label.textContent = n;
                    label.style.color = "#ddd";
                } else {
                    label.textContent = (hexWidget.value || "") + " (ungültig)";
                    label.style.color = "#e66";
                }
            };

            // picker -> hex field
            input.addEventListener("input", () => {
                hexWidget.value = input.value.toUpperCase();
                label.textContent = hexWidget.value;
                label.style.color = "#ddd";
                this.setDirtyCanvas(true, true);
            });

            // hex field -> picker
            const origCallback = hexWidget.callback;
            hexWidget.callback = function (value) {
                const n = normalizeHex(value);
                if (n && n !== value) hexWidget.value = n;
                syncFromHex();
                return origCallback?.apply(this, arguments);
            };

            const domWidget = this.addDOMWidget("color_picker", "COLOR_PICKER", wrap, {
                serialize: false,
                hideOnZoom: false,
                getMinHeight: () => 30,
                getMaxHeight: () => 30,
            });

            // place the picker directly below the hex field
            const widgets = this.widgets;
            const from = widgets.indexOf(domWidget);
            const to = widgets.indexOf(hexWidget) + 1;
            if (from > -1 && to > -1 && from !== to) {
                widgets.splice(from, 1);
                widgets.splice(to, 0, domWidget);
            }

            syncFromHex();
            this.setSize(this.computeSize());
            return ret;
        };

        // keep picker in sync when a workflow is loaded
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const ret = onConfigure?.apply(this, arguments);
            const hexWidget = this.widgets?.find((w) => w.name === HEX_WIDGET);
            hexWidget?.callback?.(hexWidget.value);
            return ret;
        };
    },
});
