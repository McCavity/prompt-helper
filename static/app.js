document.addEventListener("DOMContentLoaded", function () {
    // Live preview on builder page
    var fields = {
        expertise: document.getElementById("field-expertise"),
        task: document.getElementById("field-task"),
        context: document.getElementById("field-context"),
        constraints: document.getElementById("field-constraints"),
    };
    var output = document.getElementById("preview-output");

    if (fields.expertise && output) {
        var placeholder = output.getAttribute("data-placeholder") || "";

        function updatePreview() {
            var e = fields.expertise.value.trim();
            var t = fields.task.value.trim();
            var c = fields.context.value.trim();
            var cn = fields.constraints.value.trim();

            if (!e && !t && !c) {
                output.textContent = placeholder;
                return;
            }

            var parts = [];
            if (e) parts.push("You are a top 0.1% expert in " + e + ".");
            if (t) parts.push("TASK: " + t);
            if (c) parts.push("CONTEXT: " + c);
            if (cn) parts.push("CONSTRAINTS: " + cn);
            parts.push(
                "Ask me clarifying questions one at a time until you are at least " +
                "95% confident that you can successfully finish the task."
            );
            output.textContent = parts.join("\n\n");
        }

        Object.values(fields).forEach(function (field) {
            if (field) field.addEventListener("input", updatePreview);
        });
        updatePreview();
    }

    // Copy to clipboard with translated labels
    function copyText(text, button) {
        var labelCopy = button.getAttribute("data-label-copy") || "Copy";
        var labelCopied = button.getAttribute("data-label-copied") || "Copied!";
        navigator.clipboard.writeText(text).then(function () {
            button.textContent = labelCopied;
            setTimeout(function () { button.textContent = labelCopy; }, 1500);
        });
    }

    var copyPreview = document.getElementById("copy-preview");
    if (copyPreview && output) {
        copyPreview.addEventListener("click", function () {
            copyText(output.textContent, copyPreview);
        });
    }

    var copyPrompt = document.getElementById("copy-prompt");
    if (copyPrompt) {
        copyPrompt.addEventListener("click", function () {
            copyText(copyPrompt.getAttribute("data-text"), copyPrompt);
        });
    }
});
