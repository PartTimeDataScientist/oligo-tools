function resetInput() {
  document.getElementById('sequenceInput').value = '';
  document.getElementById('result').innerHTML = '';
}

function calculate() {
  const sequence = document.getElementById('sequenceInput').value;
  if (sequence.trim() === '') {
    alert('Please enter a sequence.');
    return;
  }

  const resultDiv = document.getElementById('result');
  //resultDiv.innerHTML = `<div aria-busy="true">Calculating...</div>`
  resultDiv.innerHTML = `<progress></progress>`

  // Make GET request to the API
  const apiUrl = `https://pepmass.fly.dev/calc/all_features?sequence=${sequence}`;
  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      displayResult(data);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      alert('Error fetching data. Please retry in a moment.');
    });
}

function displayResult(data) {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = `
    <h4>Results:</h4>
    <b>Molecular Weight:</b> ${data.MolWt}<br />
    <b>Exact Mass:</b> ${data.Exact}<br / >
    <b>Molecular Formula:</b> ${createMolecularFormula(data['Mol Formula'])}<br />
    <b>HPLC-SIM Ions:</b> ${createSIMIonList(data['HPLC-SIM Ions'])}<br />
    <b>MolWt Ions:</b> ${createIonList(data['MolWt Ions'])}<br />
    <b>HRMS Ions:</b> ${createIonList(data['HRMS Ions'])}<br />
  `;
}

function createMolecularFormula(obj) {
  let formula = '';
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      if (obj[key] > 0) {
        formula += `${key}<sub>${obj[key]}</sub>`;
      }
    }
  }
  return formula;
}

function createSIMIonList(obj) {
  let ions = '';
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
        ions += `${obj[key]}; `;
    }
  }
  return ions;
}

function createIonList(obj) {
  let ions = '';
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
        ions += `[M+${key}H]<sup>${key}+</sup>: ${obj[key]}; `;
    }
  }
  return ions;
}