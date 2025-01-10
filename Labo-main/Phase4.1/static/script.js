document.getElementById("execute").addEventListener("click", () => {
    const query = document.getElementById("query").value;

    fetch("/execute", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
    })
        .then((response) => response.json())
        .then((data) => {
            const resultDiv = document.getElementById("result");
            if (data.success) {
                if (data.data.columns) {
                    const table = document.createElement("table");
                    const thead = document.createElement("thead");
                    const tbody = document.createElement("tbody");

                    // Create table header
                    const headerRow = document.createElement("tr");
                    data.data.columns.forEach((col) => {
                        const th = document.createElement("th");
                        th.textContent = col;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);

                    // Create table rows
                    data.data.rows.forEach((row) => {
                        const tr = document.createElement("tr");
                        row.forEach((cell) => {
                            const td = document.createElement("td");
                            td.textContent = cell;
                            tr.appendChild(td);
                        });
                        tbody.appendChild(tr);
                    });

                    table.appendChild(thead);
                    table.appendChild(tbody);
                    resultDiv.innerHTML = "";
                    resultDiv.appendChild(table);
                } else {
                    resultDiv.textContent = data.data.message;
                }
            } else {
                resultDiv.textContent = `Erreur : ${data.error}`;
            }
        })
        .catch((error) => {
            console.error("Erreur:", error);
        });
});
