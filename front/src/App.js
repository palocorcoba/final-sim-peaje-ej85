import React, { useState } from "react";

function App() {
  const [nIter, setNIter] = useState(1000);
  const [desde, setDesde] = useState(0);
  const [hasta, setHasta] = useState(100);
  const [datos, setDatos] = useState(null);
  const [loading, setLoading] = useState(false);

  const [config, setConfig] = useState({
    media_llegadas: 1.2,
    prob_tipo1: 0.1,
    prob_tipo2: 0.5,
    prob_tipo3: 0.15,
    prob_tipo4: 0.15,
    prob_tipo5: 0.1,
    monto_tipo1: 0,
    monto_tipo2: 3,
    monto_tipo3: 6,
    monto_tipo4: 9,
    monto_tipo5: 12,
    tiempo_tipo1: 0.5,
    tiempo_tipo2_a: 0.75,
    tiempo_tipo2_b: 0.92,
    tiempo_tipo3_a: 0.92,
    tiempo_tipo3_b: 1.42,
    tiempo_tipo4_a: 1.5,
    tiempo_tipo4_b: 2.17,
    tiempo_tipo5_a: 2.5,
    tiempo_tipo5_b: 3.5,
  });

  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: Number(value),
    }));
  };

  const fetchData = () => {

    const sumaProbabilidades =
    config.prob_tipo1 +
    config.prob_tipo2 +
    config.prob_tipo3 +
    config.prob_tipo4 +
    config.prob_tipo5;

  if (Math.abs(sumaProbabilidades - 1) > 0.0001) {
    alert(
      `La suma de las probabilidades debe ser 1. Actualmente es ${sumaProbabilidades.toFixed(
        4
      )}`
    );
    return; // no sigue con la simulación
  }

    setLoading(true);

    const params = new URLSearchParams({
      n_iteraciones: nIter,
      desde,
      hasta,
      media_llegadas: config.media_llegadas,
      prob_tipo1: config.prob_tipo1,
      prob_tipo2: config.prob_tipo2,
      prob_tipo3: config.prob_tipo3,
      prob_tipo4: config.prob_tipo4,
      prob_tipo5: config.prob_tipo5,
      monto_tipo1: config.monto_tipo1,
      monto_tipo2: config.monto_tipo2,
      monto_tipo3: config.monto_tipo3,
      monto_tipo4: config.monto_tipo4,
      monto_tipo5: config.monto_tipo5,
      tiempo_tipo1: config.tiempo_tipo1,
      tiempo_tipo2_a: config.tiempo_tipo2_a,
      tiempo_tipo2_b: config.tiempo_tipo2_b,
      tiempo_tipo3_a: config.tiempo_tipo3_a,
      tiempo_tipo3_b: config.tiempo_tipo3_b,
      tiempo_tipo4_a: config.tiempo_tipo4_a,
      tiempo_tipo4_b: config.tiempo_tipo4_b,
      tiempo_tipo5_a: config.tiempo_tipo5_a,
      tiempo_tipo5_b: config.tiempo_tipo5_b,
    });

    fetch(`http://127.0.0.1:8000/simular?${params.toString()}`)
      .then(async (res) => {
        if (!res.ok) {
          const error = await res.json();
          alert("Error: " + error.detail);
          setLoading(false);
          return;
        }
        const data = await res.json();
        setDatos(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error de red o servidor:", err);
        alert("Ocurrió un error al conectarse con el servidor.");
        setLoading(false);
      });
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
          Media llegadas:
          <input
            type="number"
            step="0.1"
            min={0}
            name="media_llegadas"
            value={config.media_llegadas}
            onChange={handleConfigChange}
          />
        </label>
      </div>

      <div style={{ marginTop: 10 }}>
        <h3>Probabilidades por tipo de auto (deben sumar 1)</h3>
        {[1, 2, 3, 4, 5].map((tipo) => (
          <div key={tipo}>
            <label>
              Tipo {tipo}:
              <input
                type="number"
                step="0.01"
                min={0}
                max={1}
                name={`prob_tipo${tipo}`}
                value={config[`prob_tipo${tipo}`]}
                onChange={handleConfigChange}
              />
            </label>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 10 }}>
        <h3>Monto por tipo de auto</h3>
        {[1, 2, 3, 4, 5].map((tipo) => (
          <div key={tipo}>
            <label>
              Tipo {tipo}:
              <input
                type="number"
                step="1"
                min={0}
                name={`monto_tipo${tipo}`}
                value={config[`monto_tipo${tipo}`]}
                onChange={handleConfigChange}
              />
            </label>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 10 }}>
        <h3>Tiempo de atención por tipo de auto</h3>
        <div>
          <label>
            Tipo 1 (minutos):
            <input
              type="number"
              step="0.01"
              min={0}
              name="tiempo_tipo1"
              value={config.tiempo_tipo1}
              onChange={handleConfigChange}
            />
          </label>
        </div>
        {[2, 3, 4, 5].map((tipo) => (
          <div key={tipo}>
            <label>
              Tipo {tipo} (A - B):
              <input
                type="number"
                step="0.01"
                name={`tiempo_tipo${tipo}_a`}
                value={config[`tiempo_tipo${tipo}_a`]}
                onChange={handleConfigChange}
              />
              -
              <input
                type="number"
                step="0.01"
                name={`tiempo_tipo${tipo}_b`}
                value={config[`tiempo_tipo${tipo}_b`]}
                onChange={handleConfigChange}
              />
            </label>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 20 }}>
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
