import React, { useState } from "react";

function App() {
  const [nIter, setNIter] = useState(1000);
  const [desde, setDesde] = useState(0);
  const [hasta, setHasta] = useState(100);
  const [datos, setDatos] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = () => {
    setLoading(true);
    fetch(
      `http://127.0.0.1:8000/simular?n_iteraciones=${nIter}&desde=${desde}&hasta=${hasta}`
    )
      .then((res) => res.json())
      .then((data) => {
        setDatos(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const thStyle = {
    border: "1px solid #ddd",
    padding: "8px",
    background: "#eee",
    textAlign: "left",
  };

  const tdStyle = {
    border: "1px solid #ddd",
    padding: "8px",
  };

  const renderResultados = () => {
    if (!datos) return null;

    return (
      <div style={{ marginTop: 20 }}>
        <h2>Resultados</h2>
        <div
          style={{
            background: "#f9f9f9",
            padding: "10px",
            borderRadius: "4px",
            maxWidth: 600,
          }}
        >
          <p>
            <strong>Promedio de cabinas habilitadas:</strong>{" "}
            {datos.promedio_cabinas.toFixed(2)}
          </p>
          <p>
            <strong>Monto recaudado:</strong> ${datos.monto_recaudado}
          </p>
          <p>
            <strong>Porcentaje por cantidad de cabinas:</strong>
          </p>
          <ul>
            {Object.entries(datos.porcentaje_por_cantidad).map(([key, val]) => (
              <li key={key}>
                {key} cabinas: {val.toFixed(2)}%
              </li>
            ))}
          </ul>
          <p>
            <strong>Máximo de cabinas habilitadas:</strong> {datos.max_cabinas}
          </p>
        </div>
      </div>
    );
  };

  const renderTablaIteraciones = () => {
    if (!datos) return null;

    const iteraciones = datos.iteraciones || [];
    // No slice en frontend! Backend ya filtró las iteraciones mostradas.
    // Solo usamos directamente datos.iteraciones y la última iteración global

    const ultimaIteracion = datos.ultima_iteracion;

    return (
      <div style={{ marginTop: 20 }}>
        <h3>Iteraciones</h3>
        <div
          style={{
            maxHeight: "400px",
            overflowY: "auto",
            border: "1px solid #ddd",
            maxWidth: 800,
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={thStyle}>#</th>
                <th style={thStyle}>Reloj</th>
                <th style={thStyle}>Evento</th>
                <th style={thStyle}>Autos</th>
                <th style={thStyle}>En sistema</th>
                <th style={thStyle}>Cabinas habilitadas</th>
              </tr>
            </thead>
            <tbody>
              {iteraciones.map((item) => (
                <tr
                  key={item.numero_iteracion}
                  style={{
                    background:
                      item.numero_iteracion % 2 === 0 ? "#f2f2f2" : "#fff",
                  }}
                >
                  <td style={tdStyle}>{item.numero_iteracion + 1}</td>
                  <td style={tdStyle}>{item.reloj.toFixed(2)}</td>
                  <td style={tdStyle}>{item.evento}</td>
                  <td style={tdStyle}>{item.autos}</td>
                  <td style={tdStyle}>{item.en_sistema}</td>
                  <td style={tdStyle}>{item.cabinas_habilitadas}</td>
                </tr>
              ))}

              {/* Fila última iteración global */}
              {ultimaIteracion && (
                <tr style={{ background: "#e6ffe6", fontWeight: "bold" }}>
                  <td style={tdStyle}>{ultimaIteracion.numero_iteracion + 1}</td>
                  <td style={tdStyle}>{ultimaIteracion.reloj.toFixed(2)}</td>
                  <td style={tdStyle}>{ultimaIteracion.evento}</td>
                  <td style={tdStyle}>{ultimaIteracion.autos}</td>
                  <td style={tdStyle}>{ultimaIteracion.en_sistema}</td>
                  <td style={tdStyle}>{ultimaIteracion.cabinas_habilitadas}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Simulación Peaje</h1>

      <div>
        <label>
          Iteraciones:
          <input
            type="number"
            value={nIter}
            onChange={(e) => setNIter(Number(e.target.value))}
            min={1}
            max={100000}
          />
        </label>
      </div>
      <div>
        <label>
          Desde:
          <input
            type="number"
            value={desde}
            onChange={(e) => setDesde(Number(e.target.value))}
            min={0}
            max={nIter}
          />
        </label>
      </div>
      <div>
        <label>
          Hasta:
          <input
            type="number"
            value={hasta}
            onChange={(e) => setHasta(Number(e.target.value))}
            min={desde}
            max={nIter}
          />
        </label>
      </div>
      <button onClick={fetchData} disabled={loading}>
        {loading ? "Simulando..." : "Simular"}
      </button>

      {renderResultados()}
      {renderTablaIteraciones()}
    </div>
  );
}

export default App;
