document.getElementById('prediction-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const ticker = document.getElementById('ticker').value.trim().toUpperCase();
  const date = document.getElementById('date').value;

  if (!ticker || !date) {
    alert("Please enter both ticker and date.");
    return;
  }

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, date })
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || 'Prediction failed.');
    }

    const data = await res.json();

    // Show the result card
    document.getElementById('resultCard').classList.remove('d-none');

    // Fill result section
    document.getElementById('result').innerHTML = `
      <h5>Prediction for ${ticker} on ${date}:</h5>
      <p><strong>Predicted Close:</strong> $${data.predicted_price}</p>
      <p><strong>Last Close:</strong> $${data.last_close}</p>
      <p><strong>Change:</strong> ${data.pct_change}%</p>
      <p><strong>Signal:</strong>
        <span class="badge bg-${
          data.signal === 'Buy'  ? 'success' :
          data.signal === 'Sell' ? 'danger' :
          'secondary'
        }">${data.signal}</span>
      </p>
    `;

    // Draw chart
    const ctx = document.getElementById('priceChart').getContext('2d');
    if (window.chart) window.chart.destroy();

    window.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.dates,
        datasets: [
          
          {
            label: 'SMA 20',
            data: data.sma20,
            borderColor: 'green',
            borderWidth: 2,
            fill: false
          },
          {
            label: 'EMA 20',
            data: data.ema20,
            borderColor: 'orange',
            borderWidth: 2,
            fill: false
          },
          {
            label: 'Predicted Price',
            data: data.dates.map(d =>
              d === data.predicted_point.date ? data.predicted_point.price : null
            ),
            borderColor: 'red',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 6,
            pointBackgroundColor:
              data.signal === 'Buy' ? 'green' :
              data.signal === 'Sell' ? 'red' :
              'gray',
            pointHoverRadius: 8,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Date',
              color: '#ccc'
            },
            ticks: {
              color: '#ccc'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Price ($)',
              color: '#ccc'
            },
            ticks: {
              color: '#ccc'
            }
          }
        }
      }
    });

  } catch (err) {
    alert("Error: " + err.message);
    document.getElementById('result').innerHTML = `<p class="text-danger">${err.message}</p>`;
  }
});
