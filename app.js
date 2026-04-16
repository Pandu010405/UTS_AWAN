const express = require('express');
const mysql = require('mysql2');
const AWS = require('aws-sdk');
const multer = require('multer');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 1. KONEKSI DATABASE (RDS) [cite: 41, 50]
const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME
});

// 2. KONFIGURASI S3 
const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_ACCESS_KEY,
    secretAccessKey: process.env.AWS_SECRET_KEY
});

const upload = multer({ storage: multer.memoryStorage() });

// --- FITUR 1: DASHBOARD / VIEW DATA ---
app.get('/', (req, res) => {
    db.query('SELECT * FROM laporan_kesehatan', (err, results) => {
        if (err) return res.send(err);
        res.send(`<h1>HealthTrack Dashboard</h1><pre>${JSON.stringify(results, null, 2)}</pre>`);
    });
});

// --- FITUR 2 & 3: INPUT LAPORAN & UPLOAD FOTO KE S3 ---
app.post('/lapor', upload.single('foto'), (req, res) => {
    const { nama_pelapor, deskripsi } = req.body;
    const file = req.file;

    const params = {
        Bucket: process.env.S3_BUCKET,
        Key: `${Date.now()}_${file.originalname}`,
        Body: file.buffer,
        ContentType: file.mimetype
    };

    // Upload ke S3 [cite: 48]
    s3.upload(params, (err, data) => {
        if (err) return res.status(500).send(err);

        // Simpan URL S3 dan data ke RDS [cite: 50]
        const query = 'INSERT INTO laporan_kesehatan (nama, deskripsi, foto_url) VALUES (?, ?, ?)';
        db.query(query, [nama_pelapor, deskripsi, data.Location], (err, result) => {
            if (err) return res.status(500).send(err);
            res.send('Laporan Berhasil Terkirim ke Cloud!');
        });
    });
});

app.listen(3000, () => {
    console.log('Aplikasi HealthTrack berjalan di port 3000');
});