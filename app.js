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

app.get('/', (req, res) => {
    db.query('SELECT * FROM laporan_kesehatan ORDER BY id DESC', (err, results) => {
        if (err) return res.send(err);
        
        // Template HTML Dashboard
        let rows = results.map(row => `
            <tr>
                <td>${row.nama}</td>
                <td>${row.deskripsi}</td>
                <td><img src="${row.foto_url}" width="100"></td>
            </tr>
        `).join('');

        res.send(`
            <html>
            <head>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <title>HealthTrack Cloud</title>
            </head>
            <body class="container mt-5">
                <h1 class="mb-4">Dashboard Laporan Kesehatan - Pandu</h1>
                <div class="card p-4 mb-4">
                    <h3>Kirim Laporan Baru</h3>
                    <form action="/lapor" method="POST" enctype="multipart/form-data">
                        <input type="text" name="nama_pelapor" class="form-control mb-2" placeholder="Nama Anda" required>
                        <textarea name="deskripsi" class="form-control mb-2" placeholder="Deskripsi Laporan" required></textarea>
                        <input type="file" name="foto" class="form-control mb-2" required>
                        <button type="submit" class="btn btn-primary">Kirim ke Cloud</button>
                    </form>
                </div>
                <table class="table table-striped">
                    <thead><tr><th>Nama</th><th>Deskripsi</th><th>Foto</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </body>
            </html>
        `);
    });
});