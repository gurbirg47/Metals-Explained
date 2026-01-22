export default function ApiTestPage() {
    return (
        <div style={{ padding: '20px', fontFamily: 'monospace' }}>
            <h1>Metals, Explained — App Online</h1>
            <p>Frontend Build Success: {new Date().toISOString()}</p>
            <hr />
            <p>Checking Backend Health...</p>
            <div id="health-status">Pinging /api/health...</div>

            <script dangerouslySetInnerHTML={{
                __html: `
        fetch('/api/health')
          .then(r => r.json())
          .then(data => {
            document.getElementById('health-status').innerText = 'Backend OK: ' + JSON.stringify(data);
            document.getElementById('health-status').style.color = 'green';
          })
          .catch(err => {
            document.getElementById('health-status').innerText = 'Backend Error: ' + err.message;
            document.getElementById('health-status').style.color = 'red';
          });
      `}} />
        </div>
    );
}
