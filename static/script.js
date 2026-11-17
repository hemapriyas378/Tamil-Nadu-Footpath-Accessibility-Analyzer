
const API = "";

let map;
let markerLayer;

function getValue(record, possibleKeys) {
    for (const key of possibleKeys) {
        if (record[key] !== undefined && record[key] !== null && record[key] !== "") {
            return record[key];
        }
    }
    return null;
}

function initializeMap() {
    map = L.map("map").setView([10.7905, 78.7047], 7);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);
}

async function loadSummary() {
    try {
        const response = await fetch(`${API}/api/summary`);
        if (!response.ok) throw new Error("Summary API failed");

        const data = await response.json();

        document.getElementById("totalRecords").textContent =
            Number(data.total_records).toLocaleString();

        document.getElementById("districtCount").textContent =
            data.district_count;

        const features = data.feature_distribution || {};

        document.getElementById("footwayCount").textContent =
            features.footway || 0;

        document.getElementById("crossingCount").textContent =
            features.crossing || 0;

    } catch (error) {
        console.error("Summary error:", error);
    }
}

async function loadDistricts() {
    try {
        const response = await fetch(`${API}/api/districts`);
        if (!response.ok) throw new Error("District API failed");

        const data = await response.json();
        const select = document.getElementById("districtFilter");

        data.districts.forEach(district => {
            const option = document.createElement("option");
            option.value = district;
            option.textContent = district;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("District error:", error);
    }
}

async function loadRecords() {
    const district = document.getElementById("districtFilter").value;
    const feature = document.getElementById("featureFilter").value;

    const params = new URLSearchParams({ limit: "5000" });

    if (district) params.append("district", district);
    if (feature) params.append("feature_type", feature);

    try {
        const response = await fetch(`${API}/api/records?${params}`);

        if (!response.ok) throw new Error("Records API failed");

        const data = await response.json();

        displayRecords(data.records);
        displayMarkers(data.records);

        document.getElementById("recordCount").textContent =
            `Showing ${data.count.toLocaleString()} records`;

    } catch (error) {
        console.error("Records error:", error);
        document.getElementById("recordCount").textContent =
            "Unable to load records. Check the backend terminal.";
    }
}

function displayRecords(records) {
    const tbody = document.getElementById("recordsTable");
    tbody.innerHTML = "";

    records.slice(0, 200).forEach(record => {
        const latitude = getValue(record, ["latitude", "lat"]);
        const longitude = getValue(record, ["longitude", "lon", "lng"]);

        const score = getValue(record, [
            "accessibility_evidence_score"
        ]);

        const row = document.createElement("tr");

        const values = [
            getValue(record, ["district"]) ?? "-",
            getValue(record, ["feature_type"]) ?? "-",
            latitude ?? "-",
            longitude ?? "-",
            score ?? "Not available"
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });
}

function displayMarkers(records) {
    markerLayer.clearLayers();

    records.forEach(record => {
        const latitude = Number(
            getValue(record, ["latitude", "lat"])
        );

        const longitude = Number(
            getValue(record, ["longitude", "lon", "lng"])
        );

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude) ||
            latitude < 8 || latitude > 14 ||
            longitude < 76 || longitude > 81
        ) {
            return;
        }

        const district = getValue(record, ["district"]) ?? "Unknown";
        const feature = getValue(record, ["feature_type"]) ?? "Unknown";
        const score = getValue(record, [
            "accessibility_evidence_score"
        ]);

        const marker = L.circleMarker(
            [latitude, longitude],
            {
                radius: 5,
                color: "#1769aa",
                fillOpacity: 0.7
            }
        );

        marker.bindPopup(`
            <b>District:</b> ${district}<br>
            <b>Feature:</b> ${feature}<br>
            <b>Evidence Score:</b> ${score ?? "Not available"}
        `);

        markerLayer.addLayer(marker);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    initializeMap();

    await Promise.all([
        loadSummary(),
        loadDistricts()
    ]);

    await loadRecords();
    await loadCoverageChart();
    await loadDistrictComparison();
    loadDistrictComparison();
    loadSeparateDistrictCharts();
});

let coverageChart;

async function loadCoverageChart() {
    try {
        const response = await fetch("/api/coverage");

        if (!response.ok) {
            throw new Error("Coverage API failed");
        }

        const data = await response.json();

        const attributes = [
            "width",
            "surface",
            "wheelchair",
            "tactile_paving",
            "kerb",
            "sidewalk"
        ];

        const ctx = document.getElementById("coverageChart");

        if (coverageChart) {
            coverageChart.destroy();
        }

        coverageChart = new Chart(ctx, {
            type: "bar",

            data: {
                labels: data.map(item => item.district),

                datasets: attributes.map(attribute => ({
                    label: attribute.replaceAll("_", " "),
                    data: data.map(item => item[attribute])
                }))
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: "Mapped Attribute Coverage (%)"
                        }
                    },

                    x: {
                        ticks: {
                            maxRotation: 90,
                            minRotation: 60
                        }
                    }
                },

                plugins: {
                    title: {
                        display: true,
                        text: "Accessibility Attribute Coverage – 38 Districts"
                    },

                    tooltip: {
                        mode: "index",
                        intersect: false
                    }
                }
            }
        });

    } catch (error) {
        console.error("Coverage chart error:", error);
    }
}

let districtComparisonChart;

async function loadDistrictComparison() {
    try {
        const response = await fetch("/api/district-summary");

        if (!response.ok) {
            throw new Error("District comparison API failed");
        }

        const data = await response.json();

        const labels = data.map(item => item.district);

        const scores = data.map(item =>
            item.average_evidence_score === null
                ? null
                : Number(item.average_evidence_score)
        );

        const coverage = data.map(item =>
            item.average_attribute_coverage === null
                ? null
                : Number(item.average_attribute_coverage)
        );

        const ctx = document.getElementById(
            "districtComparisonChart"
        );

        if (districtComparisonChart) {
            districtComparisonChart.destroy();
        }

        districtComparisonChart = new Chart(ctx, {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Average Evidence Score",
                        data: scores,
                        yAxisID: "y",
                    },
                    {
                        label: "Average Attribute Coverage (%)",
                        data: coverage,
                        yAxisID: "y",
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: "Percentage / Score"
                        }
                    },

                    x: {
                        ticks: {
                            maxRotation: 90,
                            minRotation: 60
                        }
                    }
                },

                plugins: {
                    title: {
                        display: true,
                        text: "District Accessibility Evidence Comparison"
                    },

                    tooltip: {
                        mode: "index",
                        intersect: false
                    }
                }
            }
        });

    } catch (error) {
        console.error(
            "District comparison chart error:",
            error
        );
    }
}

async function loadDistrictComparison() {
    const canvas = document.getElementById("districtComparisonChart");

    if (!canvas) {
        console.error("District comparison chart element not found.");
        return;
    }

    try {
        const response = await fetch("/api/district-summary");

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        const labels = data.map(item => item.district);

        const evidenceScores = data.map(item =>
            item.average_evidence_score
        );

        const coverage = data.map(item =>
            item.average_attribute_coverage
        );

        const recordCounts = data.map(item =>
            item.record_count
        );

        if (window.districtComparisonChartInstance) {
            window.districtComparisonChartInstance.destroy();
        }

        window.districtComparisonChartInstance = new Chart(canvas, {
            data: {
                labels: labels,
                datasets: [
                    {
                        type: "bar",
                        label: "Average Evidence Score",
                        data: evidenceScores,
                        backgroundColor: "rgba(37, 99, 235, 0.65)",
                        borderColor: "#2563eb",
                        borderWidth: 1,
                        yAxisID: "scoreAxis"
                    },
                    {
                        type: "line",
                        label: "Attribute Coverage (%)",
                        data: coverage,
                        borderColor: "#e58b24",
                        backgroundColor: "#e58b24",
                        pointRadius: 3,
                        tension: 0.25,
                        yAxisID: "scoreAxis",
                        spanGaps: false
                    },
                    {
                        type: "line",
                        label: "Mapped Records",
                        data: recordCounts,
                        borderColor: "#15966a",
                        backgroundColor: "#15966a",
                        pointRadius: 3,
                        tension: 0.25,
                        yAxisID: "recordAxis"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: "top"
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;

                                if (value === null || value === undefined) {
                                    return context.dataset.label + ": No evidence";
                                }

                                return context.dataset.label + ": " + value;
                            }
                        }
                    }
                },
                scales: {
                    scoreAxis: {
                        type: "linear",
                        position: "left",
                        beginAtZero: true,
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: "Score / Coverage (%)"
                        }
                    },
                    recordAxis: {
                        type: "linear",
                        position: "right",
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        },
                        title: {
                            display: true,
                            text: "Mapped Records"
                        }
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 65,
                            minRotation: 45
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("District comparison error:", error);
    }
}

async function loadSeparateDistrictCharts() {
    try {
        const response = await fetch("/api/district-summary");

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        const labels = data.map(item => item.district);

        const coverageData = data.map(item =>
            item.average_attribute_coverage
        );

        const evidenceData = data.map(item =>
            item.average_evidence_score
        );

        // Attribute Coverage Chart
        const coverageCanvas = document.getElementById(
            "districtCoverageChart"
        );

        if (coverageCanvas) {
            if (window.coverageChartInstance) {
                window.coverageChartInstance.destroy();
            }

            window.coverageChartInstance = new Chart(
                coverageCanvas,
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Attribute Coverage (%)",
                            data: coverageData,
                            backgroundColor: "rgba(22, 163, 106, 0.65)",
                            borderColor: "#16a36a",
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "top"
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const value = context.raw;

                                        return value === null
                                            ? "No coverage data"
                                            : `Coverage: ${value}%`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                title: {
                                    display: true,
                                    text: "Attribute Coverage (%)"
                                }
                            },
                            x: {
                                ticks: {
                                    maxRotation: 60,
                                    minRotation: 45
                                }
                            }
                        }
                    }
                }
            );
        }

        // Evidence Score Chart
        const evidenceCanvas = document.getElementById(
            "districtEvidenceChart"
        );

        if (evidenceCanvas) {
            if (window.evidenceChartInstance) {
                window.evidenceChartInstance.destroy();
            }

            window.evidenceChartInstance = new Chart(
                evidenceCanvas,
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Average Evidence Score",
                            data: evidenceData,
                            backgroundColor: "rgba(37, 99, 235, 0.65)",
                            borderColor: "#2563eb",
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "top"
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const value = context.raw;

                                        return value === null
                                            ? "Insufficient evidence: no score available"
                                            : `Evidence Score: ${value}/100`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                min: 0,
                                max: 100,
                                title: {
                                    display: true,
                                    text: "Evidence Score (0–100)"
                                }
                            },
                            x: {
                                ticks: {
                                    maxRotation: 60,
                                    minRotation: 45
                                }
                            }
                        }
                    }
                }
            );
        }

    } catch (error) {
        console.error("Separate district charts error:", error);
    }
}
