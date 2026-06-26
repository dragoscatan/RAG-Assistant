import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [fisier, setFisier] = useState(null);
  const [intrebare, setIntrebare] = useState('');
  const [istoricChat, setIstoricChat] = useState([]);
  const [seIncarca, setSeIncarca] = useState(false);
  const [documente, setDocumente] = useState([]);


  useEffect(() => {
    fetch('http://localhost:8000/documents')
      .then(res => res.json())
      .then(data => {

        setDocumente(data.documente || []);
      })
      .catch(err => console.log("eroare la docs", err));
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!fisier) {
      alert("Selectează un fișier mai întâi!");
      return;
    }

    const formData = new FormData();
    formData.append("file", fisier);
    setSeIncarca(true);

    try {
      const raspuns = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (raspuns.ok) {
        alert("Fisier incarcat cu succes!");
        setFisier(null);
        document.getElementById('fileInput').value = '';

        const resDocs = await fetch('http://localhost:8000/documents');
        const dataDocs = await resDocs.json();
        setDocumente(dataDocs.documente || []);
      }
    } catch (eroare) {
      console.error(eroare);
    }

    setSeIncarca(false);
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (intrebare.trim() === '') return;

    const intrebareCurenta = intrebare;
    const chatNou = [...istoricChat, { tip: 'user', text: intrebareCurenta }];

    setIstoricChat(chatNou);
    setIntrebare('');
    setSeIncarca(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intrebare: intrebareCurenta,
          istoric: istoricChat // trimit pe ala vechi aici? cred ca da
        }),
      });

      const data = await res.json();
      console.log("Raspuns AI:", data); // util pt debug

      setIstoricChat([...chatNou, { tip: 'ai', text: data.raspuns_ai, surse: data.surse }]);

    } catch (e) {
      console.log("Eroare chat:", e);
    }

    setSeIncarca(false);
  };

  return (
    <div className="container">
      <h1 className="titlu">Platformă Analiză Documentație Tehnică</h1>

      <div className="top-panels">
        {/* Partea de Upload */}
        <div className="panel card">
          <h3>Adaugă un manual (PDF)</h3>
          <form onSubmit={handleUpload} className="upload-form">
            <input
              id="fileInput"
              type="file"
              accept=".pdf"
              onChange={(e) => setFisier(e.target.files[0])}
              className="file-input"
            />
            <button type="submit" disabled={seIncarca || !fisier} className="btn primary-btn">
              {seIncarca ? "Așteaptă..." : "Încarcă și Vectorizează"}
            </button>
          </form>
        </div>

        {/* Lista documente */}
        <div className="panel card">
          <h3>Baza de date activă</h3>
          {documente.length === 0 ? (
            <p className="empty-text">Nu exista niciun document incarcat.</p>
          ) : (
            <ul className="doc-list">
              {documente.map((doc, index) => (
                <li key={index}>{doc}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Zona de chat */}
      <div className="chat-section card">
        <h3>Discută cu Asistentul</h3>

        <div className="chat-box">
          {istoricChat.length === 0 && <p className="start-text">Scrie un mesaj ca sa incepi.</p>}

          {istoricChat.map((mesaj, index) => (
            <div key={index} className={`mesaj-wrapper ${mesaj.tip}`}>
              <div className="bula-mesaj">
                <div>{mesaj.text}</div>

                {mesaj.tip === 'ai' && mesaj.surse && mesaj.surse.length > 0 && (
                  <div className="surse-container">
                    <strong>Surse:</strong>
                    <ul>
                      {mesaj.surse.map((s, i) => (
                        <li key={i}>{s.document} ({s.fragmente_folosite} fragmente)</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          {seIncarca && <div className="loading-text">Se generează...</div>}
        </div>

        <form onSubmit={handleChat} className="chat-form">
          <input
            type="text"
            value={intrebare}
            onChange={(e) => setIntrebare(e.target.value)}
            placeholder="Pune o intrebare aici..."
            disabled={seIncarca}
            className="chat-input"
          />
          <button type="submit" disabled={seIncarca || !intrebare} className="btn success-btn">
            Trimite
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;