const { exec } = require('child_process');
const express = require('express');
const app = express();

exec('python3 app.py', (err, stdout, stderr) => {
    if (err) {
        console.error(`Error executing Python script: ${err}`);
        return;
    }
    console.log(`Python script output: ${stdout}`);
});

app.use(express.static('static'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/templates/index.html');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Node.js server is running on port ${PORT}`);
});

